#need to fix the result window
import sys
import pytesseract
from deep_translator import GoogleTranslator  # Import Google Translator
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint
from PIL import ImageGrab

# Set the path to Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\666\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

class DraggableWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle("Draggable Transparent Window with OCR")
        self.setGeometry(100, 100, 400, 300)  # Set the position and size of the window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)  # Frameless and always on top
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make the background translucent
        self.setWindowOpacity(0.9)  # Set opacity level to 0.9 for better visibility

        # Variables for dragging
        self.is_dragging = False
        self.offset = QPoint()

        # Timer to perform OCR every 0.5 seconds
        self.ocr_timer = QtCore.QTimer()
        self.ocr_timer.timeout.connect(self.perform_ocr)
        self.ocr_timer.start(500)  # Perform OCR every 0.5 seconds

        # Initialize result window
        self.result_window = ResultWindow()  # Create a new independent ResultWindow instance
        self.result_window.show()  # Show the result window independently

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if event.pos().x() < 10:  # Left edge
                self.is_resizing = True
                self.resize_direction = 'left'
            elif event.pos().x() > self.width() - 10:  # Right edge
                self.is_resizing = True
                self.resize_direction = 'right'
            elif event.pos().y() < 10:  # Top edge
                self.is_resizing = True
                self.resize_direction = 'top'
            elif event.pos().y() > self.height() - 10:  # Bottom edge
                self.is_resizing = True
                self.resize_direction = 'bottom'
            else:  # In the window for dragging
                self.is_dragging = True
                self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_position = event.globalPos() - self.offset
            self.move(new_position)
            event.accept()
        elif self.is_resizing:
            if self.resize_direction == 'left':
                self.resize(self.width() - (event.x() - self.offset.x()), self.height())
                self.move(event.globalPos().x(), self.pos().y())
            elif self.resize_direction == 'right':
                self.resize(event.x(), self.height())
            elif self.resize_direction == 'top':
                self.resize(self.width(), self.height() - (event.y() - self.offset.y()))
                self.move(self.pos().x(), event.globalPos().y())
            elif self.resize_direction == 'bottom':
                self.resize(self.width(), event.y())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False
            self.is_resizing = False
            self.resize_direction = None

    def paintEvent(self, event):
        """Override paintEvent to draw a red border and a solid background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a solid background color (semi-transparent)
        background_color = QColor(0, 0, 0, 76)  # Semi-transparent black
        painter.fillRect(self.rect(), background_color)

        # Set up the pen for the border
        pen = QPen(Qt.red, 2)  # Red color with a width of 2
        painter.setPen(pen)

        # Draw the border rectangle
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)  # -1 to avoid clipping the border

    def perform_ocr(self):
        # Capture the current window using ImageGrab
        x = self.x()
        y = self.y()
        width = self.width()
        height = self.height()

        # Use ImageGrab to capture the area of the draggable window
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))  # bbox is (left, top, right, bottom)

        # Perform OCR on the PIL Image
        text = pytesseract.image_to_string(screenshot)

        # Translate the OCR result
        translated_text = GoogleTranslator(source='auto', target='zh-CN').translate(text)  # Translate to English

        # Update the result window with the translated text
        self.result_window.update_text(translated_text)  # Update result window with translated text

class ResultWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Result")
        self.setGeometry(500, 100, 500, 500)  # Set the position and size of the result window to 500x500
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)  # Frameless and always on top
        self.setFixedWidth(500)
        self.setFixedHeight(500)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QLabel("Translated Result will be displayed here.")
        self.layout.addWidget(self.label)  # Add translated text label
        self.setLayout(self.layout)
        

        # Variables for dragging
        self.is_dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_position = event.globalPos() - self.offset
            self.move(new_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False

    def update_text(self, translated_text):
        self.label.setText(f"Translated Result: {translated_text}")  # Update translated text

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = DraggableWindow()
    window.show()  # Show the main window
    sys.exit(app.exec_())  # Execute the application

if __name__ == '__main__':
    main()
