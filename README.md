# Graphing Calculator

This repository contains a graphing calculator project written in Python. The purpose of this project is to provide a robust calculator application that can convert any mathematical formula into graphical representations. Additionally, it includes features such as teacher comments on student graphs, viewing already made graphs, and using an SQLite database for data handling.

## Features

- Convert mathematical formulas into graphs
- View and interact with previously created graphs
- Teachers can add comments on student graphs
- Students can view teacher comments on their dashboard
- Store and manage data using SQLite database

## Requirements

- Python 3.x
- SQLite
- PyQt6~=6.8.0
- numpy~=2.0.0
- matplotlib~=3.9.1
- logging~=0.4.9.6
- scipy~=1.15.1
- sympy~=1.13.3
- setuptools~=70.2.0

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
2. Follow the on-screen instructions to input formulas, view graphs, and add comments.

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

**Repository Information:**

- **Repository Name:** calculator
- **Owner:** tafolabi009
- **Repository ID:** 915448223
- **Primary Language:** Python (100%)
