import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QStackedWidget, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor


class User:
    def __init__(self, username, password, role, full_name, email):
        self.username = username
        self.password = password
        self.role = role  # Changed from 'type' to 'role' to match auth_system.py
        self.full_name = full_name
        self.email = email


class DatabaseHandler:
    def __init__(self):
        self.filename = "users.json"
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f)

    def add_user(self, username, password, role, full_name, email):
        if username in self.users:
            return False
        self.users[username] = {
            'password': password,  # In production, use hashing
            'role': role,
            'full_name': full_name,
            'email': email
        }
        self.save_users()
        return True

    def verify_user(self, username, password):
        if username in self.users and self.users[username]['password'] == password:
            return User(
                username,
                password,
                self.users[username]['role'],
                self.users[username]['full_name'],
                self.users[username]['email']
            )
        return None


class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setFont(QFont('Arial', 10))
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 20px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)


class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setFont(QFont('Arial', 10))
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BBDEFB;
                border-radius: 20px;
                padding: 8px 16px;
                background-color: #E3F2FD;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: white;
            }
        """)


class AuthWindow(QMainWindow):
    login_successful = pyqtSignal(User)

    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Advanced Graphing Calculator - Authentication')
        self.setMinimumSize(400, 600)
        self.setStyleSheet("background-color: #FAFAFA;")

        # Create stacked widget for login/signup pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create login and signup pages
        self.login_page = self.create_login_page()
        self.signup_page = self.create_signup_page()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.signup_page)

    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Login")
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Username field
        self.login_username = ModernLineEdit(placeholder="Username")
        layout.addWidget(self.login_username)

        # Password field
        self.login_password = ModernLineEdit(placeholder="Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.login_password)

        # Login button
        login_btn = ModernButton("Login")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        # Switch to signup
        switch_to_signup = ModernButton("Create Account")
        switch_to_signup.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        switch_to_signup.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 20px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        layout.addWidget(switch_to_signup)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def create_signup_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Create Account")
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Username
        self.signup_username = ModernLineEdit(placeholder="Username")
        layout.addWidget(self.signup_username)

        # Password
        self.signup_password = ModernLineEdit(placeholder="Password")
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.signup_password)

        # Full Name
        self.signup_fullname = ModernLineEdit(placeholder="Full Name")
        layout.addWidget(self.signup_fullname)

        # Email
        self.signup_email = ModernLineEdit(placeholder="Email")
        layout.addWidget(self.signup_email)

        # Role selection
        role_layout = QHBoxLayout()
        self.student_btn = QPushButton("Student")
        self.teacher_btn = QPushButton("Teacher")

        for btn in [self.student_btn, self.teacher_btn]:
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    border: none;
                    border-radius: 20px;
                    padding: 8px 16px;
                }
                QPushButton:checked {
                    background-color: #2196F3;
                    color: white;
                }
            """)
            role_layout.addWidget(btn)

        self.student_btn.clicked.connect(lambda: self.teacher_btn.setChecked(False))
        self.teacher_btn.clicked.connect(lambda: self.student_btn.setChecked(False))
        layout.addLayout(role_layout)

        # Signup button
        signup_btn = ModernButton("Sign Up")
        signup_btn.clicked.connect(self.handle_signup)
        layout.addWidget(signup_btn)

        # Switch to login
        switch_to_login = ModernButton("Back to Login")
        switch_to_login.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        switch_to_login.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                border: none;
                border-radius: 20px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        layout.addWidget(switch_to_login)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def handle_login(self):
        username = self.login_username.text()
        password = self.login_password.text()

        user = self.db.verify_user(username, password)
        if user:
            self.login_successful.emit(user)
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")

    def handle_signup(self):
        username = self.signup_username.text()
        password = self.signup_password.text()
        full_name = self.signup_fullname.text()
        email = self.signup_email.text()

        if not all([username, password, full_name, email]):
            QMessageBox.warning(self, "Signup Failed", "Please fill all fields")
            return

        role = "teacher" if self.teacher_btn.isChecked() else "student"

        if self.db.add_user(username, password, role, full_name, email):
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.stacked_widget.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Signup Failed", "Username already exists")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec())