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
from enum import StrEnum
from numpy import uint
from pandas import DataFrame, Series, NamedAgg
from typing import Any, Callable, Literal, Optional, Tuple, cast

# LOCAL MODULES
from nwshared import Formatter, FilePathManager, FileManager, LambdaProvider, MarkdownHelper, Displayer

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
    PROJECTNAME = "ProjectName"
    PROJECTVERSION = "ProjectVersion"
    DME = "DME"
    TME = "TME"
    DYE = "DYE"
    TYE = "TYE"
    TREND = "↕"
    EFFORTPRC = "Effort%"
    YEARLYTARGET = "YearlyTarget"
    TARGETDIFF = "TargetDiff"
    ISTARGETMET = "IsTargetMet"
    YEARLYTOTAL = "YearlyTotal"
    TOTARGET = "ToTarget"
    PERCDME = "%_DME"
    PERCTME = "%_TME"
    PERCDYE = "%_DYE"
    PERCTYE = "%_TYE"
    DE = "DE"
    TE = "TE"
    PERCDE = "%_DE"
    PERCTE = "%_TE"
    EFFORTSTATUS = "EffortStatus"
    ESISCORRECT = "ES_IsCorrect"
    ESEXPECTED = "ES_Expected"
    ESMESSAGE = "ES_Message"
    TIMERANGEID = "TimeRangeId"
    OCCURRENCES = "Occurrences"
class TTID(StrEnum):
    
    '''Collects all the ids that identify the dataframes created by TTDataFrameFactory.'''

    TTSBYMONTH = "tts_by_month"
class DEFINITIONSCN(StrEnum):
    
    '''Collects all the column names used by definitions.'''

    TERM = "Term"
    DEFINITION = "Definition"

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
    def no_mdinfo_found(id : TTID) -> str:
        return f"No MDInfo object found for id='{id}'."
    @staticmethod
    def please_run_initialize_first() -> str:
        return "Please run the 'initialize' method first."
    @staticmethod
    def this_content_successfully_saved_as(id : TTID, file_path : str) -> str:
        return f"This content (id: '{id}') has been successfully saved as '{file_path}'."

# CLASSES
@dataclass(frozen=True)
class YearlyTarget():
    
    '''Represents an amount of hours for a given year.'''

    year : int
    hours : timedelta
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
class MDInfo():

    '''Represents a collection of information related to a Markdown file.'''

    id : TTID
    file_name : str
    paragraph_title : str
