'''
A collection of components to handle "Time Tracking.xlsx".

Alias: nwtt
'''

# GLOBAL MODULES
import numpy as np
import os
import pandas as pd
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum, auto
from numpy import uint
from pandas import DataFrame, Series, NamedAgg
from pandas import Timedelta
from pathlib import Path
from re import Match
from typing import Any, Literal, Optional, Tuple, cast
from weasyprint import CSS, HTML

# LOCAL/NW MODULES
from nwshared import FilePathManager, FileManager, Displayer, Formatter

# CONSTANTS
class TTCN(StrEnum):
    
    '''Collects all the column names used by TTDataFrameFactory.'''

    DATE = "Date"
    STARTTIME = "StartTime"
    ENDTIME = "EndTime"
    EFFORT = "Effort"
    HASHTAG = "Hashtag"
    DESCRIPTOR = "Descriptor"
    ISSOFTWAREPROJECT = "IsSoftwareProject"
    ISRELEASEDAY = "IsReleaseDay"
    YEAR = "Year"
    MONTH = "Month"
    TREND = "↕"
    SOFTWAREPROJECTNAME = "SoftwareProjectName"
    SOFTWAREPROJECTVERSION = "SoftwareProjectVersion"
    HASHTAGS = "Hashtags"
    EFFORTPERC = "Effort%"
    TIMERANGE = "TimeRange"
    TIMERANGES = "TimeRanges"
    OCCURRENCES = "Occurrences"
    OCCURRENCEPERC = "Occurrence%"
    OCCURRENCETOTAL = "OccurrenceTotal"
    EFFORTSTATUS = "EffortStatus"
    ISCORRECT = "IsCorrect"
    EXPECTED = "Expected"
    MESSAGE = "Message"
    ID = "Id"
class DEFINITIONSTR(StrEnum):
    
    '''Collects all the column names used by definitions.'''

    TERM = "Term"
    DEFINITION = "Definition"
    TT = "tt"
    TTS = "tts"
class OPTION(StrEnum):

    '''Represents a collection of options.'''

    display = auto()
    save_html = auto()
    save_pdf = auto()
class EFFORTMODE(StrEnum):

    '''Represents a collection of modes for EffortHighlighter.'''

    top_one_effort_per_row = auto()
    top_three_efforts = auto()
class REPORTSTR(StrEnum):
    
    '''Collects all the strings related to TTReportManager.'''

    TTLATESTFIVE = "Latest Five"
    TTSBYMONTH = "By Month"
    TTSBYYEAR = "By Year"
    TTSBYRANGE = "By Range"
    TTSBYSPN = "By Software Project Name"
    TTSBYSPV = "By Software Project Version"
    TTSBYHASHTAGYEAR = "By Hashtag, Year"
    TTSBYHASHTAG = "By Hashtag"
    TTSBYYEARMONTHSPNV = "By Year, Month, Software Project"
    TTSBYTIMERANGES = "By Timeranges"
    DEFINITIONS = "Definitions"

# STATIC CLASSES
class _MessageCollection():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def effort_status_mismatching_effort(idx : int, start_time_str : str, end_time_str : str, actual_str : str, expected_str : str) -> str:

        '''
        "The provided row contains a mismatching effort (idx: '4', start_time: '20:00', end_time: '00:00', actual_effort: '3h 00m', expected_effort: '4h 00m')."
        '''

        message : str = "The provided row contains a mismatching effort "
        message += f"(idx: '{idx}', start_time: '{start_time_str}', end_time: '{end_time_str}', actual_effort: '{actual_str}', expected_effort: '{expected_str}')."

        return message   
    @staticmethod
    def effort_status_not_possible_to_create(idx : int, start_time_str : str, end_time_str : str, effort_str : str):

            '''
                "It has not been possible to create an EffortStatus for the provided parameters 
                (idx: '770', start_time_str: '22:00', end_time_str: '00:00 ', effort_str: '2h 00m')."
            '''

            message : str = "It has not been possible to create an EffortStatus for the provided parameters "
            message += f"(idx: '{idx}', start_time_str: '{start_time_str}', end_time_str: '{end_time_str}', effort_str: '{effort_str}')."

            return message   
    @staticmethod
    def effort_status_not_among_expected_time_values(time : str) -> str:
        return f"The provided time ('{time}') is not among the expected time values."   
    @staticmethod
    def starttime_endtime_are_empty() -> str:
        return "''start_time' and/or 'end_time' are empty, 'effort' can't be verified. We assume that it's correct."
    @staticmethod
    def effort_is_correct() -> str:
        return "The effort is correct."

    @staticmethod
    def please_run_initialize_first() -> str:
        return "Please run the 'initialize' method first."

    @staticmethod
    def provided_mode_not_supported(mode : EFFORTMODE):
        return f"The provided mode is not supported: '{mode}'."

# CLASSES
@dataclass(frozen=True)
class EffortStatus():
    
    '''Represents an effort-related status.'''

    idx : int
    start_time_str : Optional[str]
    start_time_dt : Optional[datetime]

    end_time_str : Optional[str] 
    end_time_dt : Optional[datetime]
    
    actual_str : str
    actual_td : timedelta 

    expected_td : Optional[timedelta]
    expected_str : Optional[str] 

    is_correct : bool
    message : str 
@dataclass(frozen = True)
class TTSummary():

    '''Collects all the dataframes, stylers and markdowns.'''

    tt_df : DataFrame
    tt_latest_five_df : DataFrame
    tts_by_month_df : DataFrame
    tts_by_year_df : DataFrame
    tts_by_range_df : DataFrame
    tts_by_spn_df : DataFrame
    tts_by_spv_df : DataFrame
    tts_by_hashtag_year_df : DataFrame
    tts_by_hashtag_df : DataFrame
    tts_by_year_month_spnv_df : DataFrame
    tts_by_timeranges_df : DataFrame
    ttd_effort_status_df : DataFrame
    definitions_df : DataFrame
class DefaultPathProvider():

    '''Responsible for proviving the default path to the dataset.'''

    def get_default_time_tracking_path(self)-> str:

        r'''
            "c:\...\nwtimetrackingmanager\data\Time Tracking.xlsx"
        '''
        
        path : str = os.getcwd().replace("src", "data")
        path = os.path.join(path, "Time Tracking.xlsx")

        return path
class YearProvider():

    '''Collects all the logic related to the retrieval of year-related information.'''

    def get_all_years(self) -> list[int]:

        '''Returns a list of years.'''

        years : list[int] = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

        return years
    def get_most_recent_x_years(self, x : uint) -> list[int]:

        '''Returns a list of years.'''

        years : list[int] = self.get_all_years()

        if x <= len(years):
            years = years[(len(years) - int(x)):]

        return years
