import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                            QFrame, QStackedWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, QSize
from PyQt5.QtGui import QColor, QPalette, QFont, QIcon, QLinearGradient, QGradient

class FancyButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont('Segoe UI', 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d3436;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)


class ContentCard(QFrame):
    def __init__(self, title, description, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #f0f0f0;
                border: 1px solid #3498db;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont('Segoe UI', 10))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)


class ScrollableContent(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #ecf0f1;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #ecf0f1;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #3498db;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        container = QWidget()
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)
        
        # Add dummy content
        for i in range(10):
            card = ContentCard(f"Fancy Card {i+1}", 
                              f"This is a beautiful animated card with some fancy content. "
                              f"Card {i+1} demonstrates the smooth scrolling animation effect.")
            self.layout.addWidget(card)
        
        self.setWidget(container)
        
        # Animation properties for smooth scrolling
        self.animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(500)  # 500ms for smooth animation
        
    def smoothScrollTo(self, value):
        self.animation.stop()
        self.animation.setStartValue(self.verticalScrollBar().value())
        self.animation.setEndValue(value)
        self.animation.start()


class SlidingStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(350)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.current_index = 0
        
    def slideInNext(self):
        if self.current_index < self.count() - 1:
            self.slideToIndex(self.current_index + 1)
    
    def slideInPrev(self):
        if self.current_index > 0:
            self.slideToIndex(self.current_index - 1)
    
    def slideToIndex(self, index):
        if index > self.count() - 1 or index < 0:
            return
        
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        offsetx = width
        
        # Direction of slide
        if index < self.current_index:
            offsetx = -width  # Slide from left
        
        # Move current widget out of view
        self.animation.setStartValue(QRect(0, 0, width, height))
        self.animation.setEndValue(QRect(-offsetx, 0, width, height))
        self.animation.start()
        
        def slideInNewWidget():
            self.setCurrentIndex(index)
            self.animation.setStartValue(QRect(offsetx, 0, width, height))
            self.animation.setEndValue(QRect(0, 0, width, height))
            self.animation.start()
            self.current_index = index
        
        # Connect animation finished to slide in new widget
        self.animation.finished.connect(slideInNewWidget)
        self.animation.finished.connect(lambda: self.animation.finished.disconnect())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fancy PyQt App")
        self.setMinimumSize(800, 600)
        
        # Apply fancy styling to the main window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        header = QWidget()
        header.setMinimumHeight(60)
        header.setStyleSheet("""
            background-color: #3498db;
            color: white;
        """)
        
        header_layout = QHBoxLayout(header)
        header_title = QLabel("Fancy PyQt Application")
        header_title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        header_title.setStyleSheet("color: white;")
        header_layout.addWidget(header_title)
        
        # Create stacked widget for page transitions
        self.stacked_widget = SlidingStackedWidget()
        
        # First page - scrollable content
        page1 = QWidget()
        page1_layout = QVBoxLayout(page1)
        page1_title = QLabel("Fancy Scrolling Content")
        page1_title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        page1_title.setAlignment(Qt.AlignCenter)
        page1_title.setStyleSheet("color: #2c3e50; margin: 10px;")
        
        self.scrollable = ScrollableContent()
        
        scroll_controls = QWidget()
        scroll_controls_layout = QHBoxLayout(scroll_controls)
        
        scroll_top_btn = FancyButton("Scroll to Top")
        scroll_top_btn.clicked.connect(lambda: self.scrollable.smoothScrollTo(0))
        
        scroll_bottom_btn = FancyButton("Scroll to Bottom")
        scroll_bottom_btn.clicked.connect(
            lambda: self.scrollable.smoothScrollTo(self.scrollable.verticalScrollBar().maximum()))
        
        next_page_btn = FancyButton("Next Page")
        next_page_btn.clicked.connect(self.stacked_widget.slideInNext)
        
        scroll_controls_layout.addWidget(scroll_top_btn)
        scroll_controls_layout.addWidget(scroll_bottom_btn)
        scroll_controls_layout.addWidget(next_page_btn)
        
        page1_layout.addWidget(page1_title)
        page1_layout.addWidget(self.scrollable)
        page1_layout.addWidget(scroll_controls)
        
        # Second page
        page2 = QWidget()
        page2_layout = QVBoxLayout(page2)
        page2_title = QLabel("Fancy Animations")
        page2_title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        page2_title.setAlignment(Qt.AlignCenter)
        page2_title.setStyleSheet("color: #2c3e50; margin: 10px;")
        
        self.animated_card = QFrame()
        self.animated_card.setMinimumSize(300, 200)
        self.animated_card.setStyleSheet("""
            background-color: #3498db;
            border-radius: 15px;
            color: white;
        """)
        self.animated_card.setLayout(QVBoxLayout())
        self.animated_card.layout().addWidget(QLabel("Click the buttons to animate me!"))
        self.animated_card.layout().setAlignment(Qt.AlignCenter)
        
        anim_controls = QWidget()
        anim_controls_layout = QHBoxLayout(anim_controls)
        
        move_btn = FancyButton("Move")
        move_btn.clicked.connect(self.animateCard)
        
        resize_btn = FancyButton("Resize")
        resize_btn.clicked.connect(self.resizeCard)
        
        color_btn = FancyButton("Change Color")
        color_btn.clicked.connect(self.changeCardColor)
        
        prev_btn = FancyButton("Previous Page")
        prev_btn.clicked.connect(self.stacked_widget.slideInPrev)
        
        anim_controls_layout.addWidget(move_btn)
        anim_controls_layout.addWidget(resize_btn)
        anim_controls_layout.addWidget(color_btn)
        anim_controls_layout.addWidget(prev_btn)
        
        page2_layout.addWidget(page2_title)
        page2_layout.addWidget(self.animated_card, 1, Qt.AlignCenter)
        page2_layout.addWidget(anim_controls)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(page1)
        self.stacked_widget.addWidget(page2)
        
        # Create footer
        footer = QWidget()
        footer.setMinimumHeight(40)
        footer.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_text = QLabel("© 2025 Fancy PyQt App")
        footer_text.setStyleSheet("color: white;")
        footer_layout.addWidget(footer_text)
        
        # Add widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(self.stacked_widget, 1)
        main_layout.addWidget(footer)
        
        self.setCentralWidget(central_widget)
    
    def animateCard(self):
        animation = QPropertyAnimation(self.animated_card, b"pos")
        animation.setDuration(1000)
        animation.setStartValue(self.animated_card.pos())
        
        # Move right then left
        center_x = (self.width() - self.animated_card.width()) // 2
        animation.setKeyValueAt(0.25, self.animated_card.pos() + QSize(100, 0))
        animation.setKeyValueAt(0.5, self.animated_card.pos() + QSize(-100, 0))
        animation.setKeyValueAt(0.75, self.animated_card.pos() + QSize(0, 50))
        animation.setEndValue(self.animated_card.pos())
        
        animation.setEasingCurve(QEasingCurve.OutBounce)
        animation.start()
    
    def resizeCard(self):
        animation = QPropertyAnimation(self.animated_card, b"geometry")
        animation.setDuration(1000)
        animation.setStartValue(self.animated_card.geometry())
        
        # Grow then shrink
        original_geom = self.animated_card.geometry()
        center_x = original_geom.x() + original_geom.width() // 2
        center_y = original_geom.y() + original_geom.height() // 2
        
        larger = QRect(
            center_x - (original_geom.width() * 1.5) // 2,
            center_y - (original_geom.height() * 1.5) // 2,
            original_geom.width() * 1.5,
            original_geom.height() * 1.5
        )
        
        smaller = QRect(
            center_x - (original_geom.width() * 0.8) // 2,
            center_y - (original_geom.height() * 0.8) // 2,
            original_geom.width() * 0.8,
            original_geom.height() * 0.8
        )
        
        animation.setKeyValueAt(0.4, larger)
        animation.setKeyValueAt(0.8, smaller)
        animation.setEndValue(original_geom)
        
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
    
    def changeCardColor(self):
        # We'll use a timer to create a color pulse effect
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]
        color_index = 0
        
        def updateColor():
            nonlocal color_index
            self.animated_card.setStyleSheet(f"""
                background-color: {colors[color_index]};
                border-radius: 15px;
                color: white;
            """)
            color_index = (color_index + 1) % len(colors)
        
        # Create a timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(updateColor)
        self.color_timer.start(150)  # Change color every 150ms
        
        # Stop after cycling through all colors
        QTimer.singleShot(150 * len(colors), self.color_timer.stop)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())