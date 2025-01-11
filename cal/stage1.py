import sympy as sp
import matplotlib.pyplot as plt
import numpy as np


def plot_expressions(expressions, variable, start=-10, end=10):
    """
    Plots multiple expressions on the same graph.
    Args:
        expressions (list of str): List of algebraic expressions as strings.
        variable (str): The variable used in the expressions (e.g., 'x').
        start (float): Start of the x-axis range.
        end (float): End of the x-axis range.
    """
    x = sp.symbols(variable)
    plt.figure(figsize=(8, 6))

    for expression in expressions:
        try:
            expr = sp.sympify(expression)
            x_vals = np.linspace(start, end, 400)
            y_vals = [float(expr.subs(x, val)) for val in x_vals]
            plt.plot(x_vals, y_vals, label=f"{expression}")
        except Exception as e:
            print(f"Error processing expression '{expression}': {e}")

    # Adding axis lines and labels
    plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
    plt.axvline(0, color='black', linewidth=0.5, linestyle='--')
    plt.title("Graphs of Expressions")
    plt.xlabel(variable)
    plt.ylabel("f(x)")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    # Input expressions
    print("Enter mathematical expressions (comma-separated, e.g., 'x**2, sin(x), ln(x)'):")
    user_input = input("Expressions: ")
    expressions = [expr.strip() for expr in user_input.split(",")]

    # Input variable
    variable = input("Enter the variable (default is 'x'): ") or "x"

    # Input range
    try:
        start = float(input("Enter the start of the range (default is -10): ") or -10)
        end = float(input("Enter the end of the range (default is 10): ") or 10)
    except ValueError:
        print("Invalid range input. Using default range: -10 to 10.")
        start, end = -10, 10

    # Plot expressions
    plot_expressions(expressions, variable, start, end)
