import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QStackedWidget, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from database import AdvancedDatabase


class User:
    def __init__(self, username, password, role, full_name, email, user_id=None):  # Add user_id parameter
        self.id = user_id  # Store the user ID
        self.username = username
        self.password = password
        self.role = role
        self.full_name = full_name
        self.email = email


class DatabaseHandler:
    def __init__(self):
        self.db = AdvancedDatabase()

    def add_user(self, username, password, role, full_name, email):
        return self.db.add_user(username, password, role, full_name, email)

    def verify_user(self, username, password):
        user_data = self.db.verify_user(username, password)
        if user_data:
            return User(
                username=user_data['username'],
                password=password,
                role=user_data['role'],
                full_name=user_data['full_name'],
                email=user_data['email'],
                user_id=user_data['id']  # Pass the user ID
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
                color: grey;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
    DARK_STYLE = """
        QWidget {
            background-color: #1e1e2e;
            color: black;
        }
        QLabel {
            color: white;
            font-size: 14px;
        }
        QLineEdit {
            background-color: #2d2d2d;
            border: 2px solid #3d3d3d;
            border-radius: 4px;
            color: white;
            padding: 6px;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 2px solid #2a82da;
        }
        QPushButton {
            background-color: #2a82da;
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #3292ea;
        }
        QPushButton:pressed {
            background-color: #1a72ca;
        }
        QComboBox {
            background-color: #2d2d2d;
            border: 2px solid #3d3d3d;
            border-radius: 4px;
            color: white;
            padding: 5px;
        }
        """


class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setFont(QFont('Arial', 15))
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BBDEFB;
                border-radius: 20px;
                padding: 8px 16px;
                background-color: grey;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: grey;
            }
        """)


class AuthWindow(QMainWindow):
    login_successful = pyqtSignal(User)

    def __init__(self):
        super().__init__()
        self.teacher_btn = QPushButton("Teacher")
        self.student_btn = QPushButton("Student")
        self.signup_fullname = ModernLineEdit(placeholder="Full Name")
        self.signup_email = ModernLineEdit(placeholder="Email")
        self.login_password = ModernLineEdit(placeholder="Password")
        self.signup_password = ModernLineEdit(placeholder="Password")
        self.login_username = ModernLineEdit(placeholder="Username")
        self.signup_username = ModernLineEdit(placeholder="Username")
        self.signup_page = self.create_signup_page()
        self.stacked_widget = None
        self.login_page = None
        self.db = DatabaseHandler()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Advanced Graphing Calculator - Authentication')
        self.setMinimumSize(400, 600)
        self.setStyleSheet("background-color: grey;")

        # Create stacked widget for login/signup pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create login and signup pages
        self.login_page = self.create_login_page()

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
        layout.addWidget(self.login_username)

        # Password field
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
                color: grey;
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
        layout.addWidget(self.signup_username)

        # Password
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.signup_password)

        # Full Name
        layout.addWidget(self.signup_fullname)

        # Email
        layout.addWidget(self.signup_email)

        # Role selection
        role_layout = QHBoxLayout()

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

        # Switch to log in
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

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password")
            return

        try:
            user = self.db.verify_user(username, password)
            if user:
                print(f"Debug - Login successful. User ID: {user.id}")  # Add this debug line
                self.login_successful.emit(user)
                self.close()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
        except Exception as e:
            QMessageBox.critical(self, "Login Error", f"An error occurred during login: {str(e)}")

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