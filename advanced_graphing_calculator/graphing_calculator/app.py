# app.py
from auth_system import AuthWindow, User
from main import MainWindow, GraphingCalculator
from PyQt6.QtWidgets import QApplication
import sys

class CalculatorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.calculator = GraphingCalculator()
        self.auth_window = AuthWindow()
        self.main_window = None

        # Connect authentication signal to handle_login
        self.auth_window.login_successful.connect(self.handle_login)

    def handle_login(self, user: User):
        """Handle successful login by creating and showing main window"""
        self.main_window = MainWindow(self.calculator)
        self.main_window.set_user(user)
        self.main_window.show()

    def run(self):
        """Start the application"""
        self.auth_window.show()
        return self.app.exec()

def main():
    app = CalculatorApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()