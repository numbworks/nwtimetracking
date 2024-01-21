# GLOBAL MODULES
import unittest
from datetime import timezone

# LOCAL MODULES
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
import nwcorecomponents as nwcc

# TEST CLASSES
class CreateFilePathTestCase(unittest.TestCase):

    def test_createfilepath_shouldreturnexpectedfilepath_whenproperarguments(self):
        actual : str = nwcc.create_file_path(folder_path = "C:/", file_name = "somefile.txt")
        self.assertEqual("C:/somefile.txt", actual)
class CreateNumberedFilePathTestCase(unittest.TestCase):

    def test_createnumberedfilepath_shouldreturnexpectedfilepath_whenproperarguments(self):
        actual : str = nwcc.create_numbered_file_path(folder_path = "C:/", number = 1, extension = "html")
        self.assertEqual("C:/1.html", actual)
class DecodeUnicodeCharactersTestCase(unittest.TestCase):

    def test_decodeunicodecharacters_shouldreturnexpectedstring_wheninvoked(self):
        actual : str = nwcc.decode_unicode_characters(string = "Antikt \u0026 Design")
        self.assertEqual("Antikt & Design", actual)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)