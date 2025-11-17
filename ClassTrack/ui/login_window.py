from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui.dashboard_window import DashboardWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClassTrack - Log In")
        self.setStyleSheet("background-color: #E7E9E5;")

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(80, 60, 80, 60)
        main_layout.setSpacing(40)

        # LEFT SIDE
        left_frame = QFrame()
        left_frame.setMinimumWidth(500)
        left_frame.setMaximumWidth(650)
        left_frame.setStyleSheet("background-color: white; border-radius: 15px;")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(60, 50, 60, 50)
        left_layout.setSpacing(25)

        # Title / Subtitle
        title = QLabel("Welcome To\n ClassTrack System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: 700; color: #222;")
        subtitle = QLabel("Please enter account")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 16px;")

        # Email / Password
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your name")
        self.email_input.setStyleSheet("border: none; border-bottom: 1px solid #000; padding: 12px; font-size: 16px;")
        self.email_input.returnPressed.connect(lambda: self.password_input.setFocus()) # TO c

        password_frame = QFrame()
        password_layout = QHBoxLayout(password_frame)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("border: none; border-bottom: 1px solid #000; padding: 12px; font-size: 16px; padding-right: 30px;")
        self.password_input.returnPressed.connect(self.open_dashboard)
        self.eye_btn = QPushButton("👁️")
        self.eye_btn.setCheckable(True)
        self.eye_btn.setFixedSize(25, 25)
        self.eye_btn.toggled.connect(self.toggle_password)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.eye_btn)

        # Login Button
        login_btn = QPushButton("Log In")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.open_dashboard)
        login_btn.setStyleSheet("background-color: #222; color: white; font-weight: bold; border-radius: 22px; padding: 12px; font-size: 15px;")

        # Issue Section
        issue_frame = QFrame()
        issue_layout = QVBoxLayout(issue_frame)
        issue_label = QLabel("Having Issues?")
        issue_label.setAlignment(Qt.AlignCenter)
        issue_label.setStyleSheet("font-weight: bold; font-size: 17px; color: #222;")
        issue_text = QLabel(
            "If you encounter login problems or system errors,\n"
            "please report them to our admin:\n\n"
            "📧 Email: support@thynkunlimited.com\n"
            "☎️ Contact: +63 912 345 6789\n"
        )
        issue_text.setAlignment(Qt.AlignCenter)
        issue_text.setWordWrap(True)
        issue_layout.addWidget(issue_label)
        issue_layout.addWidget(issue_text)

        # Add widgets to left layout
        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)
        left_layout.addWidget(self.email_input)
        left_layout.addWidget(password_frame)
        left_layout.addWidget(login_btn)
        left_layout.addWidget(issue_frame)
        left_layout.addStretch()

        # RIGHT SIDE (decorative)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignCenter)
        right_frame.setStyleSheet("background-color: #E7E9E5;")

        image_label = QLabel()
        pixmap = QPixmap(450, 450)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#C7CAC7"))
        painter.drawRoundedRect(0, 0, 450, 450, 60, 60)
        painter.end()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        info_text = QLabel("Decorative Panel")
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setStyleSheet("font-size: 22px; font-weight: 500; color: #333;")

        right_layout.addWidget(image_label)
        right_layout.addWidget(info_text)

        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(right_frame, 1)

    def toggle_password(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.eye_btn.setText("👁️")

    def open_dashboard(self):
        username = self.email_input.text() or "User"
        self.dashboard = DashboardWindow(username)
        self.dashboard.showMaximized()
        self.close()