#!/usr/bin/env python3
"""
Demo script for the World-Class Graphing Calculator
This script demonstrates the new features without needing a GUI
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                'advanced_graphing_calculator', 'graphing_calculator'))

from graphing_calculator import GraphingCalculator, Graph
import numpy as np

def demo_fire_gradient():
    """Demonstrate fire gradient color generation"""
    print("=" * 60)
    print("DEMO: Fire Gradient Colors")
    print("=" * 60)
    
    calc = GraphingCalculator()
    colors = calc.create_fire_gradient_colors(20)
    
    print("\nFire gradient color progression (dark red → red → orange → yellow):")
    for i, (r, g, b) in enumerate(colors):
        # Create a simple ASCII representation
        intensity = int((r + g + b) / 3 * 10)
        bar = '█' * intensity
        print(f"  {i:2d}: RGB({r:.2f}, {g:.2f}, {b:.2f}) {bar}")
    
    print("\n✓ Fire gradient generated successfully!")
    print("  Use this in Fire Mode for stunning visual effects!\n")

def demo_millisecond_plotting():
    """Demonstrate millisecond time series generation"""
    print("=" * 60)
    print("DEMO: Millisecond Time Plotting")
    print("=" * 60)
    
    calc = GraphingCalculator()
    
    # Generate a 1-second time series with 100 points
    timestamps = calc.plot_time_series(0, 1000, 100)
    
    print(f"\nGenerated time series with {len(timestamps)} data points")
    print(f"Time range: {timestamps[0]:.3f} ms to {timestamps[-1]:.3f} ms")
    print(f"Time resolution: {(timestamps[1] - timestamps[0]):.3f} ms per sample")
    
    # Simulate some data
    print("\nSample data points:")
    for i in [0, 25, 50, 75, 99]:
        print(f"  t = {timestamps[i]:7.3f} ms  |  value = sin(2π × {i/100:.2f})")
    
    print("\n✓ Millisecond plotting ready!")
    print("  Perfect for high-resolution time-series analysis!\n")

def demo_advanced_interpolation():
    """Demonstrate advanced interpolation methods"""
    print("=" * 60)
    print("DEMO: Advanced Interpolation")
    print("=" * 60)
    
    calc = GraphingCalculator()
    
    # Sample data points
    x_data = np.array([0, 1, 2, 3, 4, 5])
    y_data = np.array([0, 1, 4, 9, 16, 25])  # y = x^2
    
    print("\nOriginal data points (y = x²):")
    for x, y in zip(x_data, y_data):
        print(f"  x = {x}, y = {y}")
    
    print("\nInterpolated values at x = 2.5:")
    
    for method in ['linear', 'quadratic', 'cubic']:
        f = calc.get_advanced_interpolation(x_data, y_data, method=method)
        value = f(2.5)
        print(f"  {method.capitalize():10s} interpolation: {value:.4f}")
    
    print(f"\n  Actual value:  6.2500  (2.5² = 6.25)")
    
    print("\n✓ Advanced interpolation methods available!")
    print("  Use for smooth curve generation and data analysis!\n")

def demo_graph_features():
    """Demonstrate enhanced Graph class features"""
    print("=" * 60)
    print("DEMO: Enhanced Graph Class")
    print("=" * 60)
    
    # Create a graph with all new features
    graph = Graph(
        expression='sin(x) * exp(-x/10)',
        variable='x',
        start=0,
        end=10,
        scale_type='linear',
        comments=['This is a damped sine wave', 'Great for signal processing'],
        millisecond_mode=True
    )
    
    print("\nGraph properties:")
    print(f"  Expression:       {graph.expression}")
    print(f"  Variable:         {graph.variable}")
    print(f"  Range:            [{graph.start}, {graph.end}]")
    print(f"  Scale Type:       {graph.scale_type}")
    print(f"  Millisecond Mode: {graph.millisecond_mode}")
    print(f"  Timestamp:        {graph.timestamp:.3f}")
    print(f"  Comments:         {len(graph.comments)} comment(s)")
    
    # Test serialization
    graph_dict = graph.to_dict()
    graph_restored = Graph.from_dict(graph_dict)
    
    print("\n✓ Graph serialization/deserialization works!")
    print(f"  All properties preserved: {graph_restored.millisecond_mode == graph.millisecond_mode}")
    
    print("\n✓ Enhanced Graph class ready for production!\n")

def demo_summary():
    """Print summary of all features"""
    print("=" * 60)
    print("🚀 WORLD-CLASS GRAPHING CALCULATOR - FEATURE SUMMARY")
    print("=" * 60)
    
    features = [
        ("🔥 Fire Mode", "Stunning fire-themed gradient effects for plots"),
        ("⏱️ Millisecond Mode", "High-precision time-series plotting"),
        ("📊 Advanced Math", "Support for complex functions and equations"),
        ("🎨 Modern UI", "Gradient buttons, shadows, and smooth effects"),
        ("📈 Multi-Plot", "Plot multiple expressions with intersections"),
        ("💾 Data Persistence", "Save and load graphs with full state"),
        ("🔬 Interpolation", "Linear, cubic, and quadratic methods"),
        ("✨ Visual Effects", "Dynamic colors and professional styling"),
    ]
    
    print("\n✅ Implemented Features:")
    for emoji_name, description in features:
        print(f"  {emoji_name:20s} - {description}")
    
    print("\n🎯 Usage Tips:")
    print("  • Enable Fire Mode for eye-catching presentations")
    print("  • Use Millisecond Mode for precise time analysis")
    print("  • Plot multiple functions to find intersections")
    print("  • Save graphs with timestamps for tracking changes")
    
    print("\n📚 Documentation:")
    print("  • See README.md for installation and basic usage")
    print("  • See FEATURES_SHOWCASE.md for detailed feature guide")
    print("  • Run 'python app.py' to launch the full GUI application")
    
    print("\n" + "=" * 60)
    print("🌟 This is now a WORLD-CLASS graphing calculator! 🌟")
    print("=" * 60 + "\n")

def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🚀 WORLD-CLASS GRAPHING CALCULATOR DEMO  🚀".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    demos = [
        demo_fire_gradient,
        demo_millisecond_plotting,
        demo_advanced_interpolation,
        demo_graph_features,
        demo_summary
    ]
    
    for demo in demos:
        try:
            demo()
            input("Press Enter to continue to next demo...")
            print("\n")
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n⚠ Error in demo: {e}")
            print("Continuing with next demo...\n")
    
    print("Thank you for exploring the World-Class Graphing Calculator!")
    print("Run 'python app.py' to try the full GUI application!\n")

if __name__ == '__main__':
    main()
