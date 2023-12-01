# GLOBAL MODULES
import unittest
from unittest import mock
from unittest.mock import patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
import nwtimetrackingmanager as nwttm

# TEST CLASSES
class GetDefaultTimeTrackingPathTestCase(unittest.TestCase):

    def test_getdefaulttimetrackingpath_shouldreturnexpectedpath_wheninvoked(self):
        
        '''"C:/project_dir/src/" => "C:/project_dir/data/Time Tracking.xlsx"'''

        # Arrange
        expected : str = "C:/project_dir/data/Time Tracking.xlsx"

        # Act
        with patch.object(os, 'getcwd', return_value="C:/project_dir/src/") as mocked_context:
            actual : str = nwttm.get_default_time_tracking_path()

        # Assert
        self.assertEqual(expected, actual)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)