@dataclass(frozen = True)
class TTSummary():

    '''Collects all the dataframes and markdowns.'''

    # Dataframes
    tt_df : DataFrame
    tts_by_month_tpl : Tuple[DataFrame, DataFrame]
    tts_by_year_df : DataFrame
    tts_by_year_month_tpl : Tuple[DataFrame, DataFrame]
    tts_by_year_month_spnv_tpl : Tuple[DataFrame, DataFrame]
    tts_by_year_spnv_tpl : Tuple[DataFrame, DataFrame]
    tts_by_spn_df : DataFrame
    tts_by_spn_spv_df : DataFrame
    tts_by_hashtag_df : DataFrame
    tts_by_hashtag_year_df : DataFrame
    tts_by_efs_tpl : Tuple[DataFrame, DataFrame]
    tts_by_tr_df : DataFrame
    definitions_df : DataFrame

    # Markdowns
    tts_by_month_md : str
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

        years : list[int] = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

        return years
    def get_all_yearly_targets(self) -> list[YearlyTarget]:

        '''Returns a list of years.'''

        yearly_targets : list[YearlyTarget] = [
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

        return yearly_targets    
    def get_most_recent_x_years(self, x : uint) -> list[int]:

        '''Returns a list of years.'''

        years : list[int] = self.get_all_years()

        if x <= len(years):
            years = years[(len(years) - int(x)):]

        return years
class SoftwareProjectNameProvider():

    '''Collects all the logic related to the retrieval of software project names.'''

    def get_all_software_project_names(self) -> list[str]:

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
            "nwtraderaanalytics"
        ]

        return software_project_names
    def get_all_software_project_names_by_spv(self) -> list[str]:

        '''Returns a list of software project names to breakdown by version.'''

        software_project_names_by_spv : list[str] = [
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

        return software_project_names_by_spv
class MDInfoProvider():

    '''Collects all the logic related to the retrieval of MDInfo objects.'''

    def get_all(self) -> list[MDInfo]:

        '''Returns a list of MDInfo objects.'''

        md_infos : list[MDInfo] = [
                MDInfo(id = TTID.TTSBYMONTH, file_name = "TIMETRACKINGBYMONTH.md", paragraph_title = "Time Tracking By Month")
            ]
        
        return md_infos
@dataclass(frozen=True)
class SettingBag():

    '''Represents a collection of settings.'''

    # Without Defaults
    options_tt : list[Literal["display"]]
    options_tts_by_month : list[Literal["display", "save"]]
    options_tts_by_year : list[Literal["display"]]
    options_tts_by_year_month : list[Literal["display"]]
    options_tts_by_year_month_spnv : list[Literal["display"]]
    options_tts_by_year_spnv : list[Literal["display"]]    
    options_tts_by_spn : list[Literal["display", "log"]]
    options_tts_by_spn_spv : list[Literal["display", "log"]]
    options_tts_by_hashtag : list[Literal["display"]]
    options_tts_by_hashtag_year : list[Literal["display"]]
    options_tts_by_efs : list[Literal["display"]]
    options_tts_by_tr : list[Literal["display"]]
    options_definitions : list[Literal["display"]]    
    excel_nrows : int
    tts_by_year_month_spnv_display_only_spn : Optional[str]
    tts_by_year_spnv_display_only_spn : Optional[str]
    tts_by_spn_spv_display_only_spn : Optional[str]

    # With Defaults
    working_folder_path : str = field(default = "/home/nwtimetracking/")
    excel_path : str = field(default = DefaultPathProvider().get_default_time_tracking_path())
    excel_skiprows : int = field(default = 0)
    excel_tabname : str = field(default = "Sessions")
    years : list[int] = field(default_factory = lambda : YearProvider().get_all_years())
    yearly_targets : list[YearlyTarget] = field(default_factory = lambda : YearProvider().get_all_yearly_targets())
    now : datetime = field(default = datetime.now())
    software_project_names : list[str] = field(default_factory = lambda : SoftwareProjectNameProvider().get_all_software_project_names())
    software_project_names_by_spv : list[str] = field(default_factory = lambda : SoftwareProjectNameProvider().get_all_software_project_names_by_spv())
    tt_head_n : Optional[uint] = field(default = uint(5))
    tt_display_head_n_with_tail : bool = field(default = True)
    tt_hide_index : bool = field(default = True)
    tts_by_year_month_display_only_years : Optional[list[int]] = field(default_factory = lambda : YearProvider().get_most_recent_x_years(x = uint(1)))
    tts_by_year_month_spnv_formatters : dict = field(default_factory = lambda : { "%_DME" : "{:.2f}", "%_TME" : "{:.2f}" })
    tts_by_year_spnv_formatters : dict = field(default_factory = lambda : { "%_DYE" : "{:.2f}", "%_TYE" : "{:.2f}" })
    tts_by_spn_formatters : dict = field(default_factory = lambda : { "%_DE" : "{:.2f}", "%_TE" : "{:.2f}" })
    tts_by_spn_remove_untagged : bool = field(default = True)
    tts_by_hashtag_formatters : dict = field(default_factory = lambda : { "Effort%" : "{:.2f}" })
    tts_by_efs_is_correct : bool = field(default = False)
    tts_by_efs_n : uint = field(default = uint(25))
    tts_by_tr_unknown_id : str = field(default = "Unknown")
    tts_by_tr_remove_unknown_occurrences : bool = field(default = True)
    tts_by_tr_filter_by_top_n : Optional[uint] = field(default = uint(5))
    tts_by_tr_head_n : Optional[uint] = field(default = uint(10))
    tts_by_tr_display_head_n_with_tail : bool = field(default = False)
    md_infos : list[MDInfo] = field(default_factory = lambda : MDInfoProvider().get_all())
    md_last_update : datetime = field(default = datetime.now())
class TTDataFrameHelper():

    '''Collects helper functions for TTDataFrameFactory.'''

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
    def convert_string_to_timedelta(self, td_str : str) -> timedelta:

        '''"5h 30m" => 5:30:00'''

        td : timedelta = pd.Timedelta(value = td_str).to_pytimedelta()

        return td
    def format_timedelta(self, td : timedelta, add_plus_sign : bool) -> str:

        '''
            4 days 19:15:00	=> "115h 15m" (or +115h 15m)
            -9 days +22:30:00 => "-194h 30m"
        '''

        total_seconds : float = td.total_seconds()
        hours : int = int(total_seconds // 3600)
        minutes : int = int((total_seconds % 3600) // 60)

        hours_str : str = str(hours).zfill(2)
        minutes_str : str = str(minutes ).zfill(2)    
        formatted : str = f"{hours_str}h {minutes_str}m"

        if (add_plus_sign == True and td.days >= 0):
            formatted = f"+{formatted}"

        return formatted
    def get_trend_by_timedelta(self, td_1 : timedelta, td_2 : timedelta) -> str:

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
    def try_consolidate_trend_column_name(self, column_name : str) -> str:

        '''
            "2016"  => "2016"
            "↕1"    => "↕"
        '''

        if column_name.startswith(TTCN.TREND):
            return TTCN.TREND
        
        return column_name
    def get_yearly_target(self, yearly_targets : list[YearlyTarget], year : int) -> Optional[YearlyTarget]:

        '''Retrieves the YearlyTarget object for the provided "year" or None.'''

        for yearly_target in yearly_targets:
            if yearly_target.year == year:
                return yearly_target
            
        return None
    def is_yearly_target_met(self, effort : timedelta, yearly_target : timedelta) -> bool:

        if effort >= yearly_target:
            return True

        return False
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
    def create_time_range_id(self, start_time : str, end_time : str, unknown_id : str) -> str:
            
        '''
            Creates a unique time range identifier out of the provided parameters.
            If parameters are empty, it returns unknown_id.
        '''

        time_range_id : str = f"{start_time}-{end_time}"

        if len(start_time) == 0 or len(end_time) == 0:
            time_range_id = unknown_id

        return time_range_id
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
            actual_td : timedelta = self.convert_string_to_timedelta(td_str = effort_str)

            expected_td : timedelta = (end_time_dt - start_time_dt)
            expected_str : str = self.format_timedelta(td = expected_td, add_plus_sign = False)
            
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
        actual_td : timedelta = self.convert_string_to_timedelta(td_str = effort_str)
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
class TTDataFrameFactory():

    '''Collects all the logic related to dataframe creation out of "Time Tracking.xlsx".'''

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
    def __create_raw_tts_by_year_month_spnv(self, tt_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:
        
        '''
                Year	Month	ProjectName	        ProjectVersion	Effort
            0	2023	4	    nwtraderaanalytics	2.0.0	        0 days 09:15:00
            1	2023	5	    NW.AutoProffLibrary	1.0.0	        0 days 09:30:00
            ...
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.PROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.PROJECTVERSION] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_version(descriptor = x))

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.MONTH, TTCN.PROJECTNAME, TTCN.PROJECTVERSION])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR, TTCN.MONTH, TTCN.PROJECTNAME, TTCN.PROJECTVERSION]).reset_index(drop = True)
    
        condition_three : Series = (tts_df[TTCN.PROJECTNAME].isin(values = software_project_names))
        tts_df = tts_df.loc[condition_three]

        return tts_df
    def __create_raw_tts_by_dme(self, tt_df : DataFrame, years : list[int]) -> DataFrame:
        
        '''
                Year	Month	DME
            0	2023	4	    0 days 09:15:00
            1	2023	6	    0 days 06:45:00
            ...

            DME = DevelopmentMonthlyEffort
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.PROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.PROJECTVERSION] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_version(descriptor = x))

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.MONTH])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR, TTCN.MONTH]).reset_index(drop = True)
        tts_df.rename(columns = {TTCN.EFFORT : TTCN.DME}, inplace = True)

        return tts_df
    def __create_raw_tts_by_tme(self, tt_df : DataFrame, years : list[int]) -> DataFrame:
        
        '''
                Year	Month	TME
            0	2023	4	    0 days 09:15:00
            1	2023	6	    0 days 06:45:00
            ...

            TME = TotalMonthlyEffort
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition : Series = (tt_df[TTCN.YEAR].isin(values = years))
        tts_df = tts_df.loc[condition]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.MONTH])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR, TTCN.MONTH]).reset_index(drop = True)
        tts_df.rename(columns = {TTCN.EFFORT : TTCN.TME}, inplace = True)

        return tts_df
    def __create_raw_tts_by_year_spnv(self, tt_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:
        
        '''
                Year	ProjectName	        ProjectVersion	Effort
            0	2023	nwtraderaanalytics	2.0.0	        0 days 09:15:00
            1	2023	NW.AutoProffLibrary	1.0.0	        0 days 09:30:00
            ...
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.PROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.PROJECTVERSION] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_version(descriptor = x))

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.PROJECTNAME, TTCN.PROJECTVERSION])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR, TTCN.PROJECTNAME, TTCN.PROJECTVERSION]).reset_index(drop = True)
    
        condition_three : Series = (tts_df[TTCN.PROJECTNAME].isin(values = software_project_names))
        tts_df = tts_df.loc[condition_three]
        tts_df = tts_df.sort_values(by = [TTCN.YEAR, TTCN.PROJECTNAME, TTCN.PROJECTVERSION]).reset_index(drop = True)

        return tts_df
    def __create_raw_tts_by_dye(self, tt_df : DataFrame, years : list[int]) -> DataFrame:
        
        '''
                Year	DYE
            0	2023	0 days 09:15:00
            1	2023	0 days 06:45:00
            ...

            DYE = DevelopmentYearlyEffort
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.PROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.PROJECTVERSION] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_version(descriptor = x))

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR]).reset_index(drop = True)
        tts_df.rename(columns = {TTCN.EFFORT : TTCN.DYE}, inplace = True)

        return tts_df
    def __create_raw_tts_by_tye(self, tt_df : DataFrame, years : list[int]) -> DataFrame:
        
        '''
                Year	TYE
            0	2023	0 days 09:15:00
            1	2023	0 days 06:45:00
            ...

            TYE = TotalYearlyEffort
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition : Series = (tt_df[TTCN.YEAR].isin(values = years))
        tts_df = tts_df.loc[condition]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR]).reset_index(drop = True)
        tts_df.rename(columns = {TTCN.EFFORT : TTCN.TYE}, inplace = True)

        return tts_df
    def __create_raw_tts_by_spn(self, tt_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame: 
        
        '''
                Hashtag	ProjectName	            Effort
            0	#python	nwtraderaanalytics	    72h 00m
            1	#python	nwreadinglistmanager	66h 30m
            2	#python	nwtimetrackingmanager	18h 45m
            3	#csharp	NW.WIDJobs	            430h 00m
            ...
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.PROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.PROJECTNAME, TTCN.HASHTAG])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.PROJECTNAME]).reset_index(drop = True)

        condition_three : Series = (tts_df[TTCN.PROJECTNAME].isin(values = software_project_names))
        tts_df = tts_df.loc[condition_three] 
        tts_df = tts_df.sort_values(by = [TTCN.HASHTAG, TTCN.EFFORT], ascending = [False, False]).reset_index(drop = True)

        tts_df = tts_df[[TTCN.HASHTAG, TTCN.PROJECTNAME, TTCN.EFFORT]]

        return tts_df
    def __create_raw_de(self, tt_df : DataFrame, years : list[int]) -> timedelta:
        
        '''3 days 21:15:00'''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        summarized : timedelta = tts_df[TTCN.EFFORT].sum()

        return summarized
    def __create_raw_te(self, tt_df : DataFrame, years : list[int], remove_untagged : bool) -> timedelta:

        '''186 days 11:15:00'''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        tts_df = tts_df.loc[condition_one]

        if remove_untagged:
            condition_two : Series = (tt_df[TTCN.HASHTAG] != "#untagged")
            tts_df = tts_df.loc[condition_two]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        summarized : timedelta = tts_df[TTCN.EFFORT].sum()

        return summarized    
    def __create_raw_tts_by_spn_spv(self, tt_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

        '''
                ProjectName	                ProjectVersion	Effort
            0	NW.MarkdownTables	        1.0.0	        0 days 15:15:00
            1	NW.MarkdownTables	        1.0.1	        0 days 02:30:00
            2	NW.NGramTextClassification	1.0.0	        3 days 02:15:00
            ...
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition_one : Series = (tt_df[TTCN.YEAR].isin(values = years))
        condition_two : Series = (tt_df[TTCN.ISSOFTWAREPROJECT] == True)
        tts_df = tts_df.loc[condition_one & condition_two]

        tts_df[TTCN.PROJECTNAME] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
        tts_df[TTCN.PROJECTVERSION] = tts_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_version(descriptor = x))

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.PROJECTNAME, TTCN.PROJECTVERSION])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.PROJECTNAME, TTCN.PROJECTVERSION]).reset_index(drop = True)

        condition_three : Series = (tts_df[TTCN.PROJECTNAME].isin(values = software_project_names))
        tts_df = tts_df.loc[condition_three]
        tts_df = tts_df.sort_values(by = [TTCN.PROJECTNAME, TTCN.PROJECTVERSION]).reset_index(drop = True)

        return tts_df
    def __create_default_raw_ttm(self, year : int) -> DataFrame:

        '''
            default_df:

                    Month	2019
                0	1	    0 days
                ...
        '''

        td : timedelta = self.__df_helper.convert_string_to_timedelta(td_str = "0h 00m")

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

        ttm_df[TTCN.EFFORT] = ttm_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        ttm_df[str(year)] = ttm_df[TTCN.EFFORT]
        cn_effort = str(year)    

        ttm_df = ttm_df.groupby([TTCN.MONTH])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        ttm_df = ttm_df.sort_values(by = TTCN.MONTH).reset_index(drop = True)

        ttm_df = self.__try_complete_raw_ttm(ttm_df = ttm_df, year = year)
        ttm_df = self.__enforce_dataframe_definition_for_raw_ttm_df(df = ttm_df)

        return ttm_df
    def __create_raw_tts_by_year_hashtag(self, tt_df : DataFrame, years : list[int]) -> DataFrame:

        '''
                Year	Hashtag	        Effort
            0   2023	#csharp	        0 days 15:15:00
            1   2023	#maintenance	0 days 02:30:00
            2   2023	#powershell	    3 days 02:15:00
            ...   
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition : Series = (tt_df[TTCN.YEAR].isin(values = years))
        tts_df = tts_df.loc[condition]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.HASHTAG])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.HASHTAG, TTCN.YEAR]).reset_index(drop = True)

        return tts_df
    def __create_raw_tts_by_hashtag(self, tt_df : DataFrame) -> DataFrame:

        '''
                Hashtag	        Effort          Effort%
            0   #csharp	        0 days 15:15:00 56.49
            1   #maintenance	0 days 02:30:00 23.97
            2   #powershell	    3 days 02:15:00 6.43
            ...   
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.HASHTAG])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)

        summarized : float = tts_df[TTCN.EFFORT].sum()
        tts_df[TTCN.EFFORTPRC] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = summarized), axis = 1)     

        return tts_df

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
            
            expansion_df[cn_trend] = expansion_df.apply(lambda x : self.__df_helper.get_trend_by_timedelta(td_1 = x[cn_trend_1], td_2 = x[cn_trend_2]), axis = 1) 

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
    def __remove_unknown_occurrences(self, tts_by_tr_df : DataFrame, unknown_id : str) -> DataFrame:

        '''Removes the provided uknown_id from the "TimeRangeId" column of the provided DataFrame.'''

        condition : Series = (tts_by_tr_df[TTCN.TIMERANGEID] != unknown_id)
        tts_by_tr_df = tts_by_tr_df.loc[condition]	
        tts_by_tr_df.reset_index(drop = True, inplace = True)

        return tts_by_tr_df
    def __filter_by_year(self, df : DataFrame, years : list[int]) -> DataFrame:

        '''
            Returns a DataFrame that in the "TTCN.YEAR" column has only values contained in "years".

            Returns df if years is an empty list.    
        '''

        filtered_df : DataFrame = df.copy(deep = True)

        if len(years) > 0:
            condition : Series = filtered_df[TTCN.YEAR].isin(years)
            filtered_df = df.loc[condition]

        return filtered_df
    def __filter_by_software_project_name(self, df : DataFrame, software_project_name : Optional[str]) -> DataFrame:

        '''
            Returns a DataFrame that in the "TTCN.PROJECTNAME" column has only values that are equal to software_project_name.
            
            Returns df if software_project_name is None.   
        '''

        filtered_df : DataFrame = df.copy(deep = True)

        if software_project_name is not None:
            condition : Series = (filtered_df[TTCN.PROJECTNAME] == software_project_name)
            filtered_df = df.loc[condition]

        return filtered_df
    def __filter_by_is_correct(self, tts_by_efs_df : DataFrame, is_correct : bool) -> DataFrame:

        '''Returns a DataFrame that contains only rows that match the provided is_correct.'''

        filtered_df : DataFrame = tts_by_efs_df.copy(deep = True)

        condition : Series = (filtered_df[TTCN.ESISCORRECT] == is_correct)
        filtered_df = tts_by_efs_df.loc[condition]

        return filtered_df

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
    def create_tts_by_month_tpl(self, tt_df : DataFrame, years : list, now : datetime) -> Tuple[DataFrame, DataFrame]:

        '''
                Month	2016	↕   2017	    ↕	2018    ...
            0	1	    0h 00m	↑	13h 00m		↓	0h 00m
            1	2	    0h 00m	↑	1h 00m	    ↓	0h 00m
            ...

            Returns: (tts_by_month_df, tts_by_month_upd_df).
        '''

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
            tts_df[str(year)] = tts_df[str(year)].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))

        tts_df.rename(columns = (lambda x : self.__df_helper.try_consolidate_trend_column_name(column_name = x)), inplace = True)
        tts_upd_df : DataFrame = self.__update_future_months_to_empty(tts_by_month_df = tts_df, now = now)

        return (tts_df, tts_upd_df)
    def create_tts_by_year_df(self, tt_df : DataFrame, years : list[int], yearly_targets : list[YearlyTarget]) -> DataFrame:

        '''
            [0]
                    Date	    StartTime	EndTime	Effort	    Hashtag	    Descriptor IsSoftwareProject    IsReleaseDay	Year	Month
                0	2015-10-31	nan	        nan	    8h 00m	    #untagged	nan	       nan	                nan	            2015	10
                1	2015-11-30	nan	        nan	    10h 00m	    #untagged	nan	       nan	                nan	            2015	11            
                ...

            [1]
                    Year	Effort
                0	2016	25 days 15:15:00

            [2] 
                    Year	Effort	            YearlyTarget        TargetDiff	    IsTargetMet	
                0	2015	0 days 18:00:00	    0 days 00:00:00	    0 days 18:00:00 True
                1	2016	25 days 15:15:00	20 days 20:00:00	4 days 19:15:00 True
                ...

            [3]
                    Year	Effort	    YearlyTarget	TargetDiff	IsTargetMet
                0	2015	18h 00m	    00h 00m	        +18h 00m	True
                1	2016	615h 15m	500h 00m	    +115h 15m	True
                ...
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition : Series = (tt_df[TTCN.YEAR].isin(values = years))
        tts_df = tts_df.loc[condition]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby([TTCN.YEAR])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = TTCN.YEAR).reset_index(drop = True)

        tts_df[TTCN.YEARLYTARGET] = tts_df[TTCN.YEAR].apply(
            lambda x : cast(YearlyTarget, self.__df_helper.get_yearly_target(yearly_targets = yearly_targets, year = x)).hours)
        tts_df[TTCN.TARGETDIFF] = tts_df[TTCN.EFFORT] - tts_df[TTCN.YEARLYTARGET]
        tts_df[TTCN.ISTARGETMET] = tts_df.apply(
            lambda x : self.__df_helper.is_yearly_target_met(effort = x[TTCN.EFFORT], yearly_target = x[TTCN.YEARLYTARGET]), axis = 1)    

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))
        tts_df[TTCN.YEARLYTARGET] = tts_df[TTCN.YEARLYTARGET].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))
        tts_df[TTCN.TARGETDIFF] = tts_df[TTCN.TARGETDIFF].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = True))

        return tts_df
    def create_tts_by_year_month_tpl(self, tt_df : DataFrame, years : list[int], yearly_targets : list[YearlyTarget], display_only_years : list[int]) -> Tuple[DataFrame, DataFrame]:

        '''
            [0]

                        Year	Month	Effort
                0	    2015	11	    0 days 10:00:00
                1	    2015	10	    0 days 08:00:00
                ...

            [1]

                        Year	Month	Effort	        YearlyTotal
                0	    2015	10	    0 days 08:00:00	0 days 08:00:00
                1	    2015	11	    0 days 10:00:00	0 days 18:00:00
                ...

            [2] 

                    Year	Month	Effort	        YearlyTotal	    YearlyTarget
                0	2015	10	    0 days 08:00:00	0 days 08:00:00	0 days 00:00:00
                1	2015	11	    0 days 10:00:00	0 days 18:00:00	0 days 00:00:00
                ...
            
            [3]

                    Year	Month	Effort	        YearlyTotal	    YearlyTarget	ToTarget
                0	2015	10	    0 days 08:00:00	0 days 08:00:00	0 days 00:00:00	0 days 08:00:00
                1	2015	11	    0 days 10:00:00	0 days 18:00:00	0 days 00:00:00	0 days 10:00:00        
                ...

            [4] 
                    Year	Month	Effort	    YearlyTotal	ToTarget
                ...
                87	2023	1	    06h 00m	    06h 00m	    -394h 00m
                88	2023	2	    23h 00m	    29h 00m	    -371h 00m
                89	2023	3	    50h 15m	    79h 15m	    -321h 15m   
                ...

            Returns (tts_by_year_month_df, tts_by_year_month_flt_df).
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)

        condition : Series = (tt_df[TTCN.YEAR].isin(values = years))
        tts_df = tts_df.loc[condition]

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.convert_string_to_timedelta(td_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.MONTH])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR, TTCN.MONTH]).reset_index(drop = True)

        tts_df[TTCN.YEARLYTOTAL] = tts_df[TTCN.EFFORT].groupby(by = tts_df[TTCN.YEAR]).cumsum()

        tts_df[TTCN.YEARLYTARGET] = tts_df[TTCN.YEAR].apply(
            lambda x : cast(YearlyTarget, self.__df_helper.get_yearly_target(yearly_targets = yearly_targets, year = x)).hours)

        tts_df[TTCN.TOTARGET] = tts_df[TTCN.YEARLYTOTAL] - tts_df[TTCN.YEARLYTARGET]    
        tts_df.drop(columns = [TTCN.YEARLYTARGET], axis = 1, inplace = True)
        
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))   
        tts_df[TTCN.YEARLYTOTAL] = tts_df[TTCN.YEARLYTOTAL].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))
        tts_df[TTCN.TOTARGET] = tts_df[TTCN.TOTARGET].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = True))

        tts_flt_df : DataFrame = self.__filter_by_year(df = tts_df, years = display_only_years)

        return (tts_df, tts_flt_df)
    def create_tts_by_year_month_spnv_tpl(self, tt_df : DataFrame, years : list[int], software_project_names : list[str], software_project_name : Optional[str]) -> Tuple[DataFrame, DataFrame]:

        '''
            [0] ...
            [1]

                    Year	Month	ProjectName     	    ProjectVersion	Effort	DME	    %_DME	TME	    %_TME
                0	2023	4	    nwtraderaanalytics	    2.0.0	        09h 15m	09h 15m	100.00	19h 00m	48.68
                1	2023	6	    nwreadinglistmanager	1.0.0	        06h 45m	06h 45m	100.00	24h 45m	27.27
                ...

            Returns (tts_by_year_month_spnv_df, tts_by_year_month_spnv_flt_df).
        '''

        spnv_df : DataFrame = self.__create_raw_tts_by_year_month_spnv(tt_df = tt_df, years = years, software_project_names = software_project_names)
        dme_df : DataFrame = self.__create_raw_tts_by_dme(tt_df = tt_df, years = years)
        tme_df : DataFrame = self.__create_raw_tts_by_tme(tt_df = tt_df, years = years)

        tts_df : DataFrame = pd.merge(
            left = spnv_df, 
            right = dme_df, 
            how = "inner", 
            left_on = [TTCN.YEAR, TTCN.MONTH], 
            right_on = [TTCN.YEAR, TTCN.MONTH]
            )
        
        tts_df[TTCN.PERCDME] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = x[TTCN.DME]), axis = 1)        

        tts_df = pd.merge(
            left = tts_df, 
            right = tme_df, 
            how = "inner", 
            left_on = [TTCN.YEAR, TTCN.MONTH], 
            right_on = [TTCN.YEAR, TTCN.MONTH]
            )   
    
        tts_df[TTCN.PERCTME] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = x[TTCN.TME]), axis = 1)    
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))   
        tts_df[TTCN.DME] = tts_df[TTCN.DME].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))
        tts_df[TTCN.TME] = tts_df[TTCN.TME].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))

        tts_flt_df : DataFrame = self.__filter_by_software_project_name(df = tts_df, software_project_name = software_project_name)

        return (tts_df, tts_flt_df)
    def create_tts_by_year_spnv_tpl(self, tt_df : DataFrame, years : list[int], software_project_names : list[str], software_project_name : Optional[str]) -> Tuple[DataFrame, DataFrame]:

        '''
            [0] ...
            [1]

                    Year	ProjectName     	    ProjectVersion	Effort	DYE	    %_DYE	TYE	    %_TYE
                0	2023	nwtraderaanalytics	    2.0.0	        09h 15m	09h 15m	100.00	19h 00m	48.68
                1	2023	nwreadinglistmanager	1.0.0	        06h 45m	06h 45m	100.00	24h 45m	27.27
                ...

            Returns (tts_by_year_spnv_df, tts_by_year_spnv_flt_df).
        '''

        spnv_df : DataFrame = self.__create_raw_tts_by_year_spnv(tt_df = tt_df, years = years, software_project_names = software_project_names)
        dye_df : DataFrame = self.__create_raw_tts_by_dye(tt_df = tt_df, years = years)
        tye_df : DataFrame = self.__create_raw_tts_by_tye(tt_df = tt_df, years = years)

        tts_df : DataFrame = pd.merge(
            left = spnv_df, 
            right = dye_df, 
            how = "inner", 
            left_on = [TTCN.YEAR], 
            right_on = [TTCN.YEAR]
            )
        
        tts_df[TTCN.PERCDYE] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = x[TTCN.DYE]), axis = 1)        

        tts_df = pd.merge(
            left = tts_df, 
            right = tye_df, 
            how = "inner", 
            left_on = [TTCN.YEAR], 
            right_on = [TTCN.YEAR]
            )   
    
        tts_df[TTCN.PERCTYE] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = x[TTCN.TYE]), axis = 1)    
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))   
        tts_df[TTCN.DYE] = tts_df[TTCN.DYE].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))
        tts_df[TTCN.TYE] = tts_df[TTCN.TYE].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))

        tts_flt_df : DataFrame = self.__filter_by_software_project_name(df = tts_df, software_project_name = software_project_name)

        return (tts_df, tts_flt_df)
    def create_tts_by_spn_df(self, tt_df : DataFrame, years : list[int], software_project_names : list[str], remove_untagged : bool) -> DataFrame:

        '''
                Hashtag     ProjectName	            Effort	    DE	%_DE	TE	        %_TE
            0	#python     nwreadinglistmanager	66h 30m	93h 15m	71.31	4475h 15m	1.49
            1	#python     nwtraderaanalytics	    09h 15m	93h 15m	9.92	4475h 15m	0.21
            ...

            With remove_untagged = True:

                Hashtag     ProjectName	            Effort	DE	    %_DE	TE	        %_TE
            0	#python     nwreadinglistmanager	66h 30m	93h 15m	71.31	174h 15m	38.16
            1	#python     nwtraderaanalytics	    09h 15m	93h 15m	9.92	174h 15m	5.31
            ...
        '''

        tts_df : DataFrame = self.__create_raw_tts_by_spn(tt_df = tt_df, years = years, software_project_names = software_project_names)
        de : timedelta = self.__create_raw_de(tt_df = tt_df, years = years)
        te : timedelta = self.__create_raw_te(tt_df = tt_df, years = years, remove_untagged = remove_untagged)    

        tts_df[TTCN.DE] = de
        tts_df[TTCN.PERCDE] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = x[TTCN.DE]), axis = 1)      

        tts_df[TTCN.TE] = te
        tts_df[TTCN.PERCTE] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = x[TTCN.TE]), axis = 1)     

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))   
        tts_df[TTCN.DE] = tts_df[TTCN.DE].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))
        tts_df[TTCN.TE] = tts_df[TTCN.TE].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))

        return tts_df
    def create_tts_by_spn_spv_df(self, tt_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

        '''
                ProjectName	                ProjectVersion	Effort
            0	NW.MarkdownTables	        1.0.0	        15h 15m
            1	NW.MarkdownTables	        1.0.1	        02h 30m
            2	NW.NGramTextClassification	1.0.0	        74h 15m
            ...    
        '''

        tts_df : DataFrame = self.__create_raw_tts_by_spn_spv(tt_df = tt_df, years = years, software_project_names = software_project_names)
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))   

        return tts_df
    def create_tts_by_hashtag_year_df(self, tt_df : DataFrame, years : list[int]) -> DataFrame:

        '''
                Year	Hashtag	        Effort
            0   2023	#csharp	        67h 30m
            1   2023	#maintenance	51h 00m
            2   2023	#powershell	    04h 30m 
            ...    
        '''
    
        tts_df : DataFrame = self.__create_raw_tts_by_year_hashtag(tt_df = tt_df, years = years)
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))   

        return tts_df
    def create_tts_by_hashtag_df(self, tt_df : DataFrame) -> DataFrame:

        '''
                Hashtag	        Effort  Effort%
            0   #csharp	        67h 30m 56.49
            1   #maintenance	51h 00m 23.97
            2   #powershell	    04h 30m 6.43
            ...    
        '''
    
        tts_df : DataFrame = self.__create_raw_tts_by_hashtag(tt_df = tt_df)
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.format_timedelta(td = x, add_plus_sign = False))   

        return tts_df
    def create_tts_by_efs_tpl(self, tt_df : DataFrame, is_correct : bool) -> Tuple[DataFrame, DataFrame]:

        '''
            StartTime	EndTime	Effort	ES_IsCorrect	ES_Expected	ES_Message
            21:00       23:00   1h 00m  False           2h 00m      ...
            ...

            Returns (tts_by_efs_df, tts_by_efs_flt_df).
        '''

        tts_df : DataFrame = tt_df.copy(deep = True)
        
        tts_df[TTCN.EFFORTSTATUS] = tts_df.apply(
            lambda x : self.__df_helper.create_effort_status_and_cast_to_any(
                    idx = x.name, 
                    start_time_str = x[TTCN.STARTTIME],
                    end_time_str = x[TTCN.ENDTIME],
                    effort_str = x[TTCN.EFFORT]),
            axis = 1)
        
        tts_df[TTCN.ESISCORRECT] = tts_df[TTCN.EFFORTSTATUS].apply(lambda x : x.is_correct)
        tts_df[TTCN.ESEXPECTED] = tts_df[TTCN.EFFORTSTATUS].apply(lambda x : x.expected_str)
        tts_df[TTCN.ESMESSAGE] = tts_df[TTCN.EFFORTSTATUS].apply(lambda x : x.message)
        tts_df = tts_df[[TTCN.STARTTIME, TTCN.ENDTIME, TTCN.EFFORT, TTCN.ESISCORRECT, TTCN.ESEXPECTED, TTCN.ESMESSAGE]]

        tts_flt_df : DataFrame = self.__filter_by_is_correct(tts_by_efs_df = tts_df, is_correct = is_correct)

        return (tts_df, tts_flt_df)
    def create_tts_by_tr_df(self, tt_df : DataFrame, unknown_id : str, remove_unknown_occurrences : bool) -> DataFrame:

            '''
                    TimeRangeId	Occurrences
                0	Unknown		44
                1	18:00-20:00	19
                2	08:00-08:30	16
                ...
            '''

            tts_df : DataFrame = tt_df.copy(deep = True)
            tts_df = tts_df[[TTCN.STARTTIME, TTCN.ENDTIME]]

            tts_df[TTCN.TIMERANGEID] = tts_df.apply(
                lambda x : self.__df_helper.create_time_range_id(
                    start_time = x[TTCN.STARTTIME], 
                    end_time = x[TTCN.ENDTIME], 
                    unknown_id = unknown_id), axis = 1)

            count : NamedAgg = pd.NamedAgg(column = TTCN.TIMERANGEID, aggfunc = "count")
            tts_df = tts_df[[TTCN.TIMERANGEID]].groupby(by = [TTCN.TIMERANGEID], as_index=False).agg(count = count)
            tts_df.rename(columns={"count" : TTCN.OCCURRENCES}, inplace = True)

            ascending : bool = False
            tts_df = tts_df.sort_values(by = [TTCN.OCCURRENCES], ascending = ascending).reset_index(drop = True)

            if remove_unknown_occurrences:
                tts_df = self.__remove_unknown_occurrences(tts_by_tr_df = tts_df, unknown_id = unknown_id)

            return tts_df
    def create_definitions_df(self) -> DataFrame:

        '''Creates a dataframe containing all the definitions in use in this application.'''

        columns : list[str] = [DEFINITIONSCN.TERM, DEFINITIONSCN.DEFINITION]

        definitions : dict[str, str] = { 
            "DME": "Development Monthly Effort",
            "TME": "Total Monthly Effort",
            "DYE": "Development Yearly Effort",
            "TYE": "Total Yearly Effort",
            "DE": "Development Effort",
            "TE": "Total Effort"
        }
        
        definitions_df : DataFrame = DataFrame(
            data = definitions.items(), 
            columns = columns
        )

        return definitions_df
