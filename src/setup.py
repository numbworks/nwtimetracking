'''Contains packaging instructions.'''

# GLOBAL MODULES
from setupinfo import CLI_NAME, PROJECT_VERSION, PROJECT_AUTHOR, PROJECT_URL, LIBRARY_NAME, LIBRARY_DESCRIPTION
from setuptools import setup

# SETUP
if __name__ == "__main__":
    setup(
        name = LIBRARY_NAME,
        version = PROJECT_VERSION,
        description = LIBRARY_DESCRIPTION,
        author = PROJECT_AUTHOR,
        url = PROJECT_URL,
        py_modules = [ LIBRARY_NAME, CLI_NAME, "setupinfo" ],
        install_requires = [ 
            "numpy>=1.26.4",
            "pyarrow>=17.0.0",
            "openpyxl>=3.1.5",
            "pandas>=2.1.4",
            "requests>=2.32.3",
            "matplotlib>=3.9.2",        
            "tabulate>=0.9.0",
            "sparklines>=0.5.0",
            "weasyprint>=66.0",
            "ipython==7.23.1",
            "jinja2==3.1.6"
        ],
        python_requires = ">=3.12",
        license = "MIT",
        entry_points = {
            'console_scripts': [
                f'{CLI_NAME} = {CLI_NAME}:main',
            ],
        }
    )