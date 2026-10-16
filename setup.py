from setuptools import setup, find_packages

setup(
    name="physics_toolbox",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gspread",
        "pandas",
        "matplotlib",
        "numpy"
    ],
)