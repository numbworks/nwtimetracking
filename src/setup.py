'''Contains packaging information about nwtimetracking.py.'''

# GLOBAL MODULES
from setuptools import setup

# INFORMATION
MODULE_ALIAS : str = "nwtt"
MODULE_NAME : str = "nwtimetracking"
MODULE_VERSION : str = "5.0.1"

# SETUP
if __name__ == "__main__":
    setup(
        name = MODULE_NAME,
        version = MODULE_VERSION,
        description = "An application designed to run automated data analysis tasks on 'Time Tracking.xlsx'.",
        author = "numbworks",
        url = f"https://github.com/numbworks/{MODULE_NAME}",
        py_modules = [ MODULE_NAME ],
        install_requires = [
            "numpy>=2.1.2",
            "pyarrow>=17.0.0",
            "pandas>=2.2.3",
            "requests>=2.32.3",
            "tabulate>=0.9.0",
            "nwshared @ git+https://github.com/numbworks/nwshared.git@v1.8.0#egg=nwshared&subdirectory=src",
            "matplotlib>=3.9.2"
        ],
        python_requires = ">=3.12",
        license = "MIT"
    )