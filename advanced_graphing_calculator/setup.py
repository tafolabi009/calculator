# setup.py
from setuptools import setup, find_packages

setup(
    name="advanced_graphing_calculator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt6',
        'numpy',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': [
            'graphing_calculator=app:main',
        ],
    },
    author="Afolabi Oluwatosin",
    author_email="tafolabi009@gmail.com",
    description="An advanced graphing calculator with authentication",
    keywords="calculator, graphing, education",
    python_requires='>=3.7',
)
