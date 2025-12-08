from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from utils import DatabaseConnection


class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ClassTrack - Reset Password")
        self.setWindowIcon(QIcon("image/class.png"))
        self.setStyleSheet("background-color: white;")
        self.setMinimumWidth(500)
        self.db = DatabaseConnection()
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("RESET PASSWORD")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222; margin-bottom: 10px;")
        
        subtitle = QLabel("Enter your email to reset your password")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 14px; margin-bottom: 20px;")
        
        email_label = QLabel("Email")
        email_label.setStyleSheet("font-weight: bold; color: #222;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your registered email")
        self.email_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px; font-size: 14px;")
        
        password_label = QLabel("New Password")
        password_label.setStyleSheet("font-weight: bold; color: #222;")
        password_frame = QFrame()
        password_layout = QHBoxLayout(password_frame)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(5)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter new password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px; font-size: 14px;")
        self.password_eye_btn = QPushButton()
        self.password_eye_btn.setIcon(QIcon("image/eye.png"))
        self.password_eye_btn.setIconSize(QSize(20, 20))
        self.password_eye_btn.setCheckable(True)
        self.password_eye_btn.setFixedSize(35, 35)
        self.password_eye_btn.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; background-color: #f5f5f5;")
        self.password_eye_btn.toggled.connect(self.toggle_password)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.password_eye_btn)
        
        confirm_label = QLabel("Confirm Password")
        confirm_label.setStyleSheet("font-weight: bold; color: #222;")
        confirm_frame = QFrame()
        confirm_layout = QHBoxLayout(confirm_frame)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.setSpacing(5)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Re-enter new password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px; font-size: 14px;")
        self.confirm_input.returnPressed.connect(self.reset_password)
        self.confirm_eye_btn = QPushButton()
        self.confirm_eye_btn.setIcon(QIcon("image/eye.png"))
        self.confirm_eye_btn.setIconSize(QSize(20, 20))
        self.confirm_eye_btn.setCheckable(True)
        self.confirm_eye_btn.setFixedSize(35, 35)
        self.confirm_eye_btn.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; background-color: #f5f5f5;")
        self.confirm_eye_btn.toggled.connect(self.toggle_confirm_password)
        confirm_layout.addWidget(self.confirm_input)
        confirm_layout.addWidget(self.confirm_eye_btn)
        
        reset_btn = QPushButton("Reset Password")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self.reset_password)
        reset_btn.setStyleSheet("background-color: #222; color: white; font-weight: bold; border-radius: 20px; padding: 12px; font-size: 15px;")
        
        back_frame = QFrame()
        back_layout = QHBoxLayout(back_frame)
        back_layout.setAlignment(Qt.AlignCenter)
        back_layout.setSpacing(5)
        
        back_label = QLabel("Remember your password?")
        back_label.setStyleSheet("color: #666; font-size: 13px;")
        
        back_link = QPushButton("Back to Login")
        back_link.setCursor(Qt.PointingHandCursor)
        back_link.clicked.connect(self.reject)
        back_link.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #222;
                font-weight: bold;
                font-size: 13px;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #555;
            }
        """)
        
        back_layout.addWidget(back_label)
        back_layout.addWidget(back_link)
        
        # Add all widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(password_label)
        layout.addWidget(password_frame)
        layout.addWidget(confirm_label)
        layout.addWidget(confirm_frame)
        layout.addSpacing(10)
        layout.addWidget(reset_btn)
        layout.addWidget(back_frame)
    
    def toggle_password(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.password_eye_btn.setIcon(QIcon("image/hidden.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_eye_btn.setIcon(QIcon("image/eye.png"))
    
    def toggle_confirm_password(self, checked):
        if checked:
            self.confirm_input.setEchoMode(QLineEdit.Normal)
            self.confirm_eye_btn.setIcon(QIcon("image/hidden.png"))
        else:
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_eye_btn.setIcon(QIcon("image/eye.png"))
    
    def reset_password(self):
        # Get inputs
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        
        # Validate fields
        if not all([email, password, confirm_password]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")
            return
        
        # Validate email format
        if "@" not in email or "." not in email.split("@")[-1]:
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address")
            return
        
        # Verify email exists in database
        if not self.db.email_exists(email):
            QMessageBox.critical(self, "Verification Failed", "Email not found in our records")
            self.email_input.clear()
            self.email_input.setFocus()
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 6 characters long")
            return
        
        # Reset password in database
        success, message = self.db.reset_password(email, password)
        
        if success:
            QMessageBox.information(self, "Success", "Password reset successfully!\nYou can now login with your new password.")
            self.accept()
        else:
            QMessageBox.critical(self, "Reset Failed", message)
