"""
Setup file for regime-based factor allocation strategy
"""
from setuptools import setup, find_packages

setup(
    name='regime-factor-strategy',
    version='1.0.0',
    description='Regime-based factor allocation strategy with v4A enhancement',
    author='woodai0120',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.24.0',
        'pandas>=2.0.0',
        'matplotlib>=3.7.0',
        'seaborn>=0.12.0',
        'yfinance>=0.2.28',
        'pandas-datareader>=0.10.0',
        'scipy>=1.10.0',
        'scikit-learn>=1.3.0',
    ],
    python_requires='>=3.8',
)
