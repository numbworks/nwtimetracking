# GLOBAL MODULES
import unittest
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
from numpy import int64, uint
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from parameterized import parameterized
from types import FunctionType
from typing import Tuple
from unittest.mock import Mock, call, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwtimetracking import ComponentBag, MDInfo, TTAdapter, TTMarkdownFactory, SoftwareProjectNameProvider, YearlyTarget, SettingBag, EffortStatus, _MessageCollection
from nwtimetracking import DefaultPathProvider, YearProvider, TTDataFrameFactory, TTID, MDInfoProvider
from nwshared import MarkdownHelper, Formatter, FilePathManager, FileManager, Displayer

# SUPPORT METHODS
class SupportMethodProvider():

    '''Collection of generic purpose test-aiding methods.'''

    @staticmethod
    def get_dtype_names(df : DataFrame) -> list[str]:

        '''
            The default df.dtypes return most dtypes as "object", even if they are "string".
            This method convert them back to the standard names and return them as list[str].                 
        '''

        dtype_names : list[str] = []
        for dtype in df.convert_dtypes().dtypes:
            dtype_names.append(dtype.name)

        return dtype_names

    @staticmethod
    def are_effort_statuses_equal(ef1 : EffortStatus, ef2 : EffortStatus) -> bool:

        '''
            Returns True if all the fields of the two objects contain the same values.
        '''

        return (ef1.idx == ef2.idx and
                 ef1.start_time_str == ef2.start_time_str and 
                 ef1.start_time_dt == ef2.start_time_dt and
                 ef1.end_time_str == ef2.end_time_str and 
                 ef1.end_time_dt == ef2.end_time_dt and  
                 ef1.actual_str == ef2.actual_str and 
                 ef1.actual_td == ef2.actual_td and
                 ef1.expected_str == ef2.expected_str and 
                 ef1.expected_td == ef2.expected_td and
                 ef1.is_correct == ef2.is_correct and
                 ef1.message == ef2.message
            )

    @staticmethod
    def are_yearly_targets_equal(yt1 : YearlyTarget, yt2 : YearlyTarget) -> bool:

        '''
            Returns True if all the fields of the two objects contain the same values.
        '''

        return (yt1.hours == yt2.hours and yt1.year == yt2.year)
    
    @staticmethod
    def are_lists_of_yearly_targets_equal(list1 : list[YearlyTarget], list2 : list[YearlyTarget]) -> bool:

        '''
            Returns True if all the fields of the two objects contain the same values.
        '''

        if (list1 == None and list2 == None):
            return True

        if (list1 == None or list2 == None):
            return False

        if (len(list1) != len(list2)):
            return False

        for i in range(len(list1)):
            if (SupportMethodProvider.are_yearly_targets_equal(yt1 = list1[i], yt2 = list2[i]) == False):
                return False

        return True
