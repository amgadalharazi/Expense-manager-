import sys
import mysql.connector
from datetime import datetime
from fpdf import FPDF
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QTextEdit, QHeaderView, QFileDialog, QLabel, QSizePolicy, QHBoxLayout,
    QAbstractItemView
)
from PySide6.QtCore import Qt

# Database Connection Functions
def create_database(db_name):
    conn = mysql.connector.connect(host="localhost", user="root", password="qwiop148")
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    conn.close()

def delete_database(db_name):
    conn = mysql.connector.connect(host="localhost", user="root", password="qwiop148")
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
    conn.close()

def connect_database(db_name):
    conn = mysql.connector.connect(host="localhost", user="root", password="qwiop148", database=db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            category VARCHAR(255) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    return conn, cursor


"""________________________________________________________"""
"""                    The Design                          """
"""________________________________________________________"""

class CustomLabel(QLabel):
    def __init__(self, text, parent=None, font_size=22, border_radius=20, padding=20, min_height=50):
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
    def __init__(self, text, parent=None, font_size=14, border_radius=20, padding=10):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #3498db;
                font-size: {font_size}px;
                font-weight: bold;
                border-radius: {border_radius}px;
                color: #fff;
                padding: {padding}px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #1c6692;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(50)

class CustomLineEdit(QLineEdit):
    def __init__(self, placeholder_text="", parent=None, font_size=14, border_radius=8, padding=10):
        super().__init__(parent)
        self.setPlaceholderText(placeholder_text)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: #f9f9f9;
                font-size: {font_size}px;
                font-weight: normal;
                border: 2px solid #dcdcdc;
                border-radius: {border_radius}px;
                color: #333;
                padding: {padding}px;
            }}
            QLineEdit:focus {{
                border: 2px solid #3498db;
            }}
            QLineEdit:hover {{
                border: 2px solid #bdc3c7;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(40)

class ExpenseManager(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.conn = None
        self.cursor = None
        
        # Main layout (Vertical) to ensure the Back button is on top
        main_layout = QVBoxLayout()

        # Back Button (At the top)
        self.back_button = CustomButton("Back to Main Page", self)
        self.back_button.clicked.connect(self.go_to_main_page)
        main_layout.addWidget(self.back_button)

        # Horizontal layout for left (inputs & buttons) and right (table)
        content_layout = QHBoxLayout()

        # Left layout (Inputs & Buttons)
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)  # Align items to the top

        # Database Name Input
        self.db_name_input = CustomLineEdit(placeholder_text="Enter Database Name", parent=self)
        left_layout.addWidget(self.db_name_input)

        # Database Buttons Layout
        db_layout = QHBoxLayout()
        self.create_db_button = CustomButton("Create Database", self)
        self.create_db_button.clicked.connect(self.create_new_database)
        db_layout.addWidget(self.create_db_button)

        self.use_db_button = CustomButton("Use Database", self)
        self.use_db_button.clicked.connect(self.use_database)
        db_layout.addWidget(self.use_db_button)

        self.delete_db_button = CustomButton("Delete Database", self)
        self.delete_db_button.clicked.connect(self.delete_db)
        db_layout.addWidget(self.delete_db_button)

        left_layout.addLayout(db_layout)

        # Expense Inputs
        self.category_input = CustomLineEdit(placeholder_text="Enter Item", parent=self)
        left_layout.addWidget(self.category_input)

        self.amount_input = CustomLineEdit(placeholder_text="Enter Amount", parent=self)
        left_layout.addWidget(self.amount_input)

        # Description Input
        self.description_input = QTextEdit(self)
        self.description_input.setPlaceholderText("Enter Description")
        self.description_input.setFixedHeight(80)  # Larger fixed height, no scrolling needed for typical entries
        self.description_input.setTabChangesFocus(True)  # Tab moves to next field instead of inserting tab
        self.description_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font-family: Arial, sans-serif;
            }
            QTextEdit:focus {
                border-color: #80bdff;
            }
        """)
        left_layout.addWidget(self.description_input)

        # Expense Buttons Layout
        items_layout = QHBoxLayout()

        self.add_button = CustomButton("Add Expense", self)
        self.add_button.clicked.connect(self.add_expense)
        items_layout.addWidget(self.add_button)

        self.delete_button = CustomButton("Delete Expense", self)
        self.delete_button.clicked.connect(self.delete_expense)
        items_layout.addWidget(self.delete_button)

        left_layout.addLayout(items_layout)

        # Export Button
        self.export_button = CustomButton("Export to PDF", self)
        self.export_button.clicked.connect(self.export_to_pdf)
        left_layout.addWidget(self.export_button)

        # Create a wrapper widget for the left layout to maintain alignment
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Fixed height policy

        # Add left widget to content layout
        content_layout.addWidget(left_widget)

        # Table Styling
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Items", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Make the items Editable
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.itemChanged.connect(self.update_database)

        # Remove row numbers (index column)
        self.table.verticalHeader().setVisible(False)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #bfbfbf;
                border-radius: 5px;
                gridline-color: #d3d3d3;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                padding: 5px;
                font-weight: bold;
                border: 1px solid #bfbfbf;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        content_layout.addWidget(self.table)

        # Set stretch factor to make table expand but keep left side fixed
        content_layout.setStretchFactor(left_widget, 0)  # Don't stretch
        content_layout.setStretchFactor(self.table, 1)   # Allow stretching

        # Add content_layout to main_layout (under Back button)
        main_layout.addLayout(content_layout)

        # Set the main layout
        self.setLayout(main_layout)

    def create_new_database(self):
        db_name = self.db_name_input.text().strip()
        if db_name:
            create_database(db_name)
            QMessageBox.information(self, "Success", f"Database '{db_name}' created!")
        else:
            QMessageBox.warning(self, "Error", "Please enter a database name.")

    def use_database(self):
        db_name = self.db_name_input.text().strip()
        if not db_name:
            db_name = "mydb"  # Use the default database if no name is provided

        try:
            self.conn, self.cursor = connect_database(db_name)
            self.refresh_table()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")

    def delete_db(self):
        db_name = self.db_name_input.text().strip()
        if db_name:
            delete_database(db_name)
            QMessageBox.information(self, "Success", f"Database '{db_name}' deleted!")
        else:
            QMessageBox.warning(self, "Error", "Please enter a database name.")
        self.clear_inputs()

    def adjust_description_height(self):
        doc_height = self.description_input.document().size().height()
        max_height = 100
        self.description_input.setFixedHeight(min(max_height, int(doc_height) + 10))

    def refresh_table(self):
        if not self.cursor:
            return
        self.cursor.execute("SELECT id, date, category, amount, description FROM expenses ORDER BY id")
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, item in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(item)))

    def add_expense(self):
        if not self.cursor or not self.conn:
            QMessageBox.warning(self, "Error", "No database selected!")
            return

        today_date = datetime.today().strftime('%Y-%m-%d')
        category = self.category_input.text().strip()
        amount = self.amount_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not category or not amount:
            QMessageBox.warning(self, "Error", "Category and Amount are required!")
            return

        try:
            amount_float = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid amount. Please enter a number.")
            return

        try:
            self.cursor.execute(
                "INSERT INTO expenses (date, category, amount, description) VALUES (%s, %s, %s, %s)",
                (today_date, category, amount_float, description)
            )
            self.conn.commit()
            self.refresh_table()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")
        self.clear_inputs()

  
    def delete_expense(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an expense to delete.")
            return

        # Retrieve expense ID
        expense_id_item = self.table.item(selected_row, 0)
        if not expense_id_item:
            QMessageBox.critical(self, "Error", "Failed to retrieve expense ID.")
            return

        expense_id = expense_id_item.text()

        try:
            # Delete from database
            self.cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
            self.conn.commit()

            # Reset Auto-Increment (ONLY IF NEEDED)
            self.cursor.execute("SET @num := 0;")
            self.cursor.execute("UPDATE expenses SET id = @num := (@num+1);")
            self.cursor.execute("ALTER TABLE expenses AUTO_INCREMENT = 1;")
            self.conn.commit()

            # Refresh Table
            self.refresh_table()

            QMessageBox.information(self, "Success", "Expense deleted and IDs updated!")
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")

    def update_database(self, item):
        if not self.cursor or not self.conn:
            return

        row = item.row()
        column = item.column()
        new_value = item.text()

        # Get the expense ID (Assuming ID is always in column index 0)
        expense_id_item = self.table.item(row, 0)
        if not expense_id_item:
            return
        expense_id = expense_id_item.text()

        # Define column names matching the database
        column_mapping = {1: "date", 2: "category", 3: "amount", 4: "description"}

        if column in column_mapping:
            column_name = column_mapping[column]

            # Convert amount to float if required
            if column_name == "amount":
                try:
                    new_value = float(new_value)
                except ValueError:
                    QMessageBox.warning(self, "Error", "Invalid amount entered!")
                    return

            # Update the database
            try:
                query = f"UPDATE expenses SET {column_name} = %s WHERE id = %s"
                self.cursor.execute(query, (new_value, expense_id))
                self.conn.commit()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", f"Database error: {err}")


    def export_to_pdf(self):
        """Export expense data to a PDF file with proper formatting and error handling."""
        # Check if database connection exists
        if not self.cursor:
            QMessageBox.warning(self, "Error", "No database selected!")
            return

        # Get file name from save dialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not file_name:
            return  # User canceled the dialog
        
        # If file doesn't end with .pdf, add the extension
        if not file_name.lower().endswith('.pdf'):
            file_name += '.pdf'
        
        try:
            # Fetch data from database ordered by ID
            self.cursor.execute("""
                SELECT id, date, category, amount, description 
                FROM expenses 
                ORDER BY id ASC
            """)
            rows = self.cursor.fetchall()
            columns = ["ID", "Date", "Category", "Amount", "Description"]
            
            if not rows:
                QMessageBox.warning(self, "Error", "No data to export.")
                return
                
            # Create PDF document
            pdf = self._create_pdf_report(columns, rows, file_name)
            
            QMessageBox.information(self, "Success", f"PDF file '{file_name}' created successfully!")
            self.clear_inputs()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")
        
    def _create_pdf_report(self, columns, rows, file_name):
        """Create a formatted PDF report with the expense data."""
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Expenses Report", ln=True, align="C")
        
        # Add date
        pdf.set_font("Arial", "I", 10)
        current_date = datetime.now().strftime("%Y-%m-%d")
        pdf.cell(190, 10, f"Generated on: {current_date}", ln=True, align="R")
        pdf.ln(5)
        
        # Configure table settings
        col_widths = [20, 30, 35, 30, 75]  # Adjust column widths as needed
        total_width = sum(col_widths)
        line_height = 7
        
        # Draw header
        self._draw_table_header(pdf, columns, col_widths, line_height)
        
        # Draw rows
        pdf.set_font("Arial", "", 10)
        fill = False
        total_amount = 0
        
        for row in rows:
            # Track cursor position to check if we need a new page
            if pdf.get_y() > 250:  # Close to bottom margin
                pdf.add_page()
                self._draw_table_header(pdf, columns, col_widths, line_height)
            
            x_pos = pdf.get_x()
            max_height = line_height
            
            # Calculate row height based on content
            for i, item in enumerate(row):
                content = str(item)
                wrapped_text = self._wrap_text(pdf, content, col_widths[i] - 4)
                lines_count = len(wrapped_text)
                item_height = lines_count * line_height
                max_height = max(max_height, item_height)
                
                # Track amount for total calculation
                if i == 3:  # Amount column
                    try:
                        total_amount += float(content)
                    except ValueError:
                        pass
            
            # Draw cells with proper wrapping
            y_pos = pdf.get_y()
            for i, item in enumerate(row):
                content = str(item)
                pdf.set_xy(x_pos, y_pos)
                
                # Format amount as currency if it's in the amount column
                if i == 3:  # Amount column
                    try:
                        content = f"{float(content):.2f}"
                    except ValueError:
                        pass
                        
                # Draw cell content with wrapping
                wrapped_text = self._wrap_text(pdf, content, col_widths[i] - 4)
                for line in wrapped_text:
                    pdf.set_xy(x_pos + 2, pdf.get_y())
                    pdf.cell(col_widths[i] - 4, line_height, line, 0, 1)
                
                # Draw cell border
                pdf.rect(x_pos, y_pos, col_widths[i], max_height)
                x_pos += col_widths[i]
            
            pdf.set_y(y_pos + max_height)
            fill = not fill  # Alternate row colors
        
        # Add total row
        pdf.set_font("Arial", "B", 10)
        x_pos = pdf.get_x()
        pdf.set_xy(x_pos, pdf.get_y() + 5)
        pdf.cell(sum(col_widths[:3]), line_height, "Total:", 0, 0, "R")
        pdf.cell(col_widths[3], line_height, f"{total_amount:.2f}", 1, 1, "R")
        
        # Save PDF
        try:
            pdf.output(file_name)
            return pdf
        except Exception as e:
            raise Exception(f"Error saving PDF: {str(e)}")

    def _draw_table_header(self, pdf, columns, col_widths, line_height):
        """Draw the table header with column titles."""
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(230, 230, 230)  # Light gray background
        
        x_pos = pdf.get_x()
        y_pos = pdf.get_y()
        
        for i, col in enumerate(columns):
            pdf.set_xy(x_pos, y_pos)
            pdf.cell(col_widths[i], line_height, col, 1, 0, "C", True)
            x_pos += col_widths[i]
        
        pdf.ln(line_height)

    def _wrap_text(self, pdf, text, max_width):
        """Split text into lines that fit within the specified width."""
        lines = []
        words = text.split()
        
        if not words:
            return [""]
        
        current_line = words[0]
        for word in words[1:]:
            if pdf.get_string_width(current_line + " " + word) <= max_width:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)  # Add the last line
        
        # If text is still too long for a single line, force break it
        final_lines = []
        for line in lines:
            if pdf.get_string_width(line) <= max_width:
                final_lines.append(line)
            else:
                # Break long words if necessary
                current = ""
                for char in line:
                    if pdf.get_string_width(current + char) <= max_width:
                        current += char
                    else:
                        final_lines.append(current)
                        current = char
                if current:
                    final_lines.append(current)
        
        return final_lines if final_lines else [""]

    def clear_inputs(self):
        self.db_name_input.clear()
        self.category_input.clear()
        self.amount_input.clear()
        self.description_input.clear()

    def go_to_main_page(self):
        self.stacked_widget.setCurrentIndex(0)
        