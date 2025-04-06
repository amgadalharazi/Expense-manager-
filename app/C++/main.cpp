#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <mysql.h>
#include <sys/types.h>
#include <unistd.h> // For daemonizing on Linux
#include <signal.h> // For signal handling
#include <fstream>  // For logging to a file

// Global flag to control the daemon loop
volatile sig_atomic_t keepRunning = 1;

// Signal handler to gracefully stop the daemon
void signalHandler(int signal) {
    if (signal == SIGTERM || signal == SIGINT) {
        keepRunning = 0;
    }
}

// Function to check if a process is running by name
bool isProcessRunning(const std::string& processName) {
#ifdef _WIN32
    std::string command = "tasklist | findstr /i \"" + processName + "\" >nul 2>&1";
#else
    std::string command = "pgrep -x " + processName + " > /dev/null 2>&1";
#endif
    return system(command.c_str()) == 0;
}

// Function to log an event to the MariaDB database
void logEventToDatabase(MYSQL* conn, const std::string& eventType) {
    if (!conn) {
        std::cerr << "Database connection is not established!" << std::endl;
        return;
    }

    // Get current timestamp
    auto now = std::chrono::system_clock::now();
    std::time_t now_time = std::chrono::system_clock::to_time_t(now);
    char timestamp[100];
    std::strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", std::localtime(&now_time));

    // Prepare the SQL query
    std::string query = "INSERT INTO vscode_events (event_type, event_time) VALUES ('" +
                        eventType + "', '" + timestamp + "')";

    // Execute the query
    if (mysql_query(conn, query.c_str())) {
        std::cerr << "Error executing query: " << mysql_error(conn) << std::endl;
    } else {
        std::cout << "Logged event: " << eventType << " at " << timestamp << std::endl;
    }
}

// Function to log messages to a file
void logToFile(const std::string& message) {
    std::ofstream logFile("vscode_monitor.log", std::ios::app);
    if (logFile.is_open()) {
        logFile << message << std::endl;
        logFile.close();
    }
}

int main() {
    // Daemonize the process (Linux-specific)
#ifndef _WIN32
    pid_t pid = fork();
    if (pid < 0) {
        std::cerr << "Failed to fork process." << std::endl;
        return 1;
    }
    if (pid > 0) {
        // Parent process exits
        return 0;
    }

    // Create a new session for the child process
    if (setsid() < 0) {
        std::cerr << "Failed to create a new session." << std::endl;
        return 1;
    }

    // Change working directory to root (optional)
    chdir("/");

    // Close standard file descriptors
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);
#endif

    // Set up signal handlers
    signal(SIGTERM, signalHandler);
    signal(SIGINT, signalHandler);

    // Database connection details
    const char* host = "localhost";
    const char* user = "root"; // Replace with your MariaDB username
    const char* password = "qwiop148"; // Replace with your MariaDB password
    const char* database = "app";

    // Initialize MariaDB connection
    MYSQL* conn = mysql_init(nullptr);
    if (!mysql_real_connect(conn, host, user, password, database, 0, nullptr, 0)) {
        logToFile("Error connecting to database: " + std::string(mysql_error(conn)));
        return 1;
    }

    logToFile("Connected to MariaDB successfully!");

    // Process name for VSCode (platform-specific)
#ifdef _WIN32
    std::string processName = "Code.exe";
#else
    std::string processName = "code";
#endif

    bool wasRunning = false; // Tracks whether VSCode was running in the previous iteration

    while (keepRunning) {
        bool isRunning = isProcessRunning(processName);

        if (isRunning && !wasRunning) {
            // VSCode was just opened
            logEventToDatabase(conn, "open");
            logToFile("VSCode opened.");
            wasRunning = true;
        } else if (!isRunning && wasRunning) {
            // VSCode was just closed
            logEventToDatabase(conn, "close");
            logToFile("VSCode closed.");
            wasRunning = false;
        }

        // Wait for a short interval before checking again
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    // Clean up
    mysql_close(conn);
    logToFile("Daemon stopped.");
    return 0;
}