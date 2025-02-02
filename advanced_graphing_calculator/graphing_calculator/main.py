import sys
import logging
import numpy as np
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox,
                             QDoubleSpinBox, QTextEdit, QMessageBox, QGridLayout,
                             QListWidget, QInputDialog, QFileDialog, QFrame, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from scipy import special, optimize
from sympy import sympify, lambdify
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from graphing_calculator import GraphingCalculator
from auth_system import User
from database import AdvancedDatabase

class DarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        self.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        self.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        self.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        self.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        self.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        self.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        self.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        self.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        self.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        self.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        self.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

class ModernButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
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
        """)

class ModernLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
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
        """)

class CommentInput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            if hasattr(self.parent, 'add_comment'):
                self.parent.add_comment()  # Call parent's add_comment method
            else:
                super().keyPressEvent(event)  # Handle other keys normally
        else:
            super().keyPressEvent(event)  # Handle other keys normally

class GraphCanvas(FigureCanvas):
    def __init__(self, calculator: GraphingCalculator):
        super().__init__()
        self.calculator = calculator
        self.current_user = None
        self.history_list = QListWidget()

        # Create main layout first
        main_layout = QHBoxLayout()

        # Create sidebar
        sidebar = QWidget()
        sidebar.setMinimumWidth(350)
        sidebar.setMaximumWidth(400)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                border-right: 1px solid #333340;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(20)


        # Create main layout
        self.main_layout = QHBoxLayout()
        fig = Figure(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor('#353535')
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#353535')
        super().__init__(fig)
        self.axes.grid(True, color='#666666')
        self.axes.spines['bottom'].set_color('#666666')
        self.axes.spines['top'].set_color('#666666')
        self.axes.spines['right'].set_color('#666666')
        self.axes.spines['left'].set_color('#666666')
        self.axes.tick_params(axis='x', colors='#666666')
        self.axes.tick_params(axis='y', colors='#666666')

        self.scale_type = QComboBox()
        self.scale_type.addItems(['Radians', 'Degrees'])

class MainWindow(QMainWindow):
    def __init__(self, calculator: GraphingCalculator):
        self.auth_window = None
        super().__init__()
        self.calculator = calculator
        self.current_user = None
        self.history_list = QListWidget()
        self.graph_data = {}
        self.var_selector_layout = QHBoxLayout()
        self.var_label = QLabel("Variable:")
        self.scale_label = QLabel("Scale:")
        self.range_group = QWidget()
        self.controls_layout = QVBoxLayout()
        self.sidebar_layout = QVBoxLayout()
        self.var_selector_layout = QHBoxLayout()
        self.min_value = QDoubleSpinBox()
        self.max_value = QDoubleSpinBox()
        self.step_value = QDoubleSpinBox()
        self.student_graph_list = QListWidget()
        self.student_graph_data = {}  # Initialize dictionary to store graph data

        # Create main layout first
        main_layout = QHBoxLayout()

        # Create sidebar
        sidebar = QWidget()
        sidebar.setMinimumWidth(350)
        sidebar.setMaximumWidth(400)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                border-right: 1px solid #333340;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(20)

        # Create a widget to hold the QHBoxLayout
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)

        # Add the sidebar widget to the main layout
        main_layout.addWidget(sidebar_widget)

        # Header section
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(5)

        self.user_info = QLabel("Not logged in")
        self.user_info.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        header_layout.addWidget(self.user_info)

        logout_btn = ModernButton("Logout")
        logout_btn.setMinimumHeight(30)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                border: none;
                color: white;
                padding: 3px 5px;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff6e6e;
            }
            QPushButton:pressed {
                background-color: #ff3333;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        header_layout.addWidget(logout_btn)
        sidebar_layout.addWidget(header_widget)

        # Expression input group
        input_group = QWidget()
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(15)

        # Add expression inputs first
        input_label = QLabel("Function Input")
        input_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        sidebar_layout.addWidget(input_label)

        self.expr_input = ModernLineEdit()
        self.expr_input.setMinimumHeight(35)
        self.expr_input.setPlaceholderText("Enter expression (e.g., sin(x))")

        self.second_expr_input = ModernLineEdit()
        self.second_expr_input.setMinimumHeight(35)
        self.second_expr_input.setPlaceholderText("Enter second expression (optional)")

        sidebar_layout.addWidget(self.expr_input)
        sidebar_layout.addWidget(self.second_expr_input)

        # Controls group (variable selector and ranges)
        controls_group = QWidget()
        controls_layout = QVBoxLayout(controls_group)

        # Create a widget for the variable selector
        var_selector_widget = QWidget()
        var_selector_layout = QHBoxLayout(var_selector_widget)  # Attach layout to widget

        # Variable selector with enhanced styling
        var_label = QLabel("Variable:")
        var_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 12px;
                margin-right: 5px;
            }
        """)

        self.var_selector = QComboBox()
        self.var_selector.addItems(['x', 'y', 't', 'θ', 'r'])
        self.var_selector.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
            }
            QComboBox:hover {
                border-color: #4d4d4d;
                background-color: #353535;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)

        # Scale type selector
        scale_label = QLabel("Scale:")
        scale_label.setStyleSheet(var_label.styleSheet())  # Reuse the style

        self.scale_type = QComboBox()
        self.scale_type.addItems(['Linear', 'Log', 'Polar', 'Parametric'])
        self.scale_type.setStyleSheet(self.var_selector.styleSheet())

        # Add widgets to var_selector_layout
        var_selector_layout.addWidget(var_label)
        var_selector_layout.addWidget(self.var_selector)
        var_selector_layout.addWidget(scale_label)
        var_selector_layout.addWidget(self.scale_type)
        var_selector_layout.addStretch()  # Add stretch to keep widgets aligned to the left

        # Add var_selector_widget to controls_layout
        controls_layout.addWidget(var_selector_widget)

        # Range controls
        range_group = QWidget()
        range_layout = QGridLayout(range_group)
        range_layout.setSpacing(10)

        # Range spinbox styling
        range_spinbox_style = """
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 2px;
                min-width: 20px;
            }
            QDoubleSpinBox:hover {
                border-color: #4d4d4d;
                background-color: #353535;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #3d3d3d;
                border: none;
                width: 16px;
            }
        """

        # Create range controls
        for i, (label_text, attr_name) in enumerate([
            ("Min:", "min_value"),
            ("Max:", "max_value"),
            ("Step:", "step_value")
        ]):
            label = QLabel(label_text)
            label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

            spinbox = QDoubleSpinBox()
            spinbox.setRange(-1000, 1000)
            spinbox.setDecimals(3)
            spinbox.setValue(-10 if "min" in label_text.lower() else 10)
            spinbox.setSingleStep(0.1)
            spinbox.setStyleSheet(range_spinbox_style)

            setattr(self, attr_name, spinbox)
            range_layout.addWidget(label, i, 0)
            range_layout.addWidget(spinbox, i, 1)

        # Add range_group to controls_layout
        controls_layout.addWidget(range_group)

        # Add controls_group to sidebar_layout
        sidebar_layout.addWidget(controls_group)

                # Add spacing and margins
        controls_layout.setContentsMargins(3, 3, 3, 3)
        controls_layout.setSpacing(3)
        var_selector_layout.setSpacing(3)
        range_layout.setSpacing(3)

        # Student graph history
        student_history_label = QLabel("My Graph History")
        student_history_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        sidebar_layout.addWidget(student_history_label)

        self.student_list = QListWidget()
        self.student_list.setMinimumHeight(50)
        self.student_list.setStyleSheet("""
                            QListWidget {
                                background-color: #2d2d2d;
                                border: 2px solid #3d3d3d;
                                border-radius: 6px;
                                color: white;
                                font-size: 9px;
                            }
                            QListWidget::item {
                                padding: 9px;
                            }
                            QListWidget::item:selected {
                                background-color: #4CAF50;
                            }
                        """)
        self.student_list.itemClicked.connect(self.load_graph_from_history)
        self.load_student_graphs()
        sidebar_layout.addWidget(self.student_list)

        self.student_controls = QWidget()
        student_layout = QVBoxLayout(self.student_controls)
        student_layout.setSpacing(5)

        # Teacher controls
        self.teacher_controls = QWidget()
        teacher_layout = QVBoxLayout(self.teacher_controls)
        teacher_layout.setSpacing(10)

        teacher_label = QLabel("Teacher Controls")
        teacher_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        teacher_layout.addWidget(teacher_label)

        # Student selector
        self.student_selector = QComboBox()
        self.student_selector.setMinimumHeight(30)
        self.student_selector.setEditable(True)
        self.student_selector.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                color: white;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox QLineEdit {
                color: white;
                padding: 5px;
            }
        """)
        self.student_selector.currentIndexChanged.connect(self.load_selected_student_graphs)
        teacher_layout.addWidget(self.student_selector)

        # Student graph history
        student_history_label = QLabel("Student Graph History")
        student_history_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        teacher_layout.addWidget(student_history_label)

        self.student_graph_list = QListWidget()
        self.student_graph_list.setMinimumHeight(50)
        self.student_graph_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                color: white;
                font-size: 9px;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)
        self.student_graph_list.itemClicked.connect(self.load_graph_from_history)
        teacher_layout.addWidget(self.student_graph_list)

        # Comment section
        comment_label = QLabel("Add Comment")
        comment_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        teacher_layout.addWidget(comment_label)

        self.comment_input = CommentInput(self)
        self.comment_input.setMinimumHeight(60)
        self.comment_input.setPlaceholderText("Write a comment... (Press Enter to submit)")
        self.comment_input.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                color: white;
                padding: 10px;
                font-size: 14px;
            }
        """)
        teacher_layout.addWidget(self.comment_input)

        sidebar_layout.addWidget(self.teacher_controls)
        self.teacher_controls.hide()  # Initially hidden

        # Main content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Graph canvas
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        self.canvas = GraphCanvas(self.calculator)
        canvas_layout.addWidget(self.canvas)
        content_layout.addWidget(canvas_container)

        # Action buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)

        # Left buttons
        left_buttons = QWidget()
        left_layout = QHBoxLayout(left_buttons)
        left_layout.setSpacing(10)

        plot_btn = ModernButton("Plot Graph")
        plot_btn.clicked.connect(self.plot_graph)
        left_layout.addWidget(plot_btn)

        load_graphs_btn = ModernButton("Load Graphs")
        load_graphs_btn.clicked.connect(self.load_graphs)
        left_layout.addWidget(load_graphs_btn)

        clear_btn = ModernButton("Clear")
        clear_btn.clicked.connect(self.clear_graph)
        left_layout.addWidget(clear_btn)

        buttons_layout.addWidget(left_buttons)

        # Right buttons
        right_buttons = QWidget()
        right_layout = QHBoxLayout(right_buttons)
        right_layout.setSpacing(10)

        save_graph_btn = ModernButton("Save Graph")
        save_graph_btn.clicked.connect(self.save_graph)
        right_layout.addWidget(save_graph_btn)

        save_image_btn = ModernButton("Save Image")
        save_image_btn.clicked.connect(self.save_graph_image)
        right_layout.addWidget(save_image_btn)

        buttons_layout.addWidget(right_buttons)
        content_layout.addWidget(buttons_container)

        # Comments list
        self.comments_list = QListWidget()
        self.comments_list.setMinimumHeight(150)
        self.comments_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
            }
        """)
        content_layout.addWidget(self.comments_list)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Apply dark theme
        self.setPalette(DarkPalette())

    def set_user(self, user: User):
        """Set the current user and update the UI."""
        try:
            if not user:
                raise ValueError("No user provided")

            self.current_user = user

            if user.role == 'teacher':
                self.teacher_controls.show()
                self.student_selector.show()
                self.load_student_list()
            elif user.role == 'student':
                self.teacher_controls.hide()
                self.student_selector.hide()
                self.load_student_graphs()

                # Ensure the student graph list is in the sidebar
                if not self.student_graph_list.parent():
                    sidebar_layout.addWidget(self.student_graph_list)

            # Update user info label
            self.user_info.setText(f"Welcome, {user.full_name} ({user.role.capitalize()})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error setting user: {str(e)}")

    def load_student_graphs(self):
        """Load graphs for the logged-in student only."""
        if not self.current_user or self.current_user.role != 'student':
            QMessageBox.warning(self, "Error", "No student logged in or incorrect role")
            return

        print(f"Loading graphs for user: {self.current_user.username}, ID: {self.current_user.id}")  # Debugging

        try:
            db = AdvancedDatabase()
            graphs = db.get_user_graphs(self.current_user.id)

            print(f"Fetched graphs: {graphs}")  # Debugging

            self.student_graph_list.clear()
            self.student_graph_data = {}

            if graphs:
                for graph in graphs:
                    graph_name = graph.get('name', 'Unnamed Graph')
                    graph_id = graph.get('id')

                    if not graph_name or not graph_id:
                        print(f"Invalid graph data: {graph}")  # Debugging
                        continue

                    print(f"Adding graph to UI: {graph_name}, ID: {graph_id}")  # Debugging

                    self.student_graph_list.addItem(graph_name)
                    self.student_graph_data[graph_name] = graph
            else:
                print("No graphs found for the user.")  # Debugging
                QMessageBox.information(self, "Info", "No graphs found for your account.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading graphs: {str(e)}")
            print(f"Error: {e}")  # Debugging

    def get_user_graphs(self, user_id):
        """Fetch graphs for a specific user."""
        query = f"SELECT * FROM graphs WHERE user_id = {user_id}"
        print(f"Executing database query: {query}")  # Debugging

        try:
            # Assuming self.execute_query is a method that runs a query and returns results
            results = self.execute_query(query)
            print(f"Query results: {results}")  # Debugging
            return results
        except Exception as e:
            print(f"Database query error: {e}")  # Debugging
            return []

    def load_graph_from_history(self, item):
        try:
            graph_name = item.text()
            if graph_name in self.student_graph_data:
                graph_data = self.student_graph_data[graph_name]

                # Update expression inputs with saved graph data
                self.expr_input.setText(graph_data.get('expression', ''))
                self.second_expr_input.setText(graph_data.get('expression2', ''))  # Optional

                # Update the sidebar range spin boxes using the saved values
                if 'x_min' in graph_data:
                    self.min_value.setValue(float(graph_data['x_min']))
                if 'x_max' in graph_data:
                    self.max_value.setValue(float(graph_data['x_max']))
                # If you later add separate y-range controls, update them here accordingly

                # Plot the graph using the updated values
                self.plot_graph()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading graph: {str(e)}")

    def setup_student_view(self):
        """Set up the interface for student users."""
        if self.current_user and self.current_user.role == 'student':
            self.teacher_controls.hide()
            self.load_student_graphs()  # Load student's graphs into history
        else:
            self.teacher_controls.show()

    def save_graph_image(self):
        """Save the current graph as a PNG image"""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Graph Image", "", "PNG Files (*.png);;All Files (*)"
            )
            if file_name:
                if not file_name.endswith('.png'):
                    file_name += '.png'
                self.canvas.figure.savefig(file_name,
                                           facecolor=self.canvas.figure.get_facecolor(),
                                           edgecolor='none',
                                           bbox_inches='tight')
                QMessageBox.information(self, "Success", "Graph image saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving graph image: {str(e)}")

    def load_student_list(self):
        """Load list of students for teacher view"""
        if not self.current_user or self.current_user.role != 'teacher':
            return

        try:
            from database import AdvancedDatabase
            db = AdvancedDatabase()
            students = db.get_all_students()
            self.student_selector.clear()

            if students:
                # Store complete student data
                self.student_list = students
                # Add only usernames to the combo box
                self.student_selector.addItems([student[1] for student in students])
            else:
                QMessageBox.information(self, "Info", "No students found in database")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading student list: {str(e)}")

    def handle_logout(self):
        """Handle user logout"""
        try:
            if self.current_user:
                # Save current user's graphs before logging out
                filename = f"graphs_{self.current_user.username}.json"
                try:
                    self.calculator.save_graphs(filename)
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Could not save graphs: {str(e)}")

            # Reset application state
            self.current_user = None
            self.calculator.clear_graphs()
            self.update_history()

            # Reset UI
            self.user_info.setText("Not logged in")
            self.teacher_controls.hide()
            self.expr_input.clear()
            self.second_expr_input.clear()

            # Clear the graph
            self.canvas.axes.clear()
            self.canvas.draw()

            # Create new login window and close main window
            from auth_system import AuthWindow
            self.auth_window = AuthWindow()
            self.auth_window.login_successful.connect(self.set_user)
            self.auth_window.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during logout: {str(e)}")

    def update_history(self):
        """Update the graph history list."""
        try:
            if hasattr(self, 'history_list'):
                self.history_list.clear()
                for graph_name in self.calculator.graphs:
                    self.history_list.addItem(graph_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating history: {str(e)}")

    def update_comments(self, graph_id):
        """Update the comments list for the selected graph."""
        if not graph_id:
            QMessageBox.warning(self, "Error", "Graph ID is missing.")
            return

        try:
            db = AdvancedDatabase()
            comments = db.get_graph_comments(graph_id)

            self.comments_list.clear()
            if comments:
                for comment in comments:
                    item_text = f"{comment['teacher_name']} ({comment['timestamp']}): {comment['comment']}"
                    self.comments_list.addItem(item_text)
            else:
                QMessageBox.information(self, "No Comments", "No comments found for this graph.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading comments: {str(e)}")

    def clear_graph(self):
        """Clear the current graph from the canvas."""
        try:
            self.canvas.axes.clear()  # Clear the axes on the canvas
            self.canvas.axes.grid(True, color='#666666')  # Add the grid back
            self.canvas.draw()  # Refresh the canvas
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error clearing graph: {str(e)}")

    def load_graphs(self):
        """
        Load graphs based on user role with role-based access control.
        Teachers can view all graphs while students can only view their own.
        """
        if not hasattr(self, 'current_user') or not self.current_user:
            QMessageBox.warning(
                self,
                "Authentication Error",
                "Please log in to access your graphs"
            )
            return

        self.setCursor(Qt.CursorShape.WaitCursor)  # Show loading cursor
        try:
            # Initialize the database
            db = AdvancedDatabase()

            # Get graphs based on user role
            if self.current_user.role == "teacher":
                graphs = db.get_all_graphs()
                if not graphs:
                    QMessageBox.information(
                        self,
                        "No Data",
                        "No graphs found in the database"
                    )
                    return
            else:  # Student role
                graphs = db.get_user_graphs(self.current_user.id)
                if not graphs:
                    QMessageBox.information(
                        self,
                        "No Data",
                        f"No graphs found for user {self.current_user.username}"
                    )
                    return

            # Update UI
            self.update_graph_display(graphs)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred: {str(e)}\nPlease try again or contact support."
            )
            logging.error(f"Unexpected error in load_graphs: {str(e)}")
            raise

        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)  # Restore normal cursor

    def update_graph_display(self, graphs):
        """
        Update the UI with the loaded graphs.

        Args:
            graphs (list): List of graph dictionaries containing graph data
        """
        try:
            # Clear existing display
            self.history_list.clear()
            self.graph_data = {}

            # Sort graphs by creation date (newest first)
            sorted_graphs = sorted(
                graphs,
                key=lambda x: x.get('created_at', ''),
                reverse=True
            )

            # Update UI with sorted graphs
            for graph in sorted_graphs:
                # Add additional validation
                if not isinstance(graph, dict) or 'name' not in graph:
                    logging.warning(f"Invalid graph data format: {graph}")
                    continue

                # Create display text with additional info
                display_text = (f"{graph['name']} "
                                f"({graph.get('created_at', 'No date')})")

                # Add to list widget
                item = QListWidgetItem(display_text)
                if graph.get('is_shared', False):
                    item.setIcon(QIcon('shared_icon.png'))
                self.history_list.addItem(item)

                # Store reference with unique identifier
                self.graph_data[graph['name']] = graph

            # Select the most recent graph
            if self.history_list.count() > 0:
                self.history_list.setCurrentRow(0)

            # Update status bar
            self.statusBar().showMessage(
                f"Loaded {len(graphs)} graphs successfully",
                3000
            )

        except Exception as e:
            logging.error(f"Error updating graph display: {str(e)}")
            raise

    def load_selected_student_graphs(self):
        """Load graphs for the selected student (teacher-specific)."""
        if not hasattr(self, 'student_selector') or self.current_user.role != 'teacher':
            return

        selected_student = self.student_selector.currentText()
        if not selected_student:
            QMessageBox.warning(self, "Error", "No student selected")
            return

        self.setCursor(Qt.CursorShape.WaitCursor)  # Show loading cursor
        try:
            db = AdvancedDatabase()
            graphs = db.get_student_graphs(selected_student)

            self.student_graph_list.clear()
            self.student_graph_data = {}

            if graphs:
                for graph in graphs:
                    self.student_graph_list.addItem(graph['name'])
                    self.student_graph_data[graph['name']] = graph
            else:
                QMessageBox.information(self, "Info", f"No graphs found for {selected_student}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading student graphs: {str(e)}")
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def save_graph(self):
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please log in to save graphs")
            return

        try:
            # Get current graph data from the input field and spin boxes
            expression = self.expr_input.text().strip()
            if not expression:
                QMessageBox.warning(self, "Error", "Please enter an expression first")
                return

            # Prompt user for a graph name
            name, ok = QInputDialog.getText(self, "Save Graph", "Enter a name for this graph:")
            if not ok or not name:
                return

            graph_data = {
                'name': name,
                'expression': expression,
                'variable': self.var_selector.currentText(),
                'x_min': self.min_value.value(),
                'x_max': self.max_value.value(),
                 'y_min': self.min_value.value(),
                 'y_max': self.max_value.value(),
                'scale_type': self.scale_type.currentText().lower()
            }

            from database import AdvancedDatabase
            db = AdvancedDatabase()

            print(f"Debug - User ID: {self.current_user.id}")
            print(f"Debug - Graph Data: {graph_data}")

            db.save_graph_state(self.current_user.id, graph_data)

            # Update history after saving
            self.update_history()

            QMessageBox.information(self, "Success", "Graph saved successfully!")
        except AttributeError as e:
            QMessageBox.critical(self, "Error",
                                 "Some graph properties are not properly initialized. Please check all values.")
            print(f"Debug - AttributeError: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving graph: {str(e)}")
            print(f"Debug - General Error: {str(e)}")

    def add_comment(self):
        """Add a teacher comment to the selected graph"""
        if not self.current_user or self.current_user.role != 'teacher':
            QMessageBox.warning(self, "Error", "Only teachers can add comments")
            return

        comment_text = self.comment_input.toPlainText().strip()
        if not comment_text:
            return

        selected_items = self.student_graph_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a graph to comment on")
            return

        try:
            graph_name = selected_items[0].text()
            graph_data = self.student_graph_data[graph_name]

            db = AdvancedDatabase()
            db.add_comment(graph_data['id'], self.current_user.id, comment_text)

            self.comment_input.clear()
            self.update_comments(graph_name)
            QMessageBox.information(self, "Success", "Comment added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding comment: {str(e)}")

    def plot_graph(self):
        try:
            # Clear the plot
            self.canvas.axes.clear()
            self.canvas.axes.grid(True, color='#666666', linestyle='--', alpha=0.5)

            # Get the expression from the input field
            expression = self.expr_input.text().strip()
            if not expression:
                QMessageBox.warning(self, "Error", "Please enter an expression")
                return

            # Use the sidebar spin boxes for the range values
            # Here, we use min_value and max_value for both x- and y-axes.
            # If you want separate controls for y, you can create new spin boxes.
            x_min = self.min_value.value()
            x_max = self.max_value.value()
            y_min = self.min_value.value()  # For now, reusing the same value
            y_max = self.max_value.value()  # For now, reusing the same value

            scale_type = self.scale_type.currentText().lower()

            # Generate x values based on the selected scale type
            if scale_type == 'log':
                x_min = max(1e-10, x_min)  # Prevent log(0) errors
                x_values = np.logspace(np.log10(x_min), np.log10(x_max), 1000)
                self.canvas.axes.set_xscale('log')
            else:
                x_values = np.linspace(x_min, x_max, 1000)

            # Function to evaluate the mathematical expression
            def advanced_eval(x, expr):
                try:
                    math_funcs = {
                        'ln': np.log,
                        'log': np.log10,
                        'sin': np.sin,
                        'cos': np.cos,
                        'tan': np.tan,
                        'sqrt': np.sqrt,
                        'exp': np.exp,
                        'abs': np.abs,
                        'sinh': np.sinh,
                        'cosh': np.cosh,
                        'tanh': np.tanh,
                        'asin': np.arcsin,
                        'acos': np.arccos,
                        'atan': np.arctan,
                        'sec': lambda l: 1 / np.cos(x),
                        'csc': lambda l: 1 / np.sin(l),
                        'cot': lambda l: 1 / np.tan(x),
                        'gamma': special.gamma,
                        'erf': special.erf,
                        'erfc': special.erfc,
                        'beta': special.beta,
                        'factorial': special.factorial,
                        'pi': np.pi,
                        'e': np.e,
                        'inf': np.inf,
                        'golden': (1 + np.sqrt(5)) / 2
                    }
                    expr_sympy = sympify(expr)
                    f = lambdify('x', expr_sympy, modules=['numpy', math_funcs])
                    return f(x)
                except Exception as b:
                    raise ValueError(f"Error evaluating expression: {str(b)}")

            # Calculate y values
            y_values = np.vectorize(lambda x: advanced_eval(x, expression))(x_values)

            # Plot the graph (handle complex numbers if needed)
            if np.iscomplexobj(y_values):
                self.canvas.axes.plot(
                    x_values, y_values.real,
                    label=f"Re({expression})",
                    linewidth=2,
                    color='#1f77b4'
                )
                self.canvas.axes.plot(
                    x_values, y_values.imag,
                    label=f"Im({expression})",
                    linewidth=2,
                    linestyle='--',
                    color='#ff7f0e'
                )
            else:
                mask = np.isfinite(y_values)
                x_values = x_values[mask]
                y_values = y_values[mask]
                self.canvas.axes.plot(
                    x_values, y_values,
                    label=expression,
                    linewidth=2,
                    color='#1f77b4'
                )

            # Set the axis limits
            self.canvas.axes.set_xlim(x_min, x_max)
            self.canvas.axes.set_ylim(y_min, y_max)

            # Enhance the plot appearance
            self.canvas.axes.set_xlabel("x", fontsize=10)
            self.canvas.axes.set_ylabel("y", fontsize=10)
            self.canvas.axes.legend(fontsize=10)
            self.canvas.axes.spines['top'].set_visible(False)
            self.canvas.axes.spines['right'].set_visible(False)
            self.canvas.axes.set_title(f"Graph of {expression}", pad=10)

            # Draw coordinate axes through zero if applicable
            if x_min <= 0 <= x_max:
                self.canvas.axes.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            if y_min <= 0 <= y_max:
                self.canvas.axes.axhline(y=0, color='k', linestyle='-', alpha=0.3)

            # Add gridlines
            self.canvas.axes.grid(True, which='both', linestyle='--', alpha=0.3)

            # Refresh the canvas to display the graph
            self.canvas.draw()

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error plotting graph: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")


def main():
    # Create QApplication instance
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create calculator backend
    calculator = GraphingCalculator()

    # Create main window
    window = MainWindow(calculator)
    window.setWindowTitle("Advanced Graphing Calculator")
    window.setMinimumSize(1200, 800)
    window.show()

    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
