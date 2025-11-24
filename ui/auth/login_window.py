from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui import MainWindow
from .signup_dialog import SignupDialog
from .forgot_password_dialog import ForgotPasswordDialog
from utils import DatabaseConnection


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClassTrack - Log In")
        self.setWindowIcon(QIcon("image/class.png"))
        self.setStyleSheet("background-color: #E7E9E5;")
        self.db = DatabaseConnection()

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(120, 60, 120, 60)
        main_layout.setSpacing(150)

        # LEFT SIDE
        left_frame = QFrame()
        left_frame.setMinimumWidth(550)
        left_frame.setMaximumWidth(700)
        left_frame.setStyleSheet("background-color: white; border-radius: 15px;")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(60, 80, 60, 80)
        left_layout.setSpacing(25)

        # Title / Subtitle
        title = QLabel("Welcome to\n ClassTrack\n\n\n")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 45px; font-weight: 700; color: #222;")
        subtitle = QLabel("Please enter account")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 20px;")

        # user / Password
        user_frame = QFrame()
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(0)
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter your username")
        self.user_input.setStyleSheet("border: none; border-bottom: 1px solid #000; padding: 12px; font-size: 16px; padding-right: 30px; background-color: #E7E9E5;")
        self.user_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.user_icon = QPushButton()
        self.user_icon.setIcon(QIcon("image/profile.png"))
        self.user_icon.setIconSize(QSize(18, 18))
        self.user_icon.setCheckable(False)
        self.user_icon.setFixedSize(30, 30)
        user_layout.addWidget(self.user_input)
        user_layout.addWidget(self.user_icon)
        
        password_frame = QFrame()
        password_layout = QHBoxLayout(password_frame)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("border: none; border-bottom: 1px solid #000; padding: 12px; font-size: 16px; padding-right: 30px; background-color: #E7E9E5;")
        self.password_input.returnPressed.connect(self.open_dashboard)
        self.eye_btn = QPushButton()
        self.eye_btn.setIcon(QIcon("image/eye.png"))
        self.eye_btn.setIconSize(QSize(20, 20))
        self.eye_btn.setCheckable(True)
        self.eye_btn.setFixedSize(25, 25)
        self.eye_btn.toggled.connect(self.toggle_password)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.eye_btn)

        # Login Button
        login_btn = QPushButton("Log In")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.open_dashboard)
        login_btn.setStyleSheet("background-color: #222; color: white; font-weight: bold; border-radius: 20px; padding: 12px; font-size: 15px; ")
        
        # Forgot Password Link
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.clicked.connect(self.open_forgot_password)
        forgot_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                font-size: 13px;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #222;
            }
        """)

        # Sign Up Section
        signup_frame = QFrame()
        signup_layout = QHBoxLayout(signup_frame)
        signup_layout.setAlignment(Qt.AlignCenter)
        signup_layout.setSpacing(5)
        
        signup_label = QLabel("Don't have an account?")
        signup_label.setStyleSheet("color: #666; font-size: 14px;")
        
        signup_btn = QPushButton("Sign Up")
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.clicked.connect(self.open_signup)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #222;
                font-weight: bold;
                font-size: 14px;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #555;
            }
        """)
        
        signup_layout.addWidget(signup_label)
        signup_layout.addWidget(signup_btn)

        # Add widgets to left layout
        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)
        left_layout.addWidget(user_frame)
        left_layout.addWidget(password_frame)
        left_layout.addWidget(login_btn)
        left_layout.addWidget(forgot_btn, alignment=Qt.AlignRight)
        left_layout.addWidget(signup_frame)
        left_layout.addStretch()

        # RIGHT SIDE (decorative)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignCenter)
        right_frame.setStyleSheet("background-color: #E7E9E5;")

        image_label = QLabel()
        pixmap = QPixmap("image/prof.png")
        scaled_pixmap = pixmap.scaled(800, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        right_layout.addWidget(image_label)

        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(right_frame, 1)

    def toggle_password(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setIcon(QIcon("image/hidden.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.eye_btn.setIcon(QIcon("image/eye.png"))

    def open_signup(self):
        dialog = SignupDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Optionally auto-fill the username after successful signup
            pass
    
    def open_forgot_password(self):
        dialog = ForgotPasswordDialog(self)
        dialog.exec_()

    def open_dashboard(self):
        username = self.user_input.text()
        password = self.password_input.text()
        
        # Validate inputs
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password")
            return
        
        # Validate with database
        success, message, user_data = self.db.validate_user(username, password)
        
        if success:
            QMessageBox.information(self, "Success", f"Welcome, {user_data['username']}!")
            self.main_window = MainWindow(user_data['username'], user_data['user_id'])
            self.main_window.showMaximized()
            self.close()
        else:
            QMessageBox.critical(self, "Login Failed", message)
            self.password_input.clear()
            self.password_input.setFocus()