class BYMDFManager():
    
    '''Encapsulates additional logic related to *_by_month_df dataframes.'''

    __provided_df_invalid_column_list : Callable[[list[str]], str] = lambda column_list : f"The provided df has an invalid column list ('{column_list}')."

    def __is_year(self, value : Any) -> bool:

        """Returns True if value is a valid year."""

        try:       
            year : int = int(value)
            return 1000 <= year <= 9999
        except:
            return False
    def __is_even(self, number : int) -> bool:
        
        """Returns True if number is even."""

        return number % 2 == 0
    def __is_valid(self, column_list : list[str]) -> bool:
        
        """
            Validates the column names of a certain DataFrame according to the specified pattern.
            
            Valid::

                ["Month", "2015"]
                ["Month", "2015", "↕", "2016"]
                ["Month", "2015", "↕", "2016", "↕", "2017"]
                ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018"]
                ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019"]
                ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020"]
                ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020", "↕", "2021"]
                ...

            Invalid::

                []
                ["Month"]
                ["Month", "2015", "↕"]
                ["Month", "2015", "↕", "2016", "↕"]
                ["Month", "2015", "↕", "2016", "↕", "2017", "↕"]
                ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕"]
                ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕"]
                ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", "↕", "2020", "↕"]
                ["Month", "↕"]
                ["Month", "↕", "↕"]
                ["Month", "2015", "2015"]
                ["Month", "2015", "↕", "↕"]
                ...
        """

        if len(column_list) < 2 or column_list[0] != "Month":
            return False

        for i in range(1, len(column_list)):
            if i % 2 == 1:
                if not self.__is_year(column_list[i]):
                    return False
            else:
                if column_list[i] != '↕':
                    return False

        return self.__is_even(number = len(column_list))
    def __is_in_sequence(self, number : int) -> bool:
        
        """
            Determines if a given number is part of the sequence defined by n = (number + 5) / 6.

            Sequence: [1, 7, 13, 19, 25, 31, 37, 43, 49, 55, 61, 67, 73, 79, 85, 91, 97, 103, 109, 115, ...].
        """

        n = (number + 5) / 6

        return n.is_integer() and n > 0
    def __is_last(self, number : int, lst: list[int]) -> bool:
        
        """Determines if the given value is the last element in the provided list."""

        if not lst:
            return False

        return lst[-1] == number
    def __create_column_numbers(self, df : DataFrame) -> list[int]:
        
        """Returns a list of column numbers for df."""

        return list(range(len(df.columns)))
    def __create_index_lists(self, column_numbers : list[int]) -> list[list[int]]:
        
        """
            Creates index_lists specific for *_by_month_df dataframes.

            Steps::

                Step 1 -> column_numbers: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
                Step 2 -> tmp: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
                Step 3 -> initials: [1, 7, 13]
                Step 4 -> index_lists: [ [0, 1], [0, 7], [0, 13] ]
                Step 5 -> tmp: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
                Step 6 -> index_lists: [ [0, 1, 2, 3, 4, 5, 6, 7], [0, 7, 8, 9, 10, 11, 12, 13], [0, 13, 14, 15, 16, 17, 18, 19] ]
        """

        tmp : list[int] = list(column_numbers)
        tmp.remove(0)

        initials : list[int] = []
        for idx in range(0, len(column_numbers)):
            if self.__is_in_sequence(number = idx) and not self.__is_last(number = idx, lst = tmp):
                initials.append(idx)

        index_lists : list[list[int]] = []
        for idx in initials:
            index_list : list[int] = [0, idx]
            index_lists.append(index_list)

        for index_list in index_lists:
            start_value = index_list[1]
            start_index = tmp.index(start_value)
            index_list.extend(tmp[(start_index + 1):(start_index + 7)])

        if self.__is_even(index_lists[-1][-1]):
            index_lists[-1].remove(index_lists[-1][-1])

        return index_lists
    def __filter_by_index_list(self, df : DataFrame, index_list : list[int]) -> DataFrame:

        """Filters df to include only columns specified by index_list."""

        filtered_df : DataFrame = df.iloc[:, index_list]
        
        return filtered_df
    def __filter_by_index_lists(self, df : DataFrame, index_lists : list[list[int]]) -> list[DataFrame]:

        """Filters df to include only columns specified by index_lists."""

        sub_dfs : list[DataFrame] = []

        for index_list in index_lists:
            sub_df : DataFrame = self.__filter_by_index_list(df = df, index_list = index_list)
            sub_dfs.append(sub_df)

        return sub_dfs

    def create_sub_dfs(self, df : DataFrame) -> list[DataFrame]:

        """
            Splits df in sub_dfs.

            Examples::

                df = ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018", "↕", "2019", ...]
                sub_dfs = [
                    ["Month", "2015", "↕", "2016", "↕", "2017", "↕", "2018"],
                    ["Month", "2018", "↕", "2019", "↕", "2020", "↕", "2021"],
                    ["Month", "2021", "↕", "2022", "↕", "2023", "↕", "2024"]
                ]
        """

        column_list : list[str] = df.columns.to_list()

        if not self.__is_valid(column_list = column_list):
            raise Exception(self.__provided_df_invalid_column_list(column_list))
        
        if len(column_list) == 2:
            return [df]

        column_numbers : list[int] = self.__create_column_numbers(df = df)
        index_lists : list[list[int]] = self.__create_index_lists(column_numbers = column_numbers)
        sub_dfs : list[DataFrame] = self.__filter_by_index_lists(df = df, index_lists = index_lists)

        return sub_dfs
