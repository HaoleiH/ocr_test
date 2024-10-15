import sys
import pytesseract
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint
from PIL import Image
import numpy as np

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

        # Variables for resizing
        self.is_resizing = False
        self.resize_direction = None  # Can be 'left', 'right', 'top', or 'bottom'

        # Set up result window
        self.result_window = ResultWindow()
        self.result_window.hide()  # Start hidden

        # Timer to perform OCR every 0.5 seconds
        self.ocr_timer = QtCore.QTimer()
        self.ocr_timer.timeout.connect(self.perform_ocr)
        self.ocr_timer.start(500)  # Perform OCR every 0.5 seconds

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
        # Create a screenshot of the area within the window
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())  # Capture the current window
        screenshot.save('screenshot.png')  # Optional: save for debugging

        # Convert QPixmap to PIL Image
        img = self.qpixmap_to_pil(screenshot)

        # Perform OCR on the PIL Image
        text = pytesseract.image_to_string(img)

        # Display the OCR result in the result window
        self.result_window.update_text(text)
        self.result_window.show()  # Ensure the result window is shown

    def qpixmap_to_pil(self, qpixmap):
        """Convert QPixmap to PIL Image"""
        qimg = qpixmap.toImage()  # Convert QPixmap to QImage
        width = qimg.width()
        height = qimg.height()

        # Create a buffer to store the image data
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())

        # Create a numpy array from the buffer
        img_array = np.array(ptr).reshape((height, width, 4))  # 4 channels (RGBA)

        # Convert to PIL Image
        img = Image.fromarray(img_array, 'RGBA')
        return img.convert('RGB')  # Convert to RGB (remove alpha channel)

class ResultWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Result")
        self.setGeometry(500, 100, 300, 200)  # Set the position and size of the result window
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QLabel("OCR Result will be displayed here.")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def update_text(self, text):
        self.label.setText(text)  # Update the label with the new OCR text

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = DraggableWindow()
    window.show()  # Show the main window
    sys.exit(app.exec_())  # Execute the application

if __name__ == '__main__':
    main()
