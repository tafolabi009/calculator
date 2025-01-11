import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import json
import os


def plot_and_save_graph(expression, variable, start=-10, end=10, save_path="graph.png"):
    """
    Plots an expression and saves the graph to a file.
    Args:
        expression (str): The mathematical expression to plot.
        variable (str): The variable used in the expression (e.g., 'x').
        start (float): Start of the x-axis range.
        end (float): End of the x-axis range.
        save_path (str): Path to save the graph image.
    """
    x = sp.symbols(variable)
    expr = sp.sympify(expression)

    x_vals = np.linspace(start, end, 400)
    y_vals = []

    for val in x_vals:
        try:
            y_vals.append(float(expr.subs(x, val)))
        except Exception as e:
            y_vals.append(np.nan)  # Handle undefined points

    # Plot expression
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, label=expression, color="blue")
    plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
    plt.axvline(0, color="black", linewidth=0.5, linestyle="--")
    plt.title(f"Graph of {expression}")
    plt.xlabel(variable)
    plt.ylabel("f(x)")
    plt.legend()
    plt.grid()

    # Save graph
    plt.savefig(save_path)
    plt.show()
    print(f"Graph saved to {save_path}.")


def save_graph_data(expression, variable, start, end, file_path="graph_data.json"):
    """
    Saves graph details to a JSON file.
    Args:
        expression (str): The mathematical expression.
        variable (str): The variable used in the expression.
        start (float): Start of the x-axis range.
        end (float): End of the x-axis range.
        file_path (str): Path to save the JSON data.
    """
    data = {
        "expression": expression,
        "variable": variable,
        "start": start,
        "end": end
    }
    try:
        with open(file_path, "w") as file:
            json.dump(data, file)
        print(f"Graph data saved to {file_path}.")
    except Exception as e:
        print(f"Error saving graph data: {e}")


def load_graph_data(file_path="graph_data.json"):
    """
    Loads graph details from a JSON file.
    Args:
        file_path (str): Path to the JSON file.
    Returns:
        dict: Graph details (expression, variable, start, end), or None if loading fails.
    """
    if not os.path.exists(file_path):
        print(f"No file found at {file_path}.")
        return None

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        print(f"Graph data loaded from {file_path}.")
        return data
    except json.JSONDecodeError as e:
        print(f"Error reading graph data file: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while loading graph data: {e}")
        return None


if __name__ == "__main__":
    # User choice: new graph or load existing data
    choice = input("Do you want to create a new graph or load existing data? (new/load): ").strip().lower()

    if choice == "load":
        file_path = input(
            "Enter the file name to load the graph data (default is 'graph_data.json'): ") or "graph_data.json"
        graph_data = load_graph_data(file_path)
        if graph_data:
            expression = graph_data["expression"]
            variable = graph_data["variable"]
            start = graph_data["start"]
            end = graph_data["end"]
            save_path = input("Enter the file name to save the graph (default is 'graph.png'): ") or "graph.png"
            plot_and_save_graph(expression, variable, start, end, save_path)
        else:
            print("Failed to load graph data.")
    else:
        # Input new graph details
        expression = input("Enter the mathematical expression (e.g., sin(x), x**2): ").strip()
        variable = input("Enter the variable (default is 'x'): ") or "x"

        try:
            start = float(input("Enter the start of the range (default is -10): ") or -10)
            end = float(input("Enter the end of the range (default is 10): ") or 10)
        except ValueError:
            print("Invalid range input. Using default range: -10 to 10.")
            start, end = -10, 10

        # Plot and save graph
        save_path = input("Enter the file name to save the graph (default is 'graph.png'): ") or "graph.png"
        plot_and_save_graph(expression, variable, start, end, save_path)

        # Save graph details
        save_graph = input("Do you want to save the graph data for later? (yes/no): ").strip().lower()
        if save_graph == "yes":
            data_path = input(
                "Enter the file name to save the graph data (default is 'graph_data.json'): ") or "graph_data.json"
            save_graph_data(expression, variable, start, end, data_path)