class TTMarkdownFactory():

    '''Collects all the logic related to Markdown creation out of Time Tracking dataframes.'''

    __markdown_helper : MarkdownHelper
    __bymdf_manager : BYMDFManager

    def __init__(self, markdown_helper : MarkdownHelper, bymdf_manager : BYMDFManager) -> None:

        self.__markdown_helper = markdown_helper
        self.__bymdf_manager = bymdf_manager

    def __convert_sub_dfs(self, smaller_dfs : list[DataFrame]) -> str:

        smaller_mds : list[str] = []

        for smaller_df in smaller_dfs:
            smaller_md : str = smaller_df.to_markdown(index = False)
            smaller_mds.append(smaller_md)

        return "\n\n".join(smaller_mds)
    def create_tts_by_month_md(self, paragraph_title : str, last_update : datetime, tts_by_month_upd_df : DataFrame) -> str:

        '''Creates the expected Markdown content for the provided arguments.'''

        markdown_header : str = self.__markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = paragraph_title)
        # tts_by_month_upd_md : str = tts_by_month_upd_df.to_markdown(index = False)

        sub_dfs : list[DataFrame] = self.__bymdf_manager.create_sub_dfs(df = tts_by_month_upd_df)
        tts_by_month_upd_md = self.__convert_sub_dfs(smaller_dfs = sub_dfs) 

        md_content : str = markdown_header
        md_content += "\n"
        md_content += tts_by_month_upd_md
        md_content += "\n"

        return md_content
