import sys
import logging
import numpy as np
import time
from datetime import datetime
from PyQt6.QtGui import QPalette, QColor, QIcon, QShortcut, QKeySequence
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox,
                             QDoubleSpinBox, QTextEdit, QMessageBox, QGridLayout,
                             QListWidget, QInputDialog, QFileDialog, QFrame, QListWidgetItem,
                             QCheckBox, QStatusBar)
from PyQt6.QtCore import Qt, QSize, QTimer
from scipy import special, optimize
from sympy import sympify, lambdify, symbols, solve
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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
    def __init__(self, *args, fire_mode=False, **kwargs):
        super().__init__(*args, **kwargs)
        if fire_mode:
            # Fire-themed gradient button
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                               stop:0 #ff4500, stop:0.5 #ff6347, stop:1 #ff8c00);
                    border: none;
                    color: white;
                    padding: 10px 18px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    box-shadow: 0 4px 6px rgba(255, 69, 0, 0.4);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                               stop:0 #ff6347, stop:0.5 #ff7f50, stop:1 #ffa500);
                    box-shadow: 0 6px 8px rgba(255, 69, 0, 0.6);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                               stop:0 #ff2400, stop:0.5 #ff4500, stop:1 #ff6347);
                    box-shadow: 0 2px 4px rgba(255, 36, 0, 0.3);
                }
            """)
        else:
            # Modern gradient button with shadows
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #3498db, stop:1 #2980b9);
                    border: none;
                    color: white;
                    padding: 10px 18px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    box-shadow: 0 4px 6px rgba(52, 152, 219, 0.4);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #5dade2, stop:1 #3498db);
                    box-shadow: 0 6px 8px rgba(52, 152, 219, 0.6);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #2980b9, stop:1 #21618c);
                    box-shadow: 0 2px 4px rgba(41, 128, 185, 0.3);
                }
            """)

class ModernLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #34495e, stop:1 #2c3e50);
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                color: white;
                padding: 10px;
                font-size: 14px;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #2c3e50, stop:1 #34495e);
                box-shadow: 0 0 10px rgba(52, 152, 219, 0.5);
            }
            QLineEdit:hover {
                border: 2px solid #5dade2;
            }
        """)

class CommentInput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            if hasattr(self.parent, 'add_comment'):
                self.parent.add_comment()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

class GraphCanvas(FigureCanvas):
    def __init__(self, calculator: GraphingCalculator):
        fig = Figure(figsize=(8, 6), dpi=100)
        # Modern dark theme background
        fig.patch.set_facecolor('#1e1e1e')
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor('#1e1e1e')
        super().__init__(fig)
        self.axes.grid(True, color='#404040', linestyle='--', alpha=0.3)
        # Enhanced border colors
        self.axes.spines['bottom'].set_color('#3498db')
        self.axes.spines['top'].set_color('#3498db')
        self.axes.spines['right'].set_color('#3498db')
        self.axes.spines['left'].set_color('#3498db')
        self.axes.spines['bottom'].set_linewidth(2)
        self.axes.spines['top'].set_linewidth(2)
        self.axes.spines['right'].set_linewidth(2)
        self.axes.spines['left'].set_linewidth(2)
        self.axes.tick_params(axis='x', colors='#ecf0f1', labelsize=10)
        self.axes.tick_params(axis='y', colors='#ecf0f1', labelsize=10)
        self.calculator = calculator
        self.fire_mode = False
        
    def enable_fire_mode(self, enabled=True):
        """Enable or disable fire visual theme"""
        self.fire_mode = enabled
        if enabled:
            self.axes.set_facecolor('#1a0000')
            self.axes.spines['bottom'].set_color('#ff4500')
            self.axes.spines['top'].set_color('#ff4500')
            self.axes.spines['right'].set_color('#ff4500')
            self.axes.spines['left'].set_color('#ff4500')
            self.axes.grid(True, color='#ff6347', linestyle='--', alpha=0.2)
            self.axes.tick_params(axis='x', colors='#ffa500')
            self.axes.tick_params(axis='y', colors='#ffa500')
        else:
            self.axes.set_facecolor('#1e1e1e')
            self.axes.spines['bottom'].set_color('#3498db')
            self.axes.spines['top'].set_color('#3498db')
            self.axes.spines['right'].set_color('#3498db')
            self.axes.spines['left'].set_color('#3498db')
            self.axes.grid(True, color='#404040', linestyle='--', alpha=0.3)
            self.axes.tick_params(axis='x', colors='#ecf0f1')
            self.axes.tick_params(axis='y', colors='#ecf0f1')
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self, calculator: GraphingCalculator):
        self.auth_window = None
        super().__init__()
        # Calculate center position
        screen = QApplication.primaryScreen().geometry()
        window_size = QSize(1200, 800)  # Default size
        if window_size.width() > screen.width():
            window_size.setWidth(screen.width() * 0.9)
        if window_size.height() > screen.height():
            window_size.setHeight(screen.height() * 0.9)
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.setGeometry(x, y, window_size.width(), window_size.height())
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
        self.student_graph_data = {}
        main_layout = QHBoxLayout()
        sidebar = QWidget()
        sidebar.setMinimumWidth(5)
        sidebar.setMaximumWidth(10)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-right: 1px solid #333340;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(20)
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar_widget)
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
        input_label = QLabel("Function Input")
        input_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        sidebar_layout.addWidget(input_label)
        self.expr_input = ModernLineEdit()
        self.expr_input.setMinimumHeight(35)
        self.expr_input.setPlaceholderText("Enter expression (e.g., sin(x) or 3x+1=2x+8)")
        sidebar_layout.addWidget(self.expr_input)
        self.second_expr_input = ModernLineEdit()
        self.second_expr_input.setMinimumHeight(35)
        self.second_expr_input.setPlaceholderText("Enter second expression (optional)")
        sidebar_layout.addWidget(self.second_expr_input)
        controls_group = QWidget()
        controls_layout = QVBoxLayout(controls_group)
        var_selector_widget = QWidget()
        var_selector_layout = QHBoxLayout(var_selector_widget)
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
        scale_label = QLabel("Scale:")
        scale_label.setStyleSheet(var_label.styleSheet())
        self.scale_type = QComboBox()
        self.scale_type.addItems(['Linear', 'Log', 'Polar', 'Parametric'])
        self.scale_type.setStyleSheet(self.var_selector.styleSheet())
        var_selector_layout.addWidget(var_label)
        var_selector_layout.addWidget(self.var_selector)
        var_selector_layout.addWidget(scale_label)
        var_selector_layout.addWidget(self.scale_type)
        var_selector_layout.addStretch()
        controls_layout.addWidget(var_selector_widget)
        range_group = QWidget()
        range_layout = QGridLayout(range_group)
        range_layout.setSpacing(10)
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
        controls_layout.addWidget(range_group)
        
        # Add advanced features section
        advanced_features_label = QLabel("Advanced Features")
        advanced_features_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold; margin-top: 10px;")
        controls_layout.addWidget(advanced_features_label)
        
        # Fire mode checkbox
        self.fire_mode_checkbox = QCheckBox("🔥 Fire Mode")
        self.fire_mode_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #3d3d3d;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #ff4500, stop:1 #ff8c00);
                border: 2px solid #ff4500;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #5dade2;
            }
        """)
        self.fire_mode_checkbox.stateChanged.connect(self.toggle_fire_mode)
        self.fire_mode_checkbox.stateChanged.connect(self.sync_fire_button_from_checkbox)
        controls_layout.addWidget(self.fire_mode_checkbox)
        
        # Millisecond plotting checkbox
        self.millisecond_mode_checkbox = QCheckBox("⏱️ Millisecond Time Mode")
        self.millisecond_mode_checkbox.setStyleSheet(self.fire_mode_checkbox.styleSheet())
        controls_layout.addWidget(self.millisecond_mode_checkbox)
        
        # 3D plotting checkbox (future feature)
        self.advanced_plot_checkbox = QCheckBox("📊 3D Plot Mode")
        self.advanced_plot_checkbox.setStyleSheet(self.fire_mode_checkbox.styleSheet())
        controls_layout.addWidget(self.advanced_plot_checkbox)
        
        sidebar_layout.addWidget(controls_group)
        self.student_controls = QWidget()
        student_layout = QVBoxLayout(self.student_controls)
        student_layout.setSpacing(5)
        student_history_container = QWidget()
        student_history_layout = QVBoxLayout(student_history_container)
        student_history_label = QLabel("My Graph History")
        student_history_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        student_history_layout.addWidget(student_history_label)
        self.student_list = QListWidget()
        self.student_list.setMinimumHeight(200)
        self.student_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
        """)
        self.student_list.itemClicked.connect(self.load_graph_from_history)
        self.student_list.itemSelectionChanged.connect(self.on_graph_selection_changed)
        student_history_layout.addWidget(self.student_list)
        student_layout.addWidget(student_history_container)
        sidebar_layout.addWidget(self.student_controls)
        self.student_controls.hide()
        self.teacher_controls = QWidget()
        teacher_layout = QVBoxLayout(self.teacher_controls)
        teacher_layout.setSpacing(15)
        teacher_label = QLabel("Teacher Controls")
        teacher_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        teacher_layout.addWidget(teacher_label)
        selector_section = QWidget()
        selector_layout = QVBoxLayout(selector_section)
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
        selector_layout.addWidget(self.student_selector)
        teacher_layout.addWidget(selector_section)
        selected_student_section = QWidget()
        selected_student_layout = QVBoxLayout(selected_student_section)
        selected_student_label = QLabel("Student's Graphs")
        selected_student_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        selected_student_layout.addWidget(selected_student_label)
        self.student_graph_list = QListWidget()
        self.student_graph_list.setMinimumHeight(200)
        self.student_graph_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
        """)
        self.student_graph_list.itemClicked.connect(self.load_graph_from_history)
        self.student_graph_list.itemSelectionChanged.connect(self.on_graph_selection_changed)
        selected_student_layout.addWidget(self.student_graph_list)
        teacher_layout.addWidget(selected_student_section)
        comment_section = QWidget()
        comment_layout = QVBoxLayout(comment_section)
        comment_label = QLabel("Add Comment")
        comment_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        comment_layout.addWidget(comment_label)
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
        comment_layout.addWidget(self.comment_input)
        teacher_layout.addWidget(comment_section)
        sidebar_layout.addWidget(self.teacher_controls)
        self.teacher_controls.hide()
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        self.canvas = GraphCanvas(self.calculator)
        canvas_layout.addWidget(self.canvas)
        content_layout.addWidget(canvas_container)
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)
        left_buttons = QWidget()
        left_layout = QHBoxLayout(left_buttons)
        left_layout.setSpacing(10)
        
        # Special fire mode toggle button
        self.fire_btn = ModernButton("🔥 Fire Mode", fire_mode=True)
        self.fire_btn.setCheckable(True)
        self.fire_btn.clicked.connect(self.toggle_fire_button)
        left_layout.addWidget(self.fire_btn)
        
        plot_btn = ModernButton("📈 Plot Graph")
        plot_btn.clicked.connect(self.plot_graph)
        left_layout.addWidget(plot_btn)
        load_graphs_btn = ModernButton("📂 Load Graphs")
        load_graphs_btn.clicked.connect(self.load_graphs)
        left_layout.addWidget(load_graphs_btn)
        clear_btn = ModernButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_graph)
        left_layout.addWidget(clear_btn)
        buttons_layout.addWidget(left_buttons)
        right_buttons = QWidget()
        right_layout = QHBoxLayout(right_buttons)
        right_layout.setSpacing(10)
        save_graph_btn = ModernButton("💾 Save Graph")
        save_graph_btn.clicked.connect(self.save_graph)
        right_layout.addWidget(save_graph_btn)
        save_image_btn = ModernButton("📸 Save Image")
        save_image_btn.clicked.connect(self.save_graph_image)
        right_layout.addWidget(save_image_btn)
        buttons_layout.addWidget(right_buttons)
        content_layout.addWidget(buttons_container)
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
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setPalette(DarkPalette())
        
        # Add modern status bar
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #2c3e50, stop:1 #34495e);
                color: white;
                font-size: 12px;
                padding: 5px;
                border-top: 2px solid #3498db;
            }
        """)
        self.setStatusBar(status_bar)
        status_bar.showMessage("Welcome to World-Class Graphing Calculator! 🚀", 5000)
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Configure keyboard shortcuts for power users"""
        # Plot graph - Ctrl+Enter or Ctrl+Return
        plot_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        plot_shortcut.activated.connect(self.plot_graph)
        
        # Save graph - Ctrl+S
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_student_graph)
        
        # Clear/New graph - Ctrl+N
        clear_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        clear_shortcut.activated.connect(self.clear_graph)
        
        # Toggle fire mode - Ctrl+F
        fire_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        fire_shortcut.activated.connect(self.toggle_fire_button)
        
        # Export as image - Ctrl+E
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self.save_graph_image)
        
        # Help - F1
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self.show_help)
        
        # Focus expression input - Ctrl+L
        focus_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        focus_shortcut.activated.connect(lambda: self.expr_input.setFocus())
        
        self.statusBar().showMessage("💡 Tip: Press F1 for keyboard shortcuts", 3000)
    
    def clear_graph(self):
        """Clear the current graph"""
        self.canvas.axes.clear()
        self.canvas.axes.grid(True, color='#404040', linestyle='--', alpha=0.3)
        self.canvas.draw()
        self.statusBar().showMessage("✨ Graph cleared", 2000)
    
    def show_help(self):
        """Show help dialog with keyboard shortcuts"""
        help_text = """
        <h2>🎯 Keyboard Shortcuts</h2>
        <table style='width:100%; border-collapse: collapse;'>
        <tr><td style='padding: 5px;'><b>Ctrl+Enter</b></td><td>Plot current expression</td></tr>
        <tr><td style='padding: 5px;'><b>Ctrl+S</b></td><td>Save graph</td></tr>
        <tr><td style='padding: 5px;'><b>Ctrl+N</b></td><td>Clear graph</td></tr>
        <tr><td style='padding: 5px;'><b>Ctrl+F</b></td><td>Toggle fire mode</td></tr>
        <tr><td style='padding: 5px;'><b>Ctrl+E</b></td><td>Export as image</td></tr>
        <tr><td style='padding: 5px;'><b>Ctrl+L</b></td><td>Focus expression input</td></tr>
        <tr><td style='padding: 5px;'><b>F1</b></td><td>Show this help</td></tr>
        </table>
        
        <h3>🔥 Tips</h3>
        <ul>
        <li>Use <b>x</b> as your variable (e.g., sin(x), x**2)</li>
        <li>Separate equations with <b>=</b> to solve them</li>
        <li>Enable fire mode for stunning visualizations</li>
        <li>Use millisecond mode for time-series data</li>
        </ul>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Help - Keyboard Shortcuts")
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
            }
            QLabel {
                color: white;
                font-size: 13px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        msg.exec()

    def save_student_graph(self):
        """Save the current graph with a dialog"""
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please login first")
            return
        
        # Ask for graph name
        name, ok = QInputDialog.getText(self, "Save Graph", "Enter graph name:")
        if not ok or not name:
            return
        
        expression = self.expr_input.text().strip()
        if not expression:
            QMessageBox.warning(self, "Error", "Please enter an expression first")
            return
        
        try:
            # Get current settings
            x_min = self.min_value.value()
            x_max = self.max_value.value()
            variable = self.var_selector.currentText().strip()
            scale_type = self.scale_type.currentText().lower()
            
            # Save to database
            self.db.save_graph(
                user_id=self.current_user.id,
                name=name,
                expression=expression,
                variable=variable,
                x_min=x_min,
                x_max=x_max,
                y_min=x_min,  # Simplified
                y_max=x_max,
                scale_type=scale_type
            )
            
            self.statusBar().showMessage(f"✅ Graph '{name}' saved successfully!", 3000)
            self.load_student_graphs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save graph: {str(e)}")

    def set_user(self, user: User):
        try:
            if not user:
                raise ValueError("No user provided")
            self.current_user = user
            if user.role == 'teacher':
                self.teacher_controls.show()
                self.student_controls.hide()
                self.student_selector.show()
                self.load_student_list()
            elif user.role == 'student':
                self.teacher_controls.hide()
                self.student_controls.show()
                self.student_selector.hide()
                self.load_student_graphs()
            self.user_info.setText(f"Welcome, {user.full_name} ({user.role.capitalize()})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error setting user: {str(e)}")

    def setup_student_graph_history(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(10)
        history_label = QLabel("My Graph History")
        history_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(history_label)
        graph_list = QListWidget()
        graph_list.setMinimumHeight(200)
        graph_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
        """)
        graph_list.setWordWrap(True)
        graph_list.setSizeAdjustPolicy(QListWidget.SizeAdjustPolicy.AdjustToContents)
        layout.addWidget(graph_list)
        layout.addStretch()
        return container, graph_list

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

    def load_student_graphs(self):
        if not self.current_user or self.current_user.role != 'student':
            return
        print(f"Loading graphs for user: {self.current_user.username}")
        try:
            db = AdvancedDatabase()
            graphs = db.get_user_graphs(self.current_user.id)
            print(f"Fetched {len(graphs)} graphs")
            self.student_list.clear()
            self.student_graph_data = {}
            if graphs:
                for graph in graphs:
                    graph_name = graph.get('name', 'Unnamed Graph')
                    created_at = graph.get('created_at', 'No date')
                    display_text = f"{graph_name} ({created_at})"
                    print(f"Adding graph: {display_text}")
                    item = QListWidgetItem(display_text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                    item.setData(Qt.ItemDataRole.UserRole, graph.get('id'))
                    self.student_list.addItem(item)
                    self.student_graph_data[graph_name] = graph
                print(f"Added {self.student_list.count()} items to list")
                if self.student_list.count() > 0:
                    self.student_list.setCurrentRow(0)
            else:
                placeholder = QListWidgetItem("No saved graphs")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.student_list.addItem(placeholder)
        except Exception as e:
            print(f"Error loading graphs: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error loading graphs: {str(e)}")
        self.student_list.update()

    def on_graph_selection_changed(self):
        try:
            selected_items = self.student_graph_list.selectedItems()
            if not selected_items:
                selected_items = self.history_list.selectedItems()
            if selected_items:
                item = selected_items[0]
                graph_name = item.text().split(' (')[0]
                if graph_name in self.student_graph_data:
                    graph_data = self.student_graph_data[graph_name]
                    graph_id = graph_data.get('id')
                    if graph_id:
                        self.update_comments(graph_id)
        except Exception as e:
            logging.error(f"Error handling graph selection: {str(e)}")

    def get_user_graphs(self, user_id):
        query = f"SELECT * FROM graphs WHERE user_id = {user_id}"
        print(f"Executing database query: {query}")
        try:
            results = self.execute_query(query)
            print(f"Query results: {results}")
            return results
        except Exception as e:
            print(f"Database query error: {e}")
            return []

    def load_graph_from_history(self, item):
        try:
            graph_name = item.text().split(' (')[0]
            if graph_name in self.student_graph_data:
                graph_data = self.student_graph_data[graph_name]
                self.expr_input.setText(graph_data.get('expression', ''))
                self.second_expr_input.setText(graph_data.get('expression2', ''))
                if 'x_min' in graph_data:
                    self.min_value.setValue(float(graph_data['x_min']))
                if 'x_max' in graph_data:
                    self.max_value.setValue(float(graph_data['x_max']))
                graph_id = graph_data.get('id')
                if graph_id:
                    self.update_comments(graph_id)
                self.plot_graph()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading graph: {str(e)}")
            logging.error(f"Error loading graph from history: {str(e)}")

    def setup_student_view(self):
        if self.current_user and self.current_user.role == 'student':
            self.teacher_controls.hide()
            self.load_student_graphs()
        else:
            self.teacher_controls.show()

    def save_graph_image(self):
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
        if not self.current_user or self.current_user.role != 'teacher':
            return
        try:
            db = AdvancedDatabase()
            students = db.get_all_students()
            self.student_selector.clear()
            if students:
                self.student_list = students
                self.student_selector.addItems([student[1] for student in students])
            else:
                QMessageBox.information(self, "Info", "No students found in database")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading student list: {str(e)}")

    def handle_logout(self):
        try:
            if self.current_user:
                filename = f"graphs_{self.current_user.username}.json"
                try:
                    self.calculator.save_graphs(filename)
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Could not save graphs: {str(e)}")
            self.current_user = None
            self.calculator.clear_graphs()
            self.update_history()
            self.user_info.setText("Not logged in")
            self.teacher_controls.hide()
            self.expr_input.clear()
            self.second_expr_input.clear()
            self.canvas.axes.clear()
            self.canvas.draw()
            from auth_system import AuthWindow
            self.auth_window = AuthWindow()
            self.auth_window.login_successful.connect(self.set_user)
            self.auth_window.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during logout: {str(e)}")

    def update_history(self):
        try:
            if hasattr(self, 'history_list'):
                self.history_list.clear()
                for graph_name in self.calculator.graphs:
                    self.history_list.addItem(graph_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating history: {str(e)}")
    
    def toggle_fire_mode(self, state):
        """Toggle fire mode visual effects"""
        try:
            fire_enabled = (state == Qt.CheckState.Checked.value)
            self.canvas.enable_fire_mode(fire_enabled)
            if fire_enabled:
                self.statusBar().showMessage("🔥 Fire Mode Activated!", 3000)
            else:
                self.statusBar().showMessage("Fire Mode Deactivated", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error toggling fire mode: {str(e)}")
    
    def toggle_fire_button(self):
        """Toggle fire mode from button"""
        try:
            is_checked = self.fire_btn.isChecked()
            self.fire_mode_checkbox.blockSignals(True)  # Prevent recursion
            self.fire_mode_checkbox.setChecked(is_checked)
            self.fire_mode_checkbox.blockSignals(False)
            self.canvas.enable_fire_mode(is_checked)
            if is_checked:
                self.statusBar().showMessage("🔥 Fire Mode Activated - Prepare for awesome graphs!", 3000)
            else:
                self.statusBar().showMessage("Fire Mode Deactivated", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error toggling fire mode: {str(e)}")
    
    def sync_fire_button_from_checkbox(self, state):
        """Sync fire button state when checkbox is toggled"""
        try:
            is_checked = (state == Qt.CheckState.Checked.value)
            self.fire_btn.blockSignals(True)  # Prevent recursion
            self.fire_btn.setChecked(is_checked)
            self.fire_btn.blockSignals(False)
        except Exception as e:
            pass  # Silently fail to avoid disrupting checkbox toggle

    def update_comments(self, graph_id):
        if not graph_id:
            return
        try:
            db = AdvancedDatabase()
            comments = db.get_graph_comments(graph_id)
            self.comments_list.clear()
            if comments:
                for comment in comments:
                    teacher_name = comment.get('teacher_name', 'Unknown Teacher')
                    timestamp = comment.get('timestamp', 'No date')
                    comment_text = comment.get('comment', '')
                    formatted_comment = (
                        f"{teacher_name}\n"
                        f"Date: {timestamp}\n"
                        f"{comment_text}\n"
                        f"{'-' * 40}"
                    )
                    item = QListWidgetItem(formatted_comment)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                    self.comments_list.addItem(item)
            else:
                placeholder = QListWidgetItem("No comments yet")
                placeholder.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.comments_list.addItem(placeholder)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading comments: {str(e)}")
            logging.error(f"Error updating comments: {str(e)}")

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

    def clear_graph(self):
        try:
            self.canvas.axes.clear()
            self.canvas.axes.grid(True, linestyle='--', alpha=0.5)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error clearing graph: {str(e)}")

    # --------------------- UPDATED PLOT GRAPH METHOD ---------------------
    def plot_graph(self):
        try:
            self.canvas.axes.clear()
            self.canvas.axes.grid(True, linestyle='--', alpha=0.5)
            # Read both expressions from the input fields
            expression = self.expr_input.text().strip()
            second_expr = self.second_expr_input.text().strip()

            # If the first expression is empty but the second is provided, use it as the main expression.
            if not expression:
                if second_expr:
                    expression = second_expr
                    second_expr = ""  # clear second_expr as it is now primary
                else:
                    QMessageBox.warning(self, "Error", "Please enter an expression or equation")
                    return

            # Get range and scale values
            x_min = self.min_value.value()
            x_max = self.max_value.value()
            y_min = self.min_value.value()  # For simplicity, reusing for y-axis
            y_max = self.max_value.value()
            scale_type = self.scale_type.currentText().lower()
            variable = self.var_selector.currentText().strip()

            # Set up transformations for implicit multiplication
            transformations = standard_transformations + (implicit_multiplication_application, convert_xor,)

            # Equation mode if "=" is in the main expression
            if "=" in expression:
                left_side, right_side = expression.split("=", 1)
                var_sym = symbols(variable)
                left_expr = parse_expr(left_side, transformations=transformations)
                right_expr = parse_expr(right_side, transformations=transformations)
                solutions = solve(left_expr - right_expr, var_sym)
                if not solutions:
                    QMessageBox.information(self, "No Solution", "No solution found for the equation.")
                    return

                if scale_type == 'log':
                    x_min = max(1e-10, x_min)
                    x_values = np.logspace(np.log10(x_min), np.log10(x_max), 1000)
                    self.canvas.axes.set_xscale('log')
                else:
                    x_values = np.linspace(x_min, x_max, 1000)

                f_left = lambdify(var_sym, left_expr, modules=["numpy"])
                f_right = lambdify(var_sym, right_expr, modules=["numpy"])
                y_left = f_left(x_values)
                y_right = f_right(x_values)
                self.canvas.axes.plot(x_values, y_left, label=left_side.strip(), color='#1f77b4', linewidth=2)
                self.canvas.axes.plot(x_values, y_right, label=right_side.strip(), color='#ff7f0e', linewidth=2)

                for sol in solutions:
                    try:
                        sol_val = float(sol)
                        if x_min <= sol_val <= x_max:
                            self.canvas.axes.axvline(x=sol_val, color='green', linestyle='--', linewidth=2,
                                                     label=f'Solution: {sol_val:.2f}')
                            self.canvas.axes.annotate(f"{sol_val:.2f}",
                                                      xy=(sol_val, y_max*0.1),
                                                      xytext=(sol_val, y_max*0.2),
                                                      arrowprops=dict(arrowstyle="->", color='green'),
                                                      color='green')
                    except Exception:
                        continue
            else:
                # Normal function plotting for the main expression
                if scale_type == 'log':
                    x_min = max(1e-10, x_min)
                    x_values = np.logspace(np.log10(x_min), np.log10(x_max), 1000)
                    self.canvas.axes.set_xscale('log')
                else:
                    x_values = np.linspace(x_min, x_max, 1000)

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
                            'csc': lambda l: 1 / np.sin(x),
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
                        expr_sympy = parse_expr(expr, transformations=transformations)
                        f = lambdify('x', expr_sympy, modules=['numpy', math_funcs])
                        return f(x)
                    except Exception as b:
                        raise ValueError(f"Error evaluating expression: {str(b)}")
                # Evaluate and plot the main expression
                y_values = np.vectorize(lambda x: advanced_eval(x, expression))(x_values)
                
                # Check if fire mode is enabled
                fire_mode = self.fire_mode_checkbox.isChecked()
                millisecond_mode = self.millisecond_mode_checkbox.isChecked()
                
                # Handle millisecond mode for time-based plotting
                if millisecond_mode:
                    # Convert x-axis to millisecond timestamps
                    start_time = time.time() * 1000  # current time in ms
                    x_labels = [f"{start_time + (i * (x_max - x_min) / len(x_values)):.3f} ms" 
                               for i in range(len(x_values))]
                    self.canvas.axes.set_xlabel("Time (milliseconds)", fontsize=11, 
                                               color='#ffa500' if fire_mode else '#ecf0f1')
                
                if np.iscomplexobj(y_values):
                    if fire_mode:
                        self.canvas.axes.plot(x_values, y_values.real, label=f"Re({expression})", 
                                            linewidth=3, color='#ff4500')
                        self.canvas.axes.plot(x_values, y_values.imag, label=f"Im({expression})", 
                                            linewidth=3, linestyle='--', color='#ffa500')
                    else:
                        self.canvas.axes.plot(x_values, y_values.real, label=f"Re({expression})", 
                                            linewidth=2.5, color='#3498db')
                        self.canvas.axes.plot(x_values, y_values.imag, label=f"Im({expression})", 
                                            linewidth=2.5, linestyle='--', color='#e74c3c')
                else:
                    mask = np.isfinite(y_values)
                    x_values_filtered = x_values[mask]
                    y_values_filtered = y_values[mask]
                    
                    if fire_mode:
                        # Use fire gradient colors
                        colors = self.calculator.create_fire_gradient_colors(len(x_values_filtered))
                        for i in range(len(x_values_filtered) - 1):
                            self.canvas.axes.plot(x_values_filtered[i:i+2], y_values_filtered[i:i+2], 
                                                color=colors[i], linewidth=3, alpha=0.9)
                        # Add a label for the legend (only once)
                        self.canvas.axes.plot([], [], label=expression, linewidth=3, color='#ff4500')
                    else:
                        self.canvas.axes.plot(x_values_filtered, y_values_filtered, 
                                            label=expression, linewidth=2.5, color='#3498db')

                # If a second expression is provided, plot it as well
                if second_expr:
                    y2_values = np.vectorize(lambda x: advanced_eval(x, second_expr))(x_values_filtered if 'x_values_filtered' in locals() else x_values)
                    if fire_mode:
                        self.canvas.axes.plot(x_values_filtered if 'x_values_filtered' in locals() else x_values, 
                                            y2_values, label=second_expr, linewidth=3, color='#ffa500')
                    else:
                        self.canvas.axes.plot(x_values_filtered if 'x_values_filtered' in locals() else x_values, 
                                            y2_values, label=second_expr, linewidth=2.5, color='#e74c3c')
                    # Compute intersections symbolically
                    try:
                        var_sym = symbols(variable)
                        expr1 = parse_expr(expression, transformations=transformations)
                        expr2 = parse_expr(second_expr, transformations=transformations)
                        intersections = solve(expr1 - expr2, var_sym)
                        for sol in intersections:
                            try:
                                sol_val = float(sol)
                                if x_min <= sol_val <= x_max:
                                    self.canvas.axes.axvline(x=sol_val, color='purple', linestyle='--', linewidth=2,
                                                             label=f'Intersection: {sol_val:.2f}')
                                    f1 = lambdify(var_sym, expr1, modules=['numpy'])
                                    self.canvas.axes.annotate(f"{sol_val:.2f}",
                                                              xy=(sol_val, f1(sol_val)),
                                                              xytext=(sol_val, f1(sol_val)+0.5),
                                                              arrowprops=dict(arrowstyle="->", color='purple'),
                                                              color='purple')
                            except Exception:
                                continue
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Error computing intersections: {str(e)}")

            self.canvas.axes.set_xlim(x_min, x_max)
            self.canvas.axes.set_ylim(y_min, y_max)
            
            # Get fire mode status for styling
            fire_mode = self.fire_mode_checkbox.isChecked()
            millisecond_mode = self.millisecond_mode_checkbox.isChecked()
            
            # Apply styling based on mode
            label_color = '#ffa500' if fire_mode else '#ecf0f1'
            if not millisecond_mode:
                self.canvas.axes.set_xlabel(variable, fontsize=11, color=label_color, fontweight='bold')
            self.canvas.axes.set_ylabel("y", fontsize=11, color=label_color, fontweight='bold')
            
            # Enhanced legend
            legend = self.canvas.axes.legend(fontsize=10, facecolor='#2c3e50' if not fire_mode else '#3d0000',
                                            edgecolor=label_color, loc='best')
            legend.get_frame().set_alpha(0.9)
            for text in legend.get_texts():
                text.set_color(label_color)
            
            # Modern title with gradient effect simulation
            title_text = f"Graph of {expression}"
            if fire_mode:
                title_text = f"🔥 {title_text} 🔥"
            if millisecond_mode:
                title_text = f"⏱️ {title_text}"
            self.canvas.axes.set_title(title_text, pad=15, fontsize=13, 
                                      color=label_color, fontweight='bold')
            
            # Enhanced axis lines
            axis_color = '#ff4500' if fire_mode else '#3498db'
            if x_min <= 0 <= x_max:
                self.canvas.axes.axvline(x=0, color=axis_color, linestyle='-', alpha=0.4, linewidth=2)
            if y_min <= 0 <= y_max:
                self.canvas.axes.axhline(y=0, color=axis_color, linestyle='-', alpha=0.4, linewidth=2)
            
            self.canvas.axes.grid(True, which='both', linestyle='--', alpha=0.3)
            self.canvas.draw()
            
            # Update status bar
            if fire_mode:
                self.statusBar().showMessage("🔥 Fire Mode Plot Complete!", 2000)
            elif millisecond_mode:
                self.statusBar().showMessage("⏱️ Millisecond Mode Plot Complete!", 2000)
            else:
                self.statusBar().showMessage("✓ Plot Complete!", 2000)
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error plotting graph: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
    # ---------------------------------------------------------------------

    def save_graph(self):
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Please log in to save graphs")
            return
        try:
            expression = self.expr_input.text().strip()
            if not expression:
                QMessageBox.warning(self, "Error", "Please enter an expression first")
                return
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
            db = AdvancedDatabase()
            print(f"Debug - User ID: {self.current_user.id}")
            print(f"Debug - Graph Data: {graph_data}")
            db.save_graph_state(self.current_user.id, graph_data)
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

def main():
    app = QApplication(sys.argv)
    calculator = GraphingCalculator()
    window = MainWindow(calculator)
    window.setWindowTitle("Advanced Graphing Calculator")
    window.setMinimumSize(1200, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
