# GLOBAL MODULES
import unittest
import pandas as pd
from unittest.mock import patch
from pandas import DataFrame
from pandas.core.indexes.base import Index
from datetime import datetime
from datetime import timedelta

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
import nwtimetrackingmanager as nwttm
from nwtimetrackingmanager import YearlyTarget
from nwtimetrackingmanager import SettingCollection

# SUPPORT METHODS
class ObjectMother():

    @staticmethod
    def get_setting_collection() -> SettingCollection:

         return SettingCollection(
            years = [2015],
            yearly_targets = [
                YearlyTarget(year = 2015, hours = timedelta(hours = 0))
            ],
            excel_path = nwttm.get_default_time_tracking_path(),
            excel_books_skiprows = 0,
            excel_books_nrows = 920,
            excel_books_tabname = "Sessions",
            n_generic = 5,
            n_by_month = 12,
            now = datetime.now(),
            software_project_names = [ 
                "NW.MarkdownTables" 
                ],
            software_project_names_by_spv = [ 
                "nwreadinglistmanager" 
                ],    
            remove_untagged_from_de = True,
            definitions = { 
                "DME": "Development Monthly Effort",
                "TME": "Total Monthly Effort",
                "DYE": "Development Yearly Effort",
                "TYE": "Total Yearly Effort",
                "DE": "Development Effort",
                "TE": "Total Effort"
            },    
            tt_by_year_hashtag_years = [2023],
            tts_by_month_update_future_values_to_empty = True,     
            effort_status_n = 25,
            effort_status_is_correct = False,
            time_ranges_unknown_id = "Unknown",
            time_ranges_top_n = 5,
            time_ranges_remove_unknown_id = True,
            time_ranges_filter_by_top_n = True,
            show_sessions_df = False, 
            show_tt_by_year_df = True,
            show_tt_by_year_month_df = True,
            show_tt_by_year_month_spnv_df = False,
            show_tt_by_year_spnv_df = False, 
            show_tt_by_spn_df = True,
            show_tt_by_spn_spv_df = True,
            show_tt_by_year_hashtag = True,
            show_tt_by_hashtag = True,
            show_tts_by_month_df = True,
            show_effort_status_df = True,
            show_time_ranges_df = True
        )

    @staticmethod
    def get_sessions_dataframe_column_names() -> list[str]:

        column_names : list[str] = []
        column_names.append("Date")                 # [0], date
        column_names.append("StartTime")            # [1], str
        column_names.append("EndTime")              # [2], str
        column_names.append("Effort")               # [3], str
        column_names.append("Hashtag")              # [4], str
        column_names.append("Descriptor")           # [5], str
        column_names.append("IsSoftwareProject")    # [6], bool
        column_names.append("IsReleaseDay")         # [7], bool
        column_names.append("Year")                 # [8], int
        column_names.append("Month")                # [9], int

        return column_names


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
class GetSessionsDatasetTestCase(unittest.TestCase):

    def test_getsessionsdataset_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        excel_data_dict : dict = {
            "Date": "2015-10-31",
            "StartTime": "",
            "EndTime": "",
            "Effort": "8h 00m",
            "Hashtag": "#untagged",
            "Descriptor": "",
            "IsSoftwareProject": "False",
            "IsReleaseDay": "False",
            "Year": "2015",
            "Month": "10"
            }
        excel_data_df : DataFrame = pd.DataFrame(data = excel_data_dict, index=[0])
        setting_collection : SettingCollection = ObjectMother().get_setting_collection()
        expected_column_names : list[str] = ObjectMother().get_sessions_dataframe_column_names()

        # Act
        with patch.object(pd, 'read_excel', return_value = excel_data_df) as mocked_context:
            actual : str = nwttm.get_sessions_dataset(setting_collection = setting_collection)

        # Assert
        self.assertEqual(expected_column_names, actual.columns.tolist())


# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)