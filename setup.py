"""
Setup script for World-Class Graphing Calculator
"""
from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='graphing-calculator',
    version='2.0.0',
    author='tafolabi009',
    description='A world-class graphing calculator with advanced features',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tafolabi009/calculator',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'PyQt6>=6.8.0,<7.0.0',
        'numpy>=1.24.0,<2.0.0',
        'scipy>=1.10.0,<2.0.0',
        'sympy>=1.12,<2.0.0',
        'matplotlib>=3.7.0,<4.0.0',
    ],
    entry_points={
        'console_scripts': [
            'graphing-calculator=advanced_graphing_calculator.graphing_calculator.app:main',
        ],
    },
    include_package_data=True,
    keywords='graphing calculator mathematics visualization education',
    project_urls={
        'Bug Reports': 'https://github.com/tafolabi009/calculator/issues',
        'Source': 'https://github.com/tafolabi009/calculator',
    },
)
