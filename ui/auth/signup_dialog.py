from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from utils import DatabaseConnection


class SignupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ClassTrack - Sign Up")
        self.setWindowIcon(QIcon("image/system.png"))
        self.setStyleSheet("background-color: white;")
        self.setMinimumWidth(500)
        self.db = DatabaseConnection()
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("CREATE AN ACCOUNT")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #222; margin-bottom: 10px;")
        
        # Email
        email_label = QLabel("Email")
        email_label.setStyleSheet("font-weight: bold; color: #222;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px; font-size: 14px;")
        
        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-weight: bold; color: #222;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        self.username_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px; font-size: 14px;")
        
        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: bold; color: #222;")
        password_frame = QFrame()
        password_layout = QHBoxLayout(password_frame)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(5)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Create a password")
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
        
        # Confirm Password
        confirm_label = QLabel("Confirm Password")
        confirm_label.setStyleSheet("font-weight: bold; color: #222;")
        confirm_frame = QFrame()
        confirm_layout = QHBoxLayout(confirm_frame)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.setSpacing(5)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Re-enter your password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 10px; font-size: 14px;")
        self.confirm_input.returnPressed.connect(self.create_account)
        self.confirm_eye_btn = QPushButton()
        self.confirm_eye_btn.setIcon(QIcon("image/eye.png"))
        self.confirm_eye_btn.setIconSize(QSize(20, 20))
        self.confirm_eye_btn.setCheckable(True)
        self.confirm_eye_btn.setFixedSize(35, 35)
        self.confirm_eye_btn.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; background-color: #f5f5f5;")
        self.confirm_eye_btn.toggled.connect(self.toggle_confirm_password)
        confirm_layout.addWidget(self.confirm_input)
        confirm_layout.addWidget(self.confirm_eye_btn)
        
        # Terms & Conditions Checkbox
        self.terms_checkbox = QCheckBox("I agree to the Terms  Conditions")
        self.terms_checkbox.setStyleSheet("color: #666; font-size: 13px;")
        
        # Signup Button
        signup_btn = QPushButton("Signup")
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.clicked.connect(self.create_account)
        signup_btn.setStyleSheet("background-color: #222; color: white; font-weight: bold; border-radius: 20px; padding: 12px; font-size: 15px;")
        
        # Add all widgets to layout
        layout.addWidget(title)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(password_frame)
        layout.addWidget(confirm_label)
        layout.addWidget(confirm_frame)
        layout.addWidget(self.terms_checkbox)
        layout.addSpacing(10)
        layout.addWidget(signup_btn)
    
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
    
    def create_account(self):
        # Get input values
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        
        # Validate inputs
        if not all([email, username, password, confirm_password]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")
            return
        
        # Validate email format
        if "@" not in email or "." not in email.split("@")[-1]:
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address")
            return
        
        # Check terms and conditions
        if not self.terms_checkbox.isChecked():
            QMessageBox.warning(self, "Terms Required", "Please agree to the Terms & Conditions")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 6 characters long")
            return
        
        # Add user to database
        success, message = self.db.add_user(username, password, email)
        
        if success:
            QMessageBox.information(self, "Success", f"Account created successfully!\nWelcome, {username}!")
            self.accept()
        else:
            QMessageBox.critical(self, "Registration Failed", message)
