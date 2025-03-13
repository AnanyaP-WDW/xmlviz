"""
Setup script for the TWBCompare package.
"""
from setuptools import setup, find_packages

setup(
    name="twbcompare",
    version="0.1.0",
    description="A tool for analyzing and comparing Tableau .twb files",
    author="TWBCompare Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "twbcompare=twbcompare.cli:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 