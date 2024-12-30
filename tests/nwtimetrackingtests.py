# GLOBAL MODULES
import json
import unittest
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from numpy import int64, uint
from pandas import DataFrame
from pandas.io.formats.style import Styler
from pandas.testing import assert_frame_equal
from parameterized import parameterized
from types import FunctionType
from typing import Any, Callable, Literal, Optional, Tuple, cast
from unittest.mock import MagicMock, Mock, patch
from nwshared import MarkdownHelper, Formatter, FilePathManager, FileManager, Displayer, LambdaProvider

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwtimetracking import COLORNAME, CRITERIA, EFFORTMODE, TTCN, TTID, DEFINITIONSCN, OPTION
from nwtimetracking import _MessageCollection, BYMSplitter, EffortCell, EffortHighlighter, SettingSubset
from nwtimetracking import YearlyTarget, EffortStatus, MDInfo, TTSummary, DefaultPathProvider, YearProvider
from nwtimetracking import SoftwareProjectNameProvider, MDInfoProvider, SettingBag, ComponentBag, TTDataFrameHelper
from nwtimetracking import TTDataFrameFactory, TTMarkdownFactory, TTAdapter, BYMFactory
from nwtimetracking import TTLogger, TTSequencer, TimeTrackingProcessor

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
    def get_setting_bag() -> SettingBag:

        setting_bag : SettingBag = SettingBag(
            options_tt = [OPTION.display],                          # type: ignore
            options_tts_by_month = [OPTION.display, OPTION.save],   # type: ignore
            options_tts_by_year = [OPTION.display],                 # type: ignore
            options_tts_by_year_month = [OPTION.display],           # type: ignore
            options_tts_by_year_month_spnv = [OPTION.display],      # type: ignore
            options_tts_by_year_spnv = [OPTION.display],            # type: ignore
            options_tts_by_spn = [OPTION.display, OPTION.logdef],   # type: ignore
            options_tts_by_spn_spv = [],
            options_tts_by_hashtag = [OPTION.display],              # type: ignore
            options_tts_by_hashtag_year = [OPTION.display],         # type: ignore
            options_tts_by_efs = [OPTION.display],                  # type: ignore
            options_tts_by_tr = [OPTION.display],                   # type: ignore
            options_tts_gantt_spnv = [OPTION.display],              # type: ignore
            options_tts_gantt_hseq = [OPTION.display],              # type: ignore
            options_definitions = [OPTION.display],                 # type: ignore
            excel_nrows = 1301,
            tts_by_year_month_spnv_display_only_spn = "nwtimetracking",
            tts_by_year_spnv_display_only_spn = "nwtimetracking",
            tts_by_spn_spv_display_only_spn = "nwtimetracking"
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
    def get_yearly_targets() -> list[YearlyTarget]:

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
    def get_tts_by_year_df() -> DataFrame:

        '''
                Year	Effort	YearlyTarget	TargetDiff	IsTargetMet
            0	2024	36h 00m	250h 00m	    -214h 00m	False        
        '''

        return pd.DataFrame({
                TTCN.YEAR: np.array([2024], dtype=int64),
                TTCN.EFFORT: np.array(['36h 00m'], dtype=object),
                TTCN.YEARLYTARGET: np.array(['250h 00m'], dtype=object),
                TTCN.TARGETDIFF: np.array(['-214h 00m'], dtype=object),
                TTCN.ISTARGETMET: np.array([False], dtype=bool),
            }, index=pd.RangeIndex(start=0, stop=1, step=1))
    @staticmethod
    def get_tts_by_year_month_tpl() -> Tuple[DataFrame, DataFrame]:

        '''
                Year	Month	Effort	YearlyTotal	ToTarget
            0	2024	2	    36h 00m	36h 00m	    -214h 00m

                Year	Month	Effort	YearlyTotal	ToTarget
            0	2024	2	    36h 00m	36h 00m	    -214h 00m              
        '''

        df : DataFrame = pd.DataFrame({
                TTCN.YEAR: np.array([2024], dtype=int64),
                TTCN.MONTH: np.array([2], dtype=int64),
                TTCN.EFFORT: np.array(['36h 00m'], dtype=object),
                TTCN.YEARLYTOTAL: np.array(['36h 00m'], dtype=object),
                TTCN.TOTARGET: np.array(['-214h 00m'], dtype=object),
            }, index=pd.RangeIndex(start=0, stop=1, step=1))
        
        return (df, df)
    @staticmethod
    def get_tts_by_year_month_spnv_tpl() -> Tuple[DataFrame, DataFrame]:

        '''
                Year	Month	ProjectName	                ProjectVersion	Effort	DME	    %_DME	TME	    %_TME
            0	2024	2	    NW.NGramTextClassification	4.2.0	        01h 15m	08h 45m	14.29	36h 00m	3.47
            1	2024	2	    NW.Shared.Serialization	    1.0.0	        04h 15m	08h 45m	48.57	36h 00m	11.81
            2	2024	2	    NW.UnivariateForecasting	4.2.0	        00h 45m	08h 45m	8.57	36h 00m	2.08
            3	2024	2	    nwreadinglistmanager	    2.1.0	        02h 00m	08h 45m	22.86	36h 00m	5.56

                Year	Month	ProjectName	                ProjectVersion	Effort	DME	    %_DME	TME	    %_TME
            0	2024	2	    NW.NGramTextClassification	4.2.0	        01h 15m	08h 45m	14.29	36h 00m	3.47            
        '''

        df1 : DataFrame = pd.DataFrame({
                TTCN.YEAR: np.array([2024, 2024, 2024, 2024], dtype=int64),
                TTCN.MONTH: np.array([2, 2, 2, 2], dtype=int64),
                TTCN.PROJECTNAME: np.array(['NW.NGramTextClassification', 'NW.Shared.Serialization', 'NW.UnivariateForecasting', 'nwreadinglistmanager'], dtype=object),
                TTCN.PROJECTVERSION: np.array(['4.2.0', '1.0.0', '4.2.0', '2.1.0'], dtype=object),
                TTCN.EFFORT: np.array(['01h 15m', '04h 15m', '00h 45m', '02h 00m'], dtype=object),
                TTCN.DME: np.array(['08h 45m', '08h 45m', '08h 45m', '08h 45m'], dtype=object),
                TTCN.PERCDME: np.array([14.29, 48.57, 8.57, 22.86], dtype= np.float64),
                TTCN.TME: np.array(['36h 00m', '36h 00m', '36h 00m', '36h 00m'], dtype=object),
                TTCN.PERCTME: np.array([3.47, 11.81, 2.08, 5.56], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
        
        df2 : DataFrame = pd.DataFrame({
                TTCN.YEAR: np.array([2024], dtype=int64),
                TTCN.MONTH: np.array([2], dtype=int64),
                TTCN.PROJECTNAME: np.array(['NW.NGramTextClassification'], dtype=object),
                TTCN.PROJECTVERSION: np.array(['4.2.0'], dtype=object),
                TTCN.EFFORT: np.array(['01h 15m'], dtype=object),
                TTCN.DME: np.array(['08h 45m'], dtype=object),
                TTCN.PERCDME: np.array([14.29], dtype= np.float64),
                TTCN.TME: np.array(['36h 00m'], dtype=object),
                TTCN.PERCTME: np.array([3.47], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=1, step=1))        

        return (df1, df2)
    @staticmethod
    def get_tts_by_year_spnv_tpl() -> Tuple[DataFrame, DataFrame]:

        '''
                Year	ProjectName	                ProjectVersion	Effort	DYE	    %_DYE	TYE	        %_TYE
            0	2024	NW.NGramTextClassification	4.2.0	        01h 15m	08h 45m	14.29	36h 00m	    3.47
            1	2024	NW.Shared.Serialization	    1.0.0	        04h 15m	08h 45m	48.57	36h 00m	    11.81
            2	2024	NW.UnivariateForecasting	4.2.0	        00h 45m	08h 45m	8.57	36h 00m	    2.08
            3	2024	nwreadinglistmanager	    2.1.0	        02h 00m	08h 45m	22.86	36h 00m	    5.56

                Year	ProjectName	                ProjectVersion	Effort	DYE	    %_DYE	TYE	        %_TYE
            0	2024	NW.NGramTextClassification	4.2.0	        01h 15m	08h 45m	14.29	36h 00m	    3.47
        '''

        df1 : DataFrame = pd.DataFrame({
                TTCN.YEAR: np.array([2024, 2024, 2024, 2024], dtype=int64),
                TTCN.PROJECTNAME: np.array(['NW.NGramTextClassification', 'NW.Shared.Serialization', 'NW.UnivariateForecasting', 'nwreadinglistmanager'], dtype=object),
                TTCN.PROJECTVERSION: np.array(['4.2.0', '1.0.0', '4.2.0', '2.1.0'], dtype=object),
                TTCN.EFFORT: np.array(['01h 15m', '04h 15m', '00h 45m', '02h 00m'], dtype=object),
                TTCN.DYE: np.array(['08h 45m', '08h 45m', '08h 45m', '08h 45m'], dtype=object),
                TTCN.PERCDYE: np.array([14.29, 48.57, 8.57, 22.86], dtype= np.float64),
                TTCN.TYE: np.array(['36h 00m', '36h 00m', '36h 00m', '36h 00m'], dtype=object),
                TTCN.PERCTYE: np.array([3.47, 11.81, 2.08, 5.56], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))

        df2 : DataFrame = pd.DataFrame({
                TTCN.YEAR: np.array([2024], dtype=int64),
                TTCN.PROJECTNAME: np.array(['NW.NGramTextClassification'], dtype=object),
                TTCN.PROJECTVERSION: np.array(['4.2.0'], dtype=object),
                TTCN.EFFORT: np.array(['01h 15m'], dtype=object),
                TTCN.DYE: np.array(['08h 45m'], dtype=object),
                TTCN.PERCDYE: np.array([14.29], dtype= np.float64),
                TTCN.TYE: np.array(['36h 00m'], dtype=object),
                TTCN.PERCTYE: np.array([3.47], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=1, step=1))

        return (df1, df2)
    @staticmethod
    def get_tts_by_spn_spv_df() -> DataFrame:

        '''
                ProjectName	                ProjectVersion	Effort
            0	NW.NGramTextClassification	4.2.0	        01h 15m
            1	NW.Shared.Serialization	    1.0.0	        04h 15m
            2	NW.UnivariateForecasting	4.2.0	        00h 45m
            3	nwreadinglistmanager	    2.1.0	        02h 00m
        '''

        return pd.DataFrame({
                TTCN.PROJECTNAME: np.array(['NW.NGramTextClassification', 'NW.Shared.Serialization', 'NW.UnivariateForecasting', 'nwreadinglistmanager'], dtype=object),
                TTCN.PROJECTVERSION: np.array(['4.2.0', '1.0.0', '4.2.0', '2.1.0'], dtype=object),
                TTCN.EFFORT: np.array(['01h 15m', '04h 15m', '00h 45m', '02h 00m'], dtype=object),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))    
    @staticmethod
    def get_tts_by_month_tpl() -> Tuple[DataFrame, DataFrame]:

        '''
				Month	2024
			0	1		00h 00m
			1	2		36h 00m
			...
            10	11		00h 00m
            11  12      00h 00m

				Month	2024
            ...
			10	11		00h 00m

            now = 2024-11-30     
        '''

        df1 : DataFrame = pd.DataFrame({
                TTCN.MONTH: np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], dtype=int64),
                '2024': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object)				
            }, index=pd.RangeIndex(start=0, stop=12, step=1))

        df2 : DataFrame = pd.DataFrame({
                TTCN.MONTH: np.array(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', ''], dtype=object),
                '2024': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', ''], dtype=object)				
            }, index=pd.RangeIndex(start=0, stop=12, step=1))
            
        return (df1, df2)
    @staticmethod
    def get_tts_by_month_df(index_list : list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]) -> DataFrame:

        '''
            index_list: [0, 1]
            ...
            index_list: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        '''

        df : DataFrame = pd.DataFrame({
                TTCN.MONTH: np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], dtype=int64),
                '2015': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2015': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),
                '2016': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2016': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),
                '2017': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2017': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),
                '2018': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2018': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),
                '2019': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2019': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),
                '2020': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2020': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),
                '2021': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2021': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),
                '2022': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2022': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),		
                '2023': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object),
                '↕_2023': np.array(['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='], dtype=object),
                '2024': np.array(['00h 00m', '36h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m', '00h 00m'], dtype=object)	
            }, index=pd.RangeIndex(start=0, stop=12, step=1))
        
        df.rename(columns=lambda x: "↕" if x.startswith("↕_") else x, inplace=True)
        df = df.iloc[:, index_list]

        return df    
    @staticmethod
    def get_tts_by_tr_df() -> DataFrame:

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
                TTCN.TIMERANGEID: np.array(['08:00-08:30', '15:30-16:30', '22:00-23:00', '21:00-22:00', '20:15-21:15', '20:00-20:15', '17:15-18:00', '17:15-17:45', '17:00-18:00', '15:30-18:00', '14:30-16:45', '08:15-12:45', '14:00-19:45', '13:30-15:00', '13:30-14:00', '11:15-13:00', '11:00-13:00', '11:00-12:30', '10:15-13:00', '08:45-12:15', '23:00-23:30'], dtype=object),
                TTCN.OCCURRENCES: np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype= np.int64),
            }, index=pd.RangeIndex(start=0, stop=21, step=1))    
    @staticmethod
    def get_tts_by_spn_df() -> DataFrame:

        '''
                Hashtag	ProjectName	                Effort	DE	    %_DE	TE	    %_TE
            0	#python	nwreadinglistmanager	    02h 00m	08h 45m	22.86	36h 00m	5.56
            1	#csharp	NW.Shared.Serialization	    04h 15m	08h 45m	48.57	36h 00m	11.81
            2	#csharp	NW.NGramTextClassification	01h 15m	08h 45m	14.29	36h 00m	3.47
            3	#csharp	NW.UnivariateForecasting	00h 45m	08h 45m	8.57	36h 00m	2.08        
        '''

        return pd.DataFrame({
                TTCN.HASHTAG: np.array(['#python', '#csharp', '#csharp', '#csharp'], dtype=object),
                TTCN.PROJECTNAME: np.array(['nwreadinglistmanager', 'NW.Shared.Serialization', 'NW.NGramTextClassification', 'NW.UnivariateForecasting'], dtype=object),
                TTCN.EFFORT: np.array(['02h 00m', '04h 15m', '01h 15m', '00h 45m'], dtype=object),
                TTCN.DE: np.array(['08h 45m', '08h 45m', '08h 45m', '08h 45m'], dtype=object),
                TTCN.PERCDE: np.array([22.86, 48.57, 14.29, 8.57], dtype= np.float64),
                TTCN.TE: np.array(['36h 00m', '36h 00m', '36h 00m', '36h 00m'], dtype=object),
                TTCN.PERCTE: np.array([5.56, 11.81, 3.47, 2.08], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def get_tts_by_hashtag_year_df() -> DataFrame:

        '''
                Year	Hashtag	        Effort
            0	2024	#csharp	        06h 15m
            1	2024	#maintenance	04h 30m
            2	2024	#python	        02h 00m
            3	2024	#studying	    23h 15m
        '''

        return pd.DataFrame({
                TTCN.YEAR: np.array([2024, 2024, 2024, 2024], dtype=int64),
                TTCN.HASHTAG: np.array(['#csharp', '#maintenance', '#python', '#studying'], dtype=object),
                TTCN.EFFORT: np.array(['06h 15m', '04h 30m', '02h 00m', '23h 15m'], dtype=object),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def get_tts_by_hashtag_df() -> DataFrame:

        '''
                Hashtag	        Effort	Effort%
            0	#studying	    23h 15m	64.58
            1	#csharp	        06h 15m	17.36
            2	#maintenance	04h 30m	12.50
            3	#python	        02h 00m	5.56
        '''

        return pd.DataFrame({
                TTCN.HASHTAG: np.array(['#studying', '#csharp', '#maintenance', '#python'], dtype=object),
                TTCN.EFFORT: np.array(['23h 15m', '06h 15m', '04h 30m', '02h 00m'], dtype=object),
                TTCN.EFFORTPERC: np.array([64.58, 17.36, 12.5, 5.56], dtype= np.float64),
            }, index=pd.RangeIndex(start=0, stop=4, step=1))
    @staticmethod
    def get_definitions_df() -> DataFrame:

        columns : list[str] = [DEFINITIONSCN.TERM, DEFINITIONSCN.DEFINITION]

        definitions : dict[str, str] = { 
            TTCN.DME: "Total Development Monthly Effort",
            TTCN.TME: "Total Monthly Effort",
            TTCN.DYE: "Total Development Yearly Effort",
            TTCN.TYE: "Total Yearly Effort",
            TTCN.DE: "Total Development Effort",
            TTCN.TE: "Total Effort",
            TTCN.PERCDME: r"% of Total Development Monthly Effort",
            TTCN.PERCTME: r"% of Total Monthly Effort",
            TTCN.PERCDYE: r"% of Total Development Yearly Effort",
            TTCN.PERCTYE: r"% of Total Yearly Effort",
            TTCN.PERCDE: r"% of Total Development Effort",
            TTCN.PERCTE: r"% of Total Effort",
            TTCN.EFFORTPERC: "% of Total Effort",
            TTCN.HASHTAGSEQ: "Period of time in which the same hashtag has been used without breaks.",
            TTCN.EFFORTH: "Total Hours of Effort between StartDate and EndDate.",
            TTCN.DURATION: "Total number of days between StartDate and EndDate.",
            "tts_gantt_spnv": "Shows how much subsequent work has been performed per software project name/version.",
            "tts_gantt_hseq": "Shows how much subsequent work has been performed per hashtag."            
        }
        
        definitions_df : DataFrame = DataFrame(
            data = definitions.items(), 
            columns = columns
        )

        return definitions_df

    @staticmethod
    def get_tts_by_month_sub_md() -> str:

        lines: list[str] = [
            "## Revision History",
            "",
            "|Date|Author|Description|",
            "|---|---|---|",
            "|2020-12-22|numbworks|Created.|",
            "|2024-11-30|numbworks|Last update.|",
            "",
            "## Time Tracking By Month",
            "",
            "|   Month | 2024    |",
            "|--------:|:--------|",
            "|       1 | 00h 00m |",
            "|       2 | 36h 00m |",
            "|       3 | 00h 00m |",
            "|       4 | 00h 00m |",
            "|       5 | 00h 00m |",
            "|       6 | 00h 00m |",
            "|       7 | 00h 00m |",
            "|       8 | 00h 00m |",
            "|       9 | 00h 00m |",
            "|      10 | 00h 00m |",
            "|      11 | 00h 00m |",
            "|      12 | 00h 00m |",
        ]

        expected: str = "\n".join(lines) + "\n"

        return expected

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
    def test_nomdinfofound_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        id : TTID = TTID.TTSBYMONTH
        expected : str = "No MDInfo object found for id='tts_by_month'."

        # Act
        actual : str = _MessageCollection.no_mdinfo_found(id = id)

        # Assert
        self.assertEqual(expected, actual)
    def test_pleaseruninitializefirst_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        expected : str = "Please run the 'initialize' method first."

        # Act
        actual : str = _MessageCollection.please_run_initialize_first()

        # Assert
        self.assertEqual(expected, actual)
    def test_thiscontentsuccessfullysavedas_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        id : TTID = TTID.TTSBYMONTH
        file_path : str = "/path/to/file.csv"
        expected : str = "This content (id: 'tts_by_month') has been successfully saved as '/path/to/file.csv'."

        # Act
        actual : str = _MessageCollection.this_content_successfully_saved_as(id = id, file_path = file_path)

        # Assert
        self.assertEqual(expected, actual)
    def test_somethingfailedwhilesaving_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        file_path : str = "/path/to/file.csv"
        expected : str = "Something failed while saving '/path/to/file.csv'."

        # Act
        actual : str = _MessageCollection.something_failed_while_saving(file_path = file_path)

        # Assert
        self.assertEqual(expected, actual)
    def test_provideddfinvalidcolumnlist_shouldreturnexpectedmessage_wheninvoked(self):
        
        # Arrange
        column_list : list[str] = ["Month", "2015"]
        expected : str = (
            f"The provided df has an invalid BYM column list ('{column_list}')."
        )

        # Act
        actual : str = _MessageCollection.provided_df_invalid_bym_column_list(column_list = column_list)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        [CRITERIA.do_nothing, "No strategy available for the provided CRITERIA ('do_nothing')."],
        [CRITERIA.include, "No strategy available for the provided CRITERIA ('include')."],
        [CRITERIA.exclude, "No strategy available for the provided CRITERIA ('exclude')."]
    ])
    def test_nostrategyavailableforprovidedcriteria_shouldreturnexpectedmessage_wheninvoked(self, criteria : CRITERIA, expected : str):
        
        # Arrange
        # Act
        actual : str = _MessageCollection.no_strategy_available_for_provided_criteria(criteria = criteria)

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["months", "'months' can't be < 1."],
        ["min_duration", "'min_duration' can't be < 1."],
    ])
    def test_variablecantbelessthanone_shouldreturnexpectedmessage_wheninvoked(self, variable_name : str, expected : str):
        
        # Arrange
        # Act
        actual : str = _MessageCollection.variable_cant_be_less_than_one(variable_name = variable_name)

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
class YearlyTargetTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:
        
        # Arrange
        year : int = 2024
        hours : timedelta = timedelta(hours = 1200)

        # Act
        actual : YearlyTarget = YearlyTarget(year = year, hours = hours)

        # Assert
        self.assertEqual(actual.year, year)
        self.assertEqual(actual.hours, hours)
        self.assertIsInstance(actual.year, int)
        self.assertIsInstance(actual.hours, timedelta)
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
class MDInfoTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:
        
        # Arrange
        id : TTID = TTID.TTSBYMONTH
        file_name : str = "TIMETRACKINGBYMONTH.md"
        paragraph_title : str = "Time Tracking By Month"

        # Act
        actual : MDInfo = MDInfo(id = id, file_name = file_name, paragraph_title = paragraph_title)

        # Assert
        self.assertEqual(actual.id, id)
        self.assertEqual(actual.file_name, file_name)
        self.assertEqual(actual.paragraph_title, paragraph_title)
        self.assertIsInstance(actual.id, TTID)
        self.assertIsInstance(actual.file_name, str)
        self.assertIsInstance(actual.paragraph_title, str)
class TTSummaryTestCase(unittest.TestCase):
    
    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:
        
        # Arrange
        empty_df : DataFrame = DataFrame()
        empty_tuple : Tuple[DataFrame, DataFrame] = (empty_df, empty_df)
        empty_func : Callable[[], None] = lambda : None
        empty_sub_dfs : list[DataFrame] = []
        empty_md : str = ""

        # Act
        actual = TTSummary(
            tt_df = empty_df,
            tt_styler = empty_df,
            tts_by_month_tpl = empty_tuple,
            tts_by_month_styler = empty_df,
            tts_by_month_sub_dfs = empty_sub_dfs,
            tts_by_month_sub_md = empty_md,
            tts_by_year_df = empty_df,
            tts_by_year_styler = empty_df,
            tts_by_year_month_tpl = empty_tuple,
            tts_by_year_month_styler = empty_df,
            tts_by_year_month_spnv_tpl = empty_tuple,
            tts_by_year_month_spnv_styler = empty_df,
            tts_by_year_spnv_tpl = empty_tuple,
            tts_by_year_spnv_styler = empty_df,
            tts_by_spn_df = empty_df,
            tts_by_spn_styler = empty_df,
            tts_by_spn_spv_df = empty_df,
            tts_by_hashtag_df = empty_df,
            tts_by_hashtag_year_df = empty_df,
            tts_by_hashtag_year_styler = empty_df,
            tts_by_efs_tpl = empty_tuple,
            tts_by_efs_styler = empty_df,
            tts_by_tr_df = empty_df,
            tts_by_tr_styler = empty_df,
            tts_gantt_spnv_df = empty_df,
            tts_gantt_spnv_plot_function = empty_func,
            tts_gantt_hseq_df = empty_df,
            tts_gantt_hseq_plot_function = empty_func,
            definitions_df = empty_df
        )

        # Assert
        self.assertEqual(actual.tt_df.shape, empty_df.shape)
        self.assertEqual(actual.tt_styler.shape, empty_df.shape)

        self.assertEqual(actual.tts_by_month_tpl, empty_tuple)
        self.assertEqual(actual.tts_by_month_styler.shape, empty_df.shape)
        self.assertEqual(len(actual.tts_by_month_sub_dfs), len(empty_sub_dfs))
        self.assertEqual(actual.tts_by_month_sub_md, empty_md)

        self.assertEqual(actual.tts_by_year_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_year_styler.shape, empty_df.shape)

        self.assertEqual(actual.tts_by_year_month_tpl, empty_tuple)
        self.assertEqual(actual.tts_by_year_month_styler.shape, empty_df.shape)

        self.assertEqual(actual.tts_by_year_month_spnv_tpl, empty_tuple)
        self.assertEqual(actual.tts_by_year_month_spnv_styler.shape, empty_df.shape)

        self.assertEqual(actual.tts_by_year_spnv_tpl, empty_tuple)
        self.assertEqual(actual.tts_by_year_spnv_styler.shape, empty_df.shape)

        self.assertEqual(actual.tts_by_spn_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_spn_styler.shape, empty_df.shape)

        self.assertEqual(actual.tts_by_spn_spv_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_hashtag_df.shape, empty_df.shape)

        self.assertEqual(actual.tts_by_hashtag_year_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_hashtag_year_styler.shape, empty_df.shape)
    
        self.assertEqual(actual.tts_by_efs_tpl, empty_tuple)
        self.assertEqual(actual.tts_by_efs_styler.shape, empty_df.shape)

        self.assertEqual(actual.tts_by_tr_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_by_tr_styler.shape, empty_df.shape)

        self.assertEqual(actual.tts_gantt_spnv_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_gantt_spnv_plot_function, empty_func)

        self.assertEqual(actual.tts_gantt_hseq_df.shape, empty_df.shape)
        self.assertEqual(actual.tts_gantt_hseq_plot_function, empty_func)
        
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
class SettingBagTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:

        # Arrange
        options_tt : list[Literal[OPTION.display]] = [OPTION.display]                                                                           # type: ignore
        options_tts_by_month : list[Literal[OPTION.display, OPTION.save, OPTION.logset]] = [OPTION.display, OPTION.save]                        # type: ignore
        options_tts_by_year : list[Literal[OPTION.display, OPTION.logset]] = [OPTION.display]                                                   # type: ignore
        options_tts_by_year_month : list[Literal[OPTION.display, OPTION.logset]] = [OPTION.display]                                             # type: ignore
        options_tts_by_year_month_spnv : list[Literal[OPTION.display, OPTION.logset]] = [OPTION.display]                                        # type: ignore
        options_tts_by_year_spnv : list[Literal[OPTION.display]] = [OPTION.display]                                                             # type: ignore
        options_tts_by_spn : list[Literal[OPTION.display, OPTION.logdef, OPTION.logterm, OPTION.logset]] = [OPTION.display, OPTION.logdef]      # type: ignore
        options_tts_by_spn_spv : list[Literal[OPTION.display, OPTION.logdef, OPTION.logterm, OPTION.logset]] = [OPTION.display, OPTION.logdef]  # type: ignore
        options_tts_by_hashtag : list[Literal[OPTION.display, OPTION.logdef, OPTION.logterm, OPTION.logset]] = [OPTION.display]                 # type: ignore
        options_tts_by_hashtag_year : list[Literal[OPTION.display, OPTION.logset]] = [OPTION.display]                                           # type: ignore
        options_tts_by_efs : list[Literal[OPTION.display]] = [OPTION.display]                                                                   # type: ignore
        options_tts_by_tr : list[Literal[OPTION.display]] = [OPTION.display]                                                                    # type: ignore
        options_tts_gantt_spnv : list[Literal[OPTION.display, OPTION.plot, OPTION.logdef, OPTION.logterm, OPTION.logset]] = [OPTION.display]    # type: ignore
        options_tts_gantt_hseq : list[Literal[OPTION.display, OPTION.plot, OPTION.logdef, OPTION.logterm, OPTION.logset]] = [OPTION.display]    # type: ignore
        options_definitions : list[Literal[OPTION.display]] = [OPTION.display]                                                                  # type: ignore
        excel_nrows : int = 100
        tts_by_year_month_spnv_display_only_spn : Optional[str] = "SPN1"
        tts_by_year_spnv_display_only_spn : Optional[str] = "SPN2"
        tts_by_spn_spv_display_only_spn : Optional[str] = "SPN3"

        working_folder_path : str = "/home/nwtimetracking/"
        excel_path : str = "/workspaces/nwtimetracking/"
        excel_skiprows : int = 0
        excel_tabname : str = "Sessions"
        years : list[int] = [2020, 2021, 2022]
        yearly_targets : list = []
        now : datetime = datetime.now()
        software_project_names : list[str] = ["ProjectA", "ProjectB"]
        software_project_names_by_spv : list[str] = ["ProjectC"]
        tt_head_n : uint = uint(5)
        tt_display_head_n_with_tail : bool = True
        tt_hide_index : bool = True
        tts_by_month_effort_highlight : bool = True
        tts_by_month_effort_highlight_mode : EFFORTMODE = EFFORTMODE.top_three_efforts
        tts_by_year_effort_highlight : bool = True
        tts_by_year_effort_highlight_mode : EFFORTMODE = EFFORTMODE.top_three_efforts
        tts_by_year_effort_highlight_column_names : list[str] = [TTCN.EFFORT]
        tts_by_year_month_display_only_years : Optional[list[int]] = [2022]
        tts_by_year_month_effort_highlight : bool = True
        tts_by_year_month_effort_highlight_mode : EFFORTMODE = EFFORTMODE.top_three_efforts
        tts_by_year_month_effort_highlight_column_names : list[str] = [TTCN.EFFORT]
        tts_by_year_month_spnv_formatters : dict[str, str] = {"%_DME" : "{:.2f}", "%_TME" : "{:.2f}"}
        tts_by_year_month_spnv_effort_highlight : bool = True
        tts_by_year_month_spnv_effort_highlight_mode : EFFORTMODE = EFFORTMODE.top_three_efforts
        tts_by_year_month_spnv_effort_highlight_column_names : list[str] = [TTCN.EFFORT]
        tts_by_year_spnv_formatters : dict[str, str] = {"%_DYE" : "{:.2f}", "%_TYE" : "{:.2f}"}
        tts_by_year_spnv_effort_highlight : bool = True
        tts_by_year_spnv_effort_highlight_mode : EFFORTMODE = EFFORTMODE.top_three_efforts
        tts_by_year_spnv_effort_highlight_column_names : list[str] = [TTCN.EFFORT]
        tts_by_spn_formatters : dict[str, str] = {"%_DE" : "{:.2f}", "%_TE" : "{:.2f}"}
        tts_by_spn_remove_untagged : bool = True
        tts_by_spn_effort_highlight : bool = True
        tts_by_spn_effort_highlight_column_names : list[str] = [TTCN.EFFORT]
        tts_by_spn_effort_highlight_mode : EFFORTMODE = EFFORTMODE.top_three_efforts
        tts_by_hashtag_formatters : dict[str, str] = {"Effort%" : "{:.2f}"}
        tts_by_hashtag_year_enable_pivot : bool = False
        tts_by_hashtag_year_effort_highlight : bool = True
        tts_by_hashtag_year_effort_highlight_mode : EFFORTMODE = EFFORTMODE.top_one_effort_per_row
        tts_by_efs_is_correct : bool = False
        tts_by_efs_n : uint = uint(25)
        tts_by_tr_unknown_id : str = "Unknown"
        tts_by_tr_remove_unknown_occurrences : bool = True
        tts_by_tr_filter_by_top_n : uint = uint(5)
        tts_by_tr_head_n : uint = uint(10)
        tts_by_tr_display_head_n_with_tail : bool = False
        tts_gantt_spnv_spns : Optional[list[str]] = []
        tts_gantt_spnv_criteria : Literal[CRITERIA.do_nothing, CRITERIA.include, CRITERIA.exclude] = CRITERIA.do_nothing    # type: ignore
        tts_gantt_spnv_months : int = 4
        tts_gantt_spnv_min_duration : int = 4
        tts_gantt_spnv_fig_size : Tuple[int, int] = (10, 6)
        tts_gantt_spnv_title : Optional[str] = None
        tts_gantt_spnv_x_label : Optional[str] = None
        tts_gantt_spnv_y_label : Optional[str] = None
        tts_gantt_spnv_formatters : dict = { "StartDate": "{:%Y-%m-%d}", "EndDate": "{:%Y-%m-%d}" }
        tts_gantt_hseq_hashtags : Optional[list[str]] = []
        tts_gantt_hseq_criteria : Literal[CRITERIA.do_nothing, CRITERIA.include, CRITERIA.exclude] = CRITERIA.do_nothing    # type: ignore
        tts_gantt_hseq_months : int = 4
        tts_gantt_hseq_min_duration : int = 4
        tts_gantt_hseq_fig_size : Tuple[int, int] = (10, 6)
        tts_gantt_hseq_title : Optional[str] = None
        tts_gantt_hseq_x_label : Optional[str] = None
        tts_gantt_hseq_y_label : Optional[str] = None
        tts_gantt_hseq_formatters : dict = { "StartDate": "{:%Y-%m-%d}", "EndDate": "{:%Y-%m-%d}" }
        effort_highlighter_tags : Tuple[str, str] = (f"<mark style='background-color: {COLORNAME.skyblue}'>", "</mark>")
        md_infos : list = []
        md_last_update : datetime = datetime.now()

		# Act
        actual : SettingBag = SettingBag(
            options_tt = options_tt,
            options_tts_by_month = options_tts_by_month,
            options_tts_by_year = options_tts_by_year,
            options_tts_by_year_month = options_tts_by_year_month,
            options_tts_by_year_month_spnv = options_tts_by_year_month_spnv,
            options_tts_by_year_spnv = options_tts_by_year_spnv,
            options_tts_by_spn = options_tts_by_spn,
            options_tts_by_spn_spv = options_tts_by_spn_spv,
            options_tts_by_hashtag = options_tts_by_hashtag,
            options_tts_by_hashtag_year = options_tts_by_hashtag_year,
            options_tts_by_efs = options_tts_by_efs,
            options_tts_by_tr = options_tts_by_tr,
            options_tts_gantt_spnv = options_tts_gantt_spnv,
            options_tts_gantt_hseq = options_tts_gantt_hseq,
            options_definitions = options_definitions,
            excel_nrows = excel_nrows,
            tts_by_year_month_spnv_display_only_spn = tts_by_year_month_spnv_display_only_spn,
            tts_by_year_spnv_display_only_spn = tts_by_year_spnv_display_only_spn,
            tts_by_spn_spv_display_only_spn = tts_by_spn_spv_display_only_spn,
            working_folder_path = working_folder_path,
            excel_path = excel_path,
            excel_skiprows = excel_skiprows,
            excel_tabname = excel_tabname,
            years = years,
            yearly_targets = yearly_targets,
            now = now,
            software_project_names = software_project_names,
            software_project_names_by_spv = software_project_names_by_spv,
            tt_head_n = tt_head_n,
            tt_display_head_n_with_tail = tt_display_head_n_with_tail,
            tt_hide_index = tt_hide_index,
            tts_by_month_effort_highlight = tts_by_month_effort_highlight,
            tts_by_month_effort_highlight_mode = tts_by_month_effort_highlight_mode,
            tts_by_year_effort_highlight = tts_by_year_effort_highlight,
            tts_by_year_effort_highlight_mode = tts_by_year_effort_highlight_mode,
            tts_by_year_effort_highlight_column_names = tts_by_year_effort_highlight_column_names,
            tts_by_year_month_display_only_years = tts_by_year_month_display_only_years,
            tts_by_year_month_effort_highlight = tts_by_year_month_effort_highlight,
            tts_by_year_month_effort_highlight_mode = tts_by_year_month_effort_highlight_mode,
            tts_by_year_month_effort_highlight_column_names = tts_by_year_month_effort_highlight_column_names,
            tts_by_year_month_spnv_formatters = tts_by_year_month_spnv_formatters,
            tts_by_year_month_spnv_effort_highlight = tts_by_year_month_spnv_effort_highlight,
            tts_by_year_month_spnv_effort_highlight_mode = tts_by_year_month_spnv_effort_highlight_mode,
            tts_by_year_month_spnv_effort_highlight_column_names = tts_by_year_month_spnv_effort_highlight_column_names,
            tts_by_year_spnv_formatters = tts_by_year_spnv_formatters,
            tts_by_year_spnv_effort_highlight = tts_by_year_spnv_effort_highlight,
            tts_by_year_spnv_effort_highlight_mode = tts_by_year_spnv_effort_highlight_mode,
            tts_by_year_spnv_effort_highlight_column_names = tts_by_year_spnv_effort_highlight_column_names,
            tts_by_spn_formatters = tts_by_spn_formatters,
            tts_by_spn_remove_untagged = tts_by_spn_remove_untagged,
            tts_by_spn_effort_highlight = tts_by_spn_effort_highlight,
            tts_by_spn_effort_highlight_mode = tts_by_spn_effort_highlight_mode,
            tts_by_spn_effort_highlight_column_names = tts_by_spn_effort_highlight_column_names,
            tts_by_hashtag_formatters = tts_by_hashtag_formatters,
            tts_by_hashtag_year_enable_pivot = tts_by_hashtag_year_enable_pivot,
            tts_by_hashtag_year_effort_highlight = tts_by_hashtag_year_effort_highlight,
            tts_by_hashtag_year_effort_highlight_mode = tts_by_hashtag_year_effort_highlight_mode,
            tts_by_efs_is_correct = tts_by_efs_is_correct,
            tts_by_efs_n = tts_by_efs_n,
            tts_by_tr_unknown_id = tts_by_tr_unknown_id,
            tts_by_tr_remove_unknown_occurrences = tts_by_tr_remove_unknown_occurrences,
            tts_by_tr_filter_by_top_n = tts_by_tr_filter_by_top_n,
            tts_by_tr_head_n = tts_by_tr_head_n,
            tts_by_tr_display_head_n_with_tail = tts_by_tr_display_head_n_with_tail,
            tts_gantt_spnv_spns = tts_gantt_spnv_spns,
            tts_gantt_spnv_criteria = tts_gantt_spnv_criteria,
            tts_gantt_spnv_months = tts_gantt_spnv_months,
            tts_gantt_spnv_min_duration = tts_gantt_spnv_min_duration,
            tts_gantt_spnv_fig_size = tts_gantt_spnv_fig_size,
            tts_gantt_spnv_title = tts_gantt_spnv_title,
            tts_gantt_spnv_x_label = tts_gantt_spnv_x_label,
            tts_gantt_spnv_y_label = tts_gantt_spnv_y_label,
            tts_gantt_spnv_formatters = tts_gantt_spnv_formatters,
            tts_gantt_hseq_hashtags = tts_gantt_hseq_hashtags,
            tts_gantt_hseq_criteria = tts_gantt_hseq_criteria,
            tts_gantt_hseq_months = tts_gantt_hseq_months,
            tts_gantt_hseq_min_duration = tts_gantt_hseq_min_duration,
            tts_gantt_hseq_fig_size = tts_gantt_hseq_fig_size,
            tts_gantt_hseq_title = tts_gantt_hseq_title,
            tts_gantt_hseq_x_label = tts_gantt_hseq_x_label,
            tts_gantt_hseq_y_label = tts_gantt_hseq_y_label,
            tts_gantt_hseq_formatters = tts_gantt_hseq_formatters,
            effort_highlighter_tags = effort_highlighter_tags,
            md_infos = md_infos,
            md_last_update = md_last_update
        )

		# Assert
        self.assertEqual(actual.options_tt, options_tt)
        self.assertEqual(actual.options_tts_by_month, options_tts_by_month)
        self.assertEqual(actual.options_tts_by_year, options_tts_by_year)
        self.assertEqual(actual.options_tts_by_year_month, options_tts_by_year_month)
        self.assertEqual(actual.options_tts_by_year_month_spnv, options_tts_by_year_month_spnv)
        self.assertEqual(actual.options_tts_by_year_spnv, options_tts_by_year_spnv)
        self.assertEqual(actual.options_tts_by_spn, options_tts_by_spn)
        self.assertEqual(actual.options_tts_by_spn_spv, options_tts_by_spn_spv)
        self.assertEqual(actual.options_tts_by_hashtag, options_tts_by_hashtag)
        self.assertEqual(actual.options_tts_by_hashtag_year, options_tts_by_hashtag_year)
        self.assertEqual(actual.options_tts_by_efs, options_tts_by_efs)
        self.assertEqual(actual.options_tts_by_tr, options_tts_by_tr)
        self.assertEqual(actual.options_tts_gantt_spnv, options_tts_gantt_spnv)
        self.assertEqual(actual.options_tts_gantt_hseq, options_tts_gantt_hseq)
        self.assertEqual(actual.options_definitions, options_definitions)
        self.assertEqual(actual.excel_nrows, excel_nrows)
        self.assertEqual(actual.tts_by_year_month_spnv_display_only_spn, tts_by_year_month_spnv_display_only_spn)
        self.assertEqual(actual.tts_by_year_spnv_display_only_spn, tts_by_year_spnv_display_only_spn)
        self.assertEqual(actual.tts_by_spn_spv_display_only_spn, tts_by_spn_spv_display_only_spn)

        self.assertEqual(actual.working_folder_path, working_folder_path)
        self.assertEqual(actual.excel_path, excel_path)
        self.assertEqual(actual.excel_skiprows, excel_skiprows)
        self.assertEqual(actual.excel_tabname, excel_tabname)
        self.assertEqual(actual.years, years)
        self.assertEqual(actual.yearly_targets, yearly_targets)
        self.assertEqual(actual.now, now)
        self.assertEqual(actual.software_project_names, software_project_names)
        self.assertEqual(actual.software_project_names_by_spv, software_project_names_by_spv)
        self.assertEqual(actual.tt_head_n, tt_head_n)
        self.assertEqual(actual.tt_display_head_n_with_tail, tt_display_head_n_with_tail)
        self.assertEqual(actual.tt_hide_index, tt_hide_index)
        self.assertEqual(actual.tts_by_month_effort_highlight, tts_by_month_effort_highlight)
        self.assertEqual(actual.tts_by_month_effort_highlight_mode, tts_by_month_effort_highlight_mode)
        self.assertEqual(actual.tts_by_year_effort_highlight, tts_by_year_effort_highlight)
        self.assertEqual(actual.tts_by_year_effort_highlight_mode, tts_by_year_effort_highlight_mode)
        self.assertEqual(actual.tts_by_year_effort_highlight_column_names, tts_by_year_effort_highlight_column_names)
        self.assertEqual(actual.tts_by_year_month_display_only_years, tts_by_year_month_display_only_years)
        self.assertEqual(actual.tts_by_year_month_effort_highlight, tts_by_year_month_effort_highlight)
        self.assertEqual(actual.tts_by_year_month_effort_highlight_mode, tts_by_year_month_effort_highlight_mode)
        self.assertEqual(actual.tts_by_year_month_effort_highlight_column_names, tts_by_year_month_effort_highlight_column_names)
        self.assertEqual(actual.tts_by_year_month_spnv_formatters, tts_by_year_month_spnv_formatters)
        self.assertEqual(actual.tts_by_year_month_spnv_effort_highlight, tts_by_year_month_spnv_effort_highlight)
        self.assertEqual(actual.tts_by_year_month_spnv_effort_highlight_mode, tts_by_year_month_spnv_effort_highlight_mode)
        self.assertEqual(actual.tts_by_year_month_spnv_effort_highlight_column_names, tts_by_year_month_spnv_effort_highlight_column_names)
        self.assertEqual(actual.tts_by_year_spnv_formatters, tts_by_year_spnv_formatters)
        self.assertEqual(actual.tts_by_year_spnv_effort_highlight, tts_by_year_spnv_effort_highlight)
        self.assertEqual(actual.tts_by_year_spnv_effort_highlight_mode, tts_by_year_spnv_effort_highlight_mode)
        self.assertEqual(actual.tts_by_year_spnv_effort_highlight_column_names, tts_by_year_spnv_effort_highlight_column_names)
        self.assertEqual(actual.tts_by_spn_formatters, tts_by_spn_formatters)
        self.assertEqual(actual.tts_by_spn_remove_untagged, tts_by_spn_remove_untagged)
        self.assertEqual(actual.tts_by_spn_effort_highlight, tts_by_spn_effort_highlight)
        self.assertEqual(actual.tts_by_spn_effort_highlight_mode, tts_by_spn_effort_highlight_mode)
        self.assertEqual(actual.tts_by_spn_effort_highlight_column_names, tts_by_spn_effort_highlight_column_names)
        self.assertEqual(actual.tts_by_hashtag_formatters, tts_by_hashtag_formatters)
        self.assertEqual(actual.tts_by_hashtag_year_enable_pivot, tts_by_hashtag_year_enable_pivot)
        self.assertEqual(actual.tts_by_hashtag_year_effort_highlight_mode, tts_by_hashtag_year_effort_highlight_mode)
        self.assertEqual(actual.tts_by_hashtag_year_effort_highlight, tts_by_hashtag_year_effort_highlight)
        self.assertEqual(actual.tts_by_efs_is_correct, tts_by_efs_is_correct)
        self.assertEqual(actual.tts_by_efs_n, tts_by_efs_n)
        self.assertEqual(actual.tts_by_tr_unknown_id, tts_by_tr_unknown_id)
        self.assertEqual(actual.tts_by_tr_remove_unknown_occurrences, tts_by_tr_remove_unknown_occurrences)
        self.assertEqual(actual.tts_by_tr_filter_by_top_n, tts_by_tr_filter_by_top_n)
        self.assertEqual(actual.tts_by_tr_head_n, tts_by_tr_head_n)
        self.assertEqual(actual.tts_by_tr_display_head_n_with_tail, tts_by_tr_display_head_n_with_tail)
        self.assertEqual(actual.tts_gantt_spnv_spns, tts_gantt_spnv_spns)
        self.assertEqual(actual.tts_gantt_spnv_criteria, tts_gantt_spnv_criteria)
        self.assertEqual(actual.tts_gantt_spnv_months, tts_gantt_spnv_months)
        self.assertEqual(actual.tts_gantt_spnv_min_duration, tts_gantt_spnv_min_duration)
        self.assertEqual(actual.tts_gantt_spnv_fig_size, tts_gantt_spnv_fig_size)
        self.assertEqual(actual.tts_gantt_spnv_title, tts_gantt_spnv_title)
        self.assertEqual(actual.tts_gantt_spnv_x_label, tts_gantt_spnv_x_label)
        self.assertEqual(actual.tts_gantt_spnv_y_label, tts_gantt_spnv_y_label)
        self.assertEqual(actual.tts_gantt_spnv_formatters, tts_gantt_spnv_formatters)
        self.assertEqual(actual.tts_gantt_hseq_hashtags, tts_gantt_hseq_hashtags)
        self.assertEqual(actual.tts_gantt_hseq_criteria, tts_gantt_hseq_criteria)
        self.assertEqual(actual.tts_gantt_hseq_months, tts_gantt_hseq_months)
        self.assertEqual(actual.tts_gantt_hseq_min_duration, tts_gantt_hseq_min_duration)
        self.assertEqual(actual.tts_gantt_hseq_fig_size, tts_gantt_hseq_fig_size)
        self.assertEqual(actual.tts_gantt_hseq_title, tts_gantt_hseq_title)
        self.assertEqual(actual.tts_gantt_hseq_x_label, tts_gantt_hseq_x_label)
        self.assertEqual(actual.tts_gantt_hseq_y_label, tts_gantt_hseq_y_label)
        self.assertEqual(actual.tts_gantt_hseq_formatters, tts_gantt_hseq_formatters)
        self.assertEqual(actual.effort_highlighter_tags, effort_highlighter_tags)
        self.assertEqual(actual.md_infos, md_infos)
        self.assertEqual(actual.md_last_update, md_last_update)
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

    def test_getyearlytarget_shouldreturnexpectedhours_whenyearinlist(self):

        # Arrange
        yearly_targets : list[YearlyTarget] = ObjectMother.get_yearly_targets()
        year : int = 2024
        expected_hours : timedelta = timedelta(hours = 250)

        # Act
        actual_hours : timedelta = cast(YearlyTarget, self.df_helper.get_yearly_target(yearly_targets = yearly_targets, year = year)).hours

        # Assert
        self.assertEqual(expected_hours, actual_hours)
    def test_getyearlytarget_shouldreturnnone_whenyearnotinlist(self):

        # Arrange
        yearly_targets : list[YearlyTarget] = ObjectMother.get_yearly_targets()
        year : int = 2010

        # Act
        yearly_target : Optional[YearlyTarget] = self.df_helper.get_yearly_target(yearly_targets = yearly_targets, year = year)

        # Assert
        self.assertIsNone(yearly_target)
    def test_isyearlytargetmet_shouldreturntrue_whenyearlytargetismet(self):

        # Arrange
        effort : timedelta = pd.Timedelta(hours = 255, minutes = 30)
        yearly_target : timedelta = pd.Timedelta(hours = 250)

        # Act
        actual : bool = self.df_helper.is_yearly_target_met(effort = effort, yearly_target = yearly_target)
        
        # Assert
        self.assertTrue(actual)
    def test_isyearlytargetmet_shouldreturnfalse_whenyearlytargetisnotmet(self):

        # Arrange
        effort : timedelta = pd.Timedelta(hours = 249)
        yearly_target : timedelta = pd.Timedelta(hours = 250)

        # Act
        actual : bool = self.df_helper.is_yearly_target_met(effort = effort, yearly_target = yearly_target)

        # Assert
        self.assertFalse(actual)
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
        actual : str = self.df_helper.create_time_range_id(start_time = start_time, end_time = end_time, unknown_id = unknown_id)

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

    @parameterized.expand([
        [["Month", "2015"], True],
        [["Month", "2015", "↕", "2016"], True],
        [["Month", "2015", "↕", "2016", "↕", "2017"], True],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018"], True],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019"], True],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020"], True],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020", "↕", "2021"], True],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020", "↕", "2021", "↕", "2022"], True],
        [[], False],
        [["Month"], False],
        [["Month", "2015", "↕"], False],
        [["Month", "2015", "↕", "2016", "↕"], False],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕"], False],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕"], False],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕"], False],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020", "↕"], False],
        [["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020", "↕", "2021", "↕"], False],
        [["Month", "↕"], False],
        [["Month", "↕", "↕"], False],
        [["Month", "2015", "2015"], False],
        [["Month", "2015", "↕", "↕"], False]
    ])
    def test_isbym_shouldreturnexpectedbool_wheninvoked(self, column_list : list[str], expected : bool) -> None:
        
        # Arrange
        # Act
        actual : bool = self.df_helper.is_bym(column_list = column_list) # type: ignore

        # Assert
        self.assertEqual(expected, actual)

    def test_unboxbymcolumnlist_shouldrenamecolumnnamesprogressively_wheninvoked(self) -> None:

        # Arrange
        boxed_data : dict[str, list[Any]] = {
            TTCN.MONTH: [1, 2],
            "2015": [100, 200],
            TTCN.TREND: ["↑", "↓"],
            "2016": [500, 600],
            TTCN.TREND: ["=", "↑"],
            "2017": [900, 1000]
        }
        boxed_columns : list[str] = [TTCN.MONTH, "2015", TTCN.TREND, "2016", TTCN.TREND, "2017"]
        boxed_df : DataFrame = DataFrame(boxed_data, columns = boxed_columns)

        expected : list[str] = [TTCN.MONTH, "2015", f"{TTCN.TREND}1", "2016", f"{TTCN.TREND}2", "2017"]

        # Act
        actual : DataFrame = self.df_helper.unbox_bym_column_list(df = boxed_df)

        # Assert
        self.assertEqual(list(actual.columns), expected)
    def test_boxbymcolumnlist_shouldrevertcolumnnames_wheninvoked(self) -> None:

        # Arrange
        unboxed_data : dict[str, list[Any]] = {
            TTCN.MONTH: [1, 2],
            "2015": [100, 200],
            f"{TTCN.TREND}1": ["↑", "↓"],
            "2016": [500, 600],
            f"{TTCN.TREND}2": ["=", "↑"],
            "2017": [900, 1000]
        }
        unboxed_columns : list[str] = [TTCN.MONTH, "2015", f"{TTCN.TREND}1", "2016", f"{TTCN.TREND}2", "2017"]
        unboxed_df : DataFrame = DataFrame(unboxed_data, columns = unboxed_columns)

        expected : list[str] = [TTCN.MONTH, "2015", TTCN.TREND, "2016", TTCN.TREND, "2017"]

        # Act
        actual : DataFrame = self.df_helper.box_bym_column_list(df = unboxed_df)

        # Assert
        self.assertEqual(list(actual.columns), expected)