class TTAdapter():

    '''Adapts SettingBag properties for use in TT*Factory methods.'''

    __df_factory : TTDataFrameFactory
    __md_factory : TTMarkdownFactory

    def __init__(self, df_factory : TTDataFrameFactory, md_factory : TTMarkdownFactory) -> None:
        
        self.__df_factory = df_factory
        self.__md_factory = md_factory

    def extract_file_name_and_paragraph_title(self, id : TTID, setting_bag : SettingBag) -> Tuple[str, str]: 
    
        '''Returns (file_name, paragraph_title) for the provided id or raise an Exception.'''

        for md_info in setting_bag.md_infos:
            if md_info.id == id: 
                return (md_info.file_name, md_info.paragraph_title)

        raise Exception(_MessageCollection.no_mdinfo_found(id = id))
    
    def create_tt_df(self, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tt_df : DataFrame = self.__df_factory.create_tt_df(
            excel_path = setting_bag.excel_path,
            excel_skiprows = setting_bag.excel_skiprows,
            excel_nrows = setting_bag.excel_nrows,
            excel_tabname = setting_bag.excel_tabname
            )

        return tt_df
    def create_tts_by_month_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_month_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_tts_by_month_tpl(
            tt_df = tt_df,
            years = setting_bag.years,
            now = setting_bag.now
        )

        return tts_by_month_tpl
    def create_tts_by_year_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_year_df : DataFrame = self.__df_factory.create_tts_by_year_df(
            tt_df = tt_df,
            years = setting_bag.years,
            yearly_targets = setting_bag.yearly_targets,
        )

        return tts_by_year_df
    def create_tts_by_year_month_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        display_only_years : list[int] = []
        
        if display_only_years is not None:
            display_only_years = cast(list[int], setting_bag.tts_by_year_month_display_only_years)

        tts_by_year_month_df : Tuple[DataFrame, DataFrame] = self.__df_factory.create_tts_by_year_month_tpl(
            tt_df = tt_df,
            years = setting_bag.years,
            yearly_targets = setting_bag.yearly_targets,
            display_only_years = display_only_years
        )

        return tts_by_year_month_df
    def create_tts_by_year_month_spnv_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_year_month_spnv_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_tts_by_year_month_spnv_tpl(
            tt_df = tt_df,
            years = setting_bag.years,
            software_project_names = setting_bag.software_project_names,
            software_project_name = setting_bag.tts_by_year_month_spnv_display_only_spn
        )

        return tts_by_year_month_spnv_tpl
    def create_tts_by_year_spnv_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_year_spnv_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_tts_by_year_spnv_tpl(
            tt_df = tt_df,
            years = setting_bag.years,
            software_project_names = setting_bag.software_project_names,
            software_project_name = setting_bag.tts_by_year_spnv_display_only_spn
        )

        return tts_by_year_spnv_tpl
    def create_tts_by_spn_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_spn_df : DataFrame = self.__df_factory.create_tts_by_spn_df(
            tt_df = tt_df,
            years = setting_bag.years,
            software_project_names = setting_bag.software_project_names,
            remove_untagged = setting_bag.tts_by_spn_remove_untagged
        )

        return tts_by_spn_df
    def create_tts_by_spn_spv_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_spn_spv_df : DataFrame = self.__df_factory.create_tts_by_spn_spv_df(
            tt_df = tt_df,
            years = setting_bag.years,
            software_project_names = setting_bag.software_project_names
        )

        return tts_by_spn_spv_df
    def create_tts_by_hashtag_year_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_year_hashtag_df : DataFrame = self.__df_factory.create_tts_by_hashtag_year_df(
            tt_df = tt_df,
            years = setting_bag.years
        )

        return tts_by_year_hashtag_df
    def create_tts_by_efs_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_efs_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_tts_by_efs_tpl(
            tt_df = tt_df,
            is_correct = setting_bag.tts_by_efs_is_correct
        )

        return tts_by_efs_tpl
    def create_tts_by_tr_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_tr_df : DataFrame = self.__df_factory.create_tts_by_tr_df(
            tt_df = tt_df,
            unknown_id = setting_bag.tts_by_tr_unknown_id,
            remove_unknown_occurrences = setting_bag.tts_by_tr_remove_unknown_occurrences
        )

        return tts_by_tr_df
    def create_tts_by_month_md(self, tts_by_month_tpl : Tuple[DataFrame, DataFrame], setting_bag : SettingBag) -> str:

        '''Creates the expected Markdown content out of the provided arguments.'''

        tts_by_month_md : str = self.__md_factory.create_tts_by_month_md(
            paragraph_title = self.extract_file_name_and_paragraph_title(id = TTID.TTSBYMONTH, setting_bag = setting_bag)[1],
            last_update = setting_bag.md_last_update,
            tts_by_month_upd_df = tts_by_month_tpl[1]
        )

        return tts_by_month_md
    def create_summary(self, setting_bag : SettingBag) -> TTSummary:

        '''Creates a TTSummary object out of setting_bag.'''

        tt_df : DataFrame = self.create_tt_df(setting_bag = setting_bag)
        tts_by_month_tpl : Tuple[DataFrame, DataFrame] = self.create_tts_by_month_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_df : DataFrame = self.create_tts_by_year_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_month_tpl : Tuple[DataFrame, DataFrame] = self.create_tts_by_year_month_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_month_spnv_tpl : Tuple[DataFrame, DataFrame] = self.create_tts_by_year_month_spnv_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_spnv_tpl : Tuple[DataFrame, DataFrame] = self.create_tts_by_year_spnv_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_spn_df : DataFrame = self.create_tts_by_spn_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_spn_spv_df : DataFrame = self.create_tts_by_spn_spv_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_hashtag_df : DataFrame = self.create_tts_by_hashtag_year_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_hashtag_df : DataFrame = self.__df_factory.create_tts_by_hashtag_df(tt_df = tt_df)
        tts_by_efs_tpl : Tuple[DataFrame, DataFrame] = self.create_tts_by_efs_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_tr_df : DataFrame = self.create_tts_by_tr_df(tt_df = tt_df, setting_bag = setting_bag)
        definitions_df : DataFrame = self.__df_factory.create_definitions_df()
        tts_by_month_md : str = self.create_tts_by_month_md(tts_by_month_tpl = tts_by_month_tpl, setting_bag = setting_bag)

        tt_summary : TTSummary = TTSummary(
            tt_df = tt_df,
            tts_by_month_tpl = tts_by_month_tpl,
            tts_by_year_df = tts_by_year_df,
            tts_by_year_month_tpl = tts_by_year_month_tpl,
            tts_by_year_month_spnv_tpl = tts_by_year_month_spnv_tpl,
            tts_by_year_spnv_tpl = tts_by_year_spnv_tpl,
            tts_by_spn_df = tts_by_spn_df,
            tts_by_spn_spv_df = tts_by_spn_spv_df,
            tts_by_hashtag_year_df = tts_by_year_hashtag_df,
            tts_by_hashtag_df = tts_by_hashtag_df,
            tts_by_efs_tpl = tts_by_efs_tpl,
            tts_by_tr_df = tts_by_tr_df,
            definitions_df = definitions_df,
            tts_by_month_md = tts_by_month_md
        )

        return tt_summary
@dataclass(frozen=True)
class ComponentBag():

    '''Represents a collection of components.'''

    file_path_manager : FilePathManager = field(default = FilePathManager())
    file_manager : FileManager = field(default = FileManager(file_path_manager = FilePathManager()))

    tt_adapter : TTAdapter = field(default = TTAdapter(
        df_factory = TTDataFrameFactory(df_helper = TTDataFrameHelper()), 
        md_factory = TTMarkdownFactory(
            markdown_helper = MarkdownHelper(formatter = Formatter()),
            bymdf_manager = BYMDFManager())
        ))

    logging_function : Callable[[str], None] = field(default = LambdaProvider().get_default_logging_function())
    displayer : Displayer = field(default = Displayer())
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
    def __save_and_log(self, id : TTID, content : str) -> None:

        '''Creates the provided Markdown content using __setting_bag.'''

        file_path : str = self.__component_bag.file_path_manager.create_file_path(
            folder_path = self.__setting_bag.working_folder_path,
            file_name = self.__component_bag.tt_adapter.extract_file_name_and_paragraph_title(id = id, setting_bag = self.__setting_bag)[0]
        )
        
        self.__component_bag.file_manager.save_content(content = content, file_path = file_path)

        message : str = _MessageCollection.this_content_successfully_saved_as(id = id, file_path = file_path)
        self.__component_bag.logging_function(message)
    def __try_log_definitions(self, df : DataFrame, definitions : DataFrame) -> None:
        
        """Logs the definitions for matching column names in the DataFrame."""

        definitions_dict : dict = definitions.set_index(DEFINITIONSCN.TERM)[DEFINITIONSCN.DEFINITION].to_dict()
        
        for column_name in df.columns:
            if column_name in definitions_dict:
                print(f"{column_name}: {definitions_dict[column_name]}")

    def __orchestrate_head_n(self, df : DataFrame, head_n : Optional[uint], display_head_n_with_tail : bool) -> DataFrame:

        '''Prepares df for display().'''

        if head_n is None:
            return df
        elif head_n is not None and display_head_n_with_tail == True:
            return df.tail(n = int(head_n))
        else:
            return df.head(n = int(head_n))
    def __optimize_tt_for_display(self, tt_df : DataFrame) -> DataFrame:

        return self.__orchestrate_head_n(
            df = tt_df, 
            head_n = self.__setting_bag.tt_head_n, 
            display_head_n_with_tail = self.__setting_bag.tt_display_head_n_with_tail
        )
    def __optimize_tts_by_year_month_for_display(self, tts_by_year_month_tpl : Tuple[DataFrame, DataFrame]) -> DataFrame:

        '''
            tts_by_year_month_tpl is made of (tts_by_year_month_df, tts_by_year_month_flt_df).

            This method decides which one of the two DataFrame is to be displayed according to __setting_bag.tts_by_year_month_display_only_years.
        '''

        if self.__setting_bag.tts_by_year_month_display_only_years is None:
            return tts_by_year_month_tpl[0]

        return tts_by_year_month_tpl[1]
    def __optimize_tts_by_year_month_spnv_for_display(self, tts_by_year_month_spnv_tpl : Tuple[DataFrame, DataFrame]) -> DataFrame:

        '''
            tts_by_year_month_spnv_tpl is made of (tts_by_year_month_spnv_df, tts_by_year_month_spnv_flt_df).

            This method decides which one of the two DataFrame is to be displayed according to __setting_bag.tts_by_year_month_spnv_display_only_spn.
        '''

        if self.__setting_bag.tts_by_year_month_spnv_display_only_spn is None:
            return tts_by_year_month_spnv_tpl[0]

        return tts_by_year_month_spnv_tpl[1]
    def __optimize_tts_by_year_spnv_for_display(self, tts_by_year_spnv_tpl : Tuple[DataFrame, DataFrame]) -> DataFrame:

        '''
            tts_by_year_spnv_tpl is made of (tts_by_year_spnv_df, tts_by_year_spnv_flt_df).

            This method decides which one of the two DataFrame is to be displayed according to __setting_bag.tts_by_year_spnv_display_only_spn.
        '''

        if self.__setting_bag.tts_by_year_spnv_display_only_spn is None:
            return tts_by_year_spnv_tpl[0]

        return tts_by_year_spnv_tpl[1]
    def __optimize_tts_by_tr_for_display(self, tts_by_tr_df : DataFrame) -> DataFrame:

        return self.__orchestrate_head_n(
            df = tts_by_tr_df, 
            head_n = self.__setting_bag.tts_by_tr_head_n, 
            display_head_n_with_tail = self.__setting_bag.tts_by_tr_display_head_n_with_tail
        )

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
        df : DataFrame = self.__optimize_tt_for_display(tt_df = self.__tt_summary.tt_df)
        hide_index : bool = self.__setting_bag.tt_hide_index

        if "display" in options:
            self.__component_bag.displayer.display(df = df, hide_index = hide_index)
    def process_tts_by_month(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_month.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_month
        df : DataFrame = self.__tt_summary.tts_by_month_tpl[1]
        content : str = self.__tt_summary.tts_by_month_md
        id : TTID = TTID.TTSBYMONTH

        if "display" in options:
            self.__component_bag.displayer.display(df = df)

        if "save" in options:
            self.__save_and_log(id = id, content = content)
    def process_tts_by_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year
        df : DataFrame = self.__tt_summary.tts_by_year_df

        if "display" in options:
            self.__component_bag.displayer.display(df = df)
    def process_tts_by_year_month(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year_month.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year_month
        df : DataFrame = self.__optimize_tts_by_year_month_for_display(tts_by_year_month_tpl = self.__tt_summary.tts_by_year_month_tpl)

        if "display" in options:
            self.__component_bag.displayer.display(df = df)
    def process_tts_by_year_month_spnv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year_month_spnv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year_month_spnv
        df : DataFrame = self.__optimize_tts_by_year_month_spnv_for_display(tts_by_year_month_spnv_tpl = self.__tt_summary.tts_by_year_month_spnv_tpl)
        formatters : dict = self.__setting_bag.tts_by_year_month_spnv_formatters

        if "display" in options:
            self.__component_bag.displayer.display(df = df, formatters = formatters)
    def process_tts_by_year_spnv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year_spnv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year_spnv
        df : DataFrame = self.__optimize_tts_by_year_spnv_for_display(tts_by_year_spnv_tpl = self.__tt_summary.tts_by_year_spnv_tpl)
        formatters : dict = self.__setting_bag.tts_by_year_spnv_formatters

        if "display" in options:
            self.__component_bag.displayer.display(df = df, formatters = formatters)
    def process_tts_by_spn(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_spn.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_spn
        df : DataFrame = self.__tt_summary.tts_by_spn_df
        formatters : dict = self.__setting_bag.tts_by_spn_formatters
        definitions_df : DataFrame = self.__tt_summary.definitions_df

        if "display" in options:
            self.__component_bag.displayer.display(df = df, formatters = formatters)

        if "log" in options:
            self.__try_log_definitions(df = df, definitions = definitions_df)
    def process_tts_by_spn_spv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_spn_spv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_spn_spv
        df : DataFrame = self.__tt_summary.tts_by_spn_spv_df
        definitions_df : DataFrame = self.__tt_summary.definitions_df        

        if "display" in options:
            self.__component_bag.displayer.display(df = df)

        if "log" in options:
            self.__try_log_definitions(df = df, definitions = definitions_df)
    def process_tts_by_hashtag(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_hashtag.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_hashtag
        df : DataFrame = self.__tt_summary.tts_by_hashtag_df
        formatters : dict = self.__setting_bag.tts_by_hashtag_formatters    

        if "display" in options:
            self.__component_bag.displayer.display(df = df, formatters = formatters)
    def process_tts_by_hashtag_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_hashtag_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_hashtag_year
        df : DataFrame = self.__tt_summary.tts_by_hashtag_year_df

        if "display" in options:
            self.__component_bag.displayer.display(df = df)
    def process_tts_by_efs(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_efs.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_efs
        df : DataFrame = self.__tt_summary.tts_by_efs_tpl[1]

        if "display" in options:
            self.__component_bag.displayer.display(df = df)
    def process_tts_by_tr(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_tr.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_tr
        df : DataFrame = self.__optimize_tts_by_tr_for_display(tts_by_tr_df = self.__tt_summary.tts_by_tr_df)

        if "display" in options:
            self.__component_bag.displayer.display(df = df)
    def process_definitions(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_definitions.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_definitions
        df : DataFrame = self.__tt_summary.definitions_df

        if "display" in options:
            self.__component_bag.displayer.display(df = df)

# MAIN
if __name__ == "__main__":
    pass