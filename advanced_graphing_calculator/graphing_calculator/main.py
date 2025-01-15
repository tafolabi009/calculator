import json
import sys
from datetime import datetime

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox,
                             QDoubleSpinBox,
                             QTextEdit, QMessageBox, QGridLayout,
                             QListWidget, QInputDialog, QFileDialog)
from PyQt6.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from auth_system import User
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

        # Continue with the rest of your initialization...
        # (Add the remaining widgets and controls)
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

    def setup_sidebar_components(self, layout):
        # Header with user info
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_widget.setLayout(header_layout)

        self.user_info = QLabel("Not logged in")
        self.user_info.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        header_layout.addWidget(self.user_info)

        logout_btn = ModernButton("Logout")
        logout_btn.clicked.connect(self.handle_logout)
        header_layout.addWidget(logout_btn)

        layout.addWidget(header_widget)

        # Function input section
        input_group = QWidget()
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)

        input_label = QLabel("Function Input")
        input_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        input_layout.addWidget(input_label)

        self.expr_input = ModernLineEdit()
        self.expr_input.setPlaceholderText("Enter expression (e.g., sin(x))")
        input_layout.addWidget(self.expr_input)

        # Add range controls
        range_group = QWidget()
        range_layout = QGridLayout()
        range_group.setLayout(range_layout)

        # X range
        self.x_min = QDoubleSpinBox()
        self.x_min.setRange(-1000, 1000)
        self.x_min.setValue(-10)

        self.x_max = QDoubleSpinBox()
        self.x_max.setRange(-1000, 1000)
        self.x_max.setValue(10)

        # Y range
        self.y_min = QDoubleSpinBox()
        self.y_min.setRange(-1000, 1000)
        self.y_min.setValue(-10)

        self.y_max = QDoubleSpinBox()
        self.y_max.setRange(-1000, 1000)
        self.y_max.setValue(10)

        # Add range controls to layout
        range_layout.addWidget(QLabel("X Range:"), 0, 0)
        range_layout.addWidget(self.x_min, 0, 1)
        range_layout.addWidget(QLabel("to"), 0, 2)
        range_layout.addWidget(self.x_max, 0, 3)

        range_layout.addWidget(QLabel("Y Range:"), 1, 0)
        range_layout.addWidget(self.y_min, 1, 1)
        range_layout.addWidget(QLabel("to"), 1, 2)
        range_layout.addWidget(self.y_max, 1, 3)

        input_layout.addWidget(range_group)

        # Scale type
        self.scale_type = QComboBox()
        self.scale_type.addItems(['Radians', 'Degrees'])
        input_layout.addWidget(self.scale_type)

        layout.addWidget(input_group)

        # Add teacher controls
        self.teacher_controls = self.create_teacher_controls()
        layout.addWidget(self.teacher_controls)
        self.teacher_controls.hide()

    def setup_content_components(self, layout):
        # Graph canvas
        self.canvas = GraphCanvas()
        layout.addWidget(self.canvas)

        # Action buttons
        buttons = QWidget()
        buttons_layout = QHBoxLayout()
        buttons.setLayout(buttons_layout)

        plot_btn = ModernButton("Plot Graph")
        plot_btn.clicked.connect(self.plot_graph)
        buttons_layout.addWidget(plot_btn)

        save_btn = ModernButton("Save Graph")
        save_btn.clicked.connect(self.save_graph)
        buttons_layout.addWidget(save_btn)

        save_image_btn = ModernButton("Save Image")
        save_image_btn.clicked.connect(self.save_graph_image)
        buttons_layout.addWidget(save_image_btn)

        layout.addWidget(buttons)


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
        self.comment_input.setMinimumHeight(150)

        teacher_layout.addWidget(QLabel("Add Comment"))
        teacher_layout.addWidget(self.comment_input)

        add_comment_button = ModernButton("Add Comment")
        add_comment_button.clicked.connect(self.add_comment)
        teacher_layout.addWidget(add_comment_button)

        # Create sidebar with modern styling
        sidebar = QWidget()
        sidebar.setMinimumWidth(350)  # Increased sidebar width
        sidebar.setMaximumWidth(400)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                border-right: 1px solid #333340;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)  # Increased margins
        sidebar_layout.setSpacing(20)  # Increased spacing

        # Header section with user info and logout
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(10)

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
        logout_btn.setMinimumHeight(40)  # Increased button height
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                border: none;
                color: white;
                padding: 10px 20px;
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
        input_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        input_layout.addWidget(input_label)

        self.expr_input = ModernLineEdit()
        self.expr_input.setMinimumHeight(45)  # Increased input height
        self.expr_input.setPlaceholderText("Enter expression (e.g., sin(x))")
        input_layout.addWidget(self.expr_input)

        self.second_expr_input = ModernLineEdit()
        self.second_expr_input.setMinimumHeight(45)  # Increased input height
        self.second_expr_input.setPlaceholderText("Enter second expression (optional)")
        input_layout.addWidget(self.second_expr_input)
        sidebar_layout.addWidget(input_group)

        # Add range controls
        range_group = QWidget()
        range_layout = QGridLayout(range_group)

        # X range
        x_range_label = QLabel("X Range:")
        x_range_label.setStyleSheet("color: white; font-weight: bold;")
        range_layout.addWidget(x_range_label, 0, 0)

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
        range_layout.addWidget(self.x_min, 0, 1)

        x_to_label = QLabel("to")
        x_to_label.setStyleSheet("color: white;")
        range_layout.addWidget(x_to_label, 0, 2)

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
        range_layout.addWidget(self.x_max, 0, 3)

        # Scale type
        scale_label = QLabel("Scale Type:")
        scale_label.setStyleSheet("color: white; font-weight: bold;")
        range_layout.addWidget(scale_label, 1, 0)

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
        range_layout.addWidget(self.scale_type, 1, 1, 1, 3)

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
        self.student_selector.setMinimumHeight(45)
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
        self.student_graph_list.setMinimumHeight(300)  # Increased height
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

        self.comment_input = QTextEdit()  # Changed from QLineEdit to QTextEdit
        self.comment_input.setMinimumHeight(100)  # Set minimum height
        self.comment_input.setPlaceholderText("Write a comment...")
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

        add_comment_btn = ModernButton("Add Comment")
        add_comment_btn.setMinimumHeight(40)
        add_comment_btn.clicked.connect(self.add_comment)
        teacher_layout.addWidget(add_comment_btn)

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

        # Action buttons
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(15)

        plot_btn = ModernButton("Plot Graph")
        plot_btn.setMinimumHeight(40)
        plot_btn.clicked.connect(self.plot_graph)
        buttons_layout.addWidget(plot_btn)

        load_graphs_btn = ModernButton("Load Saved Graphs")
        load_graphs_btn.setMinimumHeight(40)
        load_graphs_btn.clicked.connect(self.load_user_graphs)
        sidebar_layout.addWidget(load_graphs_btn)

        save_graph_btn = ModernButton("Save Graph")
        save_graph_btn.setMinimumHeight(40)
        save_graph_btn.clicked.connect(self.save_graph)
        buttons_layout.addWidget(save_graph_btn)

        save_image_btn = ModernButton("Save as Image")
        save_image_btn.setMinimumHeight(40)
        save_image_btn.clicked.connect(self.save_graph_image)
        buttons_layout.addWidget(save_image_btn)

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
        content_layout.addWidget(self.student_comments_widget)

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
            # Load users from the database
            with open('users.json', 'r') as f:
                users_data = json.load(f)

            # Filter for student users
            students = [
                username for username, data in users_data.items()
                if data['role'] == 'student'
            ]

            # Update the student selector
            self.student_selector.clear()
            if students:
                self.student_selector.addItems(students)
                self.student_list = students
            else:
                QMessageBox.information(self, "Info", "No students found")

        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", "No user database found")
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

    def save_graph(self):
        """Save the current graph"""
        try:
            # Get current expression
            expression = self.expr_input.text().strip()
            if not expression:
                QMessageBox.warning(self, "Error", "Please enter an expression")
                return

            # Get name for the graph
            name, ok = QInputDialog.getText(self, "Save Graph", "Enter a name for the graph:")
            if not ok or not name:
                return

            # Create graph object
            graph = Graph(
                expression=expression,
                variable=self.var_selector.currentText(),
                start=float(self.x_min.value()),
                end=float(self.x_max.value()),
                scale_type=self.scale_type.currentText().lower(),
                comments=[]
            )

            # Save to calculator
            self.calculator.graphs[name] = graph

            # Ask user where to save the JSON file
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Graph Data",
                f"{name}.json",
                "JSON Files (*.json);;All Files (*)"
            )

            if file_name:
                # Save to JSON file
                self.calculator.save_graphs(file_name)

                # If this is a student's graph, also save as PNG
                if self.current_user and self.current_user.role == 'student':
                    png_file = file_name.rsplit('.', 1)[0] + '.png'
                    self.canvas.figure.savefig(
                        png_file,
                        facecolor=self.canvas.figure.get_facecolor(),
                        edgecolor='none',
                        bbox_inches='tight'
                    )

                # Update history
                self.update_history()
                QMessageBox.information(self, "Success", "Graph saved successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving graph: {str(e)}")

    def add_comment(self):
        """Add a teacher comment to the selected graph"""
        if not self.current_user or self.current_user.role != 'teacher':
            QMessageBox.warning(self, "Error", "Only teachers can add comments")
            return

        selected_student = self.student_selector.currentText()
        if not selected_student:
            QMessageBox.warning(self, "Error", "Please select a student")
            return

        selected_items = self.student_graph_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a graph to comment on")
            return

        graph_name = selected_items[0].text()
        comment_text = self.comment_input.toPlainText().strip()

        if not comment_text:
            QMessageBox.warning(self, "Error", "Please enter a comment")
            return

        # Add comment to graph
        comment = {
            'teacher': self.current_user.username,
            'comment': comment_text,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if graph_name in self.calculator.graphs:
            if not hasattr(self.calculator.graphs[graph_name], 'comments'):
                self.calculator.graphs[graph_name].comments = []
            self.calculator.graphs[graph_name].comments.append(comment)

            # Update comments display
            self.update_comments(graph_name)

            # Clear comment input
            self.comment_input.clear()

            # Save changes
            filename = f"graphs_{selected_student}.json"
            self.calculator.save_graphs(filename)
            QMessageBox.information(self, "Success", "Comment added successfully!")

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

    def load_user_graphs(self):
        """Load graphs for the current user"""
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please log in first")
            return

        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Load Graph Data",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            if file_name:
                self.calculator.load_graphs(file_name)
                self.update_history()

                # Load the first graph if available
                if self.history_list.count() > 0:
                    first_item = self.history_list.item(0)
                    self.load_graph_from_history(first_item)

                QMessageBox.information(self, "Success", "Graphs loaded successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading graphs: {str(e)}")

    def load_selected_student_graphs(self):
        selected_student = self.student_selector.currentText()
        if not selected_student:
            return
        try:
            filename = f"graphs_{selected_student}.json"
            self.calculator.load_graphs(filename)
            self.update_history()
        except FileNotFoundError:
            self.calculator.clear_graphs()
            self.update_history()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading graphs: {e}")

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

            # Get ranges and settings
            x_min = self.x_min.value()
            x_max = self.x_max.value()
            y_min = self.y_min.value()
            y_max = self.y_max.value()
            variable = self.var_selector.currentText()
            scale_type = self.scale_type.currentText().lower()

            # Generate x values
            x_values = np.linspace(x_min, x_max, 1000)

            # Generate y values using evaluate_expression with selected variable
            y_values = [
                self.calculator.evaluate_expression(
                    expression.replace(variable, str(x)),
                    x,
                    scale_type
                )
                for x in x_values
            ]

            # Plot the graph
            self.canvas.axes.plot(x_values, y_values, label=expression)

            # Set axis limits
            self.canvas.axes.set_xlim(x_min, x_max)
            self.canvas.axes.set_ylim(y_min, y_max)

            # Add labels and legend
            self.canvas.axes.set_xlabel(variable)
            self.canvas.axes.set_ylabel("f(" + variable + ")")
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

            def save_graph(self):
                """Save the current graph to a JSON file"""
                try:
                    expression = self.expr_input.text().strip()
                    if not expression:
                        QMessageBox.warning(self, "Error", "Please enter an expression first")
                        return

                    name, ok = QInputDialog.getText(self, "Save Graph", "Enter a name for this graph:")
                    if ok and name:
                        graph = Graph(
                            expression=expression,
                            variable=self.var_selector.currentText(),
                            start=self.x_min.value(),
                            end=self.x_max.value(),
                            scale_type=self.scale_type.currentText().lower()
                        )
                        self.calculator.save_graph(name, graph)
                        QMessageBox.information(self, "Success", "Graph saved successfully!")
                        self.update_history()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error saving graph: {str(e)}")

            def handle_logout(self):
                """Handle user logout"""
                try:
                    if self.current_user:
                        # Save any unsaved work
                        filename = f"graphs_{self.current_user.username}.json"
                        self.calculator.save_graphs(filename)

                    self.current_user = None
                    self.calculator.clear_graphs()
                    self.update_history()
                    self.user_info.setText("Not logged in")
                    self.teacher_controls.hide()
                    self.student_comments_widget.hide()
                    self.close()

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error during logout: {str(e)}")

            def closeEvent(self, event):
                """Handle application close event"""
                try:
                    if self.current_user:
                        filename = f"graphs_{self.current_user.username}.json"
                        self.calculator.save_graphs(filename)
                    event.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error saving graphs: {str(e)}")
                    event.ignore()

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

                    # Load user's graphs
                    self.load_user_graphs()

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error setting user: {str(e)}")

            def create_user_info_section(self, parent_layout):
                # User info
                self.user_info = QLabel("Not logged in")
                self.user_info.setStyleSheet("""
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                """)
                parent_layout.addWidget(self.user_info)

                # Logout button
                logout_btn = ModernButton("Logout")
                logout_btn.clicked.connect(self.handle_logout)
                parent_layout.addWidget(logout_btn)

            def create_input_section(self, parent_layout):
                # Function input group
                input_group = QWidget()
                input_layout = QVBoxLayout(input_group)

                # Function input
                self.expr_input = ModernLineEdit()
                self.expr_input.setPlaceholderText("Enter expression (e.g., sin(x))")
                input_layout.addWidget(self.expr_input)

                # Secondary input
                self.second_expr_input = ModernLineEdit()
                self.second_expr_input.setPlaceholderText("Enter second expression (optional)")
                input_layout.addWidget(self.second_expr_input)

                parent_layout.addWidget(input_group)

            def create_range_controls(self, parent_layout):
                range_group = QWidget()
                range_layout = QHBoxLayout(range_group)

                # X range controls
                self.x_min = QDoubleSpinBox()
                self.x_min.setRange(-1000, 1000)
                self.x_min.setValue(-10)
                range_layout.addWidget(QLabel("X Min:"))
                range_layout.addWidget(self.x_min)

                self.x_max = QDoubleSpinBox()
                self.x_max.setRange(-1000, 1000)
                self.x_max.setValue(10)
                range_layout.addWidget(QLabel("X Max:"))
                range_layout.addWidget(self.x_max)

                # Scale type
                self.scale_type = QComboBox()
                self.scale_type.addItems(['Radians', 'Degrees'])
                range_layout.addWidget(QLabel("Scale:"))
                range_layout.addWidget(self.scale_type)

                parent_layout.addWidget(range_group)

            def create_teacher_controls(self, parent_layout):
                self.teacher_controls = QWidget()
                teacher_layout = QVBoxLayout(self.teacher_controls)

                # Student selector
                self.student_selector = QComboBox()
                self.student_selector.setEditable(True)
                teacher_layout.addWidget(self.student_selector)

                # Graph history
                self.history_list = QListWidget()
                teacher_layout.addWidget(self.history_list)

                # Comments
                self.comment_input = QTextEdit()
                self.comment_input.setPlaceholderText("Write a comment...")
                teacher_layout.addWidget(self.comment_input)

                # Add comment button
                add_comment_btn = ModernButton("Add Comment")
                add_comment_btn.clicked.connect(self.add_comment)
                teacher_layout.addWidget(add_comment_btn)

                parent_layout.addWidget(self.teacher_controls)
                self.teacher_controls.hide()  # Hidden by default

            def create_action_buttons(self, parent_layout):
                buttons_container = QWidget()
                buttons_layout = QHBoxLayout(buttons_container)

                plot_btn = ModernButton("Plot Graph")
                plot_btn.clicked.connect(self.plot_graph)
                buttons_layout.addWidget(plot_btn)

                save_btn = ModernButton("Save Graph")
                save_btn.clicked.connect(self.save_graph)
                buttons_layout.addWidget(save_btn)

                save_image_btn = ModernButton("Save Image")
                save_image_btn.clicked.connect(self.save_graph_image)
                buttons_layout.addWidget(save_image_btn)

                parent_layout.addWidget(buttons_container)

            def load_student_list(self):
                """Load list of students for teacher view"""
                if not self.current_user or self.current_user.role != 'teacher':
                    return

                try:
                    # Load users from database
                    with open('users.json', 'r') as f:
                        users_data = json.load(f)
                        students = [
                            username for username, data in users_data.items()
                            if data['role'] == 'student'
                        ]

                    self.student_selector.clear()
                    self.student_selector.addItems(students)

                except FileNotFoundError:
                    QMessageBox.warning(self, "Warning", "No students found")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error loading student list: {str(e)}")

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