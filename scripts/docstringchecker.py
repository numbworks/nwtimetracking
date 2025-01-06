import ast
import argparse
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
    def methods_missing_docstrings() -> str:
        return "Methods missing docstrings:"
    @staticmethod
    def all_methods_have_docstrings() -> str:
        return "All methods have docstrings."
class ArgumentParser():

    '''Collects all the logic related to parsing arguments.'''

    def parse_arguments(self) -> tuple[Optional[str], list[str]]:

        '''Parses file_path and exclude arguments.'''

        try:
            parser = argparse.ArgumentParser(description=_MessageCollection.parser_description())
            parser.add_argument("file_path", help=_MessageCollection.file_path_to_the_python_file())
            parser.add_argument(
                "--exclude",
                nargs="*",
                default=[],
                help=_MessageCollection.exclude_substrings()
            )

            args: Namespace = parser.parse_args()

            return args.file_path, args.exclude
        except:
            return None, []
class DocStringManager():

    '''Collects all the logic related to docstrings management.'''

    def load_source(self, file_path: str) -> str:

        '''Loads source from file_path.'''

        source: str = ""

        with open(file_path, "r", encoding='utf-8') as file:
            source = file.read()

        return source
    def get_missing_docstrings(self, source: str, exclude: list[str]) -> list[str]:

        '''Gets missing docstrings and excludes specified substrings.'''

        tree: Module = ast.parse(source=source)

        missing: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if ast.get_docstring(item) is None:
                            method_name = f"{node.name}.{item.name}"
                            if not any(substring in method_name for substring in exclude):
                                missing.append(method_name)

        return missing
    def print_docstrings(self, missing: list[str]) -> None:

        '''Prints missing docstrings.'''

        if missing:
            print(_MessageCollection.methods_missing_docstrings())
            for method in missing:
                print(method)
        else:
            print(_MessageCollection.all_methods_have_docstrings())

# MAIN
if __name__ == "__main__":

    argument_parser: ArgumentParser = ArgumentParser()
    docstring_manager: DocStringManager = DocStringManager()

    file_path, exclude = argument_parser.parse_arguments()
    missing: list[str] = []

    if file_path is not None:

        source: str = docstring_manager.load_source(file_path=cast(str, file_path))
        missing = docstring_manager.get_missing_docstrings(source=source, exclude=exclude)
        docstring_manager.print_docstrings(missing=missing)