class SoftwareProjectNameProvider():

    '''Collects all the logic related to the retrieval of software project names.'''

    def get_all(self) -> list[str]:

        '''Returns a list of software project names.'''

        software_project_names : list[str] = [
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

        return software_project_names
    def get_latest_three(self) -> list[str]:

        '''Returns a list of software project names.'''

        software_project_names : list[str] = self.get_all()[-3:]

        return software_project_names
    def get_latest(self) -> list[str]:

        '''Returns a list of software project names.'''

        software_project_names : list[str] = self.get_all()[-1:]

        return software_project_names
@dataclass(frozen=True)
class SettingBag():

    '''Represents a collection of settings.'''

    # WITHOUT DEFAULTS
    options_tt : list[Literal[OPTION.display]]
    options_tt_latest_five : list[Literal[OPTION.display]]
    options_tts_by_month : list[Literal[OPTION.display]]
    options_tts_by_year : list[Literal[OPTION.display]]
    options_tts_by_range : list[Literal[OPTION.display]]
    options_tts_by_spn : list[Literal[OPTION.display]]
    options_tts_by_spv : list[Literal[OPTION.display]]
    options_tts_by_hashtag_year : list[Literal[OPTION.display]]
    options_tts_by_hashtag : list[Literal[OPTION.display]]
    options_tts_by_year_month_spnv : list[Literal[OPTION.display]]
    options_tts_by_timeranges : list[Literal[OPTION.display]]
    options_definitions : list[Literal[OPTION.display]]
    options_report : list[Literal[OPTION.save_html, OPTION.save_pdf]]
    excel_nrows : int

    # WITH DEFAULTS
    options_ttd_effort_status : list[Literal[OPTION.display]] = field(default_factory = list)
    working_folder_path : str = field(default = "/home/nwtimetracking/")
    excel_path : str = field(default = DefaultPathProvider().get_default_time_tracking_path())
    excel_skiprows : int = field(default = 0)
    excel_tabname : str = field(default = "Sessions")
    years : list[int] = field(default_factory = lambda : YearProvider().get_all_years())
    now : datetime = field(default = datetime.now())
    enable_effort_highlighting : bool = field(default = True)
    tts_by_spn_software_project_names : list[str] = field(default_factory = lambda : SoftwareProjectNameProvider().get_all())
    tts_by_spv_software_project_names : list[str] = field(default_factory = lambda : SoftwareProjectNameProvider().get_latest_three())
    tts_by_hashtag_formatters : dict = field(default_factory = lambda : { TTCN.EFFORTPERC : "{:.2f}" })
    tts_by_timeranges_min_occurrences : int = field(default = 10)
    tts_by_timeranges_formatters : dict = field(default_factory = lambda : { TTCN.OCCURRENCEPERC : "{:.2f}" })
    ttd_effort_status_is_correct : bool = field(default = False)
class TTDataFrameHelper():

    '''Collects helper functions for TTDataFrameFactory.'''

    def box_effort(self, effort_td : timedelta, add_plus_sign : bool) -> str:

        '''
            4 days 19:15:00	=> "115h 15m" (or +115h 15m)
            -9 days +22:30:00 => "-194h 30m"
        '''

        total_seconds : float = effort_td.total_seconds()
        hours : int = int(total_seconds // 3600)
        minutes : int = int((total_seconds % 3600) // 60)

        hours_str : str = str(hours).zfill(2)
        minutes_str : str = str(minutes ).zfill(2)

        effort_str : str = f"{hours_str}h {minutes_str}m"

        if (add_plus_sign == True and effort_td.days >= 0):
            effort_str = f"+{effort_str}"

        return effort_str
    def unbox_effort(self, effort_str : str) -> timedelta:

        '''"5h 30m" => 5:30:00'''

        effort_td : timedelta = pd.Timedelta(value = effort_str).to_pytimedelta()

        return effort_td

    def create_time_object(self, time : str) -> datetime:

        '''It creates a datetime object suitable for timedelta calculation out of the provided time.'''

        day_1_times : list[str] = [
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
        ]
        day_2_times : list[str] = [
            "00:00", "00:15", "00:30", "00:45", 
            "01:00", "01:15", "01:30", "01:45",
            "02:00", "02:15", "02:30", "02:45",
            "03:00", "03:15", "03:30", "03:45",
            "04:00", "04:15", "04:30", "04:45",
            "05:00", "05:15", "05:30", "05:45",
            "06:00", "06:15", "06:30", "06:45"
        ]

        strp_format : str = "%Y-%m-%d %H:%M"

        dt_str : Optional[str] = None
        if time in day_1_times:
            dt_str = f"1900-01-01 {time}"
        elif time in day_2_times:
            dt_str = f"1900-01-02 {time}"
        else: 
            raise ValueError(_MessageCollection.effort_status_not_among_expected_time_values(time = time))
                
        dt : datetime =  datetime.strptime(dt_str, strp_format)

        return dt
    def create_effort_status(self, idx : int, start_time_str : str, end_time_str : str, effort_str : str) -> EffortStatus:

        '''
            start_time_str, end_time_str:
                - Expects time values in the "%H:%M" format - for ex. 20:00.

            is_correct:
                start_time_str = "20:00", end_time_str = "00:00", effort_str = "4h 00m" => True
                start_time_str = "20:00", end_time_str = "00:00", effort_str = "5h 00m" => False
        '''

        try:

            if len(start_time_str) == 0 or len(end_time_str) == 0:
                return self.create_effort_status_for_none_values(idx = idx, effort_str = effort_str)

            start_time_dt : datetime = self.create_time_object(time = start_time_str)
            end_time_dt : datetime = self.create_time_object(time = end_time_str)

            actual_str : str = effort_str
            actual_td : timedelta = self.unbox_effort(effort_str = effort_str)

            expected_td : timedelta = (end_time_dt - start_time_dt)
            expected_str : str = self.box_effort(effort_td = expected_td, add_plus_sign = False)
            
            is_correct : bool = True
            if actual_td != expected_td:
                is_correct = False
            
            message : str = _MessageCollection.effort_is_correct()

            if actual_td != expected_td:
                message = _MessageCollection.effort_status_mismatching_effort(
                    idx = idx, 
                    start_time_str = start_time_str, 
                    end_time_str = end_time_str, 
                    actual_str = actual_str, 
                    expected_str = expected_str
                )
            
            effort_status : EffortStatus = EffortStatus(
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

            return effort_status
        
        except:

            error : str = _MessageCollection.effort_status_not_possible_to_create(
                idx = idx, start_time_str = start_time_str, end_time_str = end_time_str, effort_str = effort_str)

            raise ValueError(error)
    def create_effort_status_for_none_values(self, idx : int, effort_str : str) -> EffortStatus:

        '''Creates effort status for None values.'''

        actual_str : str = effort_str
        actual_td : timedelta = self.unbox_effort(effort_str = effort_str)
        is_correct : bool = True

        effort_status : EffortStatus = EffortStatus(
            idx = idx,
            start_time_str = None,
            start_time_dt = None,
            end_time_str = None,
            end_time_dt = None,
            actual_str = actual_str,
            actual_td = actual_td,
            expected_td = None,
            expected_str = None,
            is_correct = is_correct,
            message = _MessageCollection.starttime_endtime_are_empty()
            )    

        return effort_status
    def create_effort_status_and_cast_to_any(self, idx : int, start_time_str : str, end_time_str : str, effort_str : str) -> Any:

        '''
            Wrapper method created to overcome the following error raised by df.apply():

                Argument of type "(x: Unknown) -> EffortStatus" cannot be assigned to parameter "f" of type "(...) -> Series[Any]" in function "apply"
                Type "(x: Unknown) -> EffortStatus" is not assignable to type "(...) -> Series[Any]"
                    Function return type "EffortStatus" is incompatible with type "Series[Any]"
                    "EffortStatus" is not assignable to "Series[Any]"            
        '''

        return cast(Any, self.create_effort_status(idx = idx, start_time_str = start_time_str, end_time_str = end_time_str, effort_str = effort_str))    

    def calculate_percentage(self, part : float, whole : float, rounding_digits : int = 2) -> float:

        '''Calculates a percentage.'''

        prct : Optional[float] = None

        if part == 0:
            prct = 0
        elif whole == 0:
            prct = 0
        else:
            prct = (100 * part) / whole

        prct = round(number = prct, ndigits = rounding_digits)

        return prct
    def extract_software_project_name(self, descriptor : str) -> str:

        '''
            "NW.AutoProffLibrary v1.0.0"    => "NW.AutoProffLibrary"
            "nwreadinglistmanager v1.5.0"   => "nwreadinglistmanager"

            Returns "ERROR" is parsing goes wrong.
        '''

        pattern : str = r"\b[a-zA-Z\.]{2,}(?=[ v]{2}[0-9]{1}[\.]{1}[0-9]{1}[\.]{1}[0-9]{1})"
        matches : list = re.findall(pattern = pattern, string = descriptor, flags = re.MULTILINE)

        if len(matches) == 1:
            return matches[0]

        return "ERROR"
    def extract_software_project_version(self, descriptor : str) -> str: 

        '''
            "NW.AutoProffLibrary v1.0.0"    => "1.0.0"
            "nwreadinglistmanager v1.5.0"   => "1.5.0"

            Returns "ERROR" is parsing goes wrong.
        '''

        pattern : str = r"(?<=v)[0-9\.]{5}$"
        matches : list = re.findall(pattern = pattern, string = descriptor, flags = re.MULTILINE)

        if len(matches) == 1:
            return matches[0]

        return "ERROR"
    def create_time_range_id(self, start_time : str, end_time : str) -> str:
            
        '''
            Creates a unique time range identifier out of the provided parameters.

            If parameters are empty, it returns "Unknown":

                ...
                start_time: '', end_time: '', time_range_id: 'Unknown'
                start_time: '', end_time: '', time_range_id: 'Unknown'
                start_time: '08:30', end_time: '09:00', time_range_id: '08:30-09:00'
                start_time: '18:00', end_time: '19:30', time_range_id: '18:00-19:30'
                ...

            In "Time Tracking.xlsx" we don't have time ranges for the following period: [2015-10-31 -> 2019-05-31].
        '''

        unknown_id : str = "Unknown"
        time_range_id : str = f"{start_time}-{end_time}"

        if len(start_time) == 0 or len(end_time) == 0:
            time_range_id = unknown_id

        return time_range_id

    def is_year(self, value : Any) -> bool:

        """Returns True if value is a valid year."""

        try:       
            year : int = int(value)
            return 1000 <= year <= 9999
        except:
            return False
    def is_even(self, number : int) -> bool:
        
        """Returns True if number is even."""

        return number % 2 == 0
class TTDataFrameFactory():

    '''Encapsulates all the logic related to dataframe creation out of "Time Tracking.xlsx".'''

    __df_helper : TTDataFrameHelper

    def __init__(self, df_helper : TTDataFrameHelper) -> None:

        self.__df_helper = df_helper

    def __enforce_dataframe_definition_for_tt_df(self, tt_df : DataFrame) -> DataFrame:

        '''Enforces definition for the provided dataframe.'''

        column_names : list[str] = []
        column_names.append(TTCN.DATE)              # [0], date
        column_names.append(TTCN.STARTTIME)         # [1], str
        column_names.append(TTCN.ENDTIME)           # [2], str
        column_names.append(TTCN.EFFORT)            # [3], str
        column_names.append(TTCN.HASHTAG)           # [4], str
        column_names.append(TTCN.DESCRIPTOR)        # [5], str
        column_names.append(TTCN.ISSOFTWAREPROJECT) # [6], bool
        column_names.append(TTCN.ISRELEASEDAY)      # [7], bool
        column_names.append(TTCN.YEAR)              # [8], int
        column_names.append(TTCN.MONTH)             # [9], int

        tt_df = tt_df[column_names]
    
        tt_df[column_names[0]] = pd.to_datetime(tt_df[column_names[0]], format="%Y-%m-%d") 
        tt_df[column_names[0]] = tt_df[column_names[0]].apply(lambda x: x.date())

        tt_df = tt_df.astype({column_names[1]: str})
        tt_df = tt_df.astype({column_names[2]: str})
        tt_df = tt_df.astype({column_names[3]: str})
        tt_df = tt_df.astype({column_names[4]: str})
        tt_df = tt_df.astype({column_names[5]: str})
        tt_df = tt_df.astype({column_names[6]: bool})
        tt_df = tt_df.astype({column_names[7]: bool})
        tt_df = tt_df.astype({column_names[8]: int})
        tt_df = tt_df.astype({column_names[9]: int})

        tt_df[column_names[1]] = tt_df[column_names[1]].replace('nan', '')
        tt_df[column_names[2]] = tt_df[column_names[2]].replace('nan', '')
        tt_df[column_names[5]] = tt_df[column_names[5]].replace('nan', '')

        return tt_df    
    def __enforce_dataframe_definition_for_raw_ttm_df(self, df : DataFrame) -> DataFrame:

        '''Ensures that the columns of the provided dataframe have the expected data types.'''

        df = df.astype({TTCN.MONTH: int})
        # can't enforce the year column as "timedelta"

        return df     
    def __create_default_raw_ttm(self, year : int) -> DataFrame:

        '''
            default_df:

                    Month	2019
                0	1	    0 days
                ...
        '''

        td : timedelta = self.__df_helper.unbox_effort(effort_str = "0h 00m")

        default_df : DataFrame = pd.DataFrame(
            {
                f"{TTCN.MONTH}": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                f"{str(year)}": [td, td, td, td, td, td, td, td, td, td, td, td]
            },
            index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        )

        default_df = self.__enforce_dataframe_definition_for_raw_ttm_df(df = default_df)

        return default_df    
    def __create_raw_ttm(self, tt_df : DataFrame, year : int) -> DataFrame:
        
        '''
            ttm_df:

                Year	    Month	Effort
                0	2015	10	    8h 00m
                1	2015	11	    10h 00m
                2	2015	12	    0h 00m

            ttm_df:

                Year	    Month	2015	        
                0	2015	10	    0 days 08:00:00
                1	2015	11	    0 days 10:00:00
                2	2015	12	    0 days 00:00:00            

            ttm_df:

                    Month	2015
                0	1	    0 days 00:00:00
                ...
                9	10	    0 days 08:00:00
                10	11	    0 days 10:00:00
                11	12	    0 days 00:00:00
        '''

        ttm_df : DataFrame = tt_df.copy(deep=True)
        ttm_df = ttm_df[[TTCN.YEAR, TTCN.MONTH, TTCN.EFFORT]]

        condition : Series = (tt_df[TTCN.YEAR] == year)
        ttm_df = ttm_df.loc[condition]

        ttm_df[TTCN.EFFORT] = ttm_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        ttm_df[str(year)] = ttm_df[TTCN.EFFORT]
        cn_effort = str(year)    

        ttm_df = ttm_df.groupby([TTCN.MONTH])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        ttm_df = ttm_df.sort_values(by = TTCN.MONTH).reset_index(drop = True)

        ttm_df = self.__try_complete_raw_ttm(ttm_df = ttm_df, year = year)
        ttm_df = self.__enforce_dataframe_definition_for_raw_ttm_df(df = ttm_df)

        return ttm_df
    def __try_complete_raw_ttm(self, ttm_df : DataFrame, year : int) -> DataFrame:

        '''
            We expect ttm_df to have 12 months: 
            
                - if that's the case, we are done with it and we return it;
                - if it's not the case, we generate a default_df and we use it to fill the missing values.

                ttm_df
            
                        Month	2015
                    0	10	    8h 00m
                    1	11	    10h 00m
                    2	12	    0h 00m
            
                default_df:

                        Month	2015
                    0	1	    0h 00m
                    1	2	    0h 00m              
                    ... ...     ...
                    11	12	    0h 00m

                missing_df:

                        Month	2015
                    0	1	    0h 00m
                    1	2	    0h 00m              
                    ... ...     ...
                    8	9	    0h 00m                 

                completed_df
            
                        Month	2015
                    0	1	    0h 00m
                    1	2	    0h 00m
                    ... ...     ...
                    9	10	    8h 00m
                    10	11	    10h 00m
                    11	12	    0h 00m  
        '''

        if ttm_df[TTCN.MONTH].count() != 12:

            default_df : DataFrame = self.__create_default_raw_ttm(year = year)
            missing_df : DataFrame = default_df.loc[~default_df[TTCN.MONTH].astype(str).isin(ttm_df[TTCN.MONTH].astype(str))]

            completed_df : DataFrame = pd.concat([ttm_df, missing_df], ignore_index = True)
            completed_df = completed_df.sort_values(by = TTCN.MONTH, ascending = [True])
            completed_df = completed_df.reset_index(drop = True)

            return completed_df

        return ttm_df
    def __expand_raw_ttm_by_year(self, tt_df : DataFrame, years : list, tts_by_month_df : DataFrame, i : int, add_trend : bool) -> DataFrame:

        '''    
            actual_df:

                    Month	2016
                0	1	    0h 00m
                1	2	    0h 00m
                ...

            ttm_df:

                    Month	2017
                0	1	    13h 00m
                1	2	    1h 00m
                ...            

            expansion_df:

                    Month	2016	2017
                0	1	    0h 00m	13h 00m
                1	2	    0h 00m	1h 00m
                ...

            expansion_df:        

                    Month	2016	2017	    ↕1
                0	1	    0h 00m	13h 00m	    ↑
                1	2	    0h 00m	1h 00m	    ↑
                ...

            expansion_df:

                    Month	2016	↕1	2017
                0	1	    0h 00m	↑	13h 00m
                1	2	    0h 00m	↑	1h 00m
                ...

            Now that we have the expansion_df, we append it to the right of actual_df:

            actual_df:

                    Month	2016	↕1	2017
                0	1	    0h 00m	↑	13h 00m
                1	2	    0h 00m	↑	1h 00m
                ...
        '''
        
        actual_df : DataFrame = tts_by_month_df.copy(deep = True)
        ttm_df : DataFrame = self.__create_raw_ttm(tt_df = tt_df, year = years[i])

        expansion_df = pd.merge(
            left = actual_df, 
            right = ttm_df, 
            how = "inner", 
            left_on = TTCN.MONTH, 
            right_on = TTCN.MONTH)

        if add_trend == True:

            cn_trend : str = f"↕{i}"
            cn_trend_1 : str = str(years[i-1])   # for ex. "2016"
            cn_trend_2 : str = str(years[i])     # for ex. "2017"
            
            expansion_df[cn_trend] = expansion_df.apply(lambda x : self.__get_trend_by_timedelta(td_1 = x[cn_trend_1], td_2 = x[cn_trend_2]), axis = 1) 

            new_column_names : list = [TTCN.MONTH, cn_trend_1, cn_trend, cn_trend_2]   # for ex. ["Month", "2016", "↕", "2017"]
            expansion_df = expansion_df.reindex(columns = new_column_names)

            shared_columns : list = [TTCN.MONTH, str(years[i-1])] # ["Month", "2016"]
            actual_df = pd.merge(
                left = actual_df, 
                right = expansion_df, 
                how = "inner", 
                left_on = shared_columns, 
                right_on = shared_columns)

        else:
            actual_df = expansion_df

        return actual_df
    def __get_trend_by_timedelta(self, td_1 : timedelta, td_2 : timedelta) -> str:

        '''
            0h 30m, 1h 00m => "↑"
            1h 00m, 0h 30m => "↓"
            0, 0 => "="
        '''
        trend : Optional[str] = None

        if td_1 < td_2:
            trend = "↑"
        elif td_1 > td_2:
            trend = "↓"
        else:
            trend = "="

        return trend
    def __try_consolidate_trend_column_name(self, column_name : str) -> str:

        '''
            "2016"  => "2016"
            "↕1"    => "↕"
        '''

        if column_name.startswith(TTCN.TREND):
            return TTCN.TREND
        
        return column_name
    def __update_future_months_to_empty(self, tts_by_month_df : DataFrame, now : datetime) -> DataFrame:

        '''	
            If now is 2023-08-09:

                Month	2022	↕	2023
                ...
                8	    0h 00m	=	0h 00m
                9	    1h 00m	↓	0h 00m
                10	    0h 00m	=	0h 00m
                11	    0h 00m	=	0h 00m
                12	    0h 00m	=	0h 00m		            

                Month	2022	↕	2023
                ...
                8	    0h 00m	=	0h 00m
                9	    1h 00m		
                10	    0h 00m		
                11	    0h 00m		
                12	    0h 00m
        '''

        tts_by_month_upd_df : DataFrame = tts_by_month_df.copy(deep = True)

        now_year : int = now.year
        now_month : int = now.month	
        cn_year : str = str(now_year)
        new_value : str = ""

        condition : Series = (tts_by_month_upd_df[TTCN.MONTH] > now_month)
        tts_by_month_upd_df[cn_year] = np.where(condition, new_value, tts_by_month_upd_df[cn_year])
            
        idx_year : int = cast(int, tts_by_month_upd_df.columns.get_loc(cn_year))
        idx_trend : int = (idx_year - 1)
        tts_by_month_upd_df.iloc[:, idx_trend] = np.where(condition, new_value, tts_by_month_upd_df.iloc[:, idx_trend])

        return tts_by_month_upd_df
    def __extract_years(self, tt_df : DataFrame) -> list[int]:

        '''Extract years.'''

        year_list : list[int] = pd.Series(tt_df[TTCN.YEAR]).dropna().astype(int).sort_values().unique().tolist()

        return year_list

    def create_tt_df(self, excel_path : str, excel_skiprows : int, excel_nrows : int, excel_tabname : str) -> DataFrame:
        
        '''
            Retrieves the content of the "Sessions" tab and returns it as a Dataframe. 
        '''

        tt_df : DataFrame = pd.read_excel(
            io = excel_path, 	
            skiprows = excel_skiprows,
            nrows = excel_nrows,
            sheet_name = excel_tabname, 
            engine = 'openpyxl'
            )      
        tt_df = self.__enforce_dataframe_definition_for_tt_df(tt_df = tt_df)

        return tt_df
    def create_tt_latest_five_df(self, tt_df : DataFrame) -> DataFrame:

        '''Returns latest five rows of tt_df'''

        tt_latest_five_df : DataFrame = tt_df.copy(deep = True)
        tt_latest_five_df = tt_latest_five_df.tail(5)

        return tt_latest_five_df
    def create_tts_by_month_df(self, tt_df : DataFrame, now : datetime) -> DataFrame:

        '''
                2016	↕   2017	    ↕	2018    ...
            0	0h 00m	↑	13h 00m		↓	0h 00m
            1	0h 00m	↑	1h 00m	    ↓	0h 00m
            ...            
        '''

        years : list[int] = self.__extract_years(tt_df = tt_df)
        tts_df : DataFrame = pd.DataFrame()

        for i in range(len(years)):

            if i == 0:
                tts_df = self.__create_raw_ttm(tt_df = tt_df, year = years[i])
            else:
                tts_df = self.__expand_raw_ttm_by_year(
                    tt_df = tt_df, 
                    years = years, 
                    tts_by_month_df = tts_df, 
                    i = i, 
                    add_trend = True)
                
        for year in years:
            tts_df[str(year)] = tts_df[str(year)].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))

        tts_df.rename(columns = (lambda x : self.__try_consolidate_trend_column_name(column_name = x)), inplace = True)
        
        tts_df = self.__update_future_months_to_empty(tts_by_month_df = tts_df, now = now)
        tts_df.drop(columns = [TTCN.MONTH], inplace = True)

        return tts_df
    def create_tts_by_year_df(self, tt_df : DataFrame) -> DataFrame:

        '''
                2015    ↕   2016        ↕   2017        ↕   2018        ↕   2019        ↕   ...
            0  18h 00m  ↑   615h 15m    ↑   762h 45m    ↑   829h 45m    ↓   515h 15m    ↓   ...
        '''

        years : list[int] = self.__extract_years(tt_df = tt_df)

        tts_df: DataFrame = tt_df.loc[tt_df[TTCN.YEAR].isin(years)].copy(deep = True)
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df[TTCN.EFFORT] = pd.to_timedelta(tts_df[TTCN.EFFORT])

        by_year : Series = tts_df.groupby(TTCN.YEAR)[TTCN.EFFORT].sum().reindex(years, fill_value = Timedelta(0))

        column_names : list[str] = []
        row_values : list[Timedelta | str] = []

        for i, year in enumerate(years):

            column_names.append(str(year))
            row_values.append(self.__df_helper.box_effort(by_year.loc[year], False))

            if i < len(years) - 1:

                next_year : int = years[i + 1]
                current_effort : Timedelta = by_year.loc[year]
                next_effort : Timedelta = by_year.loc[next_year]

                if next_effort > current_effort:
                    arrow = "↑"
                elif next_effort < current_effort:
                    arrow = "↓"
                else:
                    arrow = "="

                column_names.append(TTCN.TREND)
                row_values.append(arrow)

        tts_df = pd.DataFrame([row_values], columns = column_names)

        return tts_df
    def create_tts_by_range_df(self, tt_df: DataFrame) -> DataFrame:

        '''
                11 Years
            0   6485h 30m
        '''

        years : list[int] = self.__extract_years(tt_df = tt_df)

        tts_df: DataFrame = tt_df.loc[tt_df[TTCN.YEAR].isin(years)].copy(deep = True)
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df[TTCN.EFFORT] = pd.to_timedelta(tts_df[TTCN.EFFORT])

        per_year : Series = tts_df.groupby(TTCN.YEAR, as_index = False)[TTCN.EFFORT].sum()
        years_count : int = int(per_year[TTCN.YEAR].nunique())
        effort_td : Timedelta = per_year[TTCN.EFFORT].sum()
        effort_str : str = self.__df_helper.box_effort(effort_td = effort_td, add_plus_sign = False)
        label : str = f"{years_count} Year" if years_count == 1 else f"{years_count} Years"

        tts_df = pd.DataFrame({label: [effort_str]})

        return tts_df
    def create_tts_by_spn_df(self, tt_df : DataFrame, software_project_names : list[str]) -> DataFrame:

        '''
                SoftwareProjectName     Effort      Hashtags
            0   nwknowledgebase         337h 15m    #adoc, #python
            1   nwtraderaanalytics      263h 15m    #python
            ...
        '''

        years : list[int] = self.__extract_years(tt_df = tt_df)

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.SOFTWAREPROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby(by = [TTCN.SOFTWAREPROJECTNAME, TTCN.HASHTAG])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.SOFTWAREPROJECTNAME]).reset_index(drop = True)

        condition_three : Series = (tts_df[TTCN.SOFTWAREPROJECTNAME].isin(values = software_project_names))
        tts_df = tts_df.loc[condition_three] 
        tts_df = tts_df.sort_values(by = [TTCN.EFFORT], ascending = [False]).reset_index(drop = True)
          
        tts_df = tts_df[[TTCN.SOFTWAREPROJECTNAME, TTCN.EFFORT, TTCN.HASHTAG]]

        hashtags_df : DataFrame = (
            tts_df
                .sort_values(by = [TTCN.SOFTWAREPROJECTNAME, TTCN.EFFORT], ascending = [True, False])
                .groupby(by = [TTCN.SOFTWAREPROJECTNAME])[TTCN.HASHTAG].agg(lambda s : ", ".join(dict.fromkeys(s.astype(str))))
                .reset_index(name = TTCN.HASHTAGS))

        effort_df : DataFrame = tts_df.groupby(by = [TTCN.SOFTWAREPROJECTNAME])[TTCN.EFFORT].sum().reset_index(name = TTCN.EFFORT)
        tts_df = effort_df.merge(right = hashtags_df, on = TTCN.SOFTWAREPROJECTNAME, how = "left")
        tts_df = tts_df.sort_values(by = [TTCN.EFFORT], ascending = [False]).reset_index(drop = True)
        tts_df = tts_df[[TTCN.SOFTWAREPROJECTNAME, TTCN.EFFORT, TTCN.HASHTAGS]]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False)) 

        return tts_df
    def create_tts_by_spv_df(self, tt_df : DataFrame, software_project_names : list[str]) -> DataFrame:

        '''
                ProjectName	                ProjectVersion	Effort
            0	NW.MarkdownTables	        1.0.0	        15h 15m
            1	NW.MarkdownTables	        1.0.1	        02h 30m
            2	NW.NGramTextClassification	1.0.0	        74h 15m
            ...    
        '''

        years : list[int] = self.__extract_years(tt_df = tt_df)

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.SOFTWAREPROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.SOFTWAREPROJECTVERSION] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_version(descriptor = x))

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby(by = [TTCN.SOFTWAREPROJECTNAME, TTCN.SOFTWAREPROJECTVERSION])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.SOFTWAREPROJECTNAME, TTCN.SOFTWAREPROJECTVERSION]).reset_index(drop = True)

        condition_three : Series = (tts_df[TTCN.SOFTWAREPROJECTNAME].isin(values = software_project_names))
        tts_df = tts_df.loc[condition_three]
        tts_df = tts_df.sort_values(by = [TTCN.SOFTWAREPROJECTNAME, TTCN.SOFTWAREPROJECTVERSION]).reset_index(drop = True)

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   

        return tts_df
    def create_tts_by_hashtag_year_df(self, tt_df : DataFrame) -> DataFrame:

        '''
                Hashtag     2015    2016    2017    2018    2019    2020    2021    2022    2023    2024    2025
            0   #adoc                                                                                       327h 45m
            1   #bash                                                                                       20h 30m
            ...
        '''

        years : list[int] = self.__extract_years(tt_df = tt_df)            

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition : Series = (tt_df[TTCN.YEAR].isin(values = years))
        tts_df = tts_df.loc[condition]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.HASHTAG])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.HASHTAG, TTCN.YEAR]).reset_index(drop = True)

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   

        tts_df = tts_df.pivot(index = TTCN.HASHTAG, columns = TTCN.YEAR, values = TTCN.EFFORT).rename_axis(None, axis=1).reset_index()
        tts_df = tts_df.fillna("")

        return tts_df
    def create_tts_by_hashtag_df(self, tt_df : DataFrame) -> DataFrame:

        '''
                Hashtag	        Effort  Effort%
            0   #csharp	        67h 30m 56.49
            1   #maintenance	51h 00m 23.97
            2   #powershell	    04h 30m 6.43
            ...    
        '''
    
        tts_df : DataFrame = tt_df.copy(deep = True)

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby(by = [TTCN.HASHTAG])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)

        summarized : float = tts_df[TTCN.EFFORT].sum()
        tts_df[TTCN.EFFORTPERC] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = summarized), axis = 1)

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))
        tts_df = tts_df.sort_values(by = TTCN.HASHTAG, ascending = True, kind = "stable").reset_index(drop = True)

        return tts_df
    def create_tts_by_year_month_spnv_df(self, tt_df : DataFrame, software_project_names : list[str]) -> DataFrame:

        '''
                Year    Month   SoftwareProjectName     SoftwareProjectVersion  Effort
            0   2025    1       nwknowledgebase         1.0.0                   01h 30m
            1   2025    4       nwknowledgebase         1.0.0                   24h 15m
            ...
        '''

        years : list[int] = self.__extract_years(tt_df = tt_df) 

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.SOFTWAREPROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.SOFTWAREPROJECTVERSION] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_version(descriptor = x))

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.MONTH, TTCN.SOFTWAREPROJECTNAME, TTCN.SOFTWAREPROJECTVERSION])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR, TTCN.MONTH, TTCN.SOFTWAREPROJECTNAME, TTCN.SOFTWAREPROJECTVERSION]).reset_index(drop = True)
    
        condition_three : Series = (tts_df[TTCN.SOFTWAREPROJECTNAME].isin(values = software_project_names))
        tts_df = tts_df.loc[condition_three]        

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))

        return tts_df
    def create_tts_by_timeranges_df(self, tt_df : DataFrame, min_occurrences : int) -> DataFrame:

            '''
                    Occurrences Occurrence%     TimeRanges
                0   71          22.33           [08:00-08:45]
                1   37          11.64           [08:00-08:30]
                ...
            '''

            tts_df : DataFrame = tt_df.copy(deep = True)
            tts_df = tts_df[[TTCN.STARTTIME, TTCN.ENDTIME]]

            tts_df[TTCN.TIMERANGE] = tts_df.apply(
                lambda x : self.__df_helper.create_time_range_id(
                    start_time = x[TTCN.STARTTIME], 
                    end_time = x[TTCN.ENDTIME]), axis = 1)

            count : NamedAgg = pd.NamedAgg(column = TTCN.TIMERANGE, aggfunc = "count")
            tts_df = tts_df[[TTCN.TIMERANGE]].groupby(by = [TTCN.TIMERANGE], as_index = False).agg(count = count)
            tts_df.rename(columns={"count" : TTCN.OCCURRENCES}, inplace = True)

            unknown_id : str = "Unknown"
            condition_one : Series = (tts_df[TTCN.TIMERANGE] != unknown_id)
            tts_df = tts_df.loc[condition_one]	
            tts_df.reset_index(drop = True, inplace = True)

            ascending : bool = False
            tts_df = tts_df.sort_values(by = [TTCN.OCCURRENCES], ascending = ascending).reset_index(drop = True)

            timeranges : NamedAgg = pd.NamedAgg(column = TTCN.TIMERANGE, aggfunc = list)
            tts_df = tts_df.groupby(by = [TTCN.OCCURRENCES], as_index = False).agg(TimeRanges = timeranges)
            tts_df = tts_df.sort_values(by = [TTCN.OCCURRENCES], ascending = ascending).reset_index(drop = True)
            tts_df = tts_df[[TTCN.OCCURRENCES, TTCN.TIMERANGES]]

            occurrences_total : int = int(tts_df[TTCN.OCCURRENCES].sum())
            tts_df[TTCN.OCCURRENCETOTAL] = occurrences_total
            tts_df[TTCN.OCCURRENCEPERC] = tts_df.apply(
                lambda x : self.__df_helper.calculate_percentage(float(x[TTCN.OCCURRENCES]), float(occurrences_total), 2), axis = 1)
            tts_df = tts_df[[TTCN.OCCURRENCES, TTCN.OCCURRENCETOTAL, TTCN.OCCURRENCEPERC, TTCN.TIMERANGES]]

            condition_two : Series = (tts_df[TTCN.OCCURRENCES] >= min_occurrences)
            tts_df = tts_df.loc[condition_two]	
            tts_df.reset_index(drop = True, inplace = True)

            tts_df = tts_df[[TTCN.OCCURRENCES, TTCN.OCCURRENCEPERC, TTCN.TIMERANGES]]

            return tts_df
    def create_ttd_effort_status_df(self, tt_df : DataFrame, is_correct : bool) -> DataFrame:

        '''
            StartTime	EndTime	Effort	IsCorrect	Expected    Message
            21:00       23:00   1h 00m  False       2h 00m      ...
            ...
        '''

        ttd_df : DataFrame = tt_df.copy(deep = True)
        
        ttd_df[TTCN.EFFORTSTATUS] = ttd_df.apply(
            lambda x : self.__df_helper.create_effort_status_and_cast_to_any(
                    idx = x.name, 
                    start_time_str = x[TTCN.STARTTIME],
                    end_time_str = x[TTCN.ENDTIME],
                    effort_str = x[TTCN.EFFORT]),
            axis = 1)
        
        ttd_df[TTCN.ISCORRECT] = ttd_df[TTCN.EFFORTSTATUS].apply(lambda x : x.is_correct)
        ttd_df[TTCN.EXPECTED] = ttd_df[TTCN.EFFORTSTATUS].apply(lambda x : x.expected_str)
        ttd_df[TTCN.MESSAGE] = ttd_df[TTCN.EFFORTSTATUS].apply(lambda x : x.message)
        ttd_df = ttd_df[[TTCN.STARTTIME, TTCN.ENDTIME, TTCN.EFFORT, TTCN.ISCORRECT, TTCN.EXPECTED, TTCN.MESSAGE]]

        condition : Series = (ttd_df[TTCN.ISCORRECT] == is_correct)
        ttd_df = ttd_df.loc[condition]

        return ttd_df    
    def create_definitions_df(self) -> DataFrame:

        '''Creates a dataframe containing all the definitions in use in this application.'''

        columns : list[str] = [DEFINITIONSTR.TERM, DEFINITIONSTR.DEFINITION]

        definitions : dict[str, str] = {
            DEFINITIONSTR.TT: "Time Tracking",
            DEFINITIONSTR.TTS: "Time Tracking Summary"
        }
        
        definitions_df : DataFrame = DataFrame(
            data = definitions.items(), 
            columns = columns
        )

        return definitions_df
