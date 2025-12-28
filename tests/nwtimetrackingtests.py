# GLOBAL MODULES
import importlib
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from numpy import int64, uint
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from parameterized import parameterized
from pathlib import Path
from typing import Any, Literal, Optional, Tuple, cast
from unittest.mock import _Call, Mock, call, patch

# LOCAL/NW MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwtimetracking import EFFORTMODE, REPORTSTR, TTCN, DEFINITIONSTR, OPTION, EffortCell, EffortHighlighter, TTAdapter, TTReportManager
from nwtimetracking import _MessageCollection, TTDataFrameFactory, TimeTrackingProcessor
from nwtimetracking import EffortStatus, TTSummary, DefaultPathProvider, YearProvider
from nwtimetracking import SoftwareProjectNameProvider, SettingBag, ComponentBag, TTDataFrameHelper
from nwshared import FilePathManager, FileManager, Displayer

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
class ObjectMother():

    '''Collects all the DTOs required by the unit tests.'''

    @staticmethod
    def get_setting_bag() -> SettingBag:

        setting_bag : SettingBag = SettingBag(
            options_tt = [OPTION.display],                          # type: ignore
            options_tt_latest_four = [OPTION.display],              # type: ignore
            options_tts_by_month = [OPTION.display],                # type: ignore
            options_tts_by_year = [OPTION.display],                 # type: ignore
            options_tts_by_range = [OPTION.display],                # type: ignore
            options_tts_by_spn = [OPTION.display],                  # type: ignore
            options_tts_by_spv = [],                                # type: ignore
            options_tts_by_hashtag_year = [OPTION.display],         # type: ignore
            options_tts_by_hashtag = [OPTION.display],              # type: ignore
            options_tts_by_year_month_spnv = [OPTION.display],      # type: ignore
            options_tts_by_timeranges = [OPTION.display],           # type: ignore
            options_ttd_effort_status = [OPTION.display],           # type: ignore
            options_definitions = [OPTION.display],                 # type: ignore
            excel_nrows = 1301,                                     # type: ignore
            tts_by_spn_software_project_names = "nwtimetracking",   # type: ignore
            tts_by_spv_software_project_names = "nwtimetracking"    # type: ignore
        )

        return setting_bag
    @staticmethod
    def get_excel_data() -> DataFrame:

        excel_data_dict : dict = {
            TTCN.DATE: "2015-10-31",
            TTCN.STARTTIME: "",
            TTCN.ENDTIME: "",
            TTCN.EFFORT: "8h 00m",
            TTCN.HASHTAG: "#untagged",
            TTCN.DESCRIPTOR: "",
            TTCN.ISSOFTWAREPROJECT: "False",
            TTCN.ISRELEASEDAY: "False",
            TTCN.YEAR: "2015",
            TTCN.MONTH: "10"
            }
        excel_data_df : DataFrame = pd.DataFrame(data = excel_data_dict, index=[0])

        return excel_data_df
    @staticmethod
    def get_tt_df_column_names() -> list[str]:

        column_names : list[str] = []
        column_names.append(TTCN.DATE)                 # [0], date
        column_names.append(TTCN.STARTTIME)            # [1], str
        column_names.append(TTCN.ENDTIME)              # [2], str
        column_names.append(TTCN.EFFORT)               # [3], str
        column_names.append(TTCN.HASHTAG)              # [4], str
        column_names.append(TTCN.DESCRIPTOR)           # [5], str
        column_names.append(TTCN.ISSOFTWAREPROJECT)    # [6], bool
        column_names.append(TTCN.ISRELEASEDAY)         # [7], bool
        column_names.append(TTCN.YEAR)                 # [8], int
        column_names.append(TTCN.MONTH)                # [9], int

        return column_names
    @staticmethod
    def get_tt_df_dtype_names() -> list[str]:

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
    def get_tt_df() -> DataFrame:

        '''
                Date	    StartTime	EndTime	Effort	Hashtag	        Descriptor	                    IsSoftwareProject	IsReleaseDay	Year	Month
            980	2024-02-12	21:00	    22:00	1h 00m	#maintenance		                            False	            False	        2024	2
            981	2024-02-13	11:00	    13:00	2h 00m	#csharp	        NW.Shared.Serialization v1.0.0	True	            True	        2024	2
            982	2024-02-13	14:30	    16:45	2h 15m	#csharp	        NW.Shared.Serialization v1.0.0	True	            True	        2024	2        
            ...
        '''

        return pd.DataFrame({
                TTCN.DATE: np.array([date(2024, 2, 12), date(2024, 2, 13), date(2024, 2, 13), date(2024, 2, 14), date(2024, 2, 14), date(2024, 2, 14), date(2024, 2, 15), date(2024, 2, 18), date(2024, 2, 18), date(2024, 2, 18), date(2024, 2, 18), date(2024, 2, 18), date(2024, 2, 19), date(2024, 2, 19), date(2024, 2, 19), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 20), date(2024, 2, 25), date(2024, 2, 25), date(2024, 2, 26)], dtype=str),
                TTCN.STARTTIME: np.array(['21:00', '11:00', '14:30', '08:00', '17:15', '20:00', '17:15', '11:00', '13:30', '17:00', '22:00', '23:00', '11:15', '15:30', '20:15', '08:45', '13:30', '15:30', '10:15', '14:00', '08:15'], dtype=str),
                TTCN.ENDTIME: np.array(['22:00', '13:00', '16:45', '08:30', '18:00', '20:15', '17:45', '12:30', '15:00', '18:00', '23:00', '23:30', '13:00', '18:00', '21:15', '12:15', '14:00', '16:30', '13:00', '19:45', '12:45'], dtype=str),
                TTCN.EFFORT: np.array(['1h 00m', '2h 00m', '2h 15m', '0h 30m', '0h 45m', '0h 15m', '0h 30m', '1h 30m', '1h 30m', '1h 00m', '1h 00m', '0h 30m', '1h 45m', '2h 30m', '1h 00m', '3h 30m', '0h 30m', '1h 00m', '2h 45m', '5h 45m', '4h 30m'], dtype=str),
                TTCN.HASHTAG: np.array(['#maintenance', '#csharp', '#csharp', '#csharp', '#csharp', '#csharp', '#csharp', '#maintenance', '#maintenance', '#python', '#python', '#maintenance', '#studying', '#studying', '#studying', '#studying', '#studying', '#studying', '#studying', '#studying', '#studying'], dtype=str),
                TTCN.DESCRIPTOR: np.array(['', 'NW.Shared.Serialization v1.0.0', 'NW.Shared.Serialization v1.0.0', 'NW.NGramTextClassification v4.2.0', 'NW.NGramTextClassification v4.2.0', 'NW.UnivariateForecasting v4.2.0', 'NW.UnivariateForecasting v4.2.0', '', '', 'nwreadinglistmanager v2.1.0', 'nwreadinglistmanager v2.1.0', '', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.', 'Books.'], dtype=str),
                TTCN.ISSOFTWAREPROJECT: np.array([False, True, True, True, True, True, True, False, False, True, True, True, False, False, False, False, False, False, False, False, False], dtype=bool),
                TTCN.ISRELEASEDAY: np.array([False, True, True, True, True, False, True, False, False, True, True, True, False, False, False, False, False, False, False, False, False], dtype=bool),
                TTCN.YEAR: np.array([2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024], dtype=int64),
                TTCN.MONTH: np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], dtype=int64),
            }, index=pd.RangeIndex(start=980, stop=1001, step=1)) 
    @staticmethod
    def get_tts_by_month_df() -> DataFrame:

        '''
                2024
            0	00h 00m
            1	36h 00m
            ...
            12	00h 00m
        '''

        df : DataFrame = pd.DataFrame({
                '2024': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object)	
            }, index=pd.RangeIndex(start=0, stop=12, step=1))

        return df
    @staticmethod
    def get_tts_by_year_df() -> DataFrame:

        '''
                2024
            0	36h 00m     
        '''

        return pd.DataFrame({
            "2024": ["36h 00m"]}
            , index=pd.RangeIndex(start=0, stop=1, step=1))
    @staticmethod
    def get_tts_by_range_df() -> DataFrame:

        '''
                1 Year
            0	36h 00m
        '''

        return pd.DataFrame({
            "1 Year": ["36h 00m"]}
            , index=pd.RangeIndex(start=0, stop=1, step=1))
    @staticmethod
    def get_tts_by_spn_df() -> DataFrame:

        '''
                SoftwareProjectName	        Effort  Hashtags
            2	NW.Shared.Serialization	    04h 15m #csharp
            1   nwreadinglistmanager	    02h 00m #python
            2	NW.NGramTextClassification	01h 15m #csharp
            3	NW.UnivariateForecasting	00h 45m #csharp
        '''

        return pd.DataFrame({
                TTCN.SOFTWAREPROJECTNAME: np.array(['NW.Shared.Serialization', 'nwreadinglistmanager', 'NW.NGramTextClassification', 'NW.UnivariateForecasting'], dtype=object),
                TTCN.EFFORT: np.array(['04h 15m', '02h 00m', '01h 15m', '00h 45m'], dtype=object),
                TTCN.HASHTAGS: np.array(['#csharp', '#python', '#csharp', '#csharp'], dtype=object)
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def get_tts_by_spv_df() -> DataFrame:

        '''
                SoftwareProjectName	        SoftwareProjectVersion	Effort
            0	NW.NGramTextClassification	4.2.0	                01h 15m
            1	NW.Shared.Serialization	    1.0.0	                04h 15m
            2	NW.UnivariateForecasting	4.2.0	                00h 45m
            3	nwreadinglistmanager	    2.1.0	                02h 00m
        '''

        return pd.DataFrame({
                TTCN.SOFTWAREPROJECTNAME: np.array(['NW.NGramTextClassification', 'NW.Shared.Serialization', 'NW.UnivariateForecasting', 'nwreadinglistmanager'], dtype=object),
                TTCN.SOFTWAREPROJECTVERSION: np.array(['4.2.0', '1.0.0', '4.2.0', '2.1.0'], dtype=object),
                TTCN.EFFORT: np.array(['01h 15m', '04h 15m', '00h 45m', '02h 00m'], dtype=object),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def get_tts_by_hashtag_year_df() -> DataFrame:

        '''
                Hashtag         2024
            0   #csharp         06h 15m
            1   #maintenance    04h 30m
            2   #python         02h 00m
            3   #studying       23h 15m
        '''

        return pd.DataFrame({
                TTCN.HASHTAG: ["#csharp", "#maintenance", "#python", "#studying"],
                2024:    ["06h 15m", "04h 30m", "02h 00m", "23h 15m"]
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def get_tts_by_hashtag_df() -> DataFrame:

        '''
                Hashtag	        Effort	Effort%
            0	#csharp	        06h 15m	17.36
            1	#maintenance	04h 30m	12.50
            2	#python	        02h 00m	5.56
            3	#studying	    23h 15m	64.58
        '''

        return pd.DataFrame({
                TTCN.HASHTAG: np.array(['#csharp', '#maintenance', '#python', '#studying'], dtype=object),
                TTCN.EFFORT: np.array(['06h 15m', '04h 30m', '02h 00m', '23h 15m'], dtype=object),
                TTCN.EFFORTPERC: np.array([17.36, 12.5, 5.56, 64.58], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def get_tts_by_year_month_spnv_df() -> DataFrame:

        '''
                Year	Month	SoftwareProjectName	        SoftwareProjectVersion	Effort
            0	2024	2	    NW.NGramTextClassification	4.2.0	                01h 15m
            1	2024	2	    NW.Shared.Serialization	    1.0.0	                04h 15m
            2	2024	2	    NW.UnivariateForecasting	4.2.0	                00h 45m
            3	2024	2	    nwreadinglistmanager	    2.1.0	                02h 00m      
        '''

        return pd.DataFrame({
                TTCN.YEAR: np.array([2024, 2024, 2024, 2024], dtype=int64),
                TTCN.MONTH: np.array([2, 2, 2, 2], dtype=int64),
                TTCN.SOFTWAREPROJECTNAME: np.array(['NW.NGramTextClassification', 'NW.Shared.Serialization', 'NW.UnivariateForecasting', 'nwreadinglistmanager'], dtype=object),
                TTCN.SOFTWAREPROJECTVERSION: np.array(['4.2.0', '1.0.0', '4.2.0', '2.1.0'], dtype=object),
                TTCN.EFFORT: np.array(['01h 15m', '04h 15m', '00h 45m', '02h 00m'], dtype=object)
            }, index=pd.Index([1, 2, 3, 4], dtype="int64"))
    @staticmethod
    def get_tts_by_timeranges_df() -> DataFrame:

        '''
            Occurrences  Occurrence%    TimeRanges
        0   1           100.0           ['08:00-08:30', ..., '22:00-23:00', '23:00-23:30']        
        '''

        return pd.DataFrame({
                TTCN.OCCURRENCES: np.array([1], dtype=int64),
                TTCN.OCCURRENCEPERC: np.array([100.0], dtype=float),
                TTCN.TIMERANGES: [[
                    '08:00-08:30', '08:15-12:45', '08:45-12:15', '10:15-13:00',
                    '11:00-12:30', '11:00-13:00', '11:15-13:00', '13:30-14:00',
                    '13:30-15:00', '14:00-19:45', '14:30-16:45', '15:30-16:30',
                    '15:30-18:00', '17:00-18:00', '17:15-17:45', '17:15-18:00',
                    '20:00-20:15', '20:15-21:15', '21:00-22:00', '22:00-23:00',
                    '23:00-23:30'
                ]],
            }, index=pd.RangeIndex(start=0, stop=1, step=1),
        )   
    @staticmethod # TBD
    def get_ttd_effort_status_df(is_correct : bool) -> DataFrame:

        '''
            Note: this applies to: get_tt_df()[-1:]

            is_correct = True:

                    StartTime   EndTime     Effort  IsCorrect   Expected    Message
                0   08:15       12:45       4h 30m  True        04h 30m     The effort is correct.

            is_correct = False:

                StartTime   EndTime     Effort  IsCorrect   Expected    Message
        '''

        if is_correct:
            return pd.DataFrame(
                {
                    TTCN.STARTTIME: np.array(["08:15"], dtype=object),
                    TTCN.ENDTIME: np.array(["12:45"], dtype=object),
                    TTCN.EFFORT: np.array(["4h 30m"], dtype=object),
                    TTCN.ISCORRECT: np.array([True], dtype=bool),
                    TTCN.EXPECTED: np.array(["04h 30m"], dtype=object),
                    TTCN.MESSAGE: np.array(["The effort is correct."], dtype=object)
                },
                index=pd.Index([1000], dtype="int64")
            )            

        return pd.DataFrame(
            {
                TTCN.STARTTIME: pd.Series(dtype=object),
                TTCN.ENDTIME: pd.Series(dtype=object),
                TTCN.EFFORT: pd.Series(dtype=object),
                TTCN.ISCORRECT: pd.Series(dtype=bool),
                TTCN.EXPECTED: pd.Series(dtype=object),
                TTCN.MESSAGE: pd.Series(dtype=object)
            }
        )   
    @staticmethod
    def get_definitions_df() -> DataFrame:

        columns : list[str] = [DEFINITIONSTR.TERM, DEFINITIONSTR.DEFINITION]

        definitions : dict[str, str] = { 
            DEFINITIONSTR.TIMETRACKING: "Time Tracking is the process of keeping track of all self-growth sessions.",
            TTCN.TIMERANGE: "A time range is defined by a start time, an end time, and an effort expressed in hours and minutes.",
            TTCN.HASHTAG: "A hashtag is a category label that summarizes the content of a self-growth session.",
            TTCN.DESCRIPTOR: "A descriptor contains additional information about the self-growth session - e.g. the software project name and version.",
            f"Trend ({TTCN.TREND})": "A trend is a gamification metric that indicates whether a measure (e.g., total work hours) has increased or decreased over time."
        }
        
        definitions_df : DataFrame = DataFrame(
            data = definitions.items(), 
            columns = columns
        )

        return definitions_df

# TEST CLASSES
class MessageCollectionTestCase(unittest.TestCase):

    def test_effortstatusmismatchingeffort_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        idx : int = 4
        start_time_str : str = "20:00"
        end_time_str : str = "00:00"
        actual_str : str = "3h 00m"
        expected_str : str = "4h 00m"
        
        expected_message : str = (
            "The provided row contains a mismatching effort "
            "(idx: '4', start_time: '20:00', end_time: '00:00', actual_effort: '3h 00m', expected_effort: '4h 00m')."
        )

        # Act
        actual_message : str = _MessageCollection.effort_status_mismatching_effort(
            idx = idx, 
            start_time_str = start_time_str, 
            end_time_str = end_time_str,
            actual_str = actual_str,
            expected_str = expected_str
        )

        # Assert
        self.assertEqual(expected_message, actual_message)
    def test_effortstatusnotpossibletocreate_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        idx : int = 770
        start_time_str : str = "22:00"
        end_time_str : str = "00:00"
        effort_str : str = "2h 00m"
        
        expected_message : str = (
            "It has not been possible to create an EffortStatus for the provided parameters "
            "(idx: '770', start_time_str: '22:00', end_time_str: '00:00', effort_str: '2h 00m')."
        )

        # Act
        actual_message : str = _MessageCollection.effort_status_not_possible_to_create(
            idx = idx, 
            start_time_str = start_time_str, 
            end_time_str = end_time_str, 
            effort_str = effort_str
        )

        # Assert
        self.assertEqual(expected_message, actual_message)
    def test_effortstatusnotamongexpectedtimevalues_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        time : str = "25:00"
        expected_message : str = "The provided time ('25:00') is not among the expected time values."

        # Act
        actual_message : str = _MessageCollection.effort_status_not_among_expected_time_values(time = time)

        # Assert
        self.assertEqual(expected_message, actual_message)
    def test_starttimeendtimeareempty_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        expected : str = "''start_time' and/or 'end_time' are empty, 'effort' can't be verified. We assume that it's correct."

        # Act
        actual : str = _MessageCollection.starttime_endtime_are_empty()

        # Assert
        self.assertEqual(expected, actual)
    def test_effortiscorrect_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        expected : str = "The effort is correct."

        # Act
        actual : str = _MessageCollection.effort_is_correct()

        # Assert
        self.assertEqual(expected, actual)
    def test_pleaseruninitializefirst_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        expected : str = "Please run the 'initialize' method first."

        # Act
        actual : str = _MessageCollection.please_run_initialize_first()

        # Assert
        self.assertEqual(expected, actual)
    def test_providedmodenotsupported_shouldreturnexpectedmessage_wheninvalidmode(self) -> None:

        # Arrange
        invalid_mode : EFFORTMODE = cast(EFFORTMODE, "invalid")
        expected : str = f"The provided mode is not supported: '{invalid_mode}'."

        # Act
        actual : str = _MessageCollection.provided_mode_not_supported(mode = invalid_mode)

        # Assert
        self.assertEqual(expected, actual)	
class EffortStatusTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:

        # Arrange
        idx : int = 1
        start_time_str : Optional[str] = "07:00"
        start_time_dt : Optional[datetime] = datetime.strptime("07:00", "%H:%M")
        end_time_str : Optional[str] = "08:00"
        end_time_dt : Optional[datetime] = datetime.strptime("08:00", "%H:%M")
        actual_str : str = "01h 00m"
        actual_td : timedelta = timedelta(hours = 1)
        expected_td : Optional[timedelta] = timedelta(hours = 1)
        expected_str : Optional[str] = "01h 00m"
        is_correct : bool = True
        message : str = "Effort matches expected."

        # Act
        actual : EffortStatus = EffortStatus(
            idx = idx,
            start_time_str = start_time_str,
            start_time_dt = start_time_dt,
            end_time_str = end_time_str,
            end_time_dt = end_time_dt,
            actual_str = actual_str,
            actual_td = actual_td,
            expected_td = expected_td,
            expected_str = expected_str,
            is_correct = is_correct,
            message = message
        )

        # Assert
        self.assertEqual(actual.idx, idx)
        self.assertEqual(actual.start_time_str, start_time_str)
        self.assertEqual(actual.start_time_dt, start_time_dt)
        self.assertEqual(actual.end_time_str, end_time_str)
        self.assertEqual(actual.end_time_dt, end_time_dt)
        self.assertEqual(actual.actual_str, actual_str)
        self.assertEqual(actual.actual_td, actual_td)
        self.assertEqual(actual.expected_td, expected_td)
        self.assertEqual(actual.expected_str, expected_str)
        self.assertEqual(actual.is_correct, is_correct)
        self.assertEqual(actual.message, message)
        self.assertIsInstance(actual.idx, int)
        self.assertIsInstance(actual.start_time_str, (str, type(None)))
        self.assertIsInstance(actual.start_time_dt, (datetime, type(None)))
        self.assertIsInstance(actual.end_time_str, (str, type(None)))
        self.assertIsInstance(actual.end_time_dt, (datetime, type(None)))
        self.assertIsInstance(actual.actual_str, str)
        self.assertIsInstance(actual.actual_td, timedelta)
        self.assertIsInstance(actual.expected_td, (timedelta, type(None)))
        self.assertIsInstance(actual.expected_str, (str, type(None)))
        self.assertIsInstance(actual.is_correct, bool)
        self.assertIsInstance(actual.message, str)
    def test_init_shouldinitializeobjectwithexpectedproperties_whenalloptionalsarenone(self) -> None:

        # Arrange
        idx : int = 1
        start_time_str : Optional[str] = None
        start_time_dt : Optional[datetime] = None
        end_time_str : Optional[str] = None
        end_time_dt : Optional[datetime] = None
        actual_str : str = "01h 00m"
        actual_td : timedelta = timedelta(hours = 1)
        expected_td : Optional[timedelta] = None
        expected_str : Optional[str] = None
        is_correct : bool = True
        message : str = "Effort recorded without expectation."

        # Act
        actual : EffortStatus = EffortStatus(
            idx = idx,
            start_time_str = start_time_str,
            start_time_dt = start_time_dt,
            end_time_str = end_time_str,
            end_time_dt = end_time_dt,
            actual_str = actual_str,
            actual_td = actual_td,
            expected_td = expected_td,
            expected_str = expected_str,
            is_correct = is_correct,
            message = message
        )

        # Assert
        self.assertEqual(actual.idx, idx)
        self.assertIsNone(actual.start_time_str)
        self.assertIsNone(actual.start_time_dt)
        self.assertIsNone(actual.end_time_str)
        self.assertIsNone(actual.end_time_dt)
        self.assertEqual(actual.actual_str, actual_str)
        self.assertEqual(actual.actual_td, actual_td)
        self.assertIsNone(actual.expected_td)
        self.assertIsNone(actual.expected_str)
        self.assertEqual(actual.is_correct, is_correct)
        self.assertEqual(actual.message, message)
class TTSummaryTestCase(unittest.TestCase):
    
    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:
        
        # Arrange
        empty_df : DataFrame = DataFrame()

        # Act
        actual = TTSummary(
            tt_df = empty_df,
            tt_latest_four_df = empty_df,
            tts_by_month_df = empty_df,
            tts_by_year_df = empty_df,
            tts_by_range_df = empty_df,
            tts_by_spn_df = empty_df,
            tts_by_spv_df = empty_df,
            tts_by_hashtag_year_df = empty_df,
            tts_by_hashtag_df = empty_df,
            tts_by_year_month_spnv_df = empty_df,
            tts_by_timeranges_df = empty_df,
            ttd_effort_status_df = empty_df,
            definitions_df = empty_df
        )

        # Assert
        self.assertEqual(actual.tt_df.shape, empty_df.shape)
        self.assertEqual(actual.tt_latest_four_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_month_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_year_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_range_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_spn_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_spv_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_hashtag_year_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_hashtag_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_year_month_spnv_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_timeranges_df.shape, empty_df.shape)
        self.assertEqual(actual.ttd_effort_status_df.shape, empty_df.shape)
        self.assertEqual(actual.definitions_df.shape, empty_df.shape)
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
        expected : list[int] = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

        # Act
        actual : list[int] = YearProvider().get_all_years()

        # Assert
        self.assertEqual(expected, actual)
    def test_getmostrecentxyears_shouldreturnlastxyears_whenxlessthantotalyears(self):

        # Arrange
        x : uint = uint(5)
        expected : list[int] = [2021, 2022, 2023, 2024, 2025]
        
        # Act
        actual : list[int] = YearProvider().get_most_recent_x_years(x)

        # Assert
        self.assertEqual(expected, actual)
    def test_getmostrecentxyears_shouldreturnallyears_whenxgreaterthantotalyears(self):

        # Arrange
        x : uint = uint(15)
        expected : list[int] = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
        
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
            "nwpackageversions",
            "nwapolloanalytics",
            "nwbuild",
            "nwrefurbishedanalytics",
            "nwknowledgebase"
        ]

        # Act
        actual : list[str] = SoftwareProjectNameProvider().get_all()

        # Assert
        self.assertEqual(expected, actual)
    def test_getlatestthree_shouldreturnexpectedlist_wheninvoked(self):

        # Arrange
        expected : list[str] = [
            "nwbuild",
            "nwrefurbishedanalytics",
            "nwknowledgebase"
        ]

        # Act
        actual : list[str] = SoftwareProjectNameProvider().get_latest_three()

        # Assert
        self.assertEqual(expected, actual)
    def test_getlatest_shouldreturnexpectedlist_wheninvoked(self):

        # Arrange
        expected : list[str] = [
            "nwknowledgebase"
        ]

        # Act
        actual : list[str] = SoftwareProjectNameProvider().get_latest()

        # Assert
        self.assertEqual(expected, actual)
class SettingBagTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:

        # Arrange
        options_tt : list[Literal[OPTION.display]] = [OPTION.display]                           # type: ignore
        options_tt_latest_four : list[Literal[OPTION.display]] = [OPTION.display]               # type: ignore
        options_tts_by_month : list[Literal[OPTION.display]] = [OPTION.display]                 # type: ignore
        options_tts_by_year : list[Literal[OPTION.display]] = [OPTION.display]                  # type: ignore
        options_tts_by_range : list[Literal[OPTION.display]] = [OPTION.display]                 # type: ignore
        options_tts_by_spn : list[Literal[OPTION.display]] = [OPTION.display]                   # type: ignore
        options_tts_by_spv : list[Literal[OPTION.display]] = [OPTION.display]                   # type: ignore
        options_tts_by_hashtag_year : list[Literal[OPTION.display]] = [OPTION.display]          # type: ignore
        options_tts_by_hashtag : list[Literal[OPTION.display]] = [OPTION.display]               # type: ignore
        options_tts_by_year_month_spnv : list[Literal[OPTION.display]] = [OPTION.display]       # type: ignore
        options_tts_by_timeranges : list[Literal[OPTION.display]] = [OPTION.display]            # type: ignore
        options_definitions : list[Literal[OPTION.display]] = [OPTION.display]                  # type: ignore
        options_report : list[Literal[OPTION.save_html, OPTION.save_pdf]] = [OPTION.save_pdf]   # type: ignore
        excel_nrows : int = 100

        options_ttd_effort_status : list[Literal[OPTION.display]] = [OPTION.display]            # type: ignore
        working_folder_path : str = "/home/nwtimetracking/"
        excel_path : str = "/workspaces/nwtimetracking/data/"
        excel_skiprows : int = 0
        excel_tabname : str = "Sessions"
        years : list[int] = [2020, 2021, 2022]
        now : datetime = datetime.now()
        enable_effort_highlighting : bool = True
        tts_by_spn_software_project_names : list[str] = ["SPN1", "SPN2"]
        tts_by_spv_software_project_names : list[str] = ["SPN3"]
        tts_by_hashtag_formatters : dict = { TTCN.EFFORTPERC : "{:.2f}" }
        tts_by_timeranges_min_occurrences : int = 10
        tts_by_timeranges_formatters : dict = { TTCN.OCCURRENCEPERC : "{:.2f}" }
        ttd_effort_status_is_correct : bool = False

		# Act
        actual : SettingBag = SettingBag(
            options_tt = options_tt,
            options_tt_latest_four = options_tt_latest_four,
            options_tts_by_month = options_tts_by_month,
            options_tts_by_year = options_tts_by_year,
            options_tts_by_range = options_tts_by_range,
            options_tts_by_spn = options_tts_by_spn,
            options_tts_by_spv = options_tts_by_spv,
            options_tts_by_hashtag_year = options_tts_by_hashtag_year,
            options_tts_by_hashtag = options_tts_by_hashtag,
            options_tts_by_year_month_spnv = options_tts_by_year_month_spnv,
            options_tts_by_timeranges = options_tts_by_timeranges,
            options_definitions = options_definitions,
            options_report = options_report,
            excel_nrows = excel_nrows,
            options_ttd_effort_status = options_ttd_effort_status,
            working_folder_path = working_folder_path,
            excel_path = excel_path,
            excel_skiprows = excel_skiprows,
            excel_tabname = excel_tabname,
            years = years,
            now = now,
            enable_effort_highlighting = enable_effort_highlighting,
            tts_by_spn_software_project_names = tts_by_spn_software_project_names,
            tts_by_spv_software_project_names = tts_by_spv_software_project_names,
            tts_by_hashtag_formatters = tts_by_hashtag_formatters,
            tts_by_timeranges_min_occurrences = tts_by_timeranges_min_occurrences,
            tts_by_timeranges_formatters = tts_by_timeranges_formatters,
            ttd_effort_status_is_correct = ttd_effort_status_is_correct
        )

		# Assert
        self.assertEqual(actual.options_tt, options_tt)
        self.assertEqual(actual.options_tt_latest_four, options_tt_latest_four)
        self.assertEqual(actual.options_tts_by_month, options_tts_by_month)
        self.assertEqual(actual.options_tts_by_year, options_tts_by_year)
        self.assertEqual(actual.options_tts_by_range, options_tts_by_range)
        self.assertEqual(actual.options_tts_by_spn, options_tts_by_spn)
        self.assertEqual(actual.options_tts_by_spv, options_tts_by_spv)
        self.assertEqual(actual.options_tts_by_hashtag_year, options_tts_by_hashtag_year)
        self.assertEqual(actual.options_tts_by_hashtag, options_tts_by_hashtag)
        self.assertEqual(actual.options_tts_by_year_month_spnv, options_tts_by_year_month_spnv)
        self.assertEqual(actual.options_tts_by_timeranges, options_tts_by_timeranges)
        self.assertEqual(actual.options_definitions, options_definitions)
        self.assertEqual(actual.options_report, options_report)
        self.assertEqual(actual.excel_nrows, excel_nrows)

        self.assertEqual(actual.options_ttd_effort_status, options_ttd_effort_status)
        self.assertEqual(actual.working_folder_path, working_folder_path)
        self.assertEqual(actual.excel_path, excel_path)
        self.assertEqual(actual.excel_skiprows, excel_skiprows)
        self.assertEqual(actual.excel_tabname, excel_tabname)
        self.assertEqual(actual.years, years)
        self.assertEqual(actual.now, now)
        self.assertEqual(actual.enable_effort_highlighting, enable_effort_highlighting)
        self.assertEqual(actual.tts_by_spn_software_project_names, tts_by_spn_software_project_names)
        self.assertEqual(actual.tts_by_spv_software_project_names, tts_by_spv_software_project_names)
        self.assertEqual(actual.tts_by_hashtag_formatters, tts_by_hashtag_formatters)
        self.assertEqual(actual.tts_by_timeranges_min_occurrences, tts_by_timeranges_min_occurrences)
        self.assertEqual(actual.tts_by_timeranges_formatters, tts_by_timeranges_formatters)
        self.assertEqual(actual.ttd_effort_status_is_correct, ttd_effort_status_is_correct)
class TTDataFrameHelperTestCase(unittest.TestCase):

    def setUp(self):

        self.df_helper = TTDataFrameHelper()
        self.sm_provider = SupportMethodProvider()

    def test_boxeffort_shouldreturnexpectedstring_whenpropertimedeltaandplussignfalse(self):    

        # Arrange
        effort_td : timedelta = pd.Timedelta(hours = 255, minutes = 30)
        expected : str = "255h 30m"

        # Act
        actual : str = self.df_helper.box_effort(effort_td = effort_td, add_plus_sign = False)
        
        # Assert
        self.assertEqual(expected, actual)
    def test_boxeffort_shouldreturnexpectedstring_whenpropertimedeltaandplussigntrue(self):    

        # Arrange
        effort_td : timedelta = pd.Timedelta(hours = 255, minutes = 30)
        expected : str = "+255h 30m"

        # Act
        actual : str = self.df_helper.box_effort(effort_td = effort_td, add_plus_sign = True)
        
        # Assert
        self.assertEqual(expected, actual)
    def test_unboxeffort_shouldreturnexpectedtimedelta_whennosingorplussign(self):

        # Arrange
        effort_str_1 : str = "5h 30m"
        effort_str_2 : str = "+5h 30m"
        expected_td : timedelta = pd.Timedelta(hours = 5, minutes = 30).to_pytimedelta()

        # Act
        actual_td_1 : timedelta = self.df_helper.unbox_effort(effort_str = effort_str_1)
        actual_td_2 : timedelta = self.df_helper.unbox_effort(effort_str = effort_str_2)

        # Assert
        self.assertEqual(expected_td, actual_td_1)
        self.assertEqual(expected_td, actual_td_2)
    def test_unboxeffort_shouldreturnexpectedtimedelta_whenminussing(self):

        # Arrange
        effort_str : str = "-5h 30m"
        expected_td : timedelta = pd.Timedelta(hours = -5, minutes = -30).to_pytimedelta()

        # Act
        actual_td : timedelta = self.df_helper.unbox_effort(effort_str = effort_str)

        # Assert
        self.assertEqual(expected_td, actual_td)

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
        actual : datetime = self.df_helper.create_time_object(time = time)

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
        actual : datetime = self.df_helper.create_time_object(time = time)

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
            self.df_helper.create_time_object(time = time)

        # Assert
        self.assertTrue(expected_message in str(context.exception))

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
        actual : EffortStatus = self.df_helper.create_effort_status(
            idx = idx, 
            start_time_str = start_time_str,
            end_time_str = end_time_str,
            effort_str = effort_str
        )

        # Assert
        comparison : bool = self.sm_provider.are_effort_statuses_equal(ef1 = expected, ef2 = actual)
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
        actual : EffortStatus = self.df_helper.create_effort_status(
            idx = idx, 
            start_time_str = start_time_str, 
            end_time_str = end_time_str, 
            effort_str = effort_str
        )

        # Assert
        comparison : bool = self.sm_provider.are_effort_statuses_equal(ef1 = expected, ef2 = actual)
        self.assertTrue(comparison) 

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
        actual_td : timedelta = self.df_helper.unbox_effort(effort_str = effort_str)
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
        actual : EffortStatus = self.df_helper.create_effort_status(
            idx = idx, 
            start_time_str = start_time_str,
            end_time_str = end_time_str,
            effort_str = effort_str)

        # Assert
        comparison : bool = self.sm_provider.are_effort_statuses_equal(ef1 = expected, ef2 = actual)
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
            self.df_helper.create_effort_status(idx = idx, start_time_str = start_time_str, end_time_str = end_time_str, effort_str = effort_str)

        # Assert
        self.assertTrue(expected_message in str(context.exception))

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
        actual : EffortStatus = self.df_helper.create_effort_status_for_none_values(idx = idx, effort_str = effort_str) # type: ignore

        # Assert
        comparison : bool = self.sm_provider.are_effort_statuses_equal(ef1 = expected, ef2 = actual)
        self.assertTrue(comparison)

    def test_createeffortstatusandcasttoany_shouldwork_withdfapply(self):

        # Arrange
        data : list[dict] = [
            {"idx": 1, "start_time_str": "07:00", "end_time_str": "08:00", "effort_str": "01h 00m"}
        ]
        df : DataFrame = pd.DataFrame(data)

        # Act
        try:

            df[TTCN.EFFORTSTATUS] = df.apply(
                lambda x : self.df_helper.create_effort_status_and_cast_to_any(
                    idx = x["idx"],
                    start_time_str = x["start_time_str"],
                    end_time_str = x["end_time_str"],
                    effort_str = x["effort_str"]
            ), axis=1)

        except Exception as e:
            self.fail(str(e))

        # Assert
        self.assertTrue(TTCN.EFFORTSTATUS in df.columns)

    def test_calculatepercentage_shouldreturnexpectedfloat_when0and16(self):

        # Arrange
        part : float = 0
        whole : float = 16
        rounding_digits : int = 2
        expected : float = 0.00
        
        # Act
        actual : float = self.df_helper.calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits)

        # Assert
        self.assertEqual(expected, actual)
    def test_calculatepercentage_shouldreturnexpectedfloat_when4and0(self):

        # Arrange
        part : float = 4
        whole : float = 0
        rounding_digits : int = 2
        expected : float = 0.00
        
        # Act
        actual : float = self.df_helper.calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits)

        # Assert
        self.assertEqual(expected, actual)        
    def test_calculatepercentage_shouldreturnexpectedfloat_when4and16(self):

        # Arrange
        part : float = 4
        whole : float = 16
        rounding_digits : int = 2
        expected : float = 25.00
        
        # Act
        actual : float = self.df_helper.calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits)

        # Assert
        self.assertEqual(expected, actual)
    def test_calculatepercentage_shouldreturnexpectedfloat_when16and16(self):

        # Arrange
        part : float = 16
        whole : float = 16
        rounding_digits : int = 2
        expected : float = 100.00
        
        # Act
        actual : float = self.df_helper.calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits)

        # Assert
        self.assertEqual(expected, actual)        
    def test_calculatepercentage_shouldreturnexpectedfloat_when3and9and4(self):

        # Arrange
        part : float = 3
        whole : float = 9
        rounding_digits : int = 4
        expected : float = 33.3333
        
        # Act
        actual : float = self.df_helper.calculate_percentage(part = part, whole = whole, rounding_digits = rounding_digits)

        # Assert
        self.assertEqual(expected, actual)

    def test_extractsoftwareprojectname_shouldreturnexpectedstring_whenproperstring(self):

        # Arrange
        descriptor : str = "NW.AutoProffLibrary v1.0.0"
        expected : str = "NW.AutoProffLibrary"

        # Act
        actual : str = self.df_helper.extract_software_project_name(descriptor = descriptor)

        # Assert
        self.assertEqual(expected, actual)
    def test_extractsoftwareprojectname_shouldreturnerrorstring_whenunproperstring(self):

        # Arrange
        descriptor : str = "Some gibberish"
        expected : str = "ERROR"

        # Act
        actual : str = self.df_helper.extract_software_project_name(descriptor = descriptor)

        # Assert
        self.assertEqual(expected, actual)   
    def test_extractsoftwareprojectversion_shouldreturnexpectedstring_whenproperstring(self):

        # Arrange
        descriptor : str = "NW.AutoProffLibrary v1.0.0"
        expected : str = "1.0.0"

        # Act
        actual : str = self.df_helper.extract_software_project_version(descriptor = descriptor)

        # Assert
        self.assertEqual(expected, actual)
    def test_extractsoftwareprojectversion_shouldreturnerrorstring_whenunproperstring(self):

        # Arrange
        descriptor : str = "Some gibberish"
        expected : str = "ERROR"

        # Act
        actual : str = self.df_helper.extract_software_project_version(descriptor = descriptor)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["07:00", "08:00", "07:00-08:00"],
        ["", "08:00", "Unknown"],
        ["07:00", "", "Unknown"]
    ])
    def test_createtimerangeid_shouldreturnexpectedtimerangeid_wheninvoked(self, start_time : str, end_time : str, expected : str):

        # Arrange
        # Act
        actual : str = self.df_helper.create_time_range_id(start_time = start_time, end_time = end_time)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        (2024, True),
        (1000, True),
        (9999, True),
        (999, False),
        (10000, False),
        ("year", False)
    ])
    def test_isyear_shouldreturnexpectedbool_wheninvoked(self, value : Any, expected : bool) -> None:
        
        # Arrange
        # Act
        actual : bool = self.df_helper.is_year(value = value)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        (2, True),
        (0, True),
        (-4, True),
        (3, False),
        (-5, False),
    ])
    def test_iseven_shouldreturnexpectedbool_wheninvoked(self, number : int, expected : bool) -> None:
        
        # Arrange
        # Act
        actual : bool = self.df_helper.is_even(number = number)

        # Assert
        self.assertEqual(expected, actual)
class TTDataFrameFactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.df_factory : TTDataFrameFactory = TTDataFrameFactory(df_helper = TTDataFrameHelper())
    
    def test_createttdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        excel_path : str = "/workspaces/nwtimetracking/"
        excel_skiprows : int = 0
        excel_nrows : int = 100
        excel_tabname : str = "Sessions"        
        excel_data_df : DataFrame = ObjectMother().get_excel_data()
        expected_column_names : list[str] = ObjectMother().get_tt_df_column_names()
        expected_dtype_names : list[str] = ObjectMother().get_tt_df_dtype_names()
        expected_nan : str = ""

        # Act
        with patch.object(pd, 'read_excel', return_value = excel_data_df) as mocked_context:
            actual : DataFrame = self.df_factory.create_tt_df(
                excel_path = excel_path,
                excel_skiprows = excel_skiprows,
                excel_nrows = excel_nrows,
                excel_tabname = excel_tabname
            )

        # Assert
        self.assertEqual(expected_column_names, actual.columns.tolist())
        self.assertEqual(expected_dtype_names, SupportMethodProvider().get_dtype_names(df = actual))
        self.assertEqual(expected_nan, actual[expected_column_names[1]][0])
        self.assertEqual(expected_nan, actual[expected_column_names[2]][0])
        self.assertEqual(expected_nan, actual[expected_column_names[5]][0])    
    def test_createttlatestfourdf_shouldreturnexpecteddataframe_wheninvoked(self): 
        
        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = tt_df[-4:]

        # Act
        actual_df : DataFrame  = self.df_factory.create_tt_latest_four_df(tt_df = tt_df)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbymonthtpl_shouldreturnexpecteddataframe_wheninvoked(self): 
        
        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_month_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_month_df(tt_df = tt_df, now = datetime(2024, 12, 1))

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbyyeardf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_year_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_year_df(tt_df = tt_df)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbyrangedf_shouldreturnexpecteddataframe_wheninvoked(self): 
        
        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_range_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_range_df(tt_df = tt_df)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbyspndf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        software_project_names : list[str] = ["NW.Shared.Serialization", "nwreadinglistmanager", "NW.NGramTextClassification", "NW.UnivariateForecasting"]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_spn_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_spn_df(
            tt_df = tt_df, 
            software_project_names = software_project_names
        )

        # Assert
        assert_frame_equal(expected_df , actual_df) 
    def test_createttsbyspvdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_spv_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_spv_df(
            tt_df = tt_df, 
            software_project_names = software_project_names
        )

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbyhashtagyeardf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_hashtag_year_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_hashtag_year_df(
            tt_df = tt_df
        )

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbyhashtagdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_hashtag_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_hashtag_df(tt_df = tt_df)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbyyearmonthspnvdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected : DataFrame = ObjectMother().get_tts_by_year_month_spnv_df()

        # Act
        actual : DataFrame = self.df_factory.create_tts_by_year_month_spnv_df(
            tt_df = tt_df,
            software_project_names = software_project_names
        )

        # Assert
        assert_frame_equal(expected, actual)
    def test_createttsbytimerangesdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        min_occurrences : int = 1
        tt_df : DataFrame = ObjectMother().get_tt_df()

        expected_df : DataFrame = ObjectMother().get_tts_by_timeranges_df()
        expected_df.sort_values(by = TTCN.TIMERANGES, ascending = True, inplace = True)
        expected_df.reset_index(drop = True, inplace = True)

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_timeranges_df(
            tt_df = tt_df, 
            min_occurrences = min_occurrences
        )
        actual_df.sort_values(by = TTCN.TIMERANGES, ascending = True, inplace = True)
        actual_df.reset_index(drop = True, inplace = True)

        # Assert
        assert_frame_equal(expected_df, actual_df)
    
    @parameterized.expand([
        [True],
        [False]
    ])    
    def test_createttdeffortstatusdf_shouldreturnexpecteddataframe_wheninvoked(self, is_correct : bool): 
        
        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()[-1:]
        expected_df : DataFrame = ObjectMother().get_ttd_effort_status_df(is_correct = is_correct)

        # Act
        actual_df : DataFrame  = self.df_factory.create_ttd_effort_status_df(tt_df = tt_df, is_correct = is_correct)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    
    def test_createdefinitionsdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        expected_df : DataFrame = ObjectMother().get_definitions_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_definitions_df()

        # Assert
        assert_frame_equal(expected_df , actual_df)
class EffortCellTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_whenvalidarguments(self) -> None:

        # Arrange
        coordinate_pair : Tuple[int, int] = (5, 10)
        effort_str : str = "10h 00m"
        effort_td : timedelta = timedelta(hours = 10)

        # Act
        effort_cell : EffortCell = EffortCell(
            coordinate_pair = coordinate_pair,
            effort_str = effort_str,
            effort_td = effort_td
        )

        # Assert
        self.assertEqual(effort_cell.coordinate_pair, coordinate_pair)
        self.assertEqual(effort_cell.effort_str, effort_str)
        self.assertEqual(effort_cell.effort_td, effort_td)
class EffortHighlighterTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.effort_highlighter : EffortHighlighter = EffortHighlighter(df_helper = TTDataFrameHelper())

        data : dict[str, list] = {
            "Month": ["1", "2"],
            "2015": ["00h 00m", "00h 00m"],
            "↕": ["↑", "↑"],
            "2016": ["18h 00m", "45h 30m"],
            "↕_duplicate_1": ["↑", "↑"],
            "2017": ["88h 30m", "65h 30m"]
        }
        columns_01 : list[str] = ["Month", "2015", "↕", "2016", "↕", "2017"]
        self.df_with_duplicates : DataFrame = DataFrame(data, columns = columns_01)

        columns_02 : list[str] = ["Month", "2015", "↕", "2016", "↕_duplicate_1", "2017"]
        self.df_without_duplicates : DataFrame = DataFrame(data, columns = columns_02)

    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:

        # Arrange
        df_helper : TTDataFrameHelper = TTDataFrameHelper()

        # Act
        actual : EffortHighlighter = EffortHighlighter(df_helper = df_helper)

        # Assert
        self.assertIsInstance(actual, EffortHighlighter)

    @parameterized.expand([
        ("00h 00m", True),
        ("10h 45m", True),
        ("101h 30m", True),
        ("+71h 00m", True),
		("+159h 00m", True),
        ("-79h 30m", True),
        ("-455h 45m", True),
        ("invalid", False),
        ("10h 60m", False),
        ("h 30m", False),
        ("-10h m", False),
        ("+h m", False)
    ])
    def test_iseffort_shouldreturnexpectedresult_wheninvoked(self, effort: str, expected: bool) -> None:
        
        # Arrange
        # Act
        actual : bool = self.effort_highlighter._EffortHighlighter__is_effort(cell_content = effort)    # type: ignore

        # Assert
        self.assertEqual(actual, expected)

    def test_appendneweffortcell_shouldappendprovidedcell_wheninvoked(self) -> None:
        
        # Arrange
        effort_cells : list[EffortCell] = []
        coordinate_pair : Tuple[int, int] = (0, 1)
        cell_content : str = "5h 30m"
        effort_td : timedelta = timedelta(hours = 5, minutes = 30)

        # Act
        self.effort_highlighter._EffortHighlighter__append_new_effort_cell(effort_cells, coordinate_pair, cell_content) # type: ignore

        # Assert
        self.assertEqual(len(effort_cells), 1)
        self.assertEqual(effort_cells[0].coordinate_pair, coordinate_pair)
        self.assertEqual(effort_cells[0].effort_str, cell_content)
        self.assertEqual(effort_cells[0].effort_td, effort_td)
    def test_extractrow_shouldreturneffortcells_whenrowhasvalidtimes(self) -> None:
        
        # Arrange
        df : DataFrame = DataFrame({"2015": ["10h 30m"], "↕": ["↑"], "2016": ["20h 45m"]})
        column_names : list[str] = ["2015", "2016"]

        # Act
        actual : list[EffortCell] = self.effort_highlighter._EffortHighlighter__extract_row(df = df, row_idx = 0, column_names = column_names)   # type: ignore

        # Assert
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].effort_str, "10h 30m")
        self.assertEqual(actual[1].effort_str, "20h 45m")

    @parameterized.expand([
        (EFFORTMODE.top_one_effort_per_row, 1),
        (EFFORTMODE.top_three_efforts, 3)
    ])
    def test_extractn_shouldreturnexpected_whenvalid(self, mode: EFFORTMODE, expected: int) -> None:
        
        # Arrange
        # Act
        actual : int = self.effort_highlighter._EffortHighlighter__extract_n(mode = mode)   # type: ignore

        # Assert
        self.assertEqual(actual, expected)

    def test_extractn_shouldraiseexception_wheninvalid(self) -> None:
        
        # Arrange
        mode : EFFORTMODE = cast(EFFORTMODE, "Invalid")

        # Act & Assert
        with self.assertRaises(Exception):
            self.effort_highlighter._EffortHighlighter__extract_n(mode = mode)   # type: ignore
    def test_extracttopneffortcells_shouldreturntopncells_wheninvoked(self) -> None:

        # Arrange
        effort_cells : list[EffortCell] = [
            EffortCell(coordinate_pair = (0, 0), effort_str = "10h 00m", effort_td = timedelta(hours = 10)),
            EffortCell(coordinate_pair = (0, 1), effort_str = "5h 30m", effort_td = timedelta(hours = 5, minutes = 30)),
            EffortCell(coordinate_pair = (0, 2), effort_str = "20h 45m", effort_td = timedelta(hours = 20, minutes = 45))
        ]

        # Act
        actual : list[EffortCell] = self.effort_highlighter._EffortHighlighter__extract_top_n_effort_cells(effort_cells = effort_cells, n = 2)   # type: ignore

        # Assert
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].effort_str, "20h 45m")
        self.assertEqual(actual[1].effort_str, "10h 00m")
    def test_calculateeffortcells_shouldreturnexpectedcells_whentoponeeffortperrow(self) -> None:
        
        # Arrange
        df : DataFrame = DataFrame({"2015": ["10h 30m", "15h 45m"], "↕": ["↑", "↑"], "2016": ["20h 45m", "20h 00m"]})
        mode : EFFORTMODE = EFFORTMODE.top_one_effort_per_row
        column_names : list[str] = ["2015", "2016"]

        # Act
        actual : list[EffortCell] = self.effort_highlighter._EffortHighlighter__calculate_effort_cells(df = df, mode = mode, column_names = column_names)   # type: ignore

        # Assert
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].effort_str, "20h 45m")
        self.assertEqual(actual[1].effort_str, "20h 00m")
    def test_calculateeffortcells_shouldreturnexpectedcells_whentopthreeefforts(self) -> None:
        
        # Arrange
        df : DataFrame = DataFrame({"2015": ["10h 30m", "15h 45m"], "↕": ["↑", "↑"], "2016": ["20h 45m", "20h 00m"]})
        mode : EFFORTMODE = EFFORTMODE.top_three_efforts
        column_names : list[str] = ["2015", "2016"]

        # Act
        actual : list[EffortCell] = self.effort_highlighter._EffortHighlighter__calculate_effort_cells(df = df, mode = mode, column_names = column_names)   # type: ignore

        # Assert
        self.assertEqual(len(actual), 3)
        self.assertEqual(actual[0].effort_str, "20h 45m")
        self.assertEqual(actual[1].effort_str, "20h 00m")
        self.assertEqual(actual[2].effort_str, "15h 45m")
    def test_calculateeffortcells_shouldraiseexception_wheninvalidmode(self) -> None:

        # Arrange
        df : DataFrame = DataFrame({"2015": ["10h 30m", "15h 45m"], "↕": ["↑", "↑"], "2016": ["20h 45m", "20h 00m"]})
        mode : EFFORTMODE = cast(EFFORTMODE, "Invalid")
        column_names : list[str] = ["2015", "2016"]

        expected : str = _MessageCollection.provided_mode_not_supported(mode)
        
        # Act
        with self.assertRaises(Exception) as context:
            self.effort_highlighter._EffortHighlighter__calculate_effort_cells(df = df, mode = mode, column_names = column_names)   # type: ignore

        # Assert
        self.assertEqual(expected, str(context.exception))
    def test_addtags_shouldsurroundeffortcellsswithtokens_wheninvoked(self) -> None:

        # Arrange
        effort_cells : list[EffortCell] = [
            EffortCell((0, 1), "00h 00m", timedelta(hours = 0, minutes = 0)),
            EffortCell((1, 3), "45h 30m", timedelta(hours = 45, minutes = 30))
        ]
        tags : Tuple[str, str] = ("[[ ", " ]]")
        expected : DataFrame = self.df_without_duplicates.copy(deep = True)
        expected.iloc[0, 1] = "[[ 00h 00m ]]"
        expected.iloc[1, 3] = "[[ 45h 30m ]]"

        # Act
        actual : DataFrame = self.effort_highlighter._EffortHighlighter__add_tags(self.df_without_duplicates, effort_cells, tags)   # type: ignore

        # Assert
        self.assertTrue(expected.equals(actual))
    def test_highlightdataframe_shouldhighlightexpectedcells_whencolumnnamesareprovided(self) -> None:

        # Arrange
        mode : EFFORTMODE = EFFORTMODE.top_one_effort_per_row
        column_names : list[str] = ["2015", "2016", "2017"]

        expected : DataFrame = self.df_without_duplicates.copy(deep = True)
        expected.iloc[0, 5] = "<mark style='background-color: pink'>88h 30m</mark>"
        expected.iloc[1, 5] = "<mark style='background-color: pink'>65h 30m</mark>"

        # Act
        actual : DataFrame = self.effort_highlighter._EffortHighlighter__highlight_dataframe(self.df_without_duplicates, mode, column_names) # type: ignore

        # Assert
        assert_frame_equal(expected, actual)
    def test_highlightdataframe_shouldhighlightexpectedcells_whencolumnnamesarenotprovided(self) -> None:

        # Arrange
        mode : EFFORTMODE = EFFORTMODE.top_one_effort_per_row
        column_names : list[str] = []

        expected : DataFrame = self.df_without_duplicates.copy(deep = True)
        expected.iloc[0, 5] = "<mark style='background-color: pink'>88h 30m</mark>"
        expected.iloc[1, 5] = "<mark style='background-color: pink'>65h 30m</mark>"

        # Act
        actual : DataFrame = self.effort_highlighter._EffortHighlighter__highlight_dataframe(self.df_without_duplicates, mode, column_names) # type: ignore

        # Assert
        assert_frame_equal(expected, actual)
    def test_getlatestyear_shouldreturnexpectedstring_whencolumnnamesarestring(self) -> None:
        
        # Arrange
        data : dict = {
            TTCN.HASHTAG : ["#python", "#studying"],
            "2022" : ["06h 15m", "23h 15m"],
            "2023" : ["06h 15m", "23h 15m"],
            "2024" : ["06h 15m", "23h 15m"],
            "2025" : ["06h 15m", "23h 15m"]
        }
        tts_by_hashtag_year_df : DataFrame = DataFrame(data)
        expected : str = "2025"

        # Act
        actual : str = self.effort_highlighter._EffortHighlighter__get_latest_year(tts_by_hashtag_year_df) # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_getlatestyear_shouldreturnexpectedstring_whencolumnnamesarenotstring(self) -> None:
        
        # Arrange
        data : dict = {
            TTCN.HASHTAG : ["#python", "#studying"],
            2022 : ["06h 15m", "23h 15m"],
            2023 : ["06h 15m", "23h 15m"],
            2024 : ["06h 15m", "23h 15m"],
            2025 : ["06h 15m", "23h 15m"]
        }
        tts_by_hashtag_year_df : DataFrame = DataFrame(data)
        expected : str = "2025"

        # Act
        actual : str = self.effort_highlighter._EffortHighlighter__get_latest_year(tts_by_hashtag_year_df) # type: ignore

        # Assert
        self.assertEqual(expected, actual)

    def test_highlightttsbymonth_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        tts_by_month_df : DataFrame = DataFrame()

        highlighted_df : Mock = Mock()
        self.effort_highlighter._EffortHighlighter__highlight_dataframe = highlighted_df  # type: ignore

        # Act
        self.effort_highlighter.highlight_tts_by_month(tts_by_month_df = tts_by_month_df)

        # Assert
        highlighted_df.assert_called_once_with(
            df = tts_by_month_df,
            mode = EFFORTMODE.top_three_efforts
        )
    def test_highlightttsbyyear_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        tts_by_year_df : DataFrame = DataFrame()

        highlighted_df : Mock = Mock()
        self.effort_highlighter._EffortHighlighter__highlight_dataframe = highlighted_df  # type: ignore

        # Act
        self.effort_highlighter.highlight_tts_by_year(tts_by_year_df = tts_by_year_df)

        # Assert
        highlighted_df.assert_called_once_with(
            df = tts_by_year_df,
            mode = EFFORTMODE.top_three_efforts
        )
    def test_highlightttsbyhashtagyear_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        tts_by_hashtag_year_df : DataFrame = DataFrame()
        latest_year : str = "2025"

        get_latest_year_mock : Mock = Mock(return_value = latest_year)
        highlighted_df : Mock = Mock()

        self.effort_highlighter._EffortHighlighter__get_latest_year = get_latest_year_mock  # type: ignore
        self.effort_highlighter._EffortHighlighter__highlight_dataframe = highlighted_df    # type: ignore

        # Act
        self.effort_highlighter.highlight_tts_by_hashtag_year(tts_by_hashtag_year_df = tts_by_hashtag_year_df)

        # Assert
        get_latest_year_mock.assert_called_once_with(tts_by_hashtag_year_df)
        highlighted_df.assert_called_once_with(
            df = tts_by_hashtag_year_df,
            mode = EFFORTMODE.top_three_efforts,
            column_names = [latest_year]
        )
    def test_highlightttsbyhashtag_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        tts_by_hashtag_df : DataFrame = DataFrame()

        highlighted_df : Mock = Mock()
        self.effort_highlighter._EffortHighlighter__highlight_dataframe = highlighted_df  # type: ignore

        # Act
        self.effort_highlighter.highlight_tts_by_hashtag(tts_by_hashtag_df = tts_by_hashtag_df)

        # Assert
        highlighted_df.assert_called_once_with(
            df = tts_by_hashtag_df,
            mode = EFFORTMODE.top_three_efforts
        )
    def test_highlightttsbyyearmonthspnv_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        tts_by_year_month_spnv_df : DataFrame = DataFrame()

        highlighted_df : Mock = Mock()
        self.effort_highlighter._EffortHighlighter__highlight_dataframe = highlighted_df  # type: ignore

        # Act
        self.effort_highlighter.highlight_tts_by_year_month_spnv(tts_by_year_month_spnv_df = tts_by_year_month_spnv_df)

        # Assert
        highlighted_df.assert_called_once_with(
            df = tts_by_year_month_spnv_df,
            mode = EFFORTMODE.top_three_efforts
        )
class TTAdapterTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.mocked_df_factory : Mock = Mock(spec = TTDataFrameFactory)
        self.mocked_effort_highlighter : Mock = Mock(spec = EffortHighlighter)

        self.adapter : TTAdapter = TTAdapter(
            df_factory = self.mocked_df_factory,  # type: ignore
            effort_highlighter = self.mocked_effort_highlighter  # type: ignore
        )

        self.tt_df : DataFrame = DataFrame()
        self.setting_bag : SettingBag = SettingBag(
            options_tt = [OPTION.display],
            options_tt_latest_four = [OPTION.display],
            options_tts_by_month = [OPTION.display],
            options_tts_by_year = [OPTION.display],
            options_tts_by_range = [OPTION.display],
            options_tts_by_spn = [OPTION.display],
            options_tts_by_spv = [OPTION.display],
            options_tts_by_hashtag_year = [OPTION.display],
            options_tts_by_hashtag = [OPTION.display],
            options_tts_by_year_month_spnv = [OPTION.display],
            options_tts_by_timeranges = [OPTION.display],
            options_definitions = [OPTION.display],
            options_report = [OPTION.save_html],
            excel_nrows = 10,
            now = datetime(year = 2025, month = 12, day = 22)
        )
    def test_createttdf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tt_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tt_df(setting_bag = self.setting_bag)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tt_df.assert_called_once_with(
            excel_path = self.setting_bag.excel_path,
            excel_skiprows = self.setting_bag.excel_skiprows,
            excel_nrows = self.setting_bag.excel_nrows,
            excel_tabname = self.setting_bag.excel_tabname
        )
    def test_createttlatestfourdf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tt_latest_four_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tt_latest_four_df(tt_df = self.tt_df)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tt_latest_four_df.assert_called_once_with(tt_df = self.tt_df)
    def test_createttsbymonthdf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_month_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_month_df(tt_df = self.tt_df, setting_bag = self.setting_bag)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_month_df.assert_called_once_with(
            tt_df = self.tt_df,
            now = self.setting_bag.now
        )
    def test_createttsbyyeardf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_year_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_year_df(tt_df = self.tt_df)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_year_df.assert_called_once_with(tt_df = self.tt_df)
    def test_createttsbyrangedf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_range_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_range_df(tt_df = self.tt_df)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_range_df.assert_called_once_with(tt_df = self.tt_df)
    def test_createttsbyspndf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_spn_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_spn_df(tt_df = self.tt_df, setting_bag = self.setting_bag)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_spn_df.assert_called_once_with(
            tt_df = self.tt_df,
            software_project_names = self.setting_bag.tts_by_spn_software_project_names
        )
    def test_createttsbyspvdf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_spv_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_spv_df(tt_df = self.tt_df, setting_bag = self.setting_bag)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_spv_df.assert_called_once_with(
            tt_df = self.tt_df,
            software_project_names = self.setting_bag.tts_by_spv_software_project_names
        )
    def test_createttsbyhashtagyeardf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_hashtag_year_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_hashtag_year_df(tt_df = self.tt_df)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_hashtag_year_df.assert_called_once_with(tt_df = self.tt_df)
    def test_createttsbyhashtagdf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_hashtag_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_hashtag_df(tt_df = self.tt_df)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_hashtag_df.assert_called_once_with(tt_df = self.tt_df)
    def test_createttsbyyearmonthspnvdf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_year_month_spnv_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_year_month_spnv_df(tt_df = self.tt_df, setting_bag = self.setting_bag)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_year_month_spnv_df.assert_called_once_with(
            tt_df = self.tt_df,
            software_project_names = self.setting_bag.tts_by_spv_software_project_names
        )
    def test_createttsbytimerangesdf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_tts_by_timeranges_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_tts_by_timeranges_df(tt_df = self.tt_df, setting_bag = self.setting_bag)  # type: ignore

        # Assert
        self.mocked_df_factory.create_tts_by_timeranges_df.assert_called_once_with(
            tt_df = self.tt_df,
            min_occurrences = self.setting_bag.tts_by_timeranges_min_occurrences
        )
    def test_createttdeffortstatusdf_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        self.mocked_df_factory.create_ttd_effort_status_df = Mock(return_value = DataFrame())

        # Act
        self.adapter._TTAdapter__create_ttd_effort_status_df(tt_df = self.tt_df, setting_bag = self.setting_bag)  # type: ignore

        # Assert
        self.mocked_df_factory.create_ttd_effort_status_df.assert_called_once_with(
            tt_df = self.tt_df,
            is_correct = self.setting_bag.ttd_effort_status_is_correct
        )
    def test_createsummary_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        tt_df : DataFrame = DataFrame()
        tt_latest_four_df : DataFrame = DataFrame()
        tts_by_month_df : DataFrame = DataFrame()
        tts_by_year_df : DataFrame = DataFrame()
        tts_by_range_df : DataFrame = DataFrame()
        tts_by_spn_df : DataFrame = DataFrame()
        tts_by_spv_df : DataFrame = DataFrame()
        tts_by_hashtag_year_df : DataFrame = DataFrame()
        tts_by_hashtag_df : DataFrame = DataFrame()
        tts_by_year_month_spnv_df : DataFrame = DataFrame()
        tts_by_timeranges_df : DataFrame = DataFrame()
        ttd_effort_status_df : DataFrame = DataFrame()
        definitions_df : DataFrame = DataFrame()

        with (
            patch.object(self.adapter, "_TTAdapter__create_tt_df", return_value = tt_df) as mocked_create_tt_df,
            patch.object(self.adapter, "_TTAdapter__create_tt_latest_four_df", return_value = tt_latest_four_df) as mocked_create_tt_latest_four_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_month_df", return_value = tts_by_month_df) as mocked_create_tts_by_month_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_year_df", return_value = tts_by_year_df) as mocked_create_tts_by_year_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_range_df", return_value = tts_by_range_df) as mocked_create_tts_by_range_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_spn_df", return_value = tts_by_spn_df) as mocked_create_tts_by_spn_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_spv_df", return_value = tts_by_spv_df) as mocked_create_tts_by_spv_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_hashtag_year_df", return_value = tts_by_hashtag_year_df) as mocked_create_tts_by_hashtag_year_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_hashtag_df", return_value = tts_by_hashtag_df) as mocked_create_tts_by_hashtag_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_year_month_spnv_df", return_value = tts_by_year_month_spnv_df) as mocked_create_tts_by_year_month_spnv_df,
            patch.object(self.adapter, "_TTAdapter__create_tts_by_timeranges_df", return_value = tts_by_timeranges_df) as mocked_create_tts_by_timeranges_df,
            patch.object(self.adapter, "_TTAdapter__create_ttd_effort_status_df", return_value = ttd_effort_status_df) as mocked_create_ttd_effort_status_df,
            patch.object(self.mocked_df_factory, "create_definitions_df", return_value = definitions_df) as mocked_create_definitions_df
        ):

            self.mocked_effort_highlighter.highlight_tts_by_month = Mock(return_value = tts_by_month_df)
            self.mocked_effort_highlighter.highlight_tts_by_year = Mock(return_value = tts_by_year_df)
            self.mocked_effort_highlighter.highlight_tts_by_hashtag_year = Mock(return_value = tts_by_hashtag_year_df)
            self.mocked_effort_highlighter.highlight_tts_by_hashtag = Mock(return_value = tts_by_hashtag_df)
            self.mocked_effort_highlighter.highlight_tts_by_year_month_spnv = Mock(return_value = tts_by_year_month_spnv_df)

            # Act
            self.adapter.create_summary(setting_bag = self.setting_bag)

            # Assert
            mocked_create_tt_df.assert_called_once_with(setting_bag = self.setting_bag)
            mocked_create_tt_latest_four_df.assert_called_once_with(tt_df = tt_df)
            mocked_create_tts_by_month_df.assert_called_once_with(tt_df = tt_df, setting_bag = self.setting_bag)
            mocked_create_tts_by_year_df.assert_called_once_with(tt_df = tt_df)
            mocked_create_tts_by_range_df.assert_called_once_with(tt_df = tt_df)
            mocked_create_tts_by_spn_df.assert_called_once_with(tt_df = tt_df, setting_bag = self.setting_bag)
            mocked_create_tts_by_spv_df.assert_called_once_with(tt_df = tt_df, setting_bag = self.setting_bag)
            mocked_create_tts_by_hashtag_year_df.assert_called_once_with(tt_df = tt_df)
            mocked_create_tts_by_hashtag_df.assert_called_once_with(tt_df = tt_df)
            mocked_create_tts_by_year_month_spnv_df.assert_called_once_with(tt_df = tt_df, setting_bag = self.setting_bag)
            mocked_create_tts_by_timeranges_df.assert_called_once_with(tt_df = tt_df, setting_bag = self.setting_bag)
            mocked_create_ttd_effort_status_df.assert_called_once_with(tt_df = tt_df, setting_bag = self.setting_bag)

            mocked_create_definitions_df.assert_called_once_with()

            self.mocked_effort_highlighter.highlight_tts_by_month.assert_called_once_with(tts_by_month_df = tts_by_month_df)
            self.mocked_effort_highlighter.highlight_tts_by_year.assert_called_once_with(tts_by_year_df = tts_by_year_df)
            self.mocked_effort_highlighter.highlight_tts_by_hashtag_year.assert_called_once_with(tts_by_hashtag_year_df = tts_by_hashtag_year_df)
            self.mocked_effort_highlighter.highlight_tts_by_hashtag.assert_called_once_with(tts_by_hashtag_df = tts_by_hashtag_df)
            self.mocked_effort_highlighter.highlight_tts_by_year_month_spnv.assert_called_once_with(tts_by_year_month_spnv_df = tts_by_year_month_spnv_df)
class TTReportManagerTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.report_manager : TTReportManager = TTReportManager()
        self.report_module : Any = importlib.import_module(TTReportManager.__module__)

        empty_df : DataFrame = DataFrame()
        self.tt_summary : TTSummary = TTSummary(
            tt_df = empty_df,
            tt_latest_four_df = empty_df,
            tts_by_month_df = empty_df,
            tts_by_year_df = empty_df,
            tts_by_range_df = empty_df,
            tts_by_spn_df = empty_df,
            tts_by_spv_df = empty_df,
            tts_by_hashtag_year_df = empty_df,
            tts_by_hashtag_df = empty_df,
            tts_by_year_month_spnv_df = empty_df,
            tts_by_timeranges_df = empty_df,
            ttd_effort_status_df = empty_df,
            definitions_df = empty_df
        )
    def test_formatforfilename_shouldreturnexpectedstring_wheninvoked(self) -> None:

        # Arrange
        last_update : datetime = datetime(year = 2025, month = 12, day = 22, hour = 15, minute = 30, second = 45)
        expected : str = "20251222"

        # Act
        actual : str = self.report_manager._TTReportManager__format_for_file_name(last_update = last_update)  # type: ignore

        # Assert
        self.assertEqual(actual, expected)
    def test_formatfortitle_shouldreturnexpectedstring_wheninvoked(self) -> None:

        # Arrange
        last_update : datetime = datetime(year = 2025, month = 12, day = 22, hour = 15, minute = 30, second = 45)
        expected : str = "2025-12-22"

        # Act
        actual : str = self.report_manager._TTReportManager__format_for_title(last_update = last_update)  # type: ignore

        # Assert
        self.assertEqual(actual, expected)
    def test_createreportfilepaths_shouldreturnexpectedpaths_wheninvoked(self) -> None:

        # Arrange
        folder_path : str = "/home/nwreadinglist"
        last_update : datetime = datetime(year = 2025, month = 12, day = 22)
        expected_html_path : Path = Path("/home/nwreadinglist") / "TIMETRACKINGREPORT20251222.html"
        expected_pdf_path : Path = Path("/home/nwreadinglist") / "TIMETRACKINGREPORT20251222.pdf"

        # Act
        actual : Tuple[Path, Path] = self.report_manager._TTReportManager__create_report_file_paths(folder_path = folder_path,last_update = last_update)  # type: ignore
        actual_html_path : Path = actual[0]
        actual_pdf_path : Path = actual[1]

        # Assert
        self.assertEqual(actual_html_path, expected_html_path)
        self.assertEqual(actual_pdf_path, expected_pdf_path)
    def test_createhtml_shouldcontainexpectedhtmlexcerpts_whenfooterisnotprovided(self) -> None:

        # Arrange
        df : DataFrame = DataFrame(data = {"A": [1.234]})
        title : str = "Some Title"
        formatters : Optional[dict] = {"A": "{:.2f}"}

        # Act
        actual : str = self.report_manager._TTReportManager__create_html(df = df, title = title, formatters = formatters)  # type: ignore

        # Assert
        self.assertIn("<div style='margin-bottom: 20px;'>", actual)
        self.assertIn(f"<h2>{title}</h2>", actual)
        self.assertIn("</div>", actual)
        self.assertIn(">1.23<", actual)
        self.assertIn("background-color: #eeeeee", actual)
        self.assertIn("white-space: nowrap", actual)
        self.assertIn("border-collapse: collapse", actual)
        self.assertNotIn("margin-top: 6px", actual)
    def test_createhtml_shouldcontainexpectedhtmlexcerpts_whenfooterisprovided(self) -> None:

        # Arrange
        df : DataFrame = DataFrame(data = {"A": [1.234]})
        title : str = "Some Title"
        formatters : Optional[dict] = {"A": "{:.2f}"}
        footer : Optional[str] = "Some Footer"

        # Act
        actual : str = self.report_manager._TTReportManager__create_html(df = df, title = title, formatters = formatters, footer = footer)  # type: ignore

        # Assert
        self.assertIn(f"{footer}", actual)
        self.assertIn("margin-top: 6px", actual)
        self.assertIn("<br/><div", actual)
    def test_createhtmlsections_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        formatters : Optional[dict] = None

        expected_call_00 : _Call = call(self.tt_summary.tt_latest_four_df, REPORTSTR.TTLATESTFIVE, formatters)
        expected_call_01 : _Call = call(self.tt_summary.tts_by_month_df, REPORTSTR.TTSBYMONTH, formatters)
        expected_call_02 : _Call = call(self.tt_summary.tts_by_year_df, REPORTSTR.TTSBYYEAR, formatters)
        expected_call_03 : _Call = call(self.tt_summary.tts_by_range_df, REPORTSTR.TTSBYRANGE, formatters)
        expected_call_04 : _Call = call(self.tt_summary.tts_by_spn_df, REPORTSTR.TTSBYSPN, formatters)
        expected_call_05 : _Call = call(self.tt_summary.tts_by_spv_df, REPORTSTR.TTSBYSPV, formatters)
        expected_call_06 : _Call = call(self.tt_summary.tts_by_hashtag_year_df, REPORTSTR.TTSBYHASHTAGYEAR, formatters)
        expected_call_07 : _Call = call(self.tt_summary.tts_by_hashtag_df, REPORTSTR.TTSBYHASHTAG, formatters)
        expected_call_08 : _Call = call(self.tt_summary.tts_by_year_month_spnv_df, REPORTSTR.TTSBYYEARMONTHSPNV, formatters)
        expected_call_09 : _Call = call(self.tt_summary.tts_by_timeranges_df, REPORTSTR.TTSBYTIMERANGES, formatters)
        expected_call_10 : _Call = call(self.tt_summary.definitions_df, REPORTSTR.DEFINITIONS, formatters)
        expected_calls : int = 11

        with patch.object(self.report_manager, "_TTReportManager__create_html", return_value = "<div></div>") as mocked_create_html:

            # Act
            actual : list[str] = self.report_manager._TTReportManager__create_html_sections(tt_summary = self.tt_summary, formatters = formatters)  # type: ignore

            # Assert
            self.assertEqual(expected_call_00, mocked_create_html.call_args_list[0])
            self.assertEqual(expected_call_01, mocked_create_html.call_args_list[1])
            self.assertEqual(expected_call_02, mocked_create_html.call_args_list[2])
            self.assertEqual(expected_call_03, mocked_create_html.call_args_list[3])
            self.assertEqual(expected_call_04, mocked_create_html.call_args_list[4])
            self.assertEqual(expected_call_05, mocked_create_html.call_args_list[5])
            self.assertEqual(expected_call_06, mocked_create_html.call_args_list[6])
            self.assertEqual(expected_call_07, mocked_create_html.call_args_list[7])
            self.assertEqual(expected_call_08, mocked_create_html.call_args_list[8])
            self.assertEqual(expected_call_09, mocked_create_html.call_args_list[9])
            self.assertEqual(expected_call_10, mocked_create_html.call_args_list[10])
            self.assertEqual(len(actual), expected_calls)
    def test_createhtmltemplate_shouldcontainexpectedhtmlexcerpts_wheninvoked(self) -> None:

        # Arrange
        html_sections : list[str] = ["<div>One</div>", "<div>Two</div>"]
        last_update : datetime = datetime(year = 2025, month = 12, day = 22)
        report_title : str = "Time Tracking Report"
        app_name : str = "nwtimetracking"

        # Act
        actual : str = self.report_manager._TTReportManager__create_html_template(html_sections = html_sections, last_update = last_update) # type: ignore

        # Assert
        self.assertIn("<meta charset=\"utf-8\">", actual)
        self.assertIn(f"<title>{report_title} | 2025-12-22</title>", actual)
        self.assertIn(f"<h1>{report_title} | 2025-12-22</h1>", actual)
        self.assertIn("".join(html_sections), actual)
        self.assertIn("avatars.githubusercontent.com/u/10279234", actual)
        self.assertIn(f"This report is generated by '{app_name}'", actual)
        self.assertIn("© 2025 numbworks.", actual)
    def test_createstylesheet_shouldcallcsswiththeexpectedstring_wheninvoked(self) -> None:

        # Arrange
        css_mock = Mock()

        with patch.object(self.report_module, "CSS", css_mock):

            # Act
            self.report_manager._TTReportManager__create_stylesheet()  # type: ignore

            # Assert
            css_mock.assert_called_once_with(string = "@page { size: A3 landscape; margin: 20mm; }")
    def test_saveasreport_shouldperformexpectedcalls_wheninvoked(self) -> None:

        # Arrange
        folder_path : str = "/home"
        last_update : datetime = datetime(year = 2025, month = 12, day = 22)
        save_html : bool = True
        save_pdf : bool = True
        formatters : Optional[dict] = None

        html_sections : list[str] = ["<div>Section</div>"]
        full_html : str = "<html><body>Report</body></html>"
        stylesheet : object = object()
        html_path : Path = Path("/home/some_file_name.html")
        pdf_path : Path = Path("/home/some_file_name.pdf")

        html_instance : Mock = Mock()

        with (
            patch.object(self.report_manager, "_TTReportManager__create_report_file_paths", return_value = (html_path, pdf_path)) as mocked_create_report_file_paths,
            patch.object(self.report_manager, "_TTReportManager__create_html_sections", return_value = html_sections) as mocked_create_html_sections,
            patch.object(self.report_manager, "_TTReportManager__create_html_template", return_value = full_html) as mocked_create_html_template,
            patch.object(self.report_manager, "_TTReportManager__create_stylesheet", return_value = stylesheet) as mocked_create_stylesheet,
            patch.object(Path, "write_text", autospec = True) as mocked_write_text,
            patch.object(self.report_module, "HTML", return_value = html_instance) as mocked_html
        ):

            # Act
            self.report_manager.save_as_report(
                tt_summary = self.tt_summary,
                folder_path = folder_path,
                last_update = last_update,
                save_html = save_html,
                save_pdf = save_pdf,
                formatters = formatters
            )

            # Assert
            mocked_create_report_file_paths.assert_called_once_with(folder_path = folder_path, last_update = last_update)
            mocked_create_html_sections.assert_called_once_with(tt_summary = self.tt_summary, formatters = formatters)
            mocked_create_html_template.assert_called_once_with(html_sections = html_sections, last_update = last_update)
            mocked_write_text.assert_called_once_with(html_path, data = full_html, encoding = "utf-8")
            mocked_html.assert_called_once_with(string = full_html)
            mocked_create_stylesheet.assert_called_once()
            html_instance.write_pdf.assert_called_once_with(target = str(pdf_path), stylesheets = [stylesheet])
class ComponentBagTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_whendefault(self) -> None:

        # Arrange
        # Act
        component_bag : ComponentBag = ComponentBag(
            file_path_manager = FilePathManager(),
            file_manager = FileManager(file_path_manager = FilePathManager()),
            displayer = Displayer(),
            tt_adapter = TTAdapter(
                df_factory = TTDataFrameFactory(df_helper = TTDataFrameHelper()),
                effort_highlighter = EffortHighlighter(df_helper = TTDataFrameHelper())
            ))

        # Assert
        self.assertIsInstance(component_bag.file_path_manager, FilePathManager)
        self.assertIsInstance(component_bag.file_manager, FileManager)
        self.assertIsInstance(component_bag.displayer, Displayer)
        self.assertIsInstance(component_bag.tt_adapter, TTAdapter)
class TimeTrackingProcessorTestCase(unittest.TestCase):

    def test_processtt_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tt_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tt_df = tt_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tt = [OPTION.display]   # type: ignore

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tt()

        # Assert
        displayer.display.assert_called_once_with(obj = tt_df)
    def test_processttlatestfour_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tt_latest_four_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tt_latest_four_df = tt_latest_four_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tt_latest_four = [OPTION.display]    # type: ignore

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()        
        tt_processor.process_tt_latest_four()

        # Assert
        displayer.display.assert_called_once_with(obj = tt_latest_four_df)
    def test_processttsbymonth_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_month_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_month_df = tts_by_month_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_month = [OPTION.display]     # type: ignore

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()        
        tt_processor.process_tts_by_month()

        # Assert
        displayer.display.assert_called_once_with(obj = tts_by_month_df)
    def test_processttsbyyear_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_year_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_year_df = tts_by_year_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_year = [OPTION.display]  # type: ignore
        
        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()        
        tt_processor.process_tts_by_year()

        # Assert
        displayer.display.assert_called_once_with(obj = tts_by_year_df)    
    def test_processttsbyrange_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_range_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_range_df = tts_by_range_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter
        
        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_range = [OPTION.display]     # type: ignore

        # Act
        processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        processor.initialize()        
        processor.process_tts_by_range()

        # Assert
        displayer.display.assert_called_once_with(obj = tts_by_range_df)
    def test_processttsbyspn_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_spn_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_spn_df = tts_by_spn_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_spn = [OPTION.display]   # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_spn()

        # Assert
        displayer.display.assert_called_once_with(obj = tts_by_spn_df)
    def test_processttsbyspv_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_spv_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_spv_df = tts_by_spv_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_spv = [OPTION.display]   # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_spv()

        # Assert
        displayer.display.assert_called_once_with(obj = tts_by_spv_df)
    def test_processttsbyhashtagyear_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_hashtag_year_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_hashtag_year_df = tts_by_hashtag_year_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_hashtag_year = [OPTION.display]  # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_hashtag_year()

        # Assert
        displayer.display.assert_called_once_with(obj = tts_by_hashtag_year_df)
    def test_processttsbyhashtag_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_hashtag_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_hashtag_df = tts_by_hashtag_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_hashtag = [OPTION.display]   # type: ignore
        setting_bag.tts_by_hashtag_formatters = { TTCN.EFFORTPERC : "{:.2f}" }

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_hashtag()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_hashtag_df, 
            formatters = setting_bag.tts_by_hashtag_formatters
        )
    def test_processttsbyyearmonthspnv_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_year_month_spnv_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_year_month_spnv_df = tts_by_year_month_spnv_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_year_month_spnv = [OPTION.display]   # type: ignore

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()        
        tt_processor.process_tts_by_year_month_spnv()

        # Assert
        displayer.display.assert_called_once_with(obj = tts_by_year_month_spnv_df)
    def test_processttsbytimeranges_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_timeranges_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_timeranges_df = tts_by_timeranges_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_timeranges = [OPTION.display]    # type: ignore
        setting_bag.tts_by_timeranges_formatters = { TTCN.OCCURRENCEPERC : "{:.2f}" }

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_timeranges()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_timeranges_df,
            formatters = setting_bag.tts_by_timeranges_formatters
        )
    def test_processttdeffortstatus_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        ttd_effort_status_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.ttd_effort_status_df = ttd_effort_status_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_ttd_effort_status = [OPTION.display]   # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_ttd_effort_status()

        # Assert
        displayer.display.assert_called_once_with(obj = ttd_effort_status_df)    
    def test_processdefinitions_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        definitions_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.definitions_df = definitions_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_definitions = [OPTION.display]  # type: ignore

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()        
        tt_processor.process_definitions()

        # Assert
        displayer.display.assert_called_once_with(obj = definitions_df)
    def test_getsummary_shouldreturnttsummaryobject_wheninvoked(self):
        
        # Arrange
        summary : Mock = Mock()

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        
        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()        
        actual : TTSummary = tt_processor.get_summary()

        # Assert
        self.assertEqual(actual, summary)

    @parameterized.expand([
        ["process_tt"],
        ["process_tt_latest_four"],
        ["process_tts_by_month"],
        ["process_tts_by_year"],
        ["process_tts_by_range"],
        ["process_tts_by_spn"],
        ["process_tts_by_spv"],
        ["process_tts_by_hashtag_year"],
        ["process_tts_by_hashtag"],
        ["process_tts_by_year_month_spnv"],
        ["process_tts_by_timeranges"],
        ["process_ttd_effort_status"],
        ["process_definitions"],
        ["get_summary"]
    ])
    def test_processmethod_shouldraiseexception_wheninitializenotrun(self, method_name : str) -> None:
        
        # Arrange
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = Mock(), setting_bag = Mock())

        # Act & Assert
        with self.assertRaises(Exception) as context:
            getattr(tt_processor, method_name)()

        self.assertEqual(str(context.exception), "Please run the 'initialize' method first.")

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)