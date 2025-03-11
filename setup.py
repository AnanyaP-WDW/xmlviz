"""
Setup script for the TwbCompare package.
"""
from setuptools import setup, find_packages

# Read version from package
with open("twbcompare/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read long description from README
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="twbcompare",
    version=version,
    description="A tool for analyzing, comparing, and visualizing Tableau .twb files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ananya Pathak",
    author_email="ananya@synciq.ai",
    url="https://github.com/AnanyaP-WDW/xmlviz",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "lxml>=4.6.0",
        "matplotlib>=3.4.0",
        "networkx>=2.5",
        "scikit-learn>=0.24.0",
        "pandas>=1.2.0",
        "scipy>=1.6.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        "console_scripts": [
            "twbcompare=twbcompare.twb_compare:main",
        ],
    },
) 