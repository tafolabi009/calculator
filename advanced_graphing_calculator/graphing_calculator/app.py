# app.py
from auth_system import AuthWindow, User
from main import MainWindow, GraphingCalculator
from PyQt6.QtWidgets import QApplication, QMessageBox
import sys


class CalculatorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.calculator = GraphingCalculator()
        self.auth_window = AuthWindow()
        self.main_window = None

        # Connect signals
        self.auth_window.login_successful.connect(self.handle_login)

    def handle_login(self, user: User):
        """Handle successful login"""
        try:
            if self.main_window is None:
                self.main_window = MainWindow(self.calculator)

            self.main_window.set_user(user)
            self.auth_window.hide()
            self.main_window.show()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error during login: {str(e)}")

    def run(self):
        """Start the application"""
        self.auth_window.show()
        return self.app.exec()


def main():
    app = CalculatorApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()