# GLOBAL MODULES
import unittest
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
from numpy import int64
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from parameterized import parameterized
from types import FunctionType
from typing import Tuple
from unittest.mock import Mock, call, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwtimetracking import ComponentBag, MarkdownProcessor, SoftwareProjectNameProvider, YearlyTarget, SettingBag, EffortStatus, _MessageCollection
from nwtimetracking import DefaultPathProvider, YearProvider, TimeTrackingManager
from nwshared import MarkdownHelper, Formatter, FilePathManager, FileManager

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

         return SettingBag(
            years = [2015],
            yearly_targets = [
                YearlyTarget(year = 2015, hours = timedelta(hours = 0))
            ],
            excel_path = DefaultPathProvider().get_default_time_tracking_path(),
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
    @staticmethod
    def create_service_objects_for_ttsbymonthmd() -> Tuple[ComponentBag, SettingBag, MarkdownProcessor]:

        component_bag : Mock = Mock()
        component_bag.logging_function = Mock()
        component_bag.file_manager.save_content = Mock()
        component_bag.markdown_helper = MarkdownHelper(formatter = Formatter())
        component_bag.file_path_manager = FilePathManager()        
        
        setting_bag : Mock = Mock()
        setting_bag.last_update = datetime(2024, 10, 1)
        setting_bag.tts_by_month_file_name = "TIMETRACKINGBYMONTH.md"
        setting_bag.working_folder_path = "/home/nwtimetracking/"
        setting_bag.show_tts_by_month_md = True
        setting_bag.save_tts_by_month_md = True

        markdown_processor : MarkdownProcessor = MarkdownProcessor(
			component_bag = component_bag, 
			setting_bag = setting_bag
			)        

        return (component_bag, setting_bag, markdown_processor) 

# TEST CLASSES
class ComponentBagTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_whendefault(self) -> None:

        # Arrange
        # Act
        component_bag : ComponentBag = ComponentBag()

        # Assert
        self.assertIsInstance(component_bag.file_path_manager, FilePathManager)
        self.assertIsInstance(component_bag.file_manager, FileManager)
        self.assertIsInstance(component_bag.logging_function, FunctionType)
        self.assertIsInstance(component_bag.markdown_helper, MarkdownHelper)
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
class TimeTrackingManagerTestCase(unittest.TestCase):

    def test_convertstringtotimedelta_shouldreturnexpectedtimedelta_whenproperstring(self):

        # Arrange
        td_str : str = "5h 30m"
        expected_td : timedelta = pd.Timedelta(hours = 5, minutes = 30).to_pytimedelta()

        # Act
        actual_td : str = TimeTrackingManager()._TimeTrackingManager__convert_string_to_timedelta(td_str = td_str) # type: ignore

        # Assert
        self.assertEqual(expected_td, actual_td)
    def test_getyearlytarget_shouldreturnexpectedhours_whenyearinlist(self):

        # Arrange
        yearly_targets : list[YearlyTarget] = ObjectMother.create_yearly_targets()
        year : int = 2024
        expected_hours : timedelta = timedelta(hours = 250)

        # Act
        actual_hours : timedelta = TimeTrackingManager()._TimeTrackingManager__get_yearly_target(yearly_targets = yearly_targets, year = year).hours # type: ignore

        # Assert
        self.assertEqual(expected_hours, actual_hours)
    def test_getyearlytarget_shouldreturnnone_whenyearnotinlist(self):

        # Arrange
        yearly_targets : list[YearlyTarget] = ObjectMother.create_yearly_targets()
        year : int = 2010

        # Act
        yearly_target : YearlyTarget = TimeTrackingManager()._TimeTrackingManager__get_yearly_target(yearly_targets = yearly_targets, year = year) # type: ignore

        # Assert
        self.assertIsNone(yearly_target)
    def test_isyearlytargetmet_shouldreturntrue_whenyearlytargetismet(self):

        # Arrange
        effort : timedelta = pd.Timedelta(hours = 255, minutes = 30)
        yearly_target : timedelta = pd.Timedelta(hours = 250)

        # Act
        actual : bool = TimeTrackingManager()._TimeTrackingManager__is_yearly_target_met(effort = effort, yearly_target = yearly_target) # type: ignore
        
        # Assert
        self.assertTrue(actual)
    def test_isyearlytargetmet_shouldreturnfalse_whenyearlytargetisnotmet(self):

        # Arrange
        effort : timedelta = pd.Timedelta(hours = 249)
        yearly_target : timedelta = pd.Timedelta(hours = 250)

        # Act
        actual : bool = TimeTrackingManager()._TimeTrackingManager__is_yearly_target_met(effort = effort, yearly_target = yearly_target) # type: ignore

        # Assert
        self.assertFalse(actual)
    def test_formattimedelta_shouldreturnexpectedstring_whenpropertimedeltaandplussignfalse(self):    

        # Arrange
        td : timedelta = pd.Timedelta(hours = 255, minutes = 30)
        expected : str = "255h 30m"

        # Act
        actual : str = TimeTrackingManager()._TimeTrackingManager__format_timedelta(td = td, add_plus_sign = False) # type: ignore
        
        # Assert
        self.assertEqual(expected, actual)
    def test_formattimedelta_shouldreturnexpectedstring_whenpropertimedeltaandplussigntrue(self):    

        # Arrange
        td : timedelta = pd.Timedelta(hours = 255, minutes = 30)
        expected : str = "+255h 30m"

        # Act
        actual : str = TimeTrackingManager()._TimeTrackingManager__format_timedelta(td = td, add_plus_sign = True) # type: ignore
        
        # Assert
        self.assertEqual(expected, actual)
    def test_extractsoftwareprojectname_shouldreturnexpectedstring_whenproperstring(self):

        # Arrange
        descriptor : str = "NW.AutoProffLibrary v1.0.0"
        expected : str = "NW.AutoProffLibrary"

        # Act
        actual : str = TimeTrackingManager()._TimeTrackingManager__extract_software_project_name(descriptor = descriptor) # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_extractsoftwareprojectname_shouldreturnerrorstring_whenunproperstring(self):

        # Arrange
        descriptor : str = "Some gibberish"
        expected : str = "ERROR"

        # Act
        actual : str = TimeTrackingManager()._TimeTrackingManager__extract_software_project_name(descriptor = descriptor) # type: ignore

        # Assert
        self.assertEqual(expected, actual)   
    def test_extractsoftwareprojectversion_shouldreturnexpectedstring_whenproperstring(self):

        # Arrange
        descriptor : str = "NW.AutoProffLibrary v1.0.0"
        expected : str = "1.0.0"

        # Act
        actual : str = TimeTrackingManager()._TimeTrackingManager__extract_software_project_version(descriptor = descriptor) # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_extractsoftwareprojectversion_shouldreturnerrorstring_whenunproperstring(self):

        # Arrange
        descriptor : str = "Some gibberish"
        expected : str = "ERROR"

        # Act
        actual : str = TimeTrackingManager()._TimeTrackingManager__extract_software_project_version(descriptor = descriptor) # type: ignore

        # Assert
        self.assertEqual(expected, actual)  
    def test_calculatepercentage_shouldreturnexpectedfloat_when0and16(self):

        # Arrange
        part : float = 0
        whole : float = 16
        rounding_digits : int = 2
        expected : float = 0.00
        
        # Act
        actual : float = TimeTrackingManager()._TimeTrackingManager__calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits) # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_calculatepercentage_shouldreturnexpectedfloat_when4and0(self):

        # Arrange
        part : float = 4
        whole : float = 0
        rounding_digits : int = 2
        expected : float = 0.00
        
        # Act
        actual : float = TimeTrackingManager()._TimeTrackingManager__calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits) # type: ignore

        # Assert
        self.assertEqual(expected, actual)        
    def test_calculatepercentage_shouldreturnexpectedfloat_when4and16(self):

        # Arrange
        part : float = 4
        whole : float = 16
        rounding_digits : int = 2
        expected : float = 25.00
        
        # Act
        actual : float = TimeTrackingManager()._TimeTrackingManager__calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits) # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_calculatepercentage_shouldreturnexpectedfloat_when16and16(self):

        # Arrange
        part : float = 16
        whole : float = 16
        rounding_digits : int = 2
        expected : float = 100.00
        
        # Act
        actual : float = TimeTrackingManager()._TimeTrackingManager__calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits) # type: ignore

        # Assert
        self.assertEqual(expected, actual)        
    def test_calculatepercentage_shouldreturnexpectedfloat_when3and9and4(self):

        # Arrange
        part : float = 3
        whole : float = 9
        rounding_digits : int = 4
        expected : float = 33.3333
        
        # Act
        actual : float = TimeTrackingManager()._TimeTrackingManager__calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits) # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_createeffortstatus_shouldreturnexpectobject_wheneffortiscorrect(self):

        # Arrange
        idx : int = 1
        start_time_str : str = "07:00" 
        end_time_str : str = "08:00"
        effort_str : str = "01h 00m"

        strp_format : str = "%Y-%m-%d %H:%M"

        start_time_dt : datetime = datetime.strptime(f"1900-01-01 {start_time_str}", strp_format)
        end_time_dt : datetime = datetime.strptime(f"1900-01-01 {end_time_str}", strp_format)
        actual_str = effort_str
        actual_td : timedelta = pd.Timedelta(value = actual_str).to_pytimedelta()
        expected_str : str = actual_str
        expected_td : timedelta = actual_td
        is_correct : bool = True
        message : str = "The effort is correct."
        expected : EffortStatus = EffortStatus(
            idx = idx,
            start_time_str = start_time_str,
            start_time_dt = start_time_dt,
            end_time_str = end_time_str,
            end_time_dt = end_time_dt,
            actual_str = effort_str,
            actual_td = actual_td,
            expected_td = expected_td,
            expected_str = expected_str,
            is_correct = is_correct,
            message = message
            )

        # Act
        actual : EffortStatus = TimeTrackingManager()._TimeTrackingManager__create_effort_status(idx = idx, start_time_str = start_time_str,end_time_str = end_time_str,effort_str = effort_str) # type: ignore

        # Assert
        comparison : bool = SupportMethodProvider().are_effort_statuses_equal(ef1 = expected, ef2 = actual)
        self.assertTrue(comparison) 
    def test_createeffortstatus_shouldreturnexpectobject_wheneffortisnotcorrect(self):

        # Arrange
        idx : int = 1
        start_time_str : str = "07:00" 
        end_time_str : str = "08:00"
        effort_str : str = "02h 00m"

        strp_format : str = "%Y-%m-%d %H:%M"

        start_time_dt : datetime = datetime.strptime(f"1900-01-01 {start_time_str}", strp_format)
        end_time_dt : datetime = datetime.strptime(f"1900-01-01 {end_time_str}", strp_format)
        actual_str = effort_str
        actual_td : timedelta = pd.Timedelta(value = actual_str).to_pytimedelta()
        expected_str : str = "01h 00m"
        expected_td : timedelta = pd.Timedelta(value = expected_str).to_pytimedelta()
        is_correct : bool = False 
        message : str = _MessageCollection.effort_status_mismatching_effort(
                            idx = idx, 
                            start_time_str = start_time_str, 
                            end_time_str = end_time_str, 
                            actual_str = actual_str, 
                            expected_str = expected_str
                    )

        expected : EffortStatus = EffortStatus(
            idx = idx,
            start_time_str = start_time_str,
            start_time_dt = start_time_dt,
            end_time_str = end_time_str,
            end_time_dt = end_time_dt,
            actual_str = effort_str,
            actual_td = actual_td,
            expected_td = expected_td,
            expected_str = expected_str,
            is_correct = is_correct,
            message = message
            )

        # Act
        actual : EffortStatus = TimeTrackingManager()._TimeTrackingManager__create_effort_status(idx = idx, start_time_str = start_time_str, end_time_str = end_time_str, effort_str = effort_str) # type: ignore

        # Assert
        comparison : bool = SupportMethodProvider().are_effort_statuses_equal(ef1 = expected, ef2 = actual)
        self.assertTrue(comparison) 

    @parameterized.expand([
        [1, "5h 30m", timedelta(hours = 5, minutes = 30)],
        [2, "2h 00m", timedelta(hours = 2, minutes = 00)]
    ])
    def test_createeffortstatusfornonevalues_shouldreturnexpectedobject_wheninvoked(
        self, 
        idx : int, 
        effort_str : str, 
        actual_td : timedelta):

        # Arrange
        expected : EffortStatus = EffortStatus(
            idx = idx,
            start_time_str = None,
            start_time_dt = None,
            end_time_str = None,
            end_time_dt = None,
            actual_str = effort_str,
            actual_td = actual_td,
            expected_td = None,
            expected_str = None,
            is_correct = True,
            message = "''start_time' and/or 'end_time' are empty, 'effort' can't be verified. We assume that it's correct."
            ) 

        # Act
        actual : EffortStatus = TimeTrackingManager()._TimeTrackingManager__create_effort_status_for_none_values(idx = idx, effort_str = effort_str) # type: ignore

        # Assert
        comparison : bool = SupportMethodProvider().are_effort_statuses_equal(ef1 = expected, ef2 = actual)
        self.assertTrue(comparison)
    @parameterized.expand([
        "07:00", "07:15", "07:30", "07:45", 
        "08:00", "08:15", "08:30", "08:45",
        "09:00", "09:15", "09:30", "09:45",
        "10:00", "10:15", "10:30", "10:45",
        "11:00", "11:15", "11:30", "11:45",
        "12:00", "12:15", "12:30", "12:45",
        "13:00", "13:15", "13:30", "13:45",
        "14:00", "14:15", "14:30", "14:45",
        "15:00", "15:15", "15:30", "15:45",
        "16:00", "16:15", "16:30", "16:45",
        "17:00", "17:15", "17:30", "17:45",
        "18:00", "18:15", "18:30", "18:45",
        "19:00", "19:15", "19:30", "19:45",
        "20:00", "20:15", "20:30", "20:45",
        "21:00", "21:15", "21:30", "21:45",
        "22:00", "22:15", "22:30", "22:45",
        "23:00", "23:15", "23:30", "23:45"
    ])
    def test_createtimeobject_shouldreturnexpecteddatatime_whenday1time(self, time : str):

        # Arrange
        strp_format : str = "%Y-%m-%d %H:%M"
        dt_str = f"1900-01-01 {time}"
        expected : datetime = datetime.strptime(dt_str, strp_format)

        # Act
        actual : datetime = TimeTrackingManager()._TimeTrackingManager__create_time_object(time = time) # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        "00:00", "00:15", "00:30", "00:45", 
        "01:00", "01:15", "01:30", "01:45",
        "02:00", "02:15", "02:30", "02:45",
        "03:00", "03:15", "03:30", "03:45",
        "04:00", "04:15", "04:30", "04:45",
        "05:00", "05:15", "05:30", "05:45",
        "06:00", "06:15", "06:30", "06:45"
    ])
    def test_createtimeobject_shouldreturnexpecteddatatime_whenday2time(self, time : str):

        # Arrange
        strp_format : str = "%Y-%m-%d %H:%M"
        dt_str = f"1900-01-02 {time}"
        expected : datetime = datetime.strptime(dt_str, strp_format)

        # Act
        actual : datetime = TimeTrackingManager()._TimeTrackingManager__create_time_object(time = time) # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    @parameterized.expand([
        "07:04",
        "00:01",
        "gibberish text"
    ])
    def test_createtimeobject_shouldraisevalueerrorexception_whennotamongtimevalues(self, time : str):

        # Arrange
        expected_message : str = _MessageCollection.effort_status_not_among_expected_time_values(time = time)
        
        # Act
        with self.assertRaises(ValueError) as context:
            actual : datetime = TimeTrackingManager()._TimeTrackingManager__create_time_object(time = time) # type: ignore

        # Assert
        self.assertTrue(expected_message in str(context.exception))
    @parameterized.expand([
        [1, "07:00", "", "5h 30m"],
        [1, "", "07:00", "5h 30m"]
    ])
    def test_createeffortstatus_shouldreturnexpectobject_whenstarttimeorendtimeareempty(
            self,
            idx : int, 
            start_time_str : str, 
            end_time_str : str, 
            effort_str : str):

        # Arrange
        actual_td : timedelta = TimeTrackingManager()._TimeTrackingManager__convert_string_to_timedelta(td_str = effort_str) # type: ignore
        expected : EffortStatus = EffortStatus(
            idx = idx,
            start_time_str = None,
            start_time_dt = None,
            end_time_str = None,
            end_time_dt = None,
            actual_str = effort_str,
            actual_td = actual_td,
            expected_td = None,
            expected_str = None,
            is_correct = True,
            message = "''start_time' and/or 'end_time' are empty, 'effort' can't be verified. We assume that it's correct."
            ) 
                
        # Act
        actual : EffortStatus = TimeTrackingManager()._TimeTrackingManager__create_effort_status(
            idx = idx, 
            start_time_str = start_time_str,
            end_time_str = end_time_str,
            effort_str = effort_str)

        # Assert
        comparison : bool = SupportMethodProvider().are_effort_statuses_equal(ef1 = expected, ef2 = actual)
        self.assertTrue(comparison)
    @parameterized.expand([
        ["Some Gibberish", "08:00", "01h 00m"],
        ["07:00", "Some Gibberish", "01h 00m"],
        ["07:00", "08:00", "Some Gibberish"]
    ])
    def test_createeffortstatus_shouldraisevalueerrorexception_whenunproperparameters(
            self, 
            start_time_str : str, 
            end_time_str : str, 
            effort_str : str):

        # Arrange
        idx : int = 1        
        expected_message : str = _MessageCollection.effort_status_not_possible_to_create(
            idx = idx, start_time_str = start_time_str, end_time_str = end_time_str, effort_str = effort_str)
        
        # Act
        with self.assertRaises(ValueError) as context:
            actual : EffortStatus = TimeTrackingManager()._TimeTrackingManager__create_effort_status(idx = idx, start_time_str = start_time_str, end_time_str = end_time_str, effort_str = effort_str)  # type: ignore

        # Assert
        self.assertTrue(expected_message in str(context.exception)) 
    @parameterized.expand([
        ["07:00", "08:00", "UNKNOWN", "07:00-08:00"],
        ["", "08:00", "UNKNOWN", "UNKNOWN"],
        ["07:00", "", "UNKNOWN", "UNKNOWN"]
    ])
    def test_createtimerangeid_shouldreturnexpectedtimerangeid_wheninvoked(
            self,
            start_time : str, 
            end_time : str, 
            unknown_id : str,
            expected : str):

        # Arrange
        # Act
        actual : str = TimeTrackingManager()._TimeTrackingManager__create_time_range_id(start_time = start_time, end_time = end_time, unknown_id = unknown_id) # type: ignore

        # Assert
        self.assertEqual(expected, actual)

    def test_getsessionsdataset_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        excel_data_df : DataFrame = ObjectMother().create_excel_data()
        setting_bag : SettingBag = ObjectMother().create_setting_bag()
        expected_column_names : list[str] = ObjectMother().create_sessions_df_column_names()
        expected_dtype_names : list[str] = ObjectMother().create_sessions_df_dtype_names()
        expected_nan : str = ""

        # Act
        with patch.object(pd, 'read_excel', return_value = excel_data_df) as mocked_context:
            actual : DataFrame = TimeTrackingManager().get_tt(setting_bag = setting_bag)

        # Assert
        self.assertEqual(expected_column_names, actual.columns.tolist())
        self.assertEqual(expected_dtype_names, SupportMethodProvider().get_dtype_names(df = actual))
        self.assertEqual(expected_nan, actual[expected_column_names[1]][0])
        self.assertEqual(expected_nan, actual[expected_column_names[2]][0])
        self.assertEqual(expected_nan, actual[expected_column_names[5]][0])
    def test_getttbyyear_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        yearly_targets : list[YearlyTarget] = [ YearlyTarget(year = 2024, hours = timedelta(hours = 250)) ]
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tt_by_year_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_year(tt_df = sessions_df, years = years, yearly_targets = yearly_targets)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_getttbyyearmonth_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        yearly_targets : list[YearlyTarget] = [ YearlyTarget(year = 2024, hours = timedelta(hours = 250)) ]
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tt_by_year_month_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_year_month(tt_df = sessions_df, years = years, yearly_targets = yearly_targets)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_getttbyyearmonthspnv_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tt_by_year_month_spnv_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_year_month_spnv(tt_df = sessions_df, years = years, software_project_names = software_project_names)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_getttbyyearspnv_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tt_by_year_spnv_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_year_spnv(tt_df = sessions_df, years = years, software_project_names = software_project_names)

        # Assert
        assert_frame_equal(expected_df , actual_df)      
    def test_getttbyspnspv_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tt_by_spn_spv_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_spn_spv(tt_df = sessions_df, years = years, software_project_names = software_project_names)

        # Assert
        assert_frame_equal(expected_df , actual_df) 
    def test_getttsbymonth_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tts_by_month_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_month(tt_df = sessions_df, years = years)

        # Assert
        assert_frame_equal(expected_df, actual_df)
    def test_updatefuturemonthstoempty_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        now : datetime = datetime(2024, 2, 27)
        tts_by_month_df : DataFrame = ObjectMother().create_tts_by_month_df()
        expected_df : DataFrame = ObjectMother().create_tts_by_month_upd_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().update_future_months_to_empty(tts_by_month_df = tts_by_month_df, now = now)

        # Assert
        assert_frame_equal(expected_df, actual_df)
    def test_createtimeranges_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        unknown_id : str = "Unknown"
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_time_ranges_df()
        expected_df.sort_values(by = "TimeRangeId", ascending = True, inplace = True)
        expected_df.reset_index(drop = True, inplace = True)

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_time_ranges(tt_df = sessions_df, unknown_id = unknown_id)
        actual_df.sort_values(by = "TimeRangeId", ascending = True, inplace = True)
        actual_df.reset_index(drop = True, inplace = True)

        # Assert
        assert_frame_equal(expected_df, actual_df)  
    def test_removeunknownid_shouldreturnexpecteddataframe_whencontainsunknownid(self):

        # Arrange
        unknown_id : str = "Unknown"
        expected_df : DataFrame = ObjectMother().create_time_ranges_df()   
        time_ranges_df : DataFrame = ObjectMother().create_time_ranges_df()
        time_ranges_df.loc[len(time_ranges_df.index)] = [unknown_id, 3]

        # Act
        actual_df : DataFrame  = TimeTrackingManager().remove_unknown_id(tts_by_time_ranges_df = time_ranges_df, unknown_id = unknown_id)

        # Assert
        assert_frame_equal(expected_df, actual_df)  
    def test_removeunknownid_shouldreturnexpecteddataframe_whendoesnotcontainunknownid(self):

        # Arrange
        unknown_id : str = "Unknown"
        expected_df : DataFrame = ObjectMother().create_time_ranges_df()   
        time_ranges_df : DataFrame = ObjectMother().create_time_ranges_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().remove_unknown_id(tts_by_time_ranges_df = time_ranges_df, unknown_id = unknown_id)

        # Assert
        assert_frame_equal(expected_df, actual_df)  
    def test_getttbyyearhashtag_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tt_by_year_hashtag_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_year_hashtag(tt_df = sessions_df, years = years)

        # Assert
        assert_frame_equal(expected_df , actual_df)  
    def test_getttbyhashtag_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tt_by_hashtag_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_hashtag(tt_df = sessions_df)

        # Assert
        assert_frame_equal(expected_df , actual_df)

    @parameterized.expand([
        [True],
        [False]
    ])
    def test_getttbyspn_shouldreturnexpecteddataframe_wheninvoked(self, remove_untagged : bool):

        # Arrange
        years : list[int] = [2024]
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        sessions_df : DataFrame = ObjectMother().create_sessions_df()
        expected_df : DataFrame = ObjectMother().create_tt_by_spn_df()

        # Act
        actual_df : DataFrame  = TimeTrackingManager().get_tts_by_spn(tt_df = sessions_df, years = years, software_project_names = software_project_names, remove_untagged = remove_untagged)

        # Assert
        assert_frame_equal(expected_df , actual_df) 
class MarkdownProcessorTestCase(unittest.TestCase):

    def test_processttsbymonthmd_shouldlogandsave_whenshowandsavearetrue(self) -> None:

		# Arrange
        file_name : str = "TIMETRACKINGBYMONTH.md"
        file_path : str = f"/home/nwtimetracking/{file_name}"
        tts_by_month_upd_df, expected = ObjectMother().create_dtos_for_ttsbymonthmd()
        component_bag, _, markdown_processor = ObjectMother().create_service_objects_for_ttsbymonthmd()        

        # Act
        markdown_processor.process_tts_by_month_md(tts_by_month_upd_df = tts_by_month_upd_df)

        # Assert
        self.assertEqual(component_bag.logging_function.call_count, 2)
        component_bag.logging_function.assert_has_calls([
            call(file_name + "\n"),
            call(expected)
        ])
        component_bag.file_manager.save_content.assert_called_with(content = expected, file_path = file_path)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)