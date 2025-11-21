from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 20, 35, 20)
        layout.setSpacing(20)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        layout.addWidget(title)
        
        # Placeholder content
        placeholder = QLabel("Content for Settings page goes here.")
        placeholder.setStyleSheet("font-size: 18px; color: #555;")
        layout.addWidget(placeholder)
        
        layout.addStretch()