class BYMFactoryTestCase(unittest.TestCase):

    def setUp(self):

        self.bym_factory = BYMFactory(df_helper = TTDataFrameHelper())

    @parameterized.expand([
        [timedelta(minutes=30), timedelta(hours=1), "↑"],
        [timedelta(hours=1), timedelta(minutes=30), "↓"],
        [timedelta(minutes=30), timedelta(minutes=30), "="],
    ])
    def test_gettrendbytimedelta_shouldreturnexpectedtrend_wheninvoked(
        self, 
        td_1 : timedelta, 
        td_2 : timedelta, 
        expected : str
    ):
        
        # Arrange
        # Act
        actual : str = self.bym_factory._BYMFactory__get_trend_by_timedelta(td_1 = td_1, td_2 = td_2)   # type: ignore

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        ["↕1", TTCN.TREND],
        ["2016", "2016"],
    ])
    def test_tryconsolidatetrendcolumnname_shouldreturnexpectedcolumnname_wheninvoked(
        self, 
        column_name: str, 
        expected: str
    ):

        # Arrange
        # Act
        actual : str = self.bym_factory._BYMFactory__try_consolidate_trend_column_name(column_name = column_name)   # type: ignore

        # Assert
        self.assertEqual(expected, actual)

    def test_createttsbymonthtpl_shouldreturnexpectedtuple_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        now : datetime = datetime(2024, 11, 30) 
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_tpl : Tuple[DataFrame, DataFrame] = ObjectMother().get_tts_by_month_tpl()

        # Act
        actual_tpl : Tuple[DataFrame, DataFrame]  = self.bym_factory.create_tts_by_month_tpl(
            tt_df = tt_df, 
            years = years,
            now = now
        )

        # Assert
        assert_frame_equal(expected_tpl[0] , actual_tpl[0])
        assert_frame_equal(expected_tpl[1] , actual_tpl[1])  
