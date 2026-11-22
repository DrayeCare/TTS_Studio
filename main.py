from PySide6.QtWidgets import QApplication
from app.application import TTSStudioApplication
import sys

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    app = TTSStudioApplication()
    app.show()
    sys.exit(qt_app.exec())