@dataclass(frozen = True)
class EffortCell():
    
    '''Collects all the information related to a DataFrame cell that are required by EffortHighlighter.'''

    coordinate_pair : Tuple[int, int]
    effort_str : str
    effort_td : timedelta
class EffortHighlighter():

    '''Encapsulates all the logic related to highlighting cells in dataframes containing efforts.'''

    __df_helper : TTDataFrameHelper

    def __init__(self, df_helper : TTDataFrameHelper) -> None:

        self.__df_helper = df_helper

    def __is_effort(self, cell_content : str) -> bool :

        '''Returns True if content in ["00h 00m", "08h 00m", "20h 45m", "101h 30m", "+71h 00m", "-455h 45m", ...].'''

        pattern : str = r"^[+-]?(\d{2,})h (0[0-9]|[1-5][0-9])m$"
        match : Optional[Match[str]] = re.fullmatch(pattern = pattern, string = cell_content)

        if match is not None:
            return True
        else:
            return False
    def __append_new_effort_cell(self, effort_cells : list[EffortCell], coordinate_pair : Tuple[int, int], cell_content : str) -> None:

        '''Creates and append new EffortCell object to effort_cells.'''

        effort_cell : EffortCell = EffortCell(
            coordinate_pair = coordinate_pair,
            effort_str = cell_content,
            effort_td = self.__df_helper.unbox_effort(effort_str = cell_content)
        )
        
        effort_cells.append(effort_cell)
    def __extract_row(self, df : DataFrame, row_idx : int, column_names : list[str]) -> list[EffortCell]:

        '''Returns a collection of EffortCell objects for provided arguments.'''

        effort_cells : list[EffortCell] = []
        col_indices : list = [df.columns.get_loc(column_name) for column_name in column_names if column_name in df.columns]

        for col_idx in col_indices:

            coordinate_pair : Tuple[int, int] = (row_idx, col_idx)
            cell_content : str = str(df.iloc[row_idx, col_idx])

            if self.__is_effort(cell_content = cell_content):
                self.__append_new_effort_cell(effort_cells, coordinate_pair, cell_content)

        return effort_cells
    def __extract_n(self, mode : EFFORTMODE) -> int:

        '''Extracts n from mode.'''

        if mode == EFFORTMODE.top_one_effort_per_row:
            return 1
        elif mode == EFFORTMODE.top_three_efforts:
            return 3
        else:
            raise Exception(_MessageCollection.provided_mode_not_supported(mode))
    def __extract_top_n_effort_cells(self, effort_cells : list[EffortCell], n : int) -> list[EffortCell]:

        '''Extracts the n objects in bym_cells with the highest effort_td.'''

        sorted_cells : list[EffortCell] = sorted(effort_cells, key = lambda cell : cell.effort_td, reverse = True)
        top_n : list[EffortCell] = sorted_cells[:n]

        return top_n
    def __calculate_effort_cells(self, df : DataFrame, mode : EFFORTMODE, column_names : list[str]) -> list[EffortCell]:

        '''Returns a list of EffortCell objects according to df and mode.'''

        effort_cells : list[EffortCell] = []

        last_row_idx : int = len(df)
        n : int = self.__extract_n(mode = mode)
        current : list[EffortCell] = []

        if mode == EFFORTMODE.top_one_effort_per_row:
            for row_idx in range(last_row_idx):

                current = self.__extract_row(df = df, row_idx = row_idx, column_names = column_names)
                current = self.__extract_top_n_effort_cells(effort_cells = current, n = n)
                effort_cells.extend(current)
                
        elif mode == EFFORTMODE.top_three_efforts:
            for row_idx in range(last_row_idx):
                
                current = self.__extract_row(df = df, row_idx = row_idx, column_names = column_names)
                effort_cells.extend(current)

            effort_cells = self.__extract_top_n_effort_cells(effort_cells = effort_cells, n = n)

        else:
            raise Exception(_MessageCollection.provided_mode_not_supported(mode))

        return effort_cells
    def __add_tags(self, df : DataFrame, effort_cells : list[EffortCell], tags : Tuple[str, str]) -> DataFrame:

        '''Adds two HTML tags around the content of the cells listed in effort_cells.'''

        tagged_df : DataFrame = df.copy(deep = True)

        left_h : str = tags[0]
        right_h : str = tags[1]

        for effort_cell in effort_cells:

            row, col = effort_cell.coordinate_pair

            if row < len(df) and col < len(df.columns):
                tagged_df.iloc[row, col] = f"{left_h}{str(df.iloc[row, col])}{right_h}"
            
        return tagged_df
    def __highlight_dataframe(self, df : DataFrame, mode : EFFORTMODE, column_names : list[str] = []) -> DataFrame:

        '''
            Expects a df containing efforts into cells - i.e. "45h 45m", "77h 45m".
            Returns a df with highlighted cells as per arguments.

            Note: column names are converted to string to aid column search when the dataframe has mixed type column names.
        '''

        highlighted_df : DataFrame = df.copy(deep = True)
        highlighted_df.columns = highlighted_df.columns.map(str)

        if len(column_names) == 0:
            column_names = highlighted_df.columns.to_list()

        effort_cells : list[EffortCell] = self.__calculate_effort_cells(
            df = highlighted_df, 
            mode = mode,
            column_names = column_names
        )

        tags : Tuple[str, str] = (f"<mark style='background-color: skyblue'>", "</mark>")
        highlighted_df = self.__add_tags(df = highlighted_df, effort_cells = effort_cells, tags = tags)

        return highlighted_df
    def __get_latest_year(self, tts_by_hashtag_year_df : DataFrame) -> str:

        '''
            [ "Hashtag", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
                -> "2025"
        '''

        latest_year : str = str(max(int(column_name) for column_name in tts_by_hashtag_year_df.columns if str(column_name).isdigit()))
        
        return latest_year

    def highlight_tts_by_month(self, tts_by_month_df : DataFrame) -> DataFrame:
        
        '''Returns the provided dataframe with adequate highlights.'''

        mode : EFFORTMODE = EFFORTMODE.top_three_efforts

        highlighted_df : DataFrame = self.__highlight_dataframe(
            df = tts_by_month_df,
            mode = mode
        )
        
        return highlighted_df
    def highlight_tts_by_year(self, tts_by_year_df : DataFrame) -> DataFrame:
        
        '''Returns the provided dataframe with adequate highlights.'''

        mode : EFFORTMODE = EFFORTMODE.top_three_efforts

        highlighted_df : DataFrame = self.__highlight_dataframe(
            df = tts_by_year_df,
            mode = mode
        )
        
        return highlighted_df
    def highlight_tts_by_hashtag_year(self, tts_by_hashtag_year_df : DataFrame) -> DataFrame:
        
        '''Returns the provided dataframe with adequate highlights.'''

        mode : EFFORTMODE = EFFORTMODE.top_three_efforts
        latest_year : str = self.__get_latest_year(tts_by_hashtag_year_df)

        highlighted_df : DataFrame = self.__highlight_dataframe(
            df = tts_by_hashtag_year_df,
            mode = mode,
            column_names = [latest_year]
        )
        
        return highlighted_df
    def highlight_tts_by_hashtag(self, tts_by_hashtag_df : DataFrame) -> DataFrame:
        
        '''Returns the provided dataframe with adequate highlights.'''

        mode : EFFORTMODE = EFFORTMODE.top_three_efforts

        highlighted_df : DataFrame = self.__highlight_dataframe(
            df = tts_by_hashtag_df,
            mode = mode
        )
        
        return highlighted_df
    def highlight_tts_by_year_month_spnv(self, tts_by_year_month_spnv_df : DataFrame) -> DataFrame:
        
        '''Returns the provided dataframe with adequate highlights.'''

        mode : EFFORTMODE = EFFORTMODE.top_three_efforts

        highlighted_df : DataFrame = self.__highlight_dataframe(
            df = tts_by_year_month_spnv_df,
            mode = mode
        )
        
        return highlighted_df