class BYMSplitterTestCase(unittest.TestCase):

    def setUp(self):
        self.bym_splitter = BYMSplitter(df_helper = TTDataFrameHelper())
    
    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:

        # Arrange
        df_helper : TTDataFrameHelper = TTDataFrameHelper()

        # Act
        bym_splitter : BYMSplitter = BYMSplitter(df_helper = df_helper)

        # Assert
        self.assertIsInstance(bym_splitter, BYMSplitter)

    @parameterized.expand([
        (1, True),
        (7, True),
        (13, True),
        (25, True),
        (49, True),
        (8, False),
        (-7, False),
    ])
    def test_isinsequence_shouldreturnexpectedbool_wheninvoked(self, number : int, expected : bool) -> None:
        
        # Arrange
        # Act
        actual : bool = self.bym_splitter._BYMSplitter__is_in_sequence(number = number)  # type: ignore
        
        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        (1, [1], True),
        (5, [1, 2, 3, 4, 5], True),
        (1, [], False),
        (0, [1], False),
        (4, [1, 2, 3, 4, 5], False),
    ])
    def test_islast_shouldreturnexpectedbool_wheninvoked(self, number : int, lst : list[int], expected : bool) -> None:
        
        # Arrange
        # Act
        actual : bool = self.bym_splitter._BYMSplitter__is_last(number = number, lst = lst)  # type: ignore

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        [[0, 1], [0, 1]],
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]]
    ])
    def test_createcolumnnumbers_shouldreturnexpectedcolumnnumbers_wheninvoked(self, index_list : list[int], expected : list[int]) -> None:
        
        # Arrange
        df : DataFrame = ObjectMother.get_tts_by_month_df(index_list = index_list)
        
        # Act
        actual : list[int] = self.bym_splitter._BYMSplitter__create_column_numbers(df = df) # type: ignore

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        [[0, 1, 2], [0, 2]],
        [[0, 1, 2, 3, 4], [0, 1, 4]]
    ])
    def test_filterbyindexlist_shouldreturnfiltereddf_wheninvoked(self, index_list : list[int], expected_indices : list[int]) -> None:
        
        # Arrange
        df : DataFrame = ObjectMother.get_tts_by_month_df(index_list = index_list)
        expected_columns : list[str] = [df.columns[i] for i in expected_indices]
        
        # Act
        filtered_df : DataFrame = self.bym_splitter._BYMSplitter__filter_by_index_list(df = df, index_list = expected_indices) # type: ignore
        
        # Assert
        self.assertEqual(filtered_df.columns.tolist(), expected_columns)

    @parameterized.expand([
        [[0, 1, 2, 3, 4], [[0, 1], [2, 3]]],
        [[0, 1, 2, 3, 4, 5], [[0, 2, 4], [1, 3, 5]]]
    ])
    def test_filterbyindexlists_shouldreturnexpectedsubdfs_wheninvoked(self, index_list : list[int], expected_indices : list[list[int]]) -> None:
        
        # Arrange
        df : DataFrame = ObjectMother.get_tts_by_month_df(index_list = index_list)
        expected_columns : list[list[str]] = [[df.columns[i] for i in index_list] for index_list in expected_indices]
        
        # Act
        sub_dfs : list[DataFrame] = self.bym_splitter._BYMSplitter__filter_by_index_lists(df = df, index_lists = expected_indices) # type: ignore
        
        # Assert
        self.assertEqual(len(sub_dfs), len(expected_columns))
        for i, sub_df in enumerate(sub_dfs):
            self.assertEqual(sub_df.columns.tolist(), expected_columns[i])

    @parameterized.expand([
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], [ [0, 1, 2, 3, 4, 5, 6, 7], [0, 7, 8, 9, 10, 11, 12, 13], [0, 13, 14, 15, 16, 17, 18, 19] ]],
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], [ [0, 1, 2, 3, 4, 5, 6, 7], [0, 7, 8, 9, 10, 11, 12, 13], [0, 13, 14, 15, 16, 17] ]]
    ])
    def test_createindexlists_shouldreturnexpectedlistoflists_wheninvoked(self, column_numbers : list[int], expected : list[list[int]]) -> None:
        
        # Arrange
        # Act
        actual : list[list[int]] = self.bym_splitter._BYMSplitter__create_index_lists(column_numbers = column_numbers) # type: ignore

        # Assert
        self.assertEqual(expected, actual)

    @parameterized.expand([
        [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 
            [ ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018"], ["Month", "2018", "↕", "2019", "↕", "2020", "↕", "2021"], ["Month", "2021", "↕", "2022", "↕", "2023", "↕", "2024"] ]
        ],
        [
            [0, 1], 
            [ ["Month", "2015"] ]
        ]
    ])
    def test_createsubdfs_shouldreturnexpectedsubdfs_wheninvoked(self, index_list : list[int], expected_column_names : list[list[str]]) -> None:
        
        # Arrange
        df : DataFrame = ObjectMother.get_tts_by_month_df(index_list = index_list)
        
        # Act
        sub_dfs : list[DataFrame] = self.bym_splitter.create_sub_dfs(df = df)
        
        # Assert
        self.assertEqual(len(sub_dfs), len(expected_column_names))
        for i, sub_df in enumerate(sub_dfs):
            self.assertEqual(sub_df.columns.tolist(), expected_column_names[i])
    
    def test_createsubdfs_shouldraiseexception_wheninvaliddf(self) -> None:
        
        # Arrange
        df : DataFrame = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.bym_splitter.create_sub_dfs(df = df)
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
    def test_applytextualhighlights_shouldsurroundeffortcellsswithtokens_wheninvoked(self) -> None:

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
        actual : DataFrame = self.effort_highlighter._EffortHighlighter__apply_textual_highlights(self.df_without_duplicates, effort_cells, tags)   # type: ignore

        # Assert
        self.assertTrue(expected.equals(actual))

    def test_createtextualstyler_shouldhighlightexpectedcells_whencolumnnamesareprovided(self) -> None:

        # Arrange
        mode : EFFORTMODE = EFFORTMODE.top_one_effort_per_row
        tags : Tuple[str, str] = ("[[ ", " ]]")
        column_names : list[str] = ["2015", "2016", "2017"]

        expected : DataFrame = self.df_without_duplicates.copy(deep = True)
        expected.iloc[0, 5] = "[[ 88h 30m ]]"
        expected.iloc[1, 5] = "[[ 65h 30m ]]"

        # Act
        actual : DataFrame = self.effort_highlighter.create_textual_styler(self.df_without_duplicates, mode, tags, column_names) # type: ignore

        # Assert
        assert_frame_equal(expected, actual)
    def test_createtextualstyler_shouldhighlightexpectedcells_whencolumnnamesarenotprovided(self) -> None:

        # Arrange
        mode : EFFORTMODE = EFFORTMODE.top_one_effort_per_row
        tags : Tuple[str, str] = ("[[ ", " ]]")
        column_names : list[str] = []

        expected : DataFrame = self.df_without_duplicates.copy(deep = True)
        expected.iloc[0, 5] = "[[ 88h 30m ]]"
        expected.iloc[1, 5] = "[[ 65h 30m ]]"

        # Act
        actual : DataFrame = self.effort_highlighter.create_textual_styler(self.df_without_duplicates, mode, tags, column_names) # type: ignore

        # Assert
        assert_frame_equal(expected, actual)
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
    def test_createttsbyyeardf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        yearly_targets : list[YearlyTarget] = [ YearlyTarget(year = 2024, hours = timedelta(hours = 250)) ]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_year_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_year_df(tt_df = tt_df, years = years, yearly_targets = yearly_targets)

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbyyearmonthtpl_shouldreturnexpectedtuple_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        yearly_targets : list[YearlyTarget] = [ YearlyTarget(year = 2024, hours = timedelta(hours = 250)) ]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_tpl : Tuple[DataFrame, DataFrame] = ObjectMother().get_tts_by_year_month_tpl()

        # Act
        actual_tpl : Tuple[DataFrame, DataFrame]  = self.df_factory.create_tts_by_year_month_tpl(
            tt_df = tt_df, 
            years = years, 
            yearly_targets = yearly_targets,
            display_only_years = years
        )

        # Assert
        assert_frame_equal(expected_tpl[0] , actual_tpl[0])
        assert_frame_equal(expected_tpl[1] , actual_tpl[1])
    def test_createttsbyyearmonthspnvtpl_shouldreturnexpectedtuple_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_tpl : Tuple[DataFrame, DataFrame] = ObjectMother().get_tts_by_year_month_spnv_tpl()

        # Act
        actual_tpl : Tuple[DataFrame, DataFrame]  = self.df_factory.create_tts_by_year_month_spnv_tpl(
            tt_df = tt_df, 
            years = years, 
            software_project_names = software_project_names,
            software_project_name = software_project_names[0]
        )

        # Assert
        assert_frame_equal(expected_tpl[0] , actual_tpl[0])
        assert_frame_equal(expected_tpl[1] , actual_tpl[1])
    def test_createttsbyyearspnvtpl_shouldreturnexpectedtuple_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_tpl : Tuple[DataFrame, DataFrame] = ObjectMother().get_tts_by_year_spnv_tpl()

        # Act
        actual_tpl : Tuple[DataFrame, DataFrame]  = self.df_factory.create_tts_by_year_spnv_tpl(
            tt_df = tt_df, 
            years = years, 
            software_project_names = software_project_names,
            software_project_name = software_project_names[0]
            )

        # Assert
        assert_frame_equal(expected_tpl[0] , actual_tpl[0])
        assert_frame_equal(expected_tpl[1] , actual_tpl[1])    
    def test_createttsbyspnspvdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        years : list[int] = [2024]
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_spn_spv_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_spn_spv_df(
            tt_df = tt_df, 
            years = years, 
            software_project_names = software_project_names
        )

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbytrdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        unknown_id : str = "Unknown"
        remove_unknown_occurrences : bool = True
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_tr_df()
        expected_df.sort_values(by = "TimeRangeId", ascending = True, inplace = True)
        expected_df.reset_index(drop = True, inplace = True)

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_tr_df(
            tt_df = tt_df, 
            unknown_id = unknown_id, 
            remove_unknown_occurrences = remove_unknown_occurrences
        )
        actual_df.sort_values(by = "TimeRangeId", ascending = True, inplace = True)
        actual_df.reset_index(drop = True, inplace = True)

        # Assert
        assert_frame_equal(expected_df, actual_df)  
    def test_createttsbyhashtagyeardf_shouldreturnexpecteddataframe_whenenablepivotisfalse(self):

        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()
        years : list[int] = [2024]
        enable_pivot : bool = False
        expected_df : DataFrame = ObjectMother().get_tts_by_hashtag_year_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_hashtag_year_df(
            tt_df = tt_df, 
            years = years, 
            enable_pivot = enable_pivot
        )

        # Assert
        assert_frame_equal(expected_df , actual_df)
    def test_createttsbyhashtagyeardf_shouldreturnexpecteddataframe_whenenablepivotistrue(self):

        # Arrange
        tt_df : DataFrame = ObjectMother().get_tt_df()
        years : list[int] = [2024]
        enable_pivot : bool = True

        expected_df : DataFrame = ObjectMother().get_tts_by_hashtag_year_df()
        expected_df = expected_df.pivot(index = TTCN.HASHTAG, columns = TTCN.YEAR, values = TTCN.EFFORT).reset_index()
        expected_df = expected_df.fillna("")

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_hashtag_year_df(
            tt_df = tt_df, 
            years = years, 
            enable_pivot = enable_pivot
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

    @parameterized.expand([
        [True],
        [False]
    ])
    def test_createttsbyspndf_shouldreturnexpecteddataframe_wheninvoked(self, remove_untagged : bool):

        # Arrange
        years : list[int] = [2024]
        software_project_names : list[str] = ["NW.NGramTextClassification", "NW.Shared.Serialization", "NW.UnivariateForecasting", "nwreadinglistmanager"]
        tt_df : DataFrame = ObjectMother().get_tt_df()
        expected_df : DataFrame = ObjectMother().get_tts_by_spn_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_tts_by_spn_df(
            tt_df = tt_df, 
            years = years, 
            software_project_names = software_project_names, 
            remove_untagged = remove_untagged
        )

        # Assert
        assert_frame_equal(expected_df , actual_df) 

    def test_createdefinitionsdf_shouldreturnexpecteddataframe_wheninvoked(self):

        # Arrange
        expected_df : DataFrame = ObjectMother().get_definitions_df()

        # Act
        actual_df : DataFrame  = self.df_factory.create_definitions_df()

        # Assert
        assert_frame_equal(expected_df , actual_df)
class TTMarkdownFactoryTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.md_factory : TTMarkdownFactory = TTMarkdownFactory(markdown_helper = MarkdownHelper(formatter = Formatter()))
        self.paragraph_title : str = "Time Tracking By Month"
        self.last_update : datetime = datetime(2024, 11, 30)
    def test_createttsbymonthsubmd_shouldreturnexpectedstring_wheninvoked(self) -> None:

		# Arrange
        tts_by_month_sub_dfs : list[DataFrame] = [ ObjectMother().get_tts_by_month_tpl()[0] ]
        expected : str = ObjectMother().get_tts_by_month_sub_md()
        expected_newlines : int = (9 + 14)

        # Act
        actual : str = self.md_factory.create_tts_by_month_sub_md(
            paragraph_title = self.paragraph_title, 
            last_update = self.last_update, 
            sub_dfs = tts_by_month_sub_dfs
        )
        actual_newlines : int = actual.count("\n")

        # Assert
        self.assertEqual(expected, actual)
        self.assertEqual(expected_newlines, actual_newlines)
class TTSequencerTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:

        # Arrange
        df_helper : TTDataFrameHelper = TTDataFrameHelper()

        # Act
        tt_sequencer : TTSequencer = TTSequencer(df_helper = df_helper)

        # Assert
        self.assertIsInstance(tt_sequencer, TTSequencer)
    def test_convertcriteriatovalue_shouldreturnboolean_wheninvoked(self) -> None:

        # Arrange
        df_helper : TTDataFrameHelper = TTDataFrameHelper()
        tt_sequencer : TTSequencer = TTSequencer(df_helper = df_helper)

        # Act & Assert
        self.assertIsNone(tt_sequencer._TTSequencer__convert_criteria_to_value(CRITERIA.do_nothing))   # type: ignore
        self.assertTrue(tt_sequencer._TTSequencer__convert_criteria_to_value(CRITERIA.include))        # type: ignore
        self.assertFalse(tt_sequencer._TTSequencer__convert_criteria_to_value(CRITERIA.exclude))       # type: ignore
    def test_convertcriteriatovalue_shouldraiseexception_wheninvalidcriteria(self) -> None:

        # Arrange
        df_helper : TTDataFrameHelper = TTDataFrameHelper()
        tt_sequencer : TTSequencer = TTSequencer(df_helper = df_helper)
        criteria : str = cast(CRITERIA, "invalid")

        # Act
        with self.assertRaises(Exception) as context:
            tt_sequencer._TTSequencer__convert_criteria_to_value(criteria = criteria)  # type: ignore

        # Assert
        self.assertEqual(
            str(context.exception),
            _MessageCollection.no_strategy_available_for_provided_criteria(criteria = criteria)
        )

    @parameterized.expand([
        ("2024-12-21", 1, "2024-11-21"),
        ("2024-12-21", 6, "2024-06-21"),
        ("2024-12-21", 12, "2023-12-21"),
    ])
    def test_calculatefromstartdate_shouldreturnexpecteddate_wheninvoked(self, now_str : str, months : int, expected_str : str) -> None:

        # Arrange
        now : datetime = datetime.strptime(now_str, "%Y-%m-%d")
        expected : date = datetime.strptime(expected_str, "%Y-%m-%d").date()
        df_helper : TTDataFrameHelper = TTDataFrameHelper()
        tt_sequencer : TTSequencer = TTSequencer(df_helper = df_helper)

        # Act
        actual : date = tt_sequencer._TTSequencer__calculate_from_start_date(now = now, months = months)   # type: ignore

        # Assert
        self.assertEqual(actual, expected)

    @parameterized.expand([
        ("14h 00m", 14),
        ("34h 15m", 34),
        ("13h 30m", 13),
        ("31h 45m", 32),
        ("07h 45m", 8),
        ("28h 15m", 28),
        ("35h 15m", 35)
    ])
    def test_roundeffort_shouldreturnexpectedint_wheninvoked(self, effort : str, expected : int) -> None:

        # Arrange
        df_helper : TTDataFrameHelper = TTDataFrameHelper()
        tt_sequencer : TTSequencer = TTSequencer(df_helper = df_helper)

        # Act
        actual : int = tt_sequencer._TTSequencer__round_effort(effort = effort)   # type: ignore

        # Assert
        self.assertEqual(actual, expected)
class TTAdapterTestCase(unittest.TestCase):

    def setUp(self) -> None:

        # Without Defaults
        self.tts_by_year_spnv_display_only_spn : Optional[str] = "nwshared"

        # With Defaults
        self.excel_path : str = "/home/nwtimetracking/nwtimetrackingmanager/data/Time Tracking.xlsx"
        self.excel_skiprows : int = 0
        self.excel_nrows : int = 100
        self.excel_tabname : str = "Sessions"
        self.years : list[int] = [2023, 2024]
        self.yearly_targets : list[YearlyTarget] = [
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
        self.now : datetime = datetime(2023, 12, 1)
        self.software_project_names : list[str] = [ "nwshared", "nwpackageversions"]
        self.software_project_names_by_spv : list[str] = [ "nwshared" ]
        self.tts_by_year_month_display_only_years : Optional[list[int]] = [2024]
        self.tts_by_hashtag_year_enable_pivot = False
        self.tts_by_spn_remove_untagged : bool = True
        self.tts_by_efs_is_correct : bool = True
        self.tts_by_tr_unknown_id : str = "Unknown"
        self.tts_by_tr_remove_unknown_occurrences : bool = True
        self.md_infos : list[MDInfo] = [
                MDInfo(id = TTID.TTSBYMONTH, file_name = "TIMETRACKINGBYMONTH.md", paragraph_title = "Time Tracking By Month")
            ]
        self.md_last_update : datetime = datetime(2023, 11, 25)

        # Other
        self.paragraph_title : str = "Time Tracking By Month"

    def test_orchestrateheadn_shouldreturnoriginaldataframe_whenheadnisnone(self) -> None:

        # Arrange
        tt_adapter : TTAdapter = TTAdapter(
            df_factory = Mock(), 
            bym_factory = Mock(), 
            bym_splitter = Mock(),
            tt_sequencer = Mock(),
            md_factory = Mock(),
            effort_highlighter = Mock()
        )

        df : DataFrame = DataFrame({"2015": ["10h 30m", "15h 45m"], "↕": ["↑", "↑"], "2016": ["20h 45m", "20h 00m"]})

        # Act
        actual : DataFrame = tt_adapter._TTAdapter__orchestrate_head_n(df = df, head_n = None, display_head_n_with_tail = False)    # type: ignore

        # Assert
        self.assertTrue(actual.equals(df))
    def test_orchestrateheadn_shouldreturntail_whenheadnisnotnoneanddisplayheadnwithtailistrue(self) -> None:

        # Arrange
        tt_adapter : TTAdapter = TTAdapter(
            df_factory = Mock(), 
            bym_factory = Mock(), 
            bym_splitter = Mock(),
            tt_sequencer = Mock(),
            md_factory = Mock(),
            effort_highlighter = Mock()
        )

        df : DataFrame = DataFrame({"2015": ["10h 30m", "15h 45m"], "↕": ["↑", "↑"], "2016": ["20h 45m", "20h 00m"]})
        head_n : Optional[int] = 2
        expected : DataFrame = df.tail(n = int(head_n))

        # Act
        actual : DataFrame = tt_adapter._TTAdapter__orchestrate_head_n(df = df, head_n = head_n, display_head_n_with_tail = True)    # type: ignore

        # Assert
        self.assertTrue(actual.equals(expected))
    def test_orchestrateheadn_shouldreturnhead_whenheadnisnotnoneanddisplayheadnwithtailisfalse(self) -> None:

        # Arrange
        tt_adapter : TTAdapter = TTAdapter(
            df_factory = Mock(), 
            bym_factory = Mock(), 
            bym_splitter = Mock(),
            tt_sequencer = Mock(),
            md_factory = Mock(),
            effort_highlighter = Mock()
        )

        df : DataFrame = DataFrame({"2015": ["10h 30m", "15h 45m"], "↕": ["↑", "↑"], "2016": ["20h 45m", "20h 00m"]})
        head_n : Optional[int] = 2
        expected : DataFrame = df.head(n = int(head_n))

        # Act
        actual : DataFrame = tt_adapter._TTAdapter__orchestrate_head_n(df = df, head_n = head_n, display_head_n_with_tail = False)    # type: ignore

        # Assert
        self.assertTrue(actual.equals(expected))
    def test_deleteduplicatetextualhighlighting_shouldreturnoriginalsubdfs_whenlessthan2dataframes(self) -> None:

        # Arrange
        tt_adapter : TTAdapter = TTAdapter(
            df_factory = Mock(), 
            bym_factory = Mock(), 
            bym_splitter = Mock(),
            tt_sequencer = Mock(),
            md_factory = Mock(),
            effort_highlighter = Mock()
        )

        sub_dfs : list[DataFrame] = [
            DataFrame({"2015": ["10h 30m", "15h 45m"], "↕": ["↑", "↑"], "2016": ["20h 45m", "20h 00m"]})
        ]
        tags : Tuple[str, str] = ("<mark style='background-color: COLORNAME.skyblue'>", "</mark>")

        # Act
        actual : List[DataFrame] = tt_adapter._TTAdapter__delete_duplicate_textual_highlighting(sub_dfs = sub_dfs, tags = tags)    # type: ignore

        # Assert
        self.assertEqual(len(actual), len(sub_dfs))
        self.assertTrue(actual[0].equals(sub_dfs[0]))
    def test_deleteduplicatetextualhighlighting_shouldremovetagsfromseconddataframeonward_whenmorethan1dataframe(self) -> None:

        # Arrange
        tt_adapter : TTAdapter = TTAdapter(
            df_factory = Mock(), 
            bym_factory = Mock(), 
            bym_splitter = Mock(),
            tt_sequencer = Mock(),
            md_factory = Mock(),
            effort_highlighter = Mock()
        )

        dict1 : dict = {
            "Month": [1, 2],
            "2021": ["00h 00m", "<tag>3h 00m</tag>"],
            "↕": ["↓", "↓"],
            "2022": ["00h 00m", "00h 00m"],
            "↕": ["↓", "↓"],
            "2023": ["00h 00m", "00h 00m"],
            "↕": ["↓", "↓"],
            "2024": ["<tag>01h 00m</tag>", "00h 00m"]
        }
        dict2 : dict = {
            "Month": [1, 2],
            "2024": ["<tag>01h 00m</tag>", "00h 00m"],
            "↕": ["↓", "↓"],
            "2025": ["00h 00m", "00h 00m"]
        }

        sub_dfs : list[DataFrame] = [
            DataFrame(dict1),
            DataFrame(dict2)
        ]
        tags : Tuple[str, str] = ("<tag>", "</tag>")
        
        expected1 : dict = {
            "Month": [1, 2],
            "2021": ["00h 00m", "<tag>3h 00m</tag>"],
            "↕": ["↓", "↓"],
            "2022": ["00h 00m", "00h 00m"],
            "↕": ["↓", "↓"],
            "2023": ["00h 00m", "00h 00m"],
            "↕": ["↓", "↓"],
            "2024": ["<tag>01h 00m</tag>", "00h 00m"]
        }
        expected2 : dict = {
            "Month": [1, 2],
            "2024": ["01h 00m", "00h 00m"],
            "↕": ["↓", "↓"],
            "2025": ["00h 00m", "00h 00m"]
        }
        expected : list[DataFrame] = [
            DataFrame(expected1),
            DataFrame(expected2)
        ]        
        # Act
        actual : list[DataFrame] = tt_adapter._TTAdapter__delete_duplicate_textual_highlighting(sub_dfs = sub_dfs, tags = tags)    # type: ignore

        # Assert
        self.assertEqual(len(actual), len(sub_dfs))
        assert_frame_equal(actual[0], expected[0])
        assert_frame_equal(actual[1], expected[1])

    def test_createttdf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.excel_path = self.excel_path
        setting_bag.excel_skiprows = self.excel_skiprows
        setting_bag.excel_nrows = 100
        setting_bag.excel_tabname = "Sessions"

        # Act
        tt_adapter._TTAdapter__create_tt_df(setting_bag = setting_bag)  # type: ignore

        # Assert
        df_factory.create_tt_df.assert_called_once_with(
            excel_path = self.excel_path,
            excel_skiprows = self.excel_skiprows,
            excel_nrows = self.excel_nrows,
            excel_tabname = self.excel_tabname
        )
    def test_createttsbymonthtpl_shouldcallbymfactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.years = self.years
        setting_bag.now = self.now

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_month_tpl(tt_df = tt_df, setting_bag = setting_bag)    # type: ignore

        # Assert
        bym_factory.create_tts_by_month_tpl.assert_called_once_with(
            tt_df = tt_df,
            years = self.years,
            now = self.now
        )
    def test_createttsbyyeardf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.years = self.years
        setting_bag.yearly_targets = self.yearly_targets

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_year_df(tt_df = tt_df, setting_bag = setting_bag)  # type: ignore

        # Assert
        df_factory.create_tts_by_year_df.assert_called_once_with(
            tt_df = tt_df,
            years = self.years,
            yearly_targets = self.yearly_targets
        )
    def test_createttsbyyearmonthdf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.years = self.years
        setting_bag.yearly_targets = self.yearly_targets
        setting_bag.tts_by_year_month_display_only_years = self.tts_by_year_month_display_only_years

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_year_month_tpl(tt_df = tt_df, setting_bag = setting_bag)   # type: ignore

        # Assert
        df_factory.create_tts_by_year_month_tpl.assert_called_once_with(
            tt_df = tt_df,
            years = self.years,
            yearly_targets = self.yearly_targets,
            display_only_years = self.tts_by_year_month_display_only_years
        )
    def test_createttsbyyearmonthspnvtpl_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.years = self.years
        setting_bag.software_project_names = self.software_project_names
        setting_bag.tts_by_year_month_spnv_display_only_spn = self.software_project_names_by_spv

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_year_month_spnv_tpl(tt_df = tt_df, setting_bag = setting_bag)  # type: ignore
        
        # Assert
        df_factory.create_tts_by_year_month_spnv_tpl.assert_called_once_with(
            tt_df = tt_df,
            years = self.years,
            software_project_names = self.software_project_names,
            software_project_name = self.software_project_names_by_spv
        )
    def test_createttsbyyearspnvtpl_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.years = self.years
        setting_bag.software_project_names = self.software_project_names
        setting_bag.tts_by_year_spnv_display_only_spn = self.tts_by_year_spnv_display_only_spn

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_year_spnv_tpl(tt_df = tt_df, setting_bag = setting_bag)    # type: ignore
        
        # Assert
        df_factory.create_tts_by_year_spnv_tpl.assert_called_once_with(
            tt_df = tt_df,
            years = self.years,
            software_project_names = self.software_project_names,
            software_project_name = self.tts_by_year_spnv_display_only_spn
        )
    def test_createttsbyspndf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.years = self.years
        setting_bag.software_project_names = self.software_project_names
        setting_bag.tts_by_spn_remove_untagged = self.tts_by_spn_remove_untagged

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_spn_df(tt_df = tt_df, setting_bag = setting_bag)   # type: ignore
        
        # Assert
        df_factory.create_tts_by_spn_df.assert_called_once_with(
            tt_df = tt_df,
            years = self.years,
            software_project_names = self.software_project_names,
            remove_untagged = self.tts_by_spn_remove_untagged
        )
    def test_createttsbyspnspvdf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.years = self.years
        setting_bag.software_project_names = self.software_project_names

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_spn_spv_df(tt_df = tt_df, setting_bag = setting_bag)   # type: ignore
        
        # Assert
        df_factory.create_tts_by_spn_spv_df.assert_called_once_with(
            tt_df = tt_df,
            years = self.years,
            software_project_names = self.software_project_names
        )
    def test_createttsbyhashtagyeardf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.years = self.years
        setting_bag.tts_by_hashtag_year_enable_pivot = self.tts_by_hashtag_year_enable_pivot

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_hashtag_year_df(tt_df = tt_df, setting_bag = setting_bag)  # type: ignore
        
        # Assert
        df_factory.create_tts_by_hashtag_year_df.assert_called_once_with(
            tt_df = tt_df,
            years = self.years,
            enable_pivot = self.tts_by_hashtag_year_enable_pivot
        )
    def test_createttsbyefstpl_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.tts_by_efs_is_correct = self.tts_by_efs_is_correct

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_efs_tpl(tt_df = tt_df, setting_bag = setting_bag)  # type: ignore
        
        # Assert
        df_factory.create_tts_by_efs_tpl.assert_called_once_with(
            tt_df = tt_df,
            is_correct = self.tts_by_efs_is_correct
        )
    def test_createttsbytrdf_shouldcalldffactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.tts_by_tr_unknown_id = self.tts_by_tr_unknown_id
        setting_bag.tts_by_tr_remove_unknown_occurrences = self.tts_by_tr_remove_unknown_occurrences

        tt_df : Mock = Mock()

        # Act
        tt_adapter._TTAdapter__create_tts_by_tr_df(tt_df = tt_df, setting_bag = setting_bag)    # type: ignore
        
        # Assert
        df_factory.create_tts_by_tr_df.assert_called_once_with(
            tt_df = tt_df,
            unknown_id = self.tts_by_tr_unknown_id,
            remove_unknown_occurrences = self.tts_by_tr_remove_unknown_occurrences
        )
    def test_createttsbymonthmd_shouldcallmdfactorywithexpectedarguments_wheninvoked(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        setting_bag : Mock = Mock()
        setting_bag.md_infos = self.md_infos
        setting_bag.md_last_update = self.md_last_update

        tts_by_month_sub_dfs : list[DataFrame] = [Mock(), Mock()]

        # Act
        tt_adapter._TTAdapter__create_tts_by_month_sub_md(tts_by_month_sub_dfs = tts_by_month_sub_dfs, setting_bag = setting_bag)   # type: ignore

        # Assert
        md_factory.create_tts_by_month_sub_md.assert_called_once_with(
            paragraph_title = self.md_infos[0].paragraph_title,
            last_update = self.md_last_update,
            sub_dfs = tts_by_month_sub_dfs
        )
    
    @parameterized.expand([
        ("_TTAdapter__create_tt_df"),
        ("_TTAdapter__create_tt_styler"),
        ("_TTAdapter__create_tts_by_month_tpl"),
        ("_TTAdapter__create_tts_by_month_styler"),
        ("_TTAdapter__create_tts_by_month_sub_dfs"),
        ("_TTAdapter__create_tts_by_month_sub_md"),
        ("_TTAdapter__create_tts_by_year_df"),
        ("_TTAdapter__create_tts_by_year_styler"),
        ("_TTAdapter__create_tts_by_year_month_tpl"),
        ("_TTAdapter__create_tts_by_year_month_styler"),
        ("_TTAdapter__create_tts_by_year_month_spnv_tpl"),
        ("_TTAdapter__create_tts_by_year_month_spnv_styler"),
        ("_TTAdapter__create_tts_by_year_spnv_tpl"),
        ("_TTAdapter__create_tts_by_year_spnv_styler"),
        ("_TTAdapter__create_tts_by_spn_df"),
        ("_TTAdapter__create_tts_by_spn_styler"),
        ("_TTAdapter__create_tts_by_spn_spv_df"),
        ("_TTAdapter__create_tts_by_hashtag_year_df"),
        ("_TTAdapter__create_tts_by_hashtag_year_styler"),
        ("_TTAdapter__create_tts_by_efs_tpl"),
        ("_TTAdapter__create_tts_by_tr_df"),
        ("_TTAdapter__create_tts_by_tr_styler"),
        ("_TTAdapter__create_tts_gantt_spnv_df"),
        ("_TTAdapter__create_tts_gantt_spnv_plot_function"),
        ("_TTAdapter__create_tts_gantt_hseq_df"),
        ("_TTAdapter__create_tts_gantt_hseq_plot_function")
    ])    
    def test_createsummary_shouldcallprivatemethod_wheninvoked(self, method_name : str) -> None:
        
        # This method uses MagicMock instead of Mock to avoid the "TypeError: Mock object is not subscriptable" error.

        # Arrange
        df_factory : MagicMock = MagicMock()
        bym_factory : MagicMock = MagicMock()
        bym_splitter : MagicMock = MagicMock()
        tt_sequencer : MagicMock = MagicMock()
        md_factory : MagicMock = MagicMock()
        effort_highlighter : MagicMock = MagicMock()

        setting_bag : SettingBag = ObjectMother.get_setting_bag()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory,
            bym_factory = bym_factory,
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        # Act, Assert
        with patch.object(TTAdapter, method_name) as mocked_method:
                   
            tt_summary : TTSummary = tt_adapter.create_summary(setting_bag = setting_bag)

            # Assert
            mocked_method.assert_called_once()

    def test_extractfilenameandparagraphtitle_shouldreturnexpectedvalues_whenidexists(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )

        id : TTID = TTID.TTSBYMONTH
        setting_bag : SettingBag = Mock(md_infos = self.md_infos)

        # Act
        actual : Tuple[str, str] = tt_adapter.extract_file_name_and_paragraph_title(id = id, setting_bag = setting_bag)

        # Assert
        self.assertEqual(actual, ("TIMETRACKINGBYMONTH.md", "Time Tracking By Month"))
    def test_extractfilenameandparagraphtitle_shouldraiseexception_wheniddoesnotexist(self) -> None:
        
        # Arrange
        df_factory : TTDataFrameFactory = Mock()
        bym_factory : BYMFactory = Mock()
        bym_splitter : BYMSplitter = Mock()
        tt_sequencer : TTSequencer = Mock()
        md_factory : TTMarkdownFactory = Mock()
        effort_highlighter : EffortHighlighter = Mock()

        tt_adapter : TTAdapter = TTAdapter(
            df_factory = df_factory, 
            bym_factory = bym_factory, 
            bym_splitter = bym_splitter,
            tt_sequencer = tt_sequencer,
            md_factory = md_factory,
            effort_highlighter = effort_highlighter
        )
        
        id : TTID = TTID.TTSBYMONTH

        md_infos : list[MDInfo] = [
            MDInfo(id = Mock(id = "other_id"), file_name = "OTHERFILE.md", paragraph_title = "Other Title")
        ]
        setting_bag : SettingBag = Mock(md_infos = md_infos)

        # Act
        with self.assertRaises(Exception) as context:
            tt_adapter.extract_file_name_and_paragraph_title(id = id, setting_bag = setting_bag)
        
        # Assert
        self.assertEqual(str(context.exception), _MessageCollection.no_mdinfo_found(id = id))   
class SettingSubsetTestCase(unittest.TestCase):

    def setUp(self) -> None:
	
        self.working_folder_path : str = "/home/nwtimetracking/"
        self.excel_skiprows : int = 0
		
        self.subset : SettingSubset = SettingSubset(
            working_folder_path = self.working_folder_path,
            excel_skiprows = self.excel_skiprows
        )
    def test_init_shouldassignproperties_wheninvoked(self) -> None:

		# Arrange
		# Act
        # Assert
        self.assertEqual(self.subset.working_folder_path, self.working_folder_path)
        self.assertEqual(self.subset.excel_skiprows, self.excel_skiprows)
        self.assertIsInstance(self.subset.working_folder_path, str)
        self.assertIsInstance(self.subset.excel_skiprows, int)
    def test_str_shouldreturnexpectedstring_wheninvoked(self) -> None:

        # Arrange
        expected : str = json.dumps({
            "working_folder_path": self.working_folder_path,
            "excel_skiprows": self.excel_skiprows
        })

        # Act
        actual_str : str = str(self.subset)
        actual_repr : str = repr(self.subset)

        # Assert
        self.assertEqual(actual_str, expected)
        self.assertEqual(actual_repr, expected)
class TTLoggerTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.definitions_df : DataFrame = ObjectMother().get_definitions_df()
        self.setting_bag : SettingBag = ObjectMother().get_setting_bag()
    def test_init_shouldinitializeobjectwithexpectedproperties_wheninvoked(self) -> None:

        # Arrange
        logging_function : Callable[[str], None] = LambdaProvider().get_default_logging_function()

        # Act
        actual : TTLogger = TTLogger(logging_function = logging_function)

        # Assert
        self.assertEqual(actual._TTLogger__logging_function, logging_function)      # type: ignore
        self.assertIsInstance(actual._TTLogger__logging_function, FunctionType)     # type: ignore

    @parameterized.expand([
        (TTCN.DME, "Total Development Monthly Effort"),
        (TTCN.TME, "Total Monthly Effort")
    ])
    def test_trylogcolumndefinitions_shouldlogdefinitions_whencolumnnamesmatch(self, column_name : str, definition : str) -> None:

        # Arrange
        logging_function : Mock = Mock()
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)
        df : DataFrame = DataFrame(columns = [column_name, "SomeColumn"])

        # Act
        tt_logger.try_log_column_definitions(df = df, definitions = self.definitions_df)

        # Assert
        logging_function.assert_any_call(f"{column_name}: {definition}")

    @parameterized.expand([
        (["SomeColumn", "SomeOtherColumn"], 0)
    ])
    def test_trylogcolumndefinitions_shouldnotlogdefinitions_whennomatchingcolumns(self, columns : list[str], expected_call_count : int) -> None:

        # Arrange
        logging_function : Mock = Mock()
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)
        df : DataFrame = DataFrame(columns = columns)

        # Act
        tt_logger.try_log_column_definitions(df = df, definitions = self.definitions_df)

        # Assert
        self.assertEqual(logging_function.call_count, expected_call_count)

    @parameterized.expand([
        (TTCN.DME, "Total Development Monthly Effort"),
        (TTCN.TME, "Total Monthly Effort")
    ])
    def test_trylogtermdefinition_shouldlogdefinition_whenmatchingtermexists(self, term : str, definition : str) -> None:

        # Arrange
        logging_function : Mock = Mock()
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)

        # Act
        tt_logger.try_log_term_definition(term = term, definitions = self.definitions_df)

        # Assert
        logging_function.assert_any_call(f"{term}: {definition}")

    @parameterized.expand([
        ("NonExistentTerm", 0)
    ])
    def test_trylogtermdefinition_shouldnotlogdefinition_whenmatchingtermdoesnotexist(self, term : str, expected_call_count : int) -> None:

        # Arrange
        logging_function : Mock = Mock()
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)

        # Act
        tt_logger.try_log_term_definition(term = term, definitions = self.definitions_df)

        # Assert
        self.assertEqual(logging_function.call_count, expected_call_count)

    def test_createsettingsubset_shouldreturnsubsetwithmatchingproperties_whenidsprovided(self) -> None:
        
        # Arrange
        logging_function : Mock = Mock()
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)        
        setting_names : list[str] = ["working_folder_path"]

        # Act
        actual : SettingSubset = tt_logger._TTLogger__create_setting_subset(setting_bag = self.setting_bag, setting_names = setting_names) # type: ignore

        # Assert
        self.assertIsInstance(actual, SettingSubset)
        self.assertEqual(actual.working_folder_path, self.setting_bag.working_folder_path)
        with self.assertRaises(AttributeError):
            _ = actual.excel_skiprows
    def test_trylogsettings_shouldlogsubset_whenidsprovided(self) -> None:
        
        # Arrange
        messages : list[str] = []
        logging_function : Callable[[str], None] = lambda msg : messages.append(msg)
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)        
        setting_names : list[str] = ["working_folder_path"]

        # Act
        tt_logger.try_log_settings(setting_bag = self.setting_bag, setting_names = setting_names)

        # Assert
        self.assertEqual(len(messages), 1)
        self.assertIn(self.setting_bag.working_folder_path, messages[0])
    def test_trylogsettings_shouldnotloganything_whenidsisempty(self) -> None:
        
        # Arrange
        messages : list[str] = []
        logging_function : Callable[[str], None] = lambda msg : messages.append(msg)
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)        
        setting_names : list[str] = []

        # Act
        tt_logger.try_log_settings(setting_bag = self.setting_bag, setting_names = setting_names)

        # Assert
        self.assertEqual(len(messages), 0)

    @parameterized.expand([
        ("Some message")
    ])
    def test_log_shouldlogmessage_whenmessageisprovided(self, msg : str) -> None:

        # Arrange
        logging_function : Mock = Mock()
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)

        # Act
        tt_logger.log(msg = msg)

        # Assert
        logging_function.assert_called_once_with(msg)

    @parameterized.expand([
        ("")
    ])
    def test_log_shouldnotlogmessage_whenmessageisempty(self, msg : str) -> None:

        # Arrange
        logging_function : Mock = Mock()
        tt_logger : TTLogger = TTLogger(logging_function = logging_function)

        # Act
        tt_logger.log(msg = msg)

        # Assert
        logging_function.assert_not_called()