class ObjectMother():

    '''Collects all the DTOs required by the unit tests.'''

    @staticmethod
    def create_setting_bag() -> SettingBag:

        setting_bag : SettingBag = SettingBag(
            options_tt = ["display"],
            options_tts_by_month = ["display", "save"],
            options_tts_by_year = ["display"],
            options_tts_by_year_month = ["display"],
            options_tts_by_year_month_spnv = ["display"],
            options_tts_by_year_spnv = ["display"],
            options_tts_by_spn = ["display", "log"],
            options_tts_by_spn_spv = [],
            options_tts_by_hashtag = ["display"],
            options_tts_by_hashtag_year = ["display"],
            options_tts_by_efs = ["display"],
            options_tts_by_tr = ["display"],
            options_definitions = ["display"],
            excel_nrows = 1301,
            tts_by_year_month_spnv_display_only_spn = "nwtimetracking",
            tts_by_year_spnv_display_only_spn = "nwtimetracking",
            tts_by_spn_spv_display_only_spn = "nwtimetracking"
        )

        return setting_bag
    @staticmethod
    def create_excel_data() -> DataFrame:

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

        return excel_data_df
    @staticmethod
    def create_sessions_df_column_names() -> list[str]:

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
    @staticmethod
    def create_sessions_df_dtype_names() -> list[str]:

        '''Note: the first one should be "date", but it's rendered by Pandas as "object".'''

        expected_dtype_names : list[str] = [
            "object",
            "string",
            "string",
            "string",
            "string",
            "string",
            "boolean",
            "boolean",
            "Int64",
            "Int64"
        ]

        return expected_dtype_names
    @staticmethod
    def create_yearly_targets() -> list[YearlyTarget]:

        yearly_targets = [
            YearlyTarget(year = 2015, hours = timedelta(hours = 0)),
            YearlyTarget(year = 2016, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2017, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2018, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2019, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2020, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2021, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2022, hours = timedelta(hours = 400)),
            YearlyTarget(year = 2023, hours = timedelta(hours = 250)),
            YearlyTarget(year = 2024, hours = timedelta(hours = 250))
        ]

        return yearly_targets
    @staticmethod
    def create_sessions_df() -> DataFrame:

        '''
                Date	    StartTime	EndTime	Effort	Hashtag	        Descriptor	                    IsSoftwareProject	IsReleaseDay	Year	Month
            980	2024-02-12	21:00	    22:00	1h 00m	#maintenance		                            False	            False	        2024	2
            981	2024-02-13	11:00	    13:00	2h 00m	#csharp	        NW.Shared.Serialization v1.0.0	True	            True	        2024	2
            982	2024-02-13	14:30	    16:45	2h 15m	#csharp	        NW.Shared.Serialization v1.0.0	True	            True	        2024	2        
            ...
        '''

        return pd.DataFrame({
                'Date': np.array([date(2024, 2, 12), date(2024, 2, 13), date(2024, 2, 13), date(2024, 2, 14), date(2024, 2, 14), date(2024, 2, 14), date(2024, 2, 15), date(2024, 2, 18), date(2024, 2, 18), date(2024, 2, 18), date(2024, 2, 18), date(2024, 2, 18), date(2024, 2, 19), date(2024, 2, 19), date(2024, 2, 19), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 26)], dtype=str),
                'StartTime': np.array(['21:00', '11:00', '14:30', '08:00', '17:15', '20:00', '17:15', '11:00', '13:30', '17:00', '22:00', '23:00', '11:15', '15:30', '20:15', '08:45', '13:30', '15:30', '10:15', '14:00', '08:15'], dtype=str),
                'EndTime': np.array(['22:00', '13:00', '16:45', '08:30', '18:00', '20:15', '17:45', '12:30', '15:00', '18:00', '23:00', '23:30', '13:00', '18:00', '21:15', '12:15', '14:00', '16:30', '13:00', '19:45', '12:45'], dtype=str),
                'Effort': np.array(['1h 00m', '2h 00m', '2h 15m', '0h 30m', '0h 45m', '0h 15m', '0h 30m', '1h 30m', '1h 30m', '1h 00m', '1h 00m', '0h 30m', '1h 45m', '2h 30m', '1h 00m', '3h 30m', '0h 30m', '1h 00m', '2h 45m', '5h 45m', '4h 30m'], dtype=str),
                'Hashtag': np.array(['#maintenance', '#csharp', '#csharp', '#csharp', '#csharp', '#csharp', '#csharp', '#maintenance', '#maintenance', '#python', '#python', '#maintenance', '#studying', '#studying', '#studying', '#studying', '#studying', '#studying', '#studying', '#studying', '#studying'], dtype=str),
                'Descriptor': np.array(['', 'NW.Shared.Serialization v1.0.0', 'NW.Shared.Serialization v1.0.0', 'NW.NGramTextClassification v4.2.0', 'NW.NGramTextClassification v4.2.0', 'NW.UnivariateForecasting v4.2.0', 'NW.UnivariateForecasting v4.2.0', '', '', 'nwreadinglistmanager v2.1.0', 'nwreadinglistmanager v2.1.0', '', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.'], dtype=str),
                'IsSoftwareProject': np.array([False, True, True, True, True, True, True, False, False, True, True, True, False, False, False, False, False, False, False, False, False], dtype=bool),
                'IsReleaseDay': np.array([False, True, True, True, True, False, True, False, False, True, True, True, False, False, False, False, False, False, False, False, False], dtype=bool),
                'Year': np.array([2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024], dtype=int64),
                'Month': np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], dtype=int64),
            }, index=pd.RangeIndex(start=980, stop=1001, step=1))

    @staticmethod
    def create_tt_by_year_df() -> DataFrame:

        '''
                Year	Effort	YearlyTarget	TargetDiff	IsTargetMet
            0	2024	36h 00m	250h 00m	    -214h 00m	False        
        '''

        return pd.DataFrame({
                'Year': np.array([2024], dtype=int64),
                'Effort': np.array(['36h 00m'], dtype=object),
                'YearlyTarget': np.array(['250h 00m'], dtype=object),
                'TargetDiff': np.array(['-214h 00m'], dtype=object),
                'IsTargetMet': np.array([False], dtype=bool),
            }, index=pd.RangeIndex(start=0, stop=1, step=1))
    @staticmethod
    def create_tt_by_year_month_df() -> DataFrame:

        '''
                Year	Month	Effort	YearlyTotal	ToTarget
            0	2024	2	    36h 00m	36h 00m	    -214h 00m
        '''

        return pd.DataFrame({
                'Year': np.array([2024], dtype=int64),
                'Month': np.array([2], dtype=int64),
                'Effort': np.array(['36h 00m'], dtype=object),
                'YearlyTotal': np.array(['36h 00m'], dtype=object),
                'ToTarget': np.array(['-214h 00m'], dtype=object),
            }, index=pd.RangeIndex(start=0, stop=1, step=1))
    @staticmethod
    def create_tt_by_year_month_spnv_df() -> DataFrame:

        '''
                Year	Month	ProjectName	                ProjectVersion	Effort	DME	    %_DME	TME	    %_TME
            0	2024	2	    NW.NGramTextClassification	4.2.0	        01h 15m	08h 45m	14.29	36h 00m	3.47
            1	2024	2	    NW.Shared.Serialization	    1.0.0	        04h 15m	08h 45m	48.57	36h 00m	11.81
            2	2024	2	    NW.UnivariateForecasting	4.2.0	        00h 45m	08h 45m	8.57	36h 00m	2.08
            3	2024	2	    nwreadinglistmanager	    2.1.0	        02h 00m	08h 45m	22.86	36h 00m	5.56
        '''

        return pd.DataFrame({
                'Year': np.array([2024, 2024, 2024, 2024], dtype=int64),
                'Month': np.array([2, 2, 2, 2], dtype=int64),
                'ProjectName': np.array(['NW.NGramTextClassification', 'NW.Shared.Serialization', 'NW.UnivariateForecasting', 'nwreadinglistmanager'], dtype=object),
                'ProjectVersion': np.array(['4.2.0', '1.0.0', '4.2.0', '2.1.0'], dtype=object),
                'Effort': np.array(['01h 15m', '04h 15m', '00h 45m', '02h 00m'], dtype=object),
                'DME': np.array(['08h 45m', '08h 45m', '08h 45m', '08h 45m'], dtype=object),
                '%_DME': np.array([14.29, 48.57, 8.57, 22.86], dtype= np.float64),
                'TME': np.array(['36h 00m', '36h 00m', '36h 00m', '36h 00m'], dtype=object),
                '%_TME': np.array([3.47, 11.81, 2.08, 5.56], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def create_tt_by_year_spnv_df() -> DataFrame:

        '''
                Year	ProjectName	                ProjectVersion	Effort	DYE	    %_DYE	TYE	        %_TYE
            0	2024	NW.NGramTextClassification	4.2.0	        01h 15m	08h 45m	14.29	36h 00m	    3.47
            1	2024	NW.Shared.Serialization	    1.0.0	        04h 15m	08h 45m	48.57	36h 00m	    11.81
            2	2024	NW.UnivariateForecasting	4.2.0	        00h 45m	08h 45m	8.57	36h 00m	    2.08
            3	2024	nwreadinglistmanager	    2.1.0	        02h 00m	08h 45m	22.86	36h 00m	    5.56
        '''

        return pd.DataFrame({
                'Year': np.array([2024, 2024, 2024, 2024], dtype=int64),
                'ProjectName': np.array(['NW.NGramTextClassification', 'NW.Shared.Serialization', 'NW.UnivariateForecasting', 'nwreadinglistmanager'], dtype=object),
                'ProjectVersion': np.array(['4.2.0', '1.0.0', '4.2.0', '2.1.0'], dtype=object),
                'Effort': np.array(['01h 15m', '04h 15m', '00h 45m', '02h 00m'], dtype=object),
                'DYE': np.array(['08h 45m', '08h 45m', '08h 45m', '08h 45m'], dtype=object),
                '%_DYE': np.array([14.29, 48.57, 8.57, 22.86], dtype= np.float64),
                'TYE': np.array(['36h 00m', '36h 00m', '36h 00m', '36h 00m'], dtype=object),
                '%_TYE': np.array([3.47, 11.81, 2.08, 5.56], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def create_tt_by_spn_df() -> DataFrame:

        '''
                Hashtag	ProjectName	                Effort	DE	    %_DE	TE	    %_TE
            0	#python	nwreadinglistmanager	    02h 00m	08h 45m	22.86	36h 00m	5.56
            1	#csharp	NW.Shared.Serialization	    04h 15m	08h 45m	48.57	36h 00m	11.81
            2	#csharp	NW.NGramTextClassification	01h 15m	08h 45m	14.29	36h 00m	3.47
            3	#csharp	NW.UnivariateForecasting	00h 45m	08h 45m	8.57	36h 00m	2.08        
        '''

        return pd.DataFrame({
                'Hashtag': np.array(['#python', '#csharp', '#csharp', '#csharp'], dtype=object),
                'ProjectName': np.array(['nwreadinglistmanager', 'NW.Shared.Serialization', 'NW.NGramTextClassification', 'NW.UnivariateForecasting'], dtype=object),
                'Effort': np.array(['02h 00m', '04h 15m', '01h 15m', '00h 45m'], dtype=object),
                'DE': np.array(['08h 45m', '08h 45m', '08h 45m', '08h 45m'], dtype=object),
                '%_DE': np.array([22.86, 48.57, 14.29, 8.57], dtype= np.float64),
                'TE': np.array(['36h 00m', '36h 00m', '36h 00m', '36h 00m'], dtype=object),
                '%_TE': np.array([5.56, 11.81, 3.47, 2.08], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def create_tt_by_spn_spv_df() -> DataFrame:

        '''
                ProjectName	                ProjectVersion	Effort
            0	NW.NGramTextClassification	4.2.0	        01h 15m
            1	NW.Shared.Serialization	    1.0.0	        04h 15m
            2	NW.UnivariateForecasting	4.2.0	        00h 45m
            3	nwreadinglistmanager	    2.1.0	        02h 00m
        '''

        return pd.DataFrame({
                'ProjectName': np.array(['NW.NGramTextClassification', 'NW.Shared.Serialization', 'NW.UnivariateForecasting', 'nwreadinglistmanager'], dtype=object),
                'ProjectVersion': np.array(['4.2.0', '1.0.0', '4.2.0', '2.1.0'], dtype=object),
                'Effort': np.array(['01h 15m', '04h 15m', '00h 45m', '02h 00m'], dtype=object),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def create_tt_by_year_hashtag_df() -> DataFrame:

        '''
                Year	Hashtag	        Effort
            0	2024	#csharp	        06h 15m
            1	2024	#maintenance	04h 30m
            2	2024	#python	        02h 00m
            3	2024	#studying	    23h 15m
        '''

        return pd.DataFrame({
                'Year': np.array([2024, 2024, 2024, 2024], dtype=int64),
                'Hashtag': np.array(['#csharp', '#maintenance', '#python', '#studying'], dtype=object),
                'Effort': np.array(['06h 15m', '04h 30m', '02h 00m', '23h 15m'], dtype=object),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def create_tt_by_hashtag_df() -> DataFrame:

        '''
                Hashtag	        Effort	Effort%
            0	#studying	    23h 15m	64.58
            1	#csharp	        06h 15m	17.36
            2	#maintenance	04h 30m	12.50
            3	#python	        02h 00m	5.56
        '''

        return pd.DataFrame({
                'Hashtag': np.array(['#studying', '#csharp', '#maintenance', '#python'], dtype=object),
                'Effort': np.array(['23h 15m', '06h 15m', '04h 30m', '02h 00m'], dtype=object),
                'Effort%': np.array([64.58, 17.36, 12.5, 5.56], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def create_tts_by_month_df() -> DataFrame:

        '''
				Month	2024
			0	1		00h 00m
			1	2		36h 00m
			...
        '''

        return pd.DataFrame({
                'Month': np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], dtype=int64),
                '2024': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object)				
            }, index=pd.RangeIndex(start=0, stop=12, step=1))
    @staticmethod
    def create_tts_by_month_upd_df() -> DataFrame:

        '''
				Month	2024
			0	1		00h 00m
			1	2		36h 00m
			...
        '''

        return pd.DataFrame({
                'Month': np.array(['1', '2', '', '', '', '', '', '', '', '', '', ''], dtype=object),
                '2024': np.array(['00h 00m', '36h 00m', '', '', '', '', '', '', '', '', '', ''], dtype=object)
            }, index=pd.RangeIndex(start=0, stop=12, step=1))
    @staticmethod
    def create_time_ranges_df() -> DataFrame:

        '''
                TimeRangeId	Occurrences
            0	08:00-08:30	1
            1	08:15-12:45	1
            2	08:45-12:15	1
            3	10:15-13:00	1
            4	11:00-12:30	1
            ...        
        '''

        return pd.DataFrame({
                'TimeRangeId': np.array(['08:00-08:30', '15:30-16:30', '22:00-23:00', '21:00-22:00', '20:15-21:15', '20:00-20:15', '17:15-18:00', '17:15-17:45', '17:00-18:00', '15:30-18:00', '14:30-16:45', '08:15-12:45', '14:00-19:45', '13:30-15:00', '13:30-14:00', '11:15-13:00', '11:00-13:00', '11:00-12:30', '10:15-13:00', '08:45-12:15', '23:00-23:30'], dtype=object),
                'Occurrences': np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype= np.int64),
            }, index=pd.RangeIndex(start=0, stop=21, step=1))

    @staticmethod
    def create_dtos_for_ttsbymonthmd() -> Tuple[DataFrame, str]:

        data : list = [
            [1, "00h 00m", "↑", "18h 00m", "↑", "88h 30m", "↓", "80h 15m", "↓", "60h 00m", "↓", "29h 15m", "↑", "53h 00m", "↓", "00h 00m", "↑", "06h 00m", "↑", "45h 45m"]
        ]
        columns : list[str] = ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020", "↕", "2021", "↕", "2022", "↕", "2023", "↕", "2024"]
        df : DataFrame = pd.DataFrame(data, columns = columns)

        lines : list[str] = [
            "## Revision History",
            "",
            "|Date|Author|Description|",
            "|---|---|---|",
            "|2020-12-22|numbworks|Created.|",
            "|2024-10-01|numbworks|Last update.|",
            "",
            "## Time Tracking By Month",
            "",
            "|   Month | 2015    | ↕   | 2016    | ↕   | 2017    | ↕   | 2018    | ↕   | 2019    | ↕   | 2020    | ↕   | 2021    | ↕   | 2022    | ↕   | 2023    | ↕   | 2024    |",
            "|--------:|:--------|:----|:--------|:----|:--------|:----|:--------|:----|:--------|:----|:--------|:----|:--------|:----|:--------|:----|:--------|:----|:--------|",
            "|       1 | 00h 00m | ↑   | 18h 00m | ↑   | 88h 30m | ↓   | 80h 15m | ↓   | 60h 00m | ↓   | 29h 15m | ↑   | 53h 00m | ↓   | 00h 00m | ↑   | 06h 00m | ↑   | 45h 45m |"
        ]
        expected : str = "\n".join(lines) + "\n"

        return (df, expected)

# TEST CLASSES
class ComponentBagTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_whendefault(self) -> None:

        # Arrange
        # Act
        component_bag : ComponentBag = ComponentBag()

        # Assert
        self.assertIsInstance(component_bag.file_path_manager, FilePathManager)
        self.assertIsInstance(component_bag.file_manager, FileManager)
        self.assertIsInstance(component_bag.tt_adapter, TTAdapter)
        self.assertIsInstance(component_bag.logging_function, FunctionType)
        self.assertIsInstance(component_bag.displayer, Displayer)
class DefaultPathProviderTestCase(unittest.TestCase):

    def test_getdefaulttimetrackingpath_shouldreturnexpectedpath_wheninvoked(self):
        
        '''"C:/project_dir/src/" => "C:/project_dir/data/Time Tracking.xlsx"'''

        # Arrange
        expected : str = "C:/project_dir/data/Time Tracking.xlsx"

        # Act
        with patch.object(os, 'getcwd', return_value="C:/project_dir/src/") as mocked_context:
            actual : str = DefaultPathProvider().get_default_time_tracking_path()

        # Assert
        self.assertEqual(expected, actual)
class YearProviderTestCase(unittest.TestCase):

    def test_getallyears_shouldreturnexpectedlist_wheninvoked(self):

        # Arrange
        expected : list[int] = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

        # Act
        actual : list[int] = YearProvider().get_all_years()

        # Assert
        self.assertEqual(expected, actual)
    def test_getallyearlytargets_shouldreturnexpectedlist_wheninvoked(self):

        # Arrange
        expected : list[YearlyTarget] = [
            YearlyTarget(year = 2015, hours = timedelta(hours = 0)),
            YearlyTarget(year = 2016, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2017, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2018, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2019, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2020, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2021, hours = timedelta(hours = 500)),
            YearlyTarget(year = 2022, hours = timedelta(hours = 400)),
            YearlyTarget(year = 2023, hours = timedelta(hours = 250)),
            YearlyTarget(year = 2024, hours = timedelta(hours = 500))
        ]

        # Act
        actual : list[YearlyTarget] = YearProvider().get_all_yearly_targets()

        # Assert
        self.assertTrue(SupportMethodProvider.are_lists_of_yearly_targets_equal(list1 = expected, list2 = actual))
    def test_getmostrecentxyears_shouldreturnlastxyears_whenxlessthantotalyears(self):

        # Arrange
        x : uint = uint(5)
        expected : list[int] = [2020, 2021, 2022, 2023, 2024]
        
        # Act
        actual : list[int] = YearProvider().get_most_recent_x_years(x)

        # Assert
        self.assertEqual(expected, actual)
    def test_getmostrecentxyears_shouldreturnallyears_whenxgreaterthantotalyears(self):

        # Arrange
        x : uint = uint(15)
        expected : list[int] = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
        
        # Act
        actual : list[int] = YearProvider().get_most_recent_x_years(x)

        # Assert
        self.assertEqual(expected, actual)
    def test_getmostrecentxyears_shouldreturnemptylist_whenxiszero(self):

        # Arrange
        x : uint = uint(0)
        expected : list[int] = []
        
        # Act
        actual : list[int] = YearProvider().get_most_recent_x_years(x)

        # Assert
        self.assertEqual(expected, actual)
class SoftwareProjectNameProviderTestCase(unittest.TestCase):

    def test_getallsoftwareprojectnames_shouldreturnexpectedlist_wheninvoked(self):

        # Arrange
        expected : list[str] = [
            "NW.MarkdownTables",
            "NW.NGramTextClassification",
            "NW.UnivariateForecasting",
            "NW.Shared.Files",
            "NW.Shared.Serialization",
            "NW.Shared.Validation",
            "nwreadinglist",
            "nwtimetracking",
            "nwtraderaanalytics",
            "nwshared",
            "nwpackageversions"
        ]

        # Act
        actual : list[str] = SoftwareProjectNameProvider().get_all_software_project_names()

        # Assert
        self.assertEqual(expected, actual)
    def test_getallsoftwareprojectnamesbyspv_shouldreturnexpectedlist_wheninvoked(self):

        # Arrange
        expected : list[str] = [
            "NW.MarkdownTables",
            "NW.NGramTextClassification",
            "NW.UnivariateForecasting",
            "NW.Shared.Files",        
            "NW.Shared.Serialization",
            "NW.Shared.Validation",
            "nwreadinglist",
            "nwtimetracking",
            "nwtraderaanalytics",
            "nwshared",
            "nwpackageversions"
        ]

        # Act
        actual : list[str] = SoftwareProjectNameProvider().get_all_software_project_names_by_spv()

        # Assert
        self.assertEqual(expected, actual)
class MDInfoProviderTestCase(unittest.TestCase):
    
    def test_getall_shouldreturnexpectedlist_wheninvoked(self):
        
        # Arrange
        expected : list[MDInfo] = [
            MDInfo(
                id = TTID.TTSBYMONTH,
                file_name="TIMETRACKINGBYMONTH.md",
                paragraph_title="Time Tracking By Month",
            )
        ]

        # Act
        actual : list[MDInfo] = MDInfoProvider().get_all()

        # Assert
        self.assertEqual(expected, actual)
        self.assertEqual(expected[0].id, actual[0].id)
        self.assertEqual(expected[0].file_name, actual[0].file_name)
        self.assertEqual(expected[0].paragraph_title, actual[0].paragraph_title)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)