
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen, QMouseEvent, QColor
from PyQt5.QtCore import Qt, QRect, QTimer
from PIL import ImageGrab
import pytesseract
from deep_translator import GoogleTranslator
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\666\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

class TransparentBox(QWidget):
    def __init__(self, left, top, width, height):
        super().__init__()

        # Set the window geometry (position and size)
        self.setGeometry(left, top, width, height)

        # Set the window flags to remove the title bar and make it frameless and always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Set the window to be transparent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set the opacity of the window (1.0 is fully opaque, 0.0 is fully transparent)
        self.setWindowOpacity(0.3)

        # Show the window
        self.show()

    def paintEvent(self, event):
        """
        Override the paint event to draw a thick-bordered box (rectangle) with QPainter.
        """
        painter = QPainter(self)

        # Create a red pen with a thick border (5 pixels)
        pen = QPen(QColor(255, 0, 0), 5)  # Red color with a 5-pixel thick border
        painter.setPen(pen)

        # Draw a rectangle filling the entire window with thick borders
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawRect(rect)


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OCR and Translation Result")

        # Get screen geometry
        screen = QApplication.desktop().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Set window size and position on the right side
        self.setGeometry(screen_width - 400, 200, 400, 300)  # Position on the right

        # Set window flags to stay on top and be frameless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Set the window to be transparent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set the opacity of the window (1.0 is fully opaque, 0.0 is fully transparent)
        self.setWindowOpacity(0.8)

        # Create a label to display the text result
        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 380, 280)  # Adjust label position and size
        self.label.setStyleSheet("color: white; font-size: 16px;")  # Set label text color and font size

        # Show the window
        self.show()

    def update_text(self, text):
        self.label.setText(text)  # Update the text displayed in the result window


class MainApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 400, 300)

        # Simulate the creation of the transparent selection box
        self.transparent_box = TransparentBox(100, 100, 400, 300)

        # Simulate showing the result window
        self.result_window = ResultWindow()

        # Start a timer to simulate updating the result window with translated text
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_translation)
        self.timer.start(2000)  # Update every 2 seconds

    def update_translation(self):
        # Simulate OCR and translation result
        translated_text = "Translated OCR text goes here"
        self.result_window.update_text(translated_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
