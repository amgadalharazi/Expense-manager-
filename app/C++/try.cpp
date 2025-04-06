#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>
#include <cstring>
#include <sys/socket.h>
#include <sys/un.h>    // Added for struct sockaddr_un
#include <unistd.h>
#include <arpa/inet.h> // Added for htonl/ntohl
#include <nlohmann/json.hpp>
#include <chrono>

using json = nlohmann::json;

int main() {
    // Get SWAYSOCK path from environment
    const char* sock_path = getenv("SWAYSOCK");
    if (!sock_path) {
        std::cerr << "SWAYSOCK not set. Are you running under Sway?" << std::endl;
        return 1;
    }

    // Connect to the Sway IPC socket
    int sock = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path)-1);

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("connect");
        close(sock);
        return 1;
    }

    // Subscribe to window events
    json subscribe_payload = json::array({"window"});
    std::string payload_str = subscribe_payload.dump();

    // Prepare IPC header
    std::string header = "i3-ipc";
    uint32_t length = htonl(payload_str.size());
    uint32_t type = htonl(2); // SUBSCRIBE message type

    // Send subscription request
    send(sock, header.c_str(), header.size(), 0);
    send(sock, &length, sizeof(length), 0);
    send(sock, &type, sizeof(type), 0);
    send(sock, payload_str.c_str(), payload_str.size(), 0);

    // Read subscription response
    char magic[6];
    uint32_t recv_length, recv_type;
    recv(sock, magic, 6, 0);
    recv(sock, &recv_length, 4, 0);
    recv(sock, &recv_type, 4, 0);
    recv_length = ntohl(recv_length);
    recv_type = ntohl(recv_type);

    std::vector<char> buf(recv_length);
    recv(sock, buf.data(), recv_length, 0);
    json response = json::parse(buf);

    if (!response.value("success", false)) {
        std::cerr << "Subscription failed" << std::endl;
        close(sock);
        return 1;
    }

    // Event loop to handle incoming focus events
    while (true) {
        // Read event header
        if (recv(sock, magic, 6, 0) != 6) break;
        recv(sock, &recv_length, 4, 0);
        recv(sock, &recv_type, 4, 0);
        recv_length = ntohl(recv_length);
        recv_type = ntohl(recv_type);

        // Read event payload
        buf.resize(recv_length);
        if (recv(sock, buf.data(), recv_length, 0) != (ssize_t)recv_length) break;
        json event = json::parse(buf);

        // Check for window focus events
        if (recv_type == 0 && event.value("change", "") == "focus") {
            json container = event.value("container", json());
            if (!container.is_null()) {
                std::string app_id = container.value("app_id", "");
                std::string name = container.value("name", "");
                std::string window_class = container.value("window_properties", json()).value("class", "");

                auto now = std::chrono::system_clock::now();
                std::time_t now_time = std::chrono::system_clock::to_time_t(now);

                std::cout << "Focus changed to: " << name
                          << " (app_id: " << app_id
                          << ", class: " << window_class
                          << ") at " << std::ctime(&now_time);
            }
        }
    }

    close(sock);
    return 0;
}