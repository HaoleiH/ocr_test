import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QColor
from PIL import ImageGrab
import pytesseract
from deep_translator import GoogleTranslator
import numpy as np

class TransparentBox(QWidget):
    def __init__(self, left, top, width, height):
        super().__init__()

        # Set the window geometry (position and size)
        self.setGeometry(left, top, width, height)

        # Set the window flags to remove the title bar and make it frameless
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

        # Set window size
        self.setGeometry(500, 200, 400, 300)

        # Create layout and labels
        layout = QVBoxLayout()

        # OCR text label
        self.ocr_label = QLabel("Extracted Text:\n")
        self.ocr_label.setWordWrap(True)
        layout.addWidget(self.ocr_label)

        # Translated text label
        self.translated_label = QLabel("Translated Text:\n")
        self.translated_label.setWordWrap(True)
        layout.addWidget(self.translated_label)

        self.setLayout(layout)

        # Show the result window
        self.show()

    def update_text(self, ocr_text, translated_text):
        """
        Update the text in the result window.
        """
        self.ocr_label.setText(f"Extracted Text:\n{ocr_text}")
        self.translated_label.setText(f"Translated Text:\n{translated_text}")


def capture_screen_area(left, top, right, bottom):
    """
    Capture a specific area of the screen.
    :param left: Left boundary
    :param top: Top boundary
    :param right: Right boundary
    :param bottom: Bottom boundary
    :return: Image of the captured area
    """
    img = ImageGrab.grab(bbox=(left, top, right, bottom))
    return img


def ocr_image(image):
    """
    Perform OCR on the given image to extract text.
    :param image: Image to extract text from
    :return: Extracted text
    """
    text = pytesseract.image_to_string(image)
    return text


def translate_text(text, target_lang='en'):
    """
    Translate the extracted text to the desired language using deep-translator.
    :param text: Text to translate
    :param target_lang: Target language for translation (default is 'en' for English)
    :return: Translated text
    """
    translator = GoogleTranslator(source='auto', target=target_lang)
    translated_text = translator.translate(text)
    return translated_text


def has_area_changed(prev_image, curr_image):
    """
    Check if the captured screen area has changed.
    :param prev_image: Previous image (as NumPy array)
    :param curr_image: Current image (as NumPy array)
    :return: Boolean indicating if the area has changed
    """
    return not np.array_equal(prev_image, curr_image)


def refresh_ocr_and_translate(box, result_window, left, top, right, bottom, prev_image):
    """
    Capture the screen area, perform OCR, and translate the text.
    Refresh every 100 ms if the area has changed.
    """
    # Capture the screen area
    captured_image = capture_screen_area(left, top, right, bottom)
    
    # Convert the captured image to a NumPy array
    curr_image = np.array(captured_image)

    # Check if the area has changed
    if has_area_changed(prev_image, curr_image):
        # Perform OCR to extract text
        extracted_text = ocr_image(captured_image)

        # Translate the extracted text
        translated_text = translate_text(extracted_text, target_lang='en')

        # Update the result window with the new text
        result_window.update_text(extracted_text, translated_text)

        # Return the current image for the next comparison
        return curr_image
    
    # If no change, return the previous image
    return prev_image


def main():
    app = QApplication(sys.argv)

    # Define the coordinates of the area to capture (left, top, right, bottom)
    left = 100
    top = 100
    right = 500
    bottom = 300

    # Show the transparent box on the selected area
    box = TransparentBox(left, top, right-left, bottom-top)

    # Create the result window
    result_window = ResultWindow()

    # Initialize previous image for change detection
    prev_image = np.array(capture_screen_area(left, top, right, bottom))

    # Create a QTimer to refresh OCR and translation every 100 ms
    timer = QTimer()
    timer.timeout.connect(lambda: refresh_ocr_and_translate(box, result_window, left, top, right, bottom, prev_image))
    timer.start(100)  # Refresh every 100 milliseconds

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
