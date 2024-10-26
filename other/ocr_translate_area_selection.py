import sys
import pytesseract
from deep_translator import GoogleTranslator
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QMouseEvent, QPixmap
import numpy as np
import cv2
from PIL import ImageGrab
import time

class AreaSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.start_pos = None
        self.end_pos = None
        self.is_drawing = False
        self.selected_area = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 800, 600)

    def paintEvent(self, event):
        if self.start_pos and self.end_pos:
            painter = QPainter(self)
            painter.setPen(Qt.red)
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.drawRect(rect)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.is_drawing = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_drawing:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.end_pos = event.pos()
            self.is_drawing = False
            self.update()
            self.selected_area = self.get_selected_area()

            # Close the selector after selection
            self.close()

            # Capture the selected area for OCR
            if self.selected_area:
                self.capture_and_translate()

    def get_selected_area(self):
        if self.start_pos and self.end_pos:
            # Normalize the rectangle to ensure valid coordinates
            x1 = min(self.start_pos.x(), self.end_pos.x())
            y1 = min(self.start_pos.y(), self.end_pos.y())
            x2 = max(self.start_pos.x(), self.end_pos.x())
            y2 = max(self.start_pos.y(), self.end_pos.y())
            return (x1, y1, x2, y2)
        return None

    def capture_and_translate(self):
        if self.selected_area:
            x1, y1, x2, y2 = self.selected_area

            # Capture the screen area using ImageGrab
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            img_np = np.array(img)
            gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

            # OCR processing
            text = pytesseract.image_to_string(gray)

            # Translate the captured text
            translated_text = GoogleTranslator(source='auto', target='en').translate(text)

            # Show the translated result
            self.show_result(translated_text)

    def show_result(self, translated_text):
        result_window = ResultWindow(translated_text)
        result_window.show()

class ResultWindow(QMainWindow):
    def __init__(self, translated_text):
        super().__init__()
        self.setWindowTitle("Translated Text")
        self.setGeometry(1000, 100, 300, 200)
        self.label = QLabel(translated_text, self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    selector = AreaSelector()
    selector.showFullScreen()
    sys.exit(app.exec_())
