# graphing_calculator.py
import numpy as np
from typing import Optional, Dict, List
import json
import os
import math


class Graph:
    def __init__(self, expression: str, variable: str, start: float, end: float,
                 scale_type: str, comments: List[str] = None):
        self.expression = expression
        self.variable = variable
        self.start = start
        self.end = end
        self.scale_type = scale_type
        self.comments = comments or []

    def to_dict(self):
        return {
            'expression': self.expression,
            'variable': self.variable,
            'start': self.start,
            'end': self.end,
            'scale_type': self.scale_type,
            'comments': self.comments
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            expression=data['expression'],
            variable=data['variable'],
            start=data['start'],
            end=data['end'],
            scale_type=data['scale_type'],
            comments=data.get('comments', [])
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