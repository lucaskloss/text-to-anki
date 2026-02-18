
import sys
from gui.control import MainController
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = MainController()
    controller.view.show()
    app.exec()