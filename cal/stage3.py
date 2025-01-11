import sympy as sp
import matplotlib.pyplot as plt
import numpy as np


def plot_advanced_features(expression, variable, start=-10, end=10):
    """
    Plots an expression with critical points, intercepts, and asymptotes highlighted.
    Args:
        expression (str): The mathematical expression to plot.
        variable (str): The variable used in the expression (e.g., 'x').
        start (float): Start of the x-axis range.
        end (float): End of the x-axis range.
    """
    x = sp.symbols(variable)
    expr = sp.sympify(expression)

    # Derivatives and roots
    derivative = sp.diff(expr, x)
    critical_points = sp.solvers.solve(derivative, x)
    x_intercepts = sp.solvers.solve(expr, x)

    # Handling asymptotes
    asymptotes = sp.solvers.solve(1 / expr, x)

    x_vals = np.linspace(start, end, 400)
    y_vals = []

    for val in x_vals:
        try:
            y_vals.append(float(expr.subs(x, val)))
        except:
            y_vals.append(np.nan)

    # Plot expression
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, label=f"{expression}", color="blue")

    # Highlight intercepts
    for intercept in x_intercepts:
        if sp.re(intercept).is_real and start <= float(intercept) <= end:
            plt.scatter(float(intercept), 0, color="red", label=f"X-Intercept: {intercept}")

    # Highlight critical points
    for point in critical_points:
        if sp.re(point).is_real and start <= float(point) <= end:
            y_critical = float(expr.subs(x, point))
            plt.scatter(float(point), y_critical, color="green", label=f"Critical Point: ({point}, {y_critical})")

    # Highlight vertical asymptotes
    for asymptote in asymptotes:
        if sp.re(asymptote).is_real and start <= float(asymptote) <= end:
            plt.axvline(float(asymptote), color="orange", linestyle="--", label=f"Asymptote: x = {asymptote}")

    # Plot settings
    plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
    plt.axvline(0, color="black", linewidth=0.5, linestyle="--")
    plt.title(f"Graph of {expression} with Advanced Features")
    plt.xlabel(variable)
    plt.ylabel("f(x)")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    # Input expression
    expression = input("Enter the mathematical expression (e.g., sin(x), x**2): ").strip()

    # Input variable
    variable = input("Enter the variable (default is 'x'): ") or "x"

    # Input range
    try:
        start = float(input("Enter the start of the range (default is -10): ") or -10)
        end = float(input("Enter the end of the range (default is 10): ") or 10)
    except ValueError:
        print("Invalid range input. Using default range: -10 to 10.")
        start, end = -10, 10

    # Plot expression with advanced features
    plot_advanced_features(expression, variable, start, end)
