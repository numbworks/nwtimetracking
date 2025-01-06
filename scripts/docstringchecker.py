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
            parser.add_argument("--file_path", required = True, help = _MessageCollection.file_path_to_the_python_file())
            parser.add_argument("--exclude", required = False, nargs = "*", default = [], help = _MessageCollection.exclude_substrings())

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

# MAIN
if __name__ == "__main__":

    argument_parser : ArgumentParser = ArgumentParser()
    docstring_manager : DocStringManager = DocStringManager()

    file_path, exclude = argument_parser.parse_arguments()

    if file_path is None:
        sys.exit(0)

    source : str = docstring_manager.load_source(file_path = cast(str, file_path))
    missing : list[str] = docstring_manager.get_missing_docstrings(source = source, exclude = exclude)
    docstring_manager.print_docstrings(missing = missing)

    if len(missing) > 0:
        sys.exit(0)
    else:
        sys.exit(1)
