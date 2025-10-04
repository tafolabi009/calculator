# Contributing to World-Class Graphing Calculator

Thank you for your interest in contributing to the World-Class Graphing Calculator! This document provides guidelines and instructions for contributing to this project.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Feature Requests](#feature-requests)
- [Bug Reports](#bug-reports)

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/calculator.git
   cd calculator
   ```

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install development dependencies:
   ```bash
   pip install -e .
   ```

4. Run the application:
   ```bash
   cd advanced_graphing_calculator/graphing_calculator
   python app.py
   ```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and modular
- Comment complex logic

Example:
```python
def calculate_intersection(expr1: str, expr2: str) -> List[float]:
    """
    Calculate intersection points between two mathematical expressions.
    
    Args:
        expr1: First mathematical expression as string
        expr2: Second mathematical expression as string
    
    Returns:
        List of x-coordinates where expressions intersect
    """
    # Implementation here
    pass
```

## Testing

Before submitting changes:

1. Test the application manually:
   ```bash
   cd advanced_graphing_calculator/graphing_calculator
   python app.py
   ```

2. Test key features:
   - Login/Registration
   - Basic plotting (e.g., `sin(x)`, `x^2`)
   - Fire mode
   - Millisecond time mode
   - Saving graphs
   - Teacher comments (if applicable)

3. Run the demo script:
   ```bash
   python demo.py
   ```

## Submitting Changes

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add feature: description of your feature"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub with:
   - Clear description of changes
   - Screenshots for UI changes
   - Test results
   - Related issue numbers (if applicable)

## Feature Requests

To request a new feature:

1. Check existing issues to avoid duplicates
2. Open a new issue with the label "enhancement"
3. Provide:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach (optional)

## Bug Reports

To report a bug:

1. Check existing issues to avoid duplicates
2. Open a new issue with the label "bug"
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots (if applicable)
   - Environment details (OS, Python version, etc.)

## Areas for Contribution

Here are some areas where contributions are especially welcome:

### High Priority
- 3D plotting implementation
- Zoom and pan controls
- Additional mathematical functions
- Performance optimization
- Unit tests

### Medium Priority
- Export to PDF/SVG
- Animation mode for parameter sweeps
- Custom color schemes
- Real-time data streaming
- Internationalization (i18n)

### Documentation
- Tutorial videos
- Example use cases
- API documentation
- User guide improvements

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Questions?

If you have questions:
- Open an issue with the label "question"
- Check existing documentation
- Review closed issues for similar questions

Thank you for contributing to making this the best graphing calculator in the world! 🚀
