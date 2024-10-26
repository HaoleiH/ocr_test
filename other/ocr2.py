# this is working but have some problmes

import sys
import numpy as np
import pytesseract
from PIL import ImageGrab
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QRubberBand
from PyQt5.QtCore import QRect, Qt, QTimer, QPoint, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QPen
from deep_translator import GoogleTranslator
import time
from threading import Thread

# Set up pytesseract to use the executable for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\666\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Translator instance (using deep-translator)
translator = GoogleTranslator(source='auto', target='en')


class OCRSelectionWindow(QWidget):
    ocr_selected = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.initUI()

        self.ocr_region = None  # The selected OCR region
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.is_selecting = False

    def initUI(self):
        self.setWindowTitle('Select OCR Region')
        self.setGeometry(100, 100, 800, 600)
        self.label = QLabel('Select an area for OCR and translation...', self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        """Mouse press event to start drawing a selection rectangle."""
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()
            self.is_selecting = True

    def mouseMoveEvent(self, event):
        """Mouse move event to resize the selection rectangle."""
        if self.is_selecting:
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        """Mouse release event to finish the region selection."""
        if event.button() == Qt.LeftButton:
            self.is_selecting = False
            rect = self.rubber_band.geometry()
            self.rubber_band.hide()
            self.ocr_region = (rect.left(), rect.top(), rect.right(), rect.bottom())
            self.label.setText(f'OCR Region selected: {self.ocr_region}')
            self.ocr_selected.emit(self.ocr_region)  # Emit signal with the selected region
            self.close()  # Close the selection window


class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.translated_text = ""

        # Start a timer to update the display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)
        self.timer.start(500)  # Update every 0.5 seconds

    def initUI(self):
        self.setWindowTitle('OCR Result')
        self.setGeometry(100, 100, 400, 200)
        self.label = QLabel('Waiting for OCR results...', self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_text(self):
        """Update the label with the latest translated text."""
        self.label.setText(self.translated_text)

    def set_translated_text(self, text):
        """Set the translated text to be displayed."""
        self.translated_text = text


def capture_and_translate(ocr_region, result_window):
    """Continuously capture the selected region and perform OCR."""
    while True:
        if ocr_region:
            # Capture the selected region of the screen
            screenshot = ImageGrab.grab(bbox=ocr_region)
            screenshot_np = np.array(screenshot)

            # Perform OCR on the captured image
            ocr_text = pytesseract.image_to_string(screenshot_np)

            # Translate the text to English
            if ocr_text.strip():
                translated_text = translator.translate(ocr_text)
                result_window.set_translated_text(translated_text)
            else:
                result_window.set_translated_text("No text detected")

        time.sleep(0.5)  # Wait for 0.5 seconds before capturing again


if __name__ == '__main__':
    # Start the PyQt application
    app = QApplication(sys.argv)

    result_window = ResultWindow()
    selection_window = OCRSelectionWindow()
    selection_window.ocr_selected.connect(lambda region: Thread(target=capture_and_translate, args=(region, result_window)).start())
    
    selection_window.show()
    result_window.show()

    sys.exit(app.exec_())
