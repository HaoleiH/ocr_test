import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor

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

        # Create a red pen with a thick border (10 pixels)
        pen = QPen(QColor(255, 0, 0), 50)  # Red color with a 10-pixel thick border
        painter.setPen(pen)

        # Draw a rectangle filling the entire window with thick borders
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawRect(rect)

def main():
    app = QApplication(sys.argv)

    # Define the coordinates and size of the box (left, top, width, height)
    left = 100
    top = 100
    width = 400
    height = 300

    # Create and show the transparent box
    box = TransparentBox(left, top, width, height)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