class TTAdapter():

    '''Adapts SettingBag properties for use in TT*Factory methods.'''

    __df_factory : TTDataFrameFactory
    __effort_highlighter : EffortHighlighter

    def __init__(
        self, 
        df_factory : TTDataFrameFactory, 
        effort_highlighter : EffortHighlighter) -> None:
        
        self.__df_factory = df_factory
        self.__effort_highlighter = effort_highlighter

    def __create_tt_df(self, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tt_df : DataFrame = self.__df_factory.create_tt_df(
            excel_path = setting_bag.excel_path,
            excel_skiprows = setting_bag.excel_skiprows,
            excel_nrows = setting_bag.excel_nrows,
            excel_tabname = setting_bag.excel_tabname
            )

        return tt_df
    def __create_tt_latest_five_df(self, tt_df : DataFrame) -> DataFrame:

        '''Creates the expected dataframes out of the provided arguments.'''

        return self.__df_factory.create_tt_latest_five_df(tt_df = tt_df)
    def __create_tts_by_month_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_month_df : DataFrame = self.__df_factory.create_tts_by_month_df(
            tt_df = tt_df,
            now = setting_bag.now
        )

        return tts_by_month_df
    def __create_tts_by_year_df(self, tt_df : DataFrame) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_year_df : DataFrame = self.__df_factory.create_tts_by_year_df(
            tt_df = tt_df
        )

        return tts_by_year_df
    def __create_tts_by_range_df(self, tt_df : DataFrame) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_range_df : DataFrame = self.__df_factory.create_tts_by_range_df(
            tt_df = tt_df
        )

        return tts_by_range_df
    def __create_tts_by_spn_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_spn_df : DataFrame = self.__df_factory.create_tts_by_spn_df(
            tt_df = tt_df,
            software_project_names = setting_bag.tts_by_spn_software_project_names
        )

        return tts_by_spn_df
    def __create_tts_by_spv_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_spn_spv_df : DataFrame = self.__df_factory.create_tts_by_spv_df(
            tt_df = tt_df,
            software_project_names = setting_bag.tts_by_spv_software_project_names
        )

        return tts_by_spn_spv_df
    def __create_tts_by_hashtag_year_df(self, tt_df : DataFrame) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_hashtag_year_df : DataFrame = self.__df_factory.create_tts_by_hashtag_year_df(tt_df = tt_df)

        return tts_by_hashtag_year_df
    def __create_tts_by_hashtag_df(self, tt_df : DataFrame) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_hashtag_df : DataFrame = self.__df_factory.create_tts_by_hashtag_df(tt_df = tt_df)

        return tts_by_hashtag_df
    def __create_tts_by_year_month_spnv_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_year_month_spnv_df : DataFrame = self.__df_factory.create_tts_by_year_month_spnv_df(
            tt_df = tt_df,
            software_project_names = setting_bag.tts_by_spv_software_project_names
        )

        return tts_by_year_month_spnv_df
    def __create_tts_by_timeranges_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_timeranges_df : DataFrame = self.__df_factory.create_tts_by_timeranges_df(
            tt_df = tt_df,
            min_occurrences = setting_bag.tts_by_timeranges_min_occurrences
        )

        return tts_by_timeranges_df
    def __create_ttd_effort_status_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        ttd_effort_status_df : DataFrame = self.__df_factory.create_ttd_effort_status_df(
            tt_df = tt_df,
            is_correct = setting_bag.ttd_effort_status_is_correct
        )

        return ttd_effort_status_df

    def create_summary(self, setting_bag : SettingBag) -> TTSummary:

        '''Creates a TTSummary object out of setting_bag.'''

        tt_df : DataFrame = self.__create_tt_df(setting_bag = setting_bag)
        tt_latest_five_df : DataFrame = self.__create_tt_latest_five_df(tt_df = tt_df)
        tts_by_month_df : DataFrame = self.__create_tts_by_month_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_df : DataFrame = self.__create_tts_by_year_df(tt_df = tt_df)
        tts_by_range_df : DataFrame = self.__create_tts_by_range_df(tt_df = tt_df)
        tts_by_spn_df : DataFrame = self.__create_tts_by_spn_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_spv_df : DataFrame = self.__create_tts_by_spv_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_hashtag_year_df : DataFrame = self.__create_tts_by_hashtag_year_df(tt_df = tt_df)
        tts_by_hashtag_df : DataFrame = self.__create_tts_by_hashtag_df(tt_df = tt_df)
        tts_by_year_month_spnv_df : DataFrame = self.__create_tts_by_year_month_spnv_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_timeranges_df : DataFrame = self.__create_tts_by_timeranges_df(tt_df = tt_df, setting_bag = setting_bag)
        ttd_effort_status_df : DataFrame = self.__create_ttd_effort_status_df(tt_df = tt_df, setting_bag = setting_bag)
        definitions_df : DataFrame = self.__df_factory.create_definitions_df()

        if setting_bag.enable_effort_highlighting:
            tts_by_month_df = self.__effort_highlighter.highlight_tts_by_month(tts_by_month_df = tts_by_month_df)
            tts_by_year_df = self.__effort_highlighter.highlight_tts_by_year(tts_by_year_df = tts_by_year_df)
            tts_by_hashtag_year_df = self.__effort_highlighter.highlight_tts_by_hashtag_year(tts_by_hashtag_year_df = tts_by_hashtag_year_df)
            tts_by_hashtag_df = self.__effort_highlighter.highlight_tts_by_hashtag(tts_by_hashtag_df = tts_by_hashtag_df)
            tts_by_year_month_spnv_df = self.__effort_highlighter.highlight_tts_by_year_month_spnv(tts_by_year_month_spnv_df = tts_by_year_month_spnv_df)

        tt_summary : TTSummary = TTSummary(
            tt_df = tt_df,
            tt_latest_five_df = tt_latest_five_df,
            tts_by_month_df = tts_by_month_df,
            tts_by_year_df = tts_by_year_df,
            tts_by_range_df = tts_by_range_df,
            tts_by_spn_df = tts_by_spn_df,
            tts_by_spv_df = tts_by_spv_df,
            tts_by_hashtag_year_df = tts_by_hashtag_year_df,
            tts_by_hashtag_df = tts_by_hashtag_df,
            tts_by_year_month_spnv_df = tts_by_year_month_spnv_df,
            tts_by_timeranges_df = tts_by_timeranges_df,
            ttd_effort_status_df = ttd_effort_status_df,
            definitions_df = definitions_df
        )

        return tt_summary
class TTReportManager():

    '''Collects all the logic related to the creation of reports out of TTSummary objects.'''

    def __format_for_file_name(self, last_update : datetime) ->  str:

        '''Example: "20251222".'''

        return last_update.strftime("%Y%m%d")
    def __format_for_title(self, last_update : datetime) ->  str:

        '''Example: "2025-12-22".'''

        return last_update.strftime("%Y-%m-%d")
    def __create_report_file_paths(self, folder_path: str, last_update : datetime) -> Tuple[Path, Path]:

        '''
            Example: 
                - /home/nwreadinglist/TIMETRACKINGREPORT20251222.html
                - /home/nwreadinglist/TIMETRACKINGREPORT20251222.pdf
        '''

        file_name : str = f"TIMETRACKINGREPORT{self.__format_for_file_name(last_update)}"
        base_path : Path = Path(folder_path) / file_name

        html_path : Path = base_path.with_suffix(".html")
        pdf_path : Path = base_path.with_suffix(".pdf")

        return (html_path, pdf_path)
    def __create_html(self, df : DataFrame, title : str, formatters : Optional[dict], footer : Optional[str] = None) -> str:

        """Converts the provided DataFrame into a styled HTML table using a layout similar to Jupyter Notebook."""

        styled = (
            df.style
            .format(formatters)
            .hide(axis="index")
            .set_table_styles(
                [
                    {
                        "selector": "thead th", 
                        "props": "background-color: #eeeeee; color: #333; font-weight: bold; padding: 8px 10px; text-align: left; border: none;"
                    },
                    {
                        "selector": "tbody td", 
                        "props": "padding: 8px 10px; text-align: left; border: none; white-space: nowrap;"
                    },
                    {
                        "selector": "tbody tr:nth-child(even)", 
                        "props": "background-color: #f5f5f5;"
                    },
                    {
                        "selector": "", 
                        "props": "border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 12px; color: #444;"
                    }
                ]
            )
        )

        footer_html : str = (
                f"<br/><div style='margin-top: 6px; font-size: 14px; color: #666;'>{footer}</div>"
                if footer
                else ""
            )
    
        return (
            "<div style='margin-bottom: 20px;'>"
            f"<h2>{title}</h2>\n"
            f"{styled.to_html()}\n"
            f"{footer_html}"
            "</div>"
            )
    def __create_html_sections(self, tt_summary : TTSummary, formatters : Optional[dict]) -> list[str]:

        '''Converts summary to a collection of HTML code blocks.'''

        html_sections: list[str] = []
        
        html_sections.append(self.__create_html(tt_summary.tt_latest_five_df, REPORTSTR.TTLATESTFIVE, formatters))
        html_sections.append(self.__create_html(tt_summary.tts_by_month_df, REPORTSTR.TTSBYMONTH, formatters))
        html_sections.append(self.__create_html(tt_summary.tts_by_year_df, REPORTSTR.TTSBYYEAR, formatters))
        html_sections.append(self.__create_html(tt_summary.tts_by_range_df, REPORTSTR.TTSBYRANGE, formatters))
        html_sections.append(self.__create_html(tt_summary.tts_by_spn_df, REPORTSTR.TTSBYSPN, formatters))
        html_sections.append(self.__create_html(tt_summary.tts_by_spv_df, REPORTSTR.TTSBYSPV, formatters))
        html_sections.append(self.__create_html(tt_summary.tts_by_hashtag_year_df, REPORTSTR.TTSBYHASHTAGYEAR, formatters))
        html_sections.append(self.__create_html(tt_summary.tts_by_hashtag_df, REPORTSTR.TTSBYHASHTAG, formatters))        
        html_sections.append(self.__create_html(tt_summary.tts_by_year_month_spnv_df, REPORTSTR.TTSBYYEARMONTHSPNV, formatters))
        html_sections.append(self.__create_html(tt_summary.tts_by_timeranges_df, REPORTSTR.TTSBYTIMERANGES, formatters))
        html_sections.append(self.__create_html(tt_summary.definitions_df, REPORTSTR.DEFINITIONS, formatters))

        return html_sections
    def __create_html_template(self, html_sections : list[str], last_update : datetime) -> str:

        '''Creates HTML template.'''

        full_html: str = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>Time Tracking Report | {self.__format_for_title(last_update)}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                h1 {{
                    text-align: left;
                    margin-bottom: 40px;
                }}
                h2 {{
                    margin-top: 40px;
                    border-bottom: 2px solid #ddd;
                    padding-bottom: 5px;
                }}
                p {{
                    margin-top: 10px;
                    margin-bottom: 10px;
                    line-height: 1.5;
                    font-size: 12px;
                }}                
            </style>
        </head>
        <body>
            <img src='https://avatars.githubusercontent.com/u/10279234' alt='NW logo' style='width:120px; height:120px; margin-bottom:10px;'>
            <h1>Time Tracking Report | {self.__format_for_title(last_update)}</h1>
            {''.join(html_sections)}
            <br/><p>© 2025 numbworks. This report is generated by 'nwtimetracking' and licensed under the MIT License. Additional information: <a href="https://github.com/numbworks">github.com/numbworks</a>.</p>
        </body>
        </html>
        """
        
        return full_html
    def __create_stylesheet(self):

        '''Creates a CSS stylesheet.'''

        stylesheet : CSS = CSS(string = "@page { size: A3 landscape; margin: 20mm; }")
        
        return stylesheet
    
    def save_as_report(
        self, 
        tt_summary: TTSummary, 
        folder_path : str, 
        last_update : datetime, 
        save_html : bool, 
        save_pdf : bool, 
        formatters : Optional[dict] = None) -> None:
        
        '''Builds an HTML report from selected DataFrames in RLSummary and saves it as both HTML and PDF.'''

        html_path, pdf_path = self.__create_report_file_paths(folder_path = folder_path, last_update = last_update)
        html_sections : list[str] = self.__create_html_sections(tt_summary = tt_summary, formatters = formatters)
        full_html : str = self.__create_html_template(html_sections = html_sections, last_update = last_update)

        if save_html:
            html_path.write_text(data = full_html, encoding = "utf-8")
        
        if save_pdf:
            HTML(string = full_html).write_pdf(target = str(pdf_path), stylesheets = [self.__create_stylesheet()])
@dataclass(frozen=True)
class ComponentBag():

    '''Represents a collection of components.'''

    file_path_manager : FilePathManager = field(default = FilePathManager())
    file_manager : FileManager = field(default = FileManager(file_path_manager = FilePathManager()))
    displayer : Displayer = field(default = Displayer())
    ttr_manager : TTReportManager = field(default = TTReportManager())
    tt_adapter : TTAdapter = field(default = TTAdapter(
        df_factory = TTDataFrameFactory(df_helper = TTDataFrameHelper()),
        effort_highlighter = EffortHighlighter(df_helper = TTDataFrameHelper())))
class TimeTrackingProcessor():

    '''Collects all the logic related to the processing of "Time Tracking.xlsx".'''

    __component_bag : ComponentBag
    __setting_bag : SettingBag
    __tt_summary : TTSummary

    def __init__(self, component_bag : ComponentBag, setting_bag : SettingBag) -> None:

        self.__component_bag = component_bag
        self.__setting_bag = setting_bag

    def __validate_summary(self) -> None:
        
        '''Raises an exception if __tt_summary is None.'''

        if not hasattr(self, '_TimeTrackingProcessor__tt_summary'):
            raise Exception(_MessageCollection.please_run_initialize_first())
    def __merge_formatters(self) -> dict:

        '''Merges all formatters in one dict'''

        formatters : dict = (
            self.__setting_bag.tts_by_hashtag_formatters | 
            self.__setting_bag.tts_by_timeranges_formatters
        )
            
        return formatters

    def initialize(self) -> None:

        '''Creates a TTSummary object and assign it to __tt_summary.'''

        self.__tt_summary = self.__component_bag.tt_adapter.create_summary(setting_bag = self.__setting_bag)
    def process_tt(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tt.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tt
        df : DataFrame = self.__tt_summary.tt_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)  
    def process_tt_latest_five(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tt_latest_five.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tt_latest_five
        df : DataFrame = self.__tt_summary.tt_latest_five_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_tts_by_month(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_month.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_month
        df : DataFrame = self.__tt_summary.tts_by_month_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_tts_by_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year
        df : DataFrame = self.__tt_summary.tts_by_year_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_tts_by_range(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_range.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_range
        df : DataFrame = self.__tt_summary.tts_by_range_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_tts_by_spn(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_spn.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_spn
        df : DataFrame = self.__tt_summary.tts_by_spn_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_tts_by_spv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_spv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_spv
        df : DataFrame = self.__tt_summary.tts_by_spv_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_tts_by_hashtag_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_hashtag_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_hashtag_year
        df : DataFrame = self.__tt_summary.tts_by_hashtag_year_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_tts_by_hashtag(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_hashtag.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_hashtag
        df : DataFrame = self.__tt_summary.tts_by_hashtag_df
        formatters : dict = self.__setting_bag.tts_by_hashtag_formatters

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df, formatters = formatters)
    def process_tts_by_year_month_spnv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year_month_spnv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year_month_spnv
        df : DataFrame = self.__tt_summary.tts_by_year_month_spnv_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_tts_by_timeranges(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_timeranges.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_timeranges
        df : DataFrame = self.__tt_summary.tts_by_timeranges_df
        formatters : dict = self.__setting_bag.tts_by_timeranges_formatters

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df, formatters = formatters)
    def process_ttd_effort_status(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_ttd_effort_status.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_ttd_effort_status
        df : DataFrame = self.__tt_summary.ttd_effort_status_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)
    def process_definitions(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_definitions.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_definitions
        df : DataFrame = self.__tt_summary.definitions_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)

    def get_summary(self) -> TTSummary:

        '''
            Returns __tt_summary.

            It raises an exception if the 'initialize' method has not been run yet.    
        '''

        self.__validate_summary()

        return self.__tt_summary
    def save_as_report(self) -> None:

        '''Builds an HTML report from selected DataFrames in RLSummary and saves it as both HTML and PDF.'''

        self.__validate_summary()

        options : list = self.__setting_bag.options_report
        formatters :dict = self.__merge_formatters()
        save_html : bool = False
        save_pdf : bool = False

        if OPTION.save_html in options:
            save_html = True

        if OPTION.save_pdf in options:
            save_pdf = True

        self.__component_bag.ttr_manager.save_as_report(
            tt_summary = self.__tt_summary,
            folder_path = self.__setting_bag.working_folder_path,
            last_update = self.__setting_bag.now,
            save_html = save_html,
            save_pdf = save_pdf,
            formatters = formatters)

# MAIN
if __name__ == "__main__":
    pass