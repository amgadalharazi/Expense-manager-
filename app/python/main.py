import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from expense_page import ExpenseManager  # Ensure this module exists


class CustomLabel(QLabel):

    def __init__(self, text, parent=None, font_size=22, border_radius=20, padding=100, min_height=50):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            padding: {padding}px;
            background-color: #3498db;
            font-size: {font_size}px;
            font-weight: bold;
            border-radius: {border_radius}px;
            color: #fff;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(min_height)


class CustomButton(QPushButton):

    def __init__(self, text, parent=None, font_size=22, border_radius=20, padding=0):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                font-size: 22px;
                font-weight: bold;
                border-radius: 20px;
                color: #fff;
                padding: 50px;
            }
            QPushButton:hover {
                background-color: #2980b9;  /* Darker shade on hover */
            }
            QPushButton:pressed {
                background-color: #1c6692;  /* Even darker when clicked */
            }
        """)
        # Set the button to expand horizontally
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(50)  # Ensures the button has a reasonable height


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Amgard")
        self.setGeometry(100, 100, 1000, 400)
        self.setStyleSheet("background-color: #f5f5f5;")

        # Stacked widget to manage multiple pages
        self.stacked_widget = QStackedWidget(self)

        # Create Main Page
        self.main_page = QWidget()
        main_layout = QVBoxLayout(self.main_page)

        self.welcome = CustomLabel("Welcome to Amgard", font_size=24)
        
        # Expense manager
        self.expense_button = CustomButton("Go to Expense Manager")
        self.expense_button.clicked.connect(self.go_to_expense_manager)
        
        # Notes manager
        self.notes_button = CustomButton("Add Notes")
        #self.notes_button.click.connect(self.go_to_notes)

        # Add stretchable space between label & button
        main_layout.addWidget(self.welcome, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addStretch(1)  # Pushes the button to the center
        main_layout.addWidget(self.expense_button)  # Button now stretches automatically
        main_layout.addStretch(2)  # Pushes everything upwards slightly
        main_layout.addWidget(self.notes_button)
        
        

        # Create Expense Manager Page
        self.expense_manager = ExpenseManager(self.stacked_widget)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_page)  # Index 0
        self.stacked_widget.addWidget(self.expense_manager)  # Index 1

        # Main Layout
        container_layout = QVBoxLayout(self)
        container_layout.addWidget(self.stacked_widget)
        self.setLayout(container_layout)

    def go_to_expense_manager(self):
        """Switch to the expense manager page."""
        self.stacked_widget.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
