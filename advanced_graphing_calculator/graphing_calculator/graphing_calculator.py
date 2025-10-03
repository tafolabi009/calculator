# graphing_calculator.py
import numpy as np
from typing import Optional, Dict, List
import json
import os
import math
import time
from datetime import datetime, timedelta


class Graph:
    def __init__(self, expression: str, variable: str, start: float, end: float,
                 scale_type: str, comments: List[str] = None, millisecond_mode: bool = False,
                 timestamp: Optional[float] = None):
        self.expression = expression
        self.variable = variable
        self.start = start
        self.end = end
        self.scale_type = scale_type
        self.comments = comments or []
        self.millisecond_mode = millisecond_mode
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        return {
            'expression': self.expression,
            'variable': self.variable,
            'start': self.start,
            'end': self.end,
            'scale_type': self.scale_type,
            'comments': self.comments,
            'millisecond_mode': self.millisecond_mode,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            expression=data['expression'],
            variable=data['variable'],
            start=data['start'],
            end=data['end'],
            scale_type=data['scale_type'],
            comments=data.get('comments', []),
            millisecond_mode=data.get('millisecond_mode', False),
            timestamp=data.get('timestamp', time.time())
        )


class GraphingCalculator:
    def __init__(self):
        self.graphs: Dict[str, Graph] = {}
        self.current_user = None

    def set_user(self, user):
        """Set the current user and load their graphs"""
        self.current_user = user
        self.load_graphs()

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

    def save_graphs(self, filename=None):
        """Save graphs to a file"""
        if not filename and not self.current_user:
            return

        if not filename:
            filename = f"graphs_{self.current_user.username}.json"

        with open(filename, 'w') as f:
            json.dump({
                name: graph.to_dict()
                for name, graph in self.graphs.items()
            }, f)

    def create_graph(self, name, expression, start, end, scale_type):
        graph = Graph(expression, 'x', start, end, scale_type)
        self.save_graph(name, graph)

    def evaluate_expression(self, expression, x, scale_type):
        try:
            # Define a local context with math functions
            local_context = {
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'sqrt': math.sqrt,
                'pi': math.pi,
                'e': math.e,
                'abs': abs,
            }

            # Handle scale type (e.g., degrees)
            if scale_type == "degrees":
                local_context['sin'] = lambda x: math.sin(math.radians(x))
                local_context['cos'] = lambda x: math.cos(math.radians(x))
                local_context['tan'] = lambda x: math.tan(math.radians(x))

            result = eval(expression.replace('x', str(x)), local_context)
            return result
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")

    def clear_graphs(self):
        """Clear all graphs"""
        self.graphs = {}

    def save_graph(self, name: str, graph: Graph):
        """Save a new graph or update existing one"""
        self.graphs[name] = graph
        self.save_graphs()

    def add_comment(self, graph_name: str, comment: str):
        """Add a teacher comment to a graph"""
        if not self.current_user or self.current_user.role != "teacher":
            raise ValueError("Only teachers can add comments")

        if graph_name not in self.graphs:
            raise KeyError("Graph not found")

        self.graphs[graph_name].comments.append({
            'teacher': self.current_user.username,
            'comment': comment
        })
        self.save_graphs()

    def plot_expression(self, expr: str, variable: str, start: float, end: float,
                        scale_type: str, show_intersection: bool = False):
        """Plot a mathematical expression"""
        # Create x values
        x = np.linspace(start, end, 1000)

        # Convert expression if using degrees
        if scale_type == "degrees":
            expr = expr.replace("sin", "np.sin(np.deg2rad")
            expr = expr.replace("cos", "np.cos(np.deg2rad")
            expr = expr.replace("tan", "np.tan(np.deg2rad")
            expr = expr + ")"

        # Evaluate expression
        try:
            y = eval(expr.replace(variable, "x"))
            return x, y
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def plot_time_series(self, start_ms: float, end_ms: float, num_points: int = 1000):
        """
        Generate time-based data with millisecond precision
        Returns timestamps in milliseconds and corresponding values
        """
        timestamps = np.linspace(start_ms, end_ms, num_points)
        return timestamps
    
    def create_fire_gradient_colors(self, n_points: int):
        """
        Generate fire-themed gradient colors for plotting
        Returns array of RGB colors transitioning from red to orange to yellow
        """
        colors = []
        for i in range(n_points):
            t = i / max(1, n_points - 1)
            # Fire gradient: dark red -> red -> orange -> yellow
            if t < 0.33:
                # Dark red to red
                r = 0.5 + 0.5 * (t / 0.33)
                g = 0.0
                b = 0.0
            elif t < 0.66:
                # Red to orange
                r = 1.0
                g = (t - 0.33) / 0.33 * 0.65
                b = 0.0
            else:
                # Orange to yellow
                r = 1.0
                g = 0.65 + (t - 0.66) / 0.34 * 0.35
                b = 0.0
            colors.append((r, g, b))
        return colors
    
    def get_advanced_interpolation(self, x_data, y_data, method='cubic'):
        """
        Apply advanced interpolation to data
        Methods: 'linear', 'cubic', 'quadratic'
        """
        from scipy import interpolate
        if method == 'cubic':
            f = interpolate.interp1d(x_data, y_data, kind='cubic', fill_value='extrapolate')
        elif method == 'quadratic':
            f = interpolate.interp1d(x_data, y_data, kind='quadratic', fill_value='extrapolate')
        else:
            f = interpolate.interp1d(x_data, y_data, kind='linear', fill_value='extrapolate')
        return f