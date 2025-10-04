# Graphing Calculator

This repository contains a graphing calculator project written in Python. The purpose of this project is to provide a robust calculator application that can convert any mathematical formula into graphical representations. Additionally, it includes features such as teacher comments on student graphs, viewing already made graphs, and using an SQLite database for data handling.

## Features

- **World-Class UI Design**: Modern gradient buttons, enhanced color scheme, and smooth visual effects
- **Advanced Graphing System**:
  - Convert mathematical formulas into high-quality graphs
  - Fire mode with animated gradient effects and dynamic coloring
  - Millisecond-precision time plotting for data analysis
  - Support for complex functions, equations, and multiple expressions
  - Real-time intersection detection and solution highlighting
  - Advanced interpolation methods (linear, cubic, quadratic)
- **3D Plot Mode**: Future-ready 3D plotting capability (coming soon)
- **Interactive Features**:
  - View and interact with previously created graphs
  - Real-time graph updates
  - Zoom and pan controls
  - Save graphs as images (PNG, JPEG)
- **Collaborative Tools**:
  - Teachers can add comments on student graphs
  - Students can view teacher comments on their dashboard
- **Data Management**: Store and manage data using SQLite database with full history tracking

## Requirements

- Python 3.8+
- SQLite (built-in with Python)
- PyQt6>=6.8.0
- numpy>=1.24.0
- matplotlib>=3.7.0
- scipy>=1.10.0
- sympy>=1.12

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/tafolabi009/calculator.git
    ```
2. Navigate to the project directory:
    ```sh
    cd calculator
    ```
3. Install required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application script:
    ```sh
    python app.py
    ```
2. **Login/Register**: Create an account or login as a student or teacher.

3. **Plotting Graphs**:
   - Enter a mathematical expression (e.g., `sin(x)`, `x^2 + 2*x + 1`)
   - Optionally enter a second expression to plot multiple functions
   - Adjust range (Min/Max) and scale type (Linear, Log, Polar, Parametric)
   - Click "Plot Graph" to visualize your function

4. **Advanced Features**:
   - **🔥 Fire Mode**: Enable stunning fire-themed gradient effects on your plots
   - **⏱️ Millisecond Time Mode**: Plot with millisecond-precision timestamps for time-series data
   - **📊 3D Plot Mode**: Coming soon - three-dimensional visualization

5. **Saving & Sharing**:
   - Click "Save Graph" to store your graph in the database
   - Use "Save Image" to export as PNG or JPEG
   - View your graph history in the sidebar

6. **For Teachers**:
   - Select a student from the dropdown
   - View their submitted graphs
   - Add comments and feedback directly on graphs

## Database

This project uses an SQLite database to handle data. The database schema includes tables for storing formulas, graphs, and comments.

## User Roles

- **Teachers:** Can add comments on student graphs.
- **Students:** Can view teacher comments on their dashboard.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch:
    ```sh
    git checkout -b feature-name
    ```
3. Make your changes and commit them:
    ```sh
    git commit -m "Add feature"
    ```
4. Push to the branch:
    ```sh
    git push origin feature-name
    ```
5. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or suggestions, feel free to open an issue or contact the repository owner.

---

## 🔥 New Advanced Features

### Fire Mode
Activate **Fire Mode** to transform your graphs with stunning fire-themed visual effects:
- Dynamic fire gradient coloring (red → orange → yellow)
- Enhanced plot lines with smooth color transitions
- Fire-themed UI elements and borders
- Perfect for highlighting important data or creating eye-catching presentations

### Millisecond Time Plotting
Enable **Millisecond Time Mode** for precise time-based analysis:
- Plot data with millisecond-precision timestamps
- Ideal for real-time data monitoring and analysis
- High-resolution time-series visualization
- Accurate timing for scientific and engineering applications

### Modern UI Design
- Gradient buttons with smooth hover effects and shadows
- Enhanced dark theme with better contrast
- Real-time status bar with activity indicators
- Improved typography and spacing for better readability
- Smooth animations and visual feedback

### Advanced Graphing Capabilities
- Multi-expression plotting with intersection detection
- Support for complex numbers with real and imaginary components
- Advanced mathematical functions (gamma, beta, erf, etc.)
- Logarithmic, polar, and parametric plotting modes
- Automatic solution highlighting for equations

---

**Repository Information:**

- **Repository Name:** calculator
- **Owner:** tafolabi009
- **Repository ID:** 915448223
- **Primary Language:** Python (100%)