class ComponentBagTestCase(unittest.TestCase):

    def test_init_shouldinitializeobjectwithexpectedproperties_whendefault(self) -> None:

        # Arrange
        # Act
        component_bag : ComponentBag = ComponentBag(
            file_path_manager = FilePathManager(),
            file_manager = FileManager(file_path_manager = FilePathManager()),
            displayer = Displayer(),
            tt_logger = TTLogger(logging_function = LambdaProvider().get_default_logging_function()),
            tt_adapter = TTAdapter(
                df_factory = TTDataFrameFactory(df_helper = TTDataFrameHelper()), 
                bym_factory = BYMFactory(df_helper = TTDataFrameHelper()),
                bym_splitter = BYMSplitter(df_helper = TTDataFrameHelper()),
                tt_sequencer = TTSequencer(df_helper = TTDataFrameHelper()),
                md_factory = TTMarkdownFactory(markdown_helper = MarkdownHelper(formatter = Formatter())
                ),
                effort_highlighter = EffortHighlighter(df_helper = TTDataFrameHelper())
            ))

        # Assert
        self.assertIsInstance(component_bag.file_path_manager, FilePathManager)
        self.assertIsInstance(component_bag.file_manager, FileManager)
        self.assertIsInstance(component_bag.displayer, Displayer)
        self.assertIsInstance(component_bag.tt_logger, TTLogger)
        self.assertIsInstance(component_bag.tt_adapter, TTAdapter)
class TimeTrackingProcessorTestCase(unittest.TestCase):

    @parameterized.expand([
        ("content.md", "/home/nwtimetracking/"),
    ])
    def test_saveandlog_shouldcallexpecteddependenciesandlogexpectedmessage_wheninvoked(self, file_name : str, folder_path : str) -> None:

        # Arrange
        id : TTID = TTID.TTSBYMONTH
        content : str = "Some Content"
        paragraph_title : str = "Some paragraph title"

        file_path : str = f"{folder_path}/{file_name}"
        expected : str = _MessageCollection.this_content_successfully_saved_as(id = id, file_path = file_path)

        component_bag : Mock = Mock()
        component_bag.file_path_manager.create_file_path = Mock()
        component_bag.file_path_manager.create_file_path.return_value = file_path
        component_bag.tt_adapter.extract_file_name_and_paragraph_title = Mock()
        component_bag.tt_adapter.extract_file_name_and_paragraph_title.return_value = (paragraph_title, None)
        component_bag.file_manager.save_content = Mock()
        component_bag.tt_logger.log = Mock()

        setting_bag : SettingBag = ObjectMother().get_setting_bag()

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor._TimeTrackingProcessor__save_and_log(id = id, content = content)  # type: ignore

        # Assert
        component_bag.file_path_manager.create_file_path.assert_called()
        component_bag.file_manager.save_content.assert_called()
        component_bag.tt_logger.log.assert_called_once_with(expected)

    @parameterized.expand([
        ("content.md", "/home/nwtimetracking/"),
    ])
    def test_saveandlog_shouldlogexpectedmessage_whenexceptionisraised(self, file_name : str, folder_path : str) -> None:

        # Arrange
        id : TTID = TTID.TTSBYMONTH
        content : str = "Some Content"
        paragraph_title : str = "Some paragraph title"
        error_message : str = "Some saving issue happened."

        file_path : str = f"{folder_path}/{file_name}"
        expected : str = _MessageCollection.something_failed_while_saving(file_path = file_path)

        component_bag : Mock = Mock()
        component_bag.file_path_manager.create_file_path = Mock()
        component_bag.file_path_manager.create_file_path.return_value = file_path
        component_bag.tt_adapter.extract_file_name_and_paragraph_title = Mock()
        component_bag.tt_adapter.extract_file_name_and_paragraph_title.return_value = (paragraph_title, None)
        component_bag.file_manager.save_content = Mock()
        component_bag.file_manager.save_content.side_effect = Exception(error_message)
        component_bag.tt_logger.log = Mock()

        setting_bag : SettingBag = ObjectMother().get_setting_bag()

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor._TimeTrackingProcessor__save_and_log(id = id, content = content)  # type: ignore

        # Assert
        component_bag.file_path_manager.create_file_path.assert_called()
        component_bag.file_manager.save_content.assert_called()
        component_bag.tt_logger.log.assert_called_once_with(expected)

    def test_processtt_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tt_styler : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tt_styler = tt_styler

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tt = [OPTION.display]   # type: ignore
        setting_bag.tt_head_n = 5
        setting_bag.tt_display_head_n_with_tail = False
        setting_bag.tt_hide_index = True

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tt()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tt_styler, 
            hide_index = True,
            formatters = None
        )
    def test_processttsbymonth_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_month_styler : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_month_styler = tts_by_month_styler

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
        displayer.display.assert_called_once_with(
            obj = tts_by_month_styler, 
            hide_index = False, 
            formatters = None
        )
    def test_processttsbymonth_shouldsaveandlog_whenoptionissave(self) -> None:
        
        # Arrange
        tts_by_month_tpl: Tuple[DataFrame, DataFrame] = (Mock(), Mock())

        summary: Mock = Mock()
        summary.tts_by_month_tpl = tts_by_month_tpl

        displayer: Mock = Mock()
        tt_adapter: Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag: Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag: Mock = Mock()
        setting_bag.options_tts_by_month = [OPTION.save]  # type: ignore

		# Act, Assert
        with patch("nwtimetracking.TimeTrackingProcessor._TimeTrackingProcessor__save_and_log") as save_and_log:

            tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(
                component_bag = component_bag, 
                setting_bag = setting_bag
            )
            tt_processor.initialize()		
            tt_processor.process_tts_by_month()

            # Assert
            save_and_log.assert_called()
    def test_processttsbyyear_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_year_styler : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_year_styler = tts_by_year_styler

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
        displayer.display.assert_called_once_with(
            obj = tts_by_year_styler,
            hide_index = False,
            formatters = None
        )
    def test_processttsbyyearmonth_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_year_month_styler : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_year_month_styler = tts_by_year_month_styler

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_year_month = [OPTION.display]    # type: ignore

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()        
        tt_processor.process_tts_by_year_month()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_year_month_styler,
            hide_index = False, 
            formatters = None
        )
    def test_processttsbyyearmonthspnv_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_year_month_spnv_styler : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_year_month_spnv_styler = tts_by_year_month_spnv_styler

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_year_month_spnv = [OPTION.display]   # type: ignore
        setting_bag.tts_by_year_month_spnv_formatters = {"%_DME": "{:.2f}", "%_TME": "{:.2f}"}

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()        
        tt_processor.process_tts_by_year_month_spnv()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_year_month_spnv_styler,
            hide_index = False, 
            formatters = setting_bag.tts_by_year_month_spnv_formatters
        )
    def test_processttsbyyearspnv_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_year_spnv_styler : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_year_spnv_styler = tts_by_year_spnv_styler

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter
        
        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_year_spnv = [OPTION.display]     # type: ignore
        setting_bag.tts_by_year_spnv_formatters = {"%_DYE": "{:.2f}", "%_TYE": "{:.2f}"}

        # Act
        processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        processor.initialize()        
        processor.process_tts_by_year_spnv()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_year_spnv_styler,
            hide_index = False,
            formatters = setting_bag.tts_by_year_spnv_formatters
        )
    def test_processttsbyspn_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_spn_styler : DataFrame = Mock()
        definitions_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_spn_styler = tts_by_spn_styler
        summary.definitions_df = definitions_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_spn = [OPTION.display]   # type: ignore
        setting_bag.tts_by_spn_formatters = {"%_DE" : "{:.2f}", "%_TE" : "{:.2f}"}

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_spn()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_spn_styler, 
            hide_index = False, 
            formatters = setting_bag.tts_by_spn_formatters
        )
    def test_processttsbyspn_shouldlog_whenoptionislog(self) -> None:
        
        # Arrange
        tts_by_spn_styler : DataFrame = Mock()
        definitions_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_spn_styler = tts_by_spn_styler
        summary.definitions_df = definitions_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter
        component_bag.tt_logger.try_log_column_definitions = Mock()

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_spn = [OPTION.logdef]  # type: ignore

        # Act, 
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_spn()

        # Assert
        component_bag.tt_logger.try_log_column_definitions.assert_called_once_with(
            df = tts_by_spn_styler, 
            definitions = definitions_df)
    def test_processttsbyspnspv_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_spn_spv_df : DataFrame = Mock()
        definitions_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_spn_spv_df = tts_by_spn_spv_df
        summary.definitions_df = definitions_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_spn_spv = [OPTION.display]   # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_spn_spv()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_spn_spv_df, 
            hide_index = False, 
            formatters = None
        )
    def test_processttsbyspnspv_shouldlog_whenoptionislog(self) -> None:
        
        # Arrange
        tts_by_spn_spv_df : DataFrame = Mock()
        definitions_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_spn_spv_df = tts_by_spn_spv_df
        summary.definitions_df = definitions_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter
        component_bag.tt_logger.try_log_column_definitions = Mock()

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_spn_spv = [OPTION.logdef]  # type: ignore

        # Act, 
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_spn_spv()

        # Assert
        component_bag.tt_logger.try_log_column_definitions.assert_called_once_with(
            df = tts_by_spn_spv_df, 
            definitions = definitions_df)
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
        setting_bag.tts_by_hashtag_formatters = {"Effort%" : "{:.2f}"}

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_hashtag()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_hashtag_df, 
            hide_index = False, 
            formatters = setting_bag.tts_by_hashtag_formatters
        )
    def test_processttsbyhashtag_shouldlog_whenoptionislog(self) -> None:
        
        # Arrange
        tts_by_hashtag_df : DataFrame = Mock()
        definitions_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_hashtag_df = tts_by_hashtag_df
        summary.definitions_df = definitions_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter
        component_bag.tt_logger.try_log_column_definitions = Mock()

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_hashtag = [OPTION.logdef]  # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_hashtag()

        # Assert
        component_bag.tt_logger.try_log_column_definitions.assert_called_once_with(
            df = tts_by_hashtag_df, 
            definitions = definitions_df)
    def test_processttsbyefs_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_efs_styler : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_efs_styler = tts_by_efs_styler

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_efs = [OPTION.display]   # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_efs()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_efs_styler, 
            hide_index = False, 
            formatters = None
        )
    def test_processttsbytr_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_by_tr_styler : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_by_tr_styler = tts_by_tr_styler

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_by_tr = [OPTION.display]    # type: ignore
        setting_bag.tts_by_tr_head_n = uint(10)

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_by_tr()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_by_tr_styler,
            hide_index = False, 
            formatters = None
        )
    def test_processttsganttspnv_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_gantt_spnv_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_gantt_spnv_df = tts_gantt_spnv_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_gantt_spnv = [OPTION.display]    # type: ignore
        setting_bag.tts_gantt_spnv_formatters = { "StartDate": "{:%Y-%m-%d}", "EndDate": "{:%Y-%m-%d}" }

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_gantt_spnv()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_gantt_spnv_df,
            hide_index = False,
            formatters = { "StartDate": "{:%Y-%m-%d}", "EndDate": "{:%Y-%m-%d}" }
        )
    def test_processttsganttspnv_shouldplot_whenoptionisplot(self) -> None:
        
        # Arrange
        tts_gantt_spnv_plot_function : Mock = Mock(spec = Callable[[], None])

        summary : Mock = Mock()
        summary.tts_gantt_spnv_plot_function = tts_gantt_spnv_plot_function

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_gantt_spnv = [OPTION.plot]    # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_gantt_spnv()

        # Assert
        summary.tts_gantt_spnv_plot_function.assert_called_once()
    def test_processttsgantthseq_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tts_gantt_hseq_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tts_gantt_hseq_df = tts_gantt_hseq_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_gantt_hseq = [OPTION.display]    # type: ignore
        setting_bag.tts_gantt_hseq_formatters = { "StartDate": "{:%Y-%m-%d}", "EndDate": "{:%Y-%m-%d}" }

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_gantt_hseq()

        # Assert
        displayer.display.assert_called_once_with(
            obj = tts_gantt_hseq_df,
            hide_index = False,
            formatters = { "StartDate": "{:%Y-%m-%d}", "EndDate": "{:%Y-%m-%d}" }
        )
    def test_processttsgantthseq_shouldplot_whenoptionisplot(self) -> None:
        
        # Arrange
        tts_gantt_hseq_plot_function : Mock = Mock(spec = Callable[[], None])

        summary : Mock = Mock()
        summary.tts_gantt_hseq_plot_function = tts_gantt_hseq_plot_function

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tts_gantt_hseq = [OPTION.plot]    # type: ignore

        # Act
        tt_processor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tts_gantt_hseq()

        # Assert
        summary.tts_gantt_hseq_plot_function.assert_called_once()
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
        displayer.display.assert_called_once_with(
            obj = definitions_df, 
            hide_index = False, 
            formatters = None
        )
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
        ["process_tts_by_month"],
        ["process_tts_by_year"],
        ["process_tts_by_year_month"],
        ["process_tts_by_year_month_spnv"],
        ["process_tts_by_year_spnv"],
        ["process_tts_by_spn"],
        ["process_tts_by_spn_spv"],
        ["process_tts_by_hashtag"],
        ["process_tts_by_hashtag_year"],
        ["process_tts_by_efs"],
        ["process_tts_by_tr"],
        ["process_tts_gantt_spnv"],
        ["process_tts_gantt_hseq"],
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