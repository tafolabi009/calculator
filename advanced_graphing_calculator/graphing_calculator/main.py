import sys

import numpy as np
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox,
                             QDoubleSpinBox,
                             QTextEdit, QMessageBox, QGridLayout,
                             QListWidget, QInputDialog, )
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from auth_system import User
from database import AdvancedDatabase
from graphing_calculator import GraphingCalculator, Graph


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
            self.parent.add_comment()  # Call parent's add_comment method
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

        # Create input group
        input_group = QWidget()
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(15)

        # Add function input label
        input_label = QLabel("Function Input")
        input_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        input_layout.addWidget(input_label)

        # Add expression inputs
        self.expr_input = ModernLineEdit()
        self.expr_input.setMinimumHeight(45)
        self.expr_input.setPlaceholderText("Enter expression (e.g., sin(x))")
        input_layout.addWidget(self.expr_input)

        self.second_expr_input = ModernLineEdit()
        self.second_expr_input.setMinimumHeight(45)
        self.second_expr_input.setPlaceholderText("Enter second expression (optional)")
        input_layout.addWidget(self.second_expr_input)

        # Add range and variable controls after the expression inputs
        range_group = QWidget()
        range_layout = QGridLayout(range_group)
        range_layout.setSpacing(10)

        # Variable selector
        var_label = QLabel("Variable:")
        var_label.setStyleSheet("color: white; font-weight: bold;")
        self.var_selector = QComboBox()
        self.var_selector.addItems(['x', 'y', 't'])
        self.var_selector.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        range_layout.addWidget(var_label, 0, 0)
        range_layout.addWidget(self.var_selector, 0, 1, 1, 3)

        # X range
        x_range_label = QLabel("X Range:")
        x_range_label.setStyleSheet("color: white; font-weight: bold;")
        range_layout.addWidget(x_range_label, 1, 0)

        self.x_min = QDoubleSpinBox()
        self.x_min.setRange(-1000, 1000)
        self.x_min.setValue(-10)
        self.x_min.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        range_layout.addWidget(self.x_min, 1, 1)

        x_to_label = QLabel("to")
        x_to_label.setStyleSheet("color: white;")
        range_layout.addWidget(x_to_label, 1, 2)

        self.x_max = QDoubleSpinBox()
        self.x_max.setRange(-1000, 1000)
        self.x_max.setValue(10)
        self.x_max.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        range_layout.addWidget(self.x_max, 1, 3)

        # Y range
        y_range_label = QLabel("Y Range:")
        y_range_label.setStyleSheet("color: white; font-weight: bold;")
        range_layout.addWidget(y_range_label, 2, 0)

        self.y_min = QDoubleSpinBox()
        self.y_min.setRange(-1000, 1000)
        self.y_min.setValue(-10)
        self.y_min.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        range_layout.addWidget(self.y_min, 2, 1)

        y_to_label = QLabel("to")
        y_to_label.setStyleSheet("color: white;")
        range_layout.addWidget(y_to_label, 2, 2)

        self.y_max = QDoubleSpinBox()
        self.y_max.setRange(-1000, 1000)
        self.y_max.setValue(10)
        self.y_max.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        range_layout.addWidget(self.y_max, 2, 3)

        # Scale type
        scale_label = QLabel("Scale:")
        scale_label.setStyleSheet("color: white; font-weight: bold;")
        range_layout.addWidget(scale_label, 3, 0)

        self.scale_type = QComboBox()
        self.scale_type.addItems(['Radians', 'Degrees'])
        self.scale_type.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        range_layout.addWidget(self.scale_type, 3, 1, 1, 3)

        input_layout.addWidget(range_group)

        # Add Load Graphs button
        load_graphs_btn = ModernButton("Load Graphs")
        load_graphs_btn.clicked.connect(self.load_user_graphs)
        input_layout.addWidget(load_graphs_btn)
        # Add input group to sidebar
        sidebar_layout.addWidget(input_group)

        # Create canvas container
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        self.canvas = GraphCanvas()
        canvas_layout.addWidget(self.canvas)

        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(canvas_container)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def __init__(self):
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
        # Add these to the __init__ after creating the main layout

        self.scale_type = QComboBox()
        self.scale_type.addItems(['Radians', 'Degrees'])


class MainWindow(QMainWindow):
    def __init__(self, calculator: GraphingCalculator):
        super().__init__()
        self.calculator = calculator
        self.current_user = None

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

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

        # Create sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)

        # Add components to sidebar
        self.setup_sidebar_components(sidebar_layout)

        # Create content area
        content = QWidget()
        content_layout = QVBoxLayout()
        content.setLayout(content_layout)

        # Add components to content area
        self.setup_content_components(content_layout)

        # Add widgets to main layout
        layout.addWidget(sidebar)
        layout.addWidget(content)

        # Initialize other instance variables
        self.history_list = QListWidget()

        # Set window properties
        self.setWindowTitle("Graphing Calculator")
        self.setMinimumSize(1200, 800)
        self.setPalette(DarkPalette())

    def set_user(self, user: User):
        """Set the current user and update UI accordingly"""
        try:
            self.current_user = user
            self.calculator.set_user(user)

            # Update UI based on user role
            if user.role == "teacher":
                self.teacher_controls.show()
                self.student_comments_widget.hide()
                self.load_student_list()
            else:
                self.teacher_controls.hide()
                self.student_comments_widget.show()

            # Update user info label
            self.user_info.setText(f"Welcome, {user.full_name}\n({user.role.capitalize()})")

            # Clear any existing graphs
            self.calculator.clear_graphs()
            self.update_history()

            # Update UI layout
            self.adjustSize()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error setting user: {str(e)}")

    def setup_main_content(self):
        """Set up the main content area"""
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Add all main content components here...

        self.main_layout.addWidget(content)

    def __init__(self, calculator: GraphingCalculator):
        super().__init__()
        self.calculator = calculator
        self.current_user = None
        self.history_list = QListWidget()  # Initialize history_list

        # Main layout
        main_layout = QHBoxLayout()

        # Expand teacher controls
        self.teacher_controls = QWidget()
        teacher_layout = QVBoxLayout(self.teacher_controls)

        self.comment_input = QTextEdit()
        self.comment_input.setMinimumHeight(50)
        self.comment_input = CommentInput(self)

        teacher_layout.addWidget(QLabel("Add Comment"))
        teacher_layout.addWidget(self.comment_input)

        add_comment_button = ModernButton("Add Comment")
        add_comment_button.clicked.connect(self.add_comment)
        teacher_layout.addWidget(add_comment_button)

        # Create sidebar with modern styling
        sidebar = QWidget()
        sidebar.setMinimumWidth(400)  # Increased sidebar width
        sidebar.setMaximumWidth(450)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                border-right: 1px solid #333340;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)  # Increased margins
        sidebar_layout.setSpacing(10)  # Increased spacing

        # Header section with user info and logout
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

        # Add logout button
        logout_btn = ModernButton("Logout")
        logout_btn.setMinimumHeight(35)  # Increased button height
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

        # Expression input with improved styling
        input_group = QWidget()
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(15)

        input_label = QLabel("Function Input")
        input_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        input_layout.addWidget(input_label)

        self.expr_input = ModernLineEdit()
        self.expr_input.setMinimumHeight(35)  # Increased input height
        self.expr_input.setPlaceholderText("Enter expression (e.g., sin(x))")
        input_layout.addWidget(self.expr_input)

        self.second_expr_input = ModernLineEdit()
        self.second_expr_input.setMinimumHeight(35)  # Increased input height
        self.second_expr_input.setPlaceholderText("Enter second expression (optional)")
        input_layout.addWidget(self.second_expr_input)
        sidebar_layout.addWidget(input_group)

        # Add variable selector and range controls
        controls_group = QWidget()
        controls_layout = QVBoxLayout(controls_group)

        # Variable selector
        var_selector_group = QWidget()
        var_selector_layout = QHBoxLayout(var_selector_group)

        var_label = QLabel("Variable:")
        var_label.setStyleSheet("color: white; font-weight: bold;")
        self.var_selector = QComboBox()  # Make it an instance variable with self
        self.var_selector.addItems(['x', 'y', 't'])
        self.var_selector.setStyleSheet("""
                    QComboBox {
                        background-color: #2d2d2d;
                        color: white;
                        border: 2px solid #3d3d3d;
                        border-radius: 4px;
                        padding: 5px;
                    }
                """)
        var_selector_layout.addWidget(var_label)
        var_selector_layout.addWidget(self.var_selector)
        controls_layout.addWidget(var_selector_group)

        # Range controls
        range_group = QWidget()
        range_layout = QGridLayout(range_group)

        # X range
        x_label = QLabel("X Range:")
        x_label.setStyleSheet("color: white; font-weight: bold;")
        range_layout.addWidget(x_label, 0, 0)

        self.x_min = QDoubleSpinBox()  # Make it an instance variable
        self.x_min.setRange(-1000, 1000)
        self.x_min.setValue(-10)
        self.x_min.setStyleSheet("""
                    QDoubleSpinBox {
                        background-color: #2d2d2d;
                        color: white;
                        border: 2px solid #3d3d3d;
                        border-radius: 4px;
                        padding: 5px;
                    }
                """)
        range_layout.addWidget(self.x_min, 0, 1)

        range_layout.addWidget(QLabel("to", styleSheet="color: white;"), 0, 2)

        self.x_max = QDoubleSpinBox()  # Make it an instance variable
        self.x_max.setRange(-1000, 1000)
        self.x_max.setValue(10)
        self.x_max.setStyleSheet("""
                    QDoubleSpinBox {
                        background-color: #2d2d2d;
                        color: white;
                        border: 2px solid #3d3d3d;
                        border-radius: 4px;
                        padding: 5px;
                    }
                """)
        range_layout.addWidget(self.x_max, 0, 3)

        # Y range
        y_label = QLabel("Y Range:")
        y_label.setStyleSheet("color: white; font-weight: bold;")
        range_layout.addWidget(y_label, 1, 0)

        self.y_min = QDoubleSpinBox()  # Make it an instance variable
        self.y_min.setRange(-1000, 1000)
        self.y_min.setValue(-10)
        self.y_min.setStyleSheet("""
                    QDoubleSpinBox {
                        background-color: #2d2d2d;
                        color: white;
                        border: 2px solid #3d3d3d;
                        border-radius: 4px;
                        padding: 5px;
                    }
                """)
        range_layout.addWidget(self.y_min, 1, 1)

        range_layout.addWidget(QLabel("to", styleSheet="color: white;"), 1, 2)

        self.y_max = QDoubleSpinBox()  # Make it an instance variable
        self.y_max.setRange(-1000, 1000)
        self.y_max.setValue(10)
        self.y_max.setStyleSheet("""
                    QDoubleSpinBox {
                        background-color: #2d2d2d;
                        color: white;
                        border: 2px solid #3d3d3d;
                        border-radius: 4px;
                        padding: 5px;
                    }
                """)
        range_layout.addWidget(self.y_max, 1, 3)

        controls_layout.addWidget(range_group)
        input_layout.addWidget(controls_group)
        # Scale type
        scale_label = QLabel("Scale Type:")
        scale_label.setStyleSheet("color: white; font-weight: bold;")
        range_layout.addWidget(scale_label, 2, 0)

        self.scale_type = QComboBox()
        self.scale_type.addItems(['Radians', 'Degrees'])
        self.scale_type.setStyleSheet("""
                    QComboBox {
                        background-color: #2d2d2d;
                        color: white;
                        border: 2px solid #3d3d3d;
                        border-radius: 4px;
                        padding: 5px;
                    }
                """)
        range_layout.addWidget(self.scale_type, 2, 1, 1, 3)

        input_layout.addWidget(range_group)

        # Teacher-specific controls
        self.teacher_controls = QWidget()
        teacher_layout = QVBoxLayout(self.teacher_controls)
        teacher_layout.setSpacing(15)

        teacher_label = QLabel("Teacher Controls")
        teacher_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        teacher_layout.addWidget(teacher_label)

        # Add a searchable student selector
        self.student_selector = QComboBox()
        self.student_selector.setMinimumHeight(35)
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

        # Add student graph history
        student_history_label = QLabel("Student Graph History")
        student_history_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        teacher_layout.addWidget(student_history_label)

        self.student_graph_list = QListWidget()
        self.student_graph_list.setMinimumHeight(30)  # Increased height
        self.student_graph_list.setStyleSheet("""
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
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)
        self.student_graph_list.itemClicked.connect(self.load_graph_from_history)
        teacher_layout.addWidget(self.student_graph_list)

        # Add comments section
        comment_label = QLabel("Add Comment")
        comment_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        teacher_layout.addWidget(comment_label)

        # In the teacher controls section, replace the comment input creation with:
        self.comment_input = CommentInput(self)  # Use custom CommentInput
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
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Main content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Graph canvas
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        self.canvas = GraphCanvas()
        canvas_layout.addWidget(self.canvas)
        content_layout.addWidget(canvas_container)


        # Action buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_container.setLayout(buttons_layout)
        buttons_layout.setSpacing(10)

        # Left side buttons
        left_buttons = QWidget()
        left_layout = QHBoxLayout()
        left_buttons.setLayout(left_layout)
        left_layout.setSpacing(10)

        plot_btn = ModernButton("Plot Graph")
        plot_btn.clicked.connect(self.plot_graph)
        left_layout.addWidget(plot_btn)

        load_graphs_btn = ModernButton("Load Graphs")  # Moved here
        load_graphs_btn.clicked.connect(self.load_graphs())  # Add parentheses
        left_layout.addWidget(load_graphs_btn)

        clear_btn = ModernButton("Clear")
        clear_btn.clicked.connect(self.clear_graph)
        left_layout.addWidget(clear_btn)

        # Right side buttons
        right_buttons = QWidget()
        right_layout = QHBoxLayout()
        right_buttons.setLayout(right_layout)
        right_layout.setSpacing(10)

        save_graph_btn = ModernButton("Save Graph")
        save_graph_btn.clicked.connect(self.save_graph)
        right_layout.addWidget(save_graph_btn)

        save_image_btn = ModernButton("Save Image")
        save_image_btn.clicked.connect(self.save_graph_image)
        right_layout.addWidget(save_image_btn)

        buttons_layout.addWidget(right_buttons)
        content_layout.addWidget(buttons_container)

        # Comments section for students
        self.student_comments_widget = QWidget()
        comments_layout = QVBoxLayout(self.student_comments_widget)

        comments_label = QLabel("Teacher Comments")
        comments_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        comments_layout.addWidget(comments_label)


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
        comments_layout.addWidget(self.comments_list)
        content_layout.addWidget(self.comments_list)

        main_layout.addWidget(content)

        # Set central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Apply dark theme
        self.setPalette(DarkPalette())

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
            self.student_comments_widget.hide()
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

    def update_comments(self, graph_name):
        """Update the comments list for the selected graph"""
        self.comments_list.clear()
        if graph_name in self.calculator.graphs:
            comments = self.calculator.graphs[graph_name].comments
            for comment in comments:
                if isinstance(comment, dict):
                    item_text = f"{comment['teacher']} ({comment['timestamp']}): {comment['comment']}"
                else:
                    item_text = str(comment)
                self.comments_list.addItem(item_text)

    def load_graphs(self, filename=None):
        """Load graphs from a file"""
        if not filename and not self.current_user:
            return

        if not filename:
            filename = f"graphs_{self.current_user.username}.json"

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.graphs = {
                    name: Graph.from_dict(graph_data)
                    for name, graph_data in data.items()
                }

    def save_graph(self):
        """Save the current graph to the database"""
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please log in to save graphs")
            return

        try:
            # Get current graph data
            expression = self.expr_input.text().strip()
            if not expression:
                QMessageBox.warning(self, "Error", "Please enter an expression first")
                return

            # Get graph name from user
            name, ok = QInputDialog.getText(self, "Save Graph", "Enter a name for this graph:")
            if not ok or not name:
                return

            # Create graph data dictionary
            graph_data = {
                'name': name,
                'expression': expression,
                'variable': self.var_selector.currentText(),
                'x_min': self.x_min.value(),
                'x_max': self.x_max.value(),
                'y_min': self.y_min.value(),
                'y_max': self.y_max.value(),
                'scale_type': self.scale_type.currentText().lower()
            }

            # Save to database
            from database import AdvancedDatabase
            db = AdvancedDatabase()

            # Print debug information
            print(f"Debug - User ID: {self.current_user.id}")
            print(f"Debug - Graph Data: {graph_data}")

            db.save_graph_state(self.current_user.id, graph_data)

            # Update the history list
            self.update_history()

            QMessageBox.information(self, "Success", "Graph saved successfully!")
        except AttributeError as e:
            QMessageBox.critical(self, "Error",
                                 "Some graph properties are not properly initialized. Please check all values.")
            print(f"Debug - AttributeError: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving graph: {str(e)}")
            print(f"Debug - General Error: {str(e)}")

    def load_user_graphs(self):
        """Load graphs for the current user from database"""
        if not self.current_user:
            return

        try:
            db = AdvancedDatabase()
            graphs = db.get_user_graph_history(self.current_user.id)

            # Clear current history
            self.history_list.clear()

            # Add graphs to history list
            for graph in graphs:
                self.history_list.addItem(graph['name'])

            # Store the graph data for reference
            self.graph_data = {graph['name']: graph for graph in graphs}

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading graphs: {str(e)}")

    def load_selected_student_graphs(self):
        """Load graphs for selected student"""
        selected_student = self.student_selector.currentText()
        if not selected_student:
            return

        try:
            db = AdvancedDatabase()
            graphs = db.get_student_graphs(selected_student)

            # Clear and update student graph list
            self.student_graph_list.clear()
            for graph in graphs:
                self.student_graph_list.addItem(graph['name'])

            # Store the graph data for reference
            self.student_graph_data = {graph['name']: graph for graph in graphs}

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading student graphs: {str(e)}")

    def add_comment(self):
        """Add a teacher comment to the selected graph"""
        if not self.current_user or self.current_user.role != 'teacher':
            QMessageBox.warning(self, "Error", "Only teachers can add comments")
            return

        comment_text = self.comment_input.toPlainText().strip()
        if not comment_text:
            return  # Don't show warning for empty comments on Enter press

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

    def load_graph_from_history(self, item):
        """Load and display a graph from history when selected"""
        if not item:
            return

        graph_name = item.text()
        if graph_name in self.calculator.graphs:
            try:
                graph = self.calculator.graphs[graph_name]

                # Update UI controls with graph data
                self.expr_input.setText(graph.expression)
                self.x_min.setValue(graph.start)
                self.x_max.setValue(graph.end)
                self.scale_type.setCurrentText(graph.scale_type.capitalize())

                # Plot the graph
                self.plot_graph()

                # Update comments
                self.update_comments(graph_name)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading graph: {str(e)}")

    def plot_graph(self):
        try:
            # Clear the plot
            self.canvas.axes.clear()
            self.canvas.axes.grid(True, color='#666666')

            # Get input values
            expression = self.expr_input.text().strip()
            if not expression:
                QMessageBox.warning(self, "Error", "Please enter an expression")
                return

            x_min = self.x_min.value()
            x_max = self.x_max.value()
            y_min = self.y_min.value()
            y_max = self.y_max.value()
            scale_type = self.scale_type.currentText().lower()

            # Generate x values
            x_values = np.linspace(x_min, x_max, 1000)

            # Generate y values using evaluate_expression
            y_values = [
                self.calculator.evaluate_expression(expression, x, scale_type)
                for x in x_values
            ]

            # Plot the graph
            self.canvas.axes.plot(x_values, y_values, label='Graph')

            # Set axis limits
            self.canvas.axes.set_xlim(x_min, x_max)
            self.canvas.axes.set_ylim(y_min, y_max)

            # Add labels and legend
            self.canvas.axes.set_xlabel("x")
            self.canvas.axes.set_ylabel("y")
            self.canvas.axes.legend()

            # Refresh the canvas
            self.canvas.draw()

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error plotting graph: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")

            def update_history(self):
                """Update the graph history list."""
                if hasattr(self, 'history_list'):
                    self.history_list.clear()
                    for graph_name in self.calculator.graphs:
                        self.history_list.addItem(graph_name)

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
