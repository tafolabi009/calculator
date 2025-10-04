"""
Unit tests for GraphingCalculator class
"""
import unittest
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'advanced_graphing_calculator', 'graphing_calculator'))

from graphing_calculator import GraphingCalculator, Graph


class TestGraphingCalculator(unittest.TestCase):
    """Test cases for GraphingCalculator"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = GraphingCalculator()

    def test_calculator_initialization(self):
        """Test calculator initializes correctly"""
        self.assertIsInstance(self.calculator, GraphingCalculator)
        self.assertIsInstance(self.calculator.graphs, dict)
        self.assertEqual(len(self.calculator.graphs), 0)

    def test_evaluate_expression_basic(self):
        """Test basic expression evaluation"""
        result = self.calculator.evaluate_expression("2*x", 5, "linear")
        self.assertEqual(result, 10)

    def test_evaluate_expression_trig(self):
        """Test trigonometric expressions"""
        result = self.calculator.evaluate_expression("sin(x)", 0, "linear")
        self.assertAlmostEqual(result, 0, places=10)

    def test_evaluate_expression_degrees(self):
        """Test expressions with degree scale"""
        result = self.calculator.evaluate_expression("sin(x)", 90, "degrees")
        self.assertAlmostEqual(result, 1, places=10)

    def test_plot_expression(self):
        """Test plotting mathematical expression"""
        x, y = self.calculator.plot_expression("x**2", "x", -10, 10, "linear")
        self.assertIsInstance(x, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertEqual(len(x), 1000)
        self.assertEqual(len(y), 1000)

    def test_plot_expression_invalid(self):
        """Test plotting with invalid expression"""
        with self.assertRaises(Exception):
            self.calculator.plot_expression("invalid!", "x", -10, 10, "linear")

    def test_create_fire_gradient_colors(self):
        """Test fire gradient color generation"""
        colors = self.calculator.create_fire_gradient_colors(100)
        self.assertEqual(len(colors), 100)
        # Check colors are valid RGB tuples
        self.assertEqual(len(colors[0]), 3)
        # Check all values are between 0 and 1
        for color in colors:
            for value in color:
                self.assertTrue(0 <= value <= 1)

    def test_plot_time_series(self):
        """Test time series plotting"""
        timestamps = self.calculator.plot_time_series(0, 1000, 500)
        self.assertIsInstance(timestamps, np.ndarray)
        self.assertEqual(len(timestamps), 500)
        self.assertEqual(timestamps[0], 0)
        self.assertEqual(timestamps[-1], 1000)

    def test_clear_graphs(self):
        """Test clearing all graphs"""
        # Create a test graph first
        self.calculator.graphs['test'] = Graph('x**2', 'x', -10, 10, 'linear')
        self.assertEqual(len(self.calculator.graphs), 1)
        
        # Clear and verify
        self.calculator.clear_graphs()
        self.assertEqual(len(self.calculator.graphs), 0)

    def test_save_graph(self):
        """Test saving a graph"""
        graph = Graph('sin(x)', 'x', -10, 10, 'linear')
        self.calculator.save_graph('test_graph', graph)
        self.assertIn('test_graph', self.calculator.graphs)
        self.assertEqual(self.calculator.graphs['test_graph'].expression, 'sin(x)')


class TestGraph(unittest.TestCase):
    """Test cases for Graph class"""

    def test_graph_creation(self):
        """Test creating a Graph object"""
        graph = Graph('x**2', 'x', -10, 10, 'linear')
        self.assertEqual(graph.expression, 'x**2')
        self.assertEqual(graph.variable, 'x')
        self.assertEqual(graph.start, -10)
        self.assertEqual(graph.end, 10)
        self.assertEqual(graph.scale_type, 'linear')


if __name__ == '__main__':
    unittest.main()
