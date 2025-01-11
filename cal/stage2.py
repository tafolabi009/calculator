import sympy as sp
import matplotlib.pyplot as plt
import numpy as np


def plot_with_scaling_and_units(expression, variable, start=-10, end=10, scale_y=1, radians=True):
    """
    Plots an expression with adjustable axis scaling and radians/degrees toggle.
    Args:
        expression (str): The mathematical expression to plot.
        variable (str): The variable used in the expression (e.g., 'x').
        start (float): Start of the x-axis range.
        end (float): End of the x-axis range.
        scale_y (float): Scaling factor for the y-axis.
        radians (bool): Use radians (True) or degrees (False) for trigonometric functions.
    """
    x = sp.symbols(variable)
    expr = sp.sympify(expression)

    x_vals = np.linspace(start, end, 400)
    if radians:
        y_vals = [float(expr.subs(x, val)) * scale_y for val in x_vals]
    else:
        y_vals = [float(expr.subs(x, np.radians(val))) * scale_y for val in x_vals]

    plt.figure(figsize=(8, 6))
    plt.plot(x_vals, y_vals, label=f"{expression} ({'Radians' if radians else 'Degrees'})")
    plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
    plt.axvline(0, color='black', linewidth=0.5, linestyle='--')
    plt.title(f"Graph of {expression}")
    plt.xlabel(variable)
    plt.ylabel(f"f(x) * {scale_y}")
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

    # Input y-axis scale
    try:
        scale_y = float(input("Enter the y-axis scaling factor (default is 1): ") or 1)
    except ValueError:
        print("Invalid scaling factor. Using default: 1.")
        scale_y = 1

    # Input radians or degrees
    unit_choice = input("Use radians or degrees? (default is 'radians'): ").strip().lower()
    radians = unit_choice in ['radians', 'r', '']

    # Plot expression with scaling and units
    plot_with_scaling_and_units(expression, variable, start, end, scale_y, radians)
