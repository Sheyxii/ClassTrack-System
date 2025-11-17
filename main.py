from PyQt5.QtWidgets import QApplication
import sys
from ui.login_window import LoginWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.showMaximized()
    sys.exit(app.exec_())