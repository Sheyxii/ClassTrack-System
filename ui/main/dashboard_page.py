from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
sys.path.append('..')
from utils.database import DatabaseConnection


class DashboardPage(QWidget):
    def __init__(self, username, user_id=1):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.db = DatabaseConnection()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 0, 35, 20)
        layout.setSpacing(20)

        # Dashboard title
        dashboard_title = QLabel("Dashboard")
        dashboard_title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222;")
        dashboard_title.setContentsMargins(0, 20, 0, 10)
        layout.addWidget(dashboard_title, alignment=Qt.AlignLeft)

        # Welcome Card
        welcome_card = self.create_welcome_card()
        layout.addWidget(welcome_card)

        layout.addStretch()

    def create_welcome_card(self):
        welcome_card = QFrame()
        welcome_card.setStyleSheet("""
            QFrame {
                background-color: #E6EFFA;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        welcome_card.setMinimumHeight(400)
        welcome_card.setMaximumHeight(500)
        welcome_card.setMinimumWidth(850)

        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(10, 10, 10, 10)
        welcome_layout.setSpacing(10)
        welcome_layout.setAlignment(Qt.AlignCenter)

        welcome_title = QLabel(f"Welcome back, {self.username}!")
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("font-size: 60px; font-weight: bold; color: #333;")
        
        welcome_sub = QLabel("Your students are waiting to learn")
        welcome_sub.setAlignment(Qt.AlignCenter)
        welcome_sub.setStyleSheet("font-size: 28px; color: #555;")

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_sub)

        return welcome_card
