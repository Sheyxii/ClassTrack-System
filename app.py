from PyQt5.QtWidgets import QApplication
import sys
from ui import LoginWindow
from utils.populate_bscs2b import populate_bscs2b


if __name__ == "__main__":
    # Auto-populate BSCS 2B section with default students on first run
    try:
        populate_bscs2b(silent=True)
    except Exception as e:
        print(f"Note: Could not auto-populate default students: {e}")
    
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.showMaximized()
    sys.exit(app.exec_())   