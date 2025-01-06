'''A script to check which methods in a Python file lack of docstrings.'''

# IMPORTS
import ast
import argparse
import sys
from ast import Module
from argparse import Namespace
from typing import Optional, cast

# CLASSES
class _MessageCollection():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def parser_description() -> str:
        return "Check if all methods in a Python file have docstrings."
    @staticmethod
    def file_path_to_the_python_file() -> str:
        return "File path to the Python file to check."
    @staticmethod
    def exclude_substrings() -> str:
        return "List of substrings to exclude from the output."
    
    @staticmethod
    def all_methods_have_docstrings() -> str:
        return "All methods have docstrings."
class ArgumentParser():

    '''Collects all the logic related to parsing arguments.'''

    def parse_arguments(self) -> tuple[Optional[str], list[str]]:

        '''Parses file_path and exclude arguments.'''

        try:
            parser = argparse.ArgumentParser(description = _MessageCollection.parser_description())
            parser.add_argument("--file_path", "-fp", required = True, help = _MessageCollection.file_path_to_the_python_file())
            parser.add_argument("--exclude", "-e", required = False, action = "append", default = [], help = _MessageCollection.exclude_substrings())

            args: Namespace = parser.parse_args()

            return args.file_path, args.exclude
        except:
            return None, []
class DocStringManager():

    '''Collects all the logic related to docstrings management.'''

    def load_source(self, file_path : str) -> str:

        '''Loads source from file_path.'''

        source : str = ""

        with open(file_path, "r", encoding='utf-8') as file:
            source = file.read()

        return source
    def get_missing_docstrings(self, source : str, exclude : list[str]) -> list[str]:

        '''Returns all the method names missing docstrings by excluding specified substrings.'''

        tree : Module = ast.parse(source=source)

        method_names : list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if ast.get_docstring(item) is None:
                            method_name = f"{node.name}.{item.name}"
                            if not any(substring in method_name for substring in exclude):
                                method_names.append(method_name)

        return method_names
    def print_docstrings(self, missing: list[str]) -> None:

        '''Prints missing docstrings.'''

        if missing:
            for method in missing:
                print(method)
        else:
            print(_MessageCollection.all_methods_have_docstrings())
class DocStringChecker():

    '''Collects all the logic related to docstrings checking.'''

    __argument_parser : ArgumentParser
    __docstring_manager : DocStringManager

    def __init__(
        self, 
        argument_parser : ArgumentParser = ArgumentParser(), 
        docstring_manager : DocStringManager = DocStringManager()) -> None:

        self.__argument_parser = argument_parser
        self.__docstring_manager = docstring_manager

    def run(self) -> None:

        '''Runs the docstring check.'''

        file_path, exclude = self.__argument_parser.parse_arguments()

        if file_path is None:
            sys.exit()

        source : str = self.__docstring_manager.load_source(file_path = cast(str, file_path))
        missing : list[str] = self.__docstring_manager.get_missing_docstrings(source = source, exclude = exclude)
        self.__docstring_manager.print_docstrings(missing = missing)

# MAIN
if __name__ == "__main__":
    DocStringChecker().run()



