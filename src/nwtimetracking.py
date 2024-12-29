'''
A collection of components to handle "Time Tracking.xlsx".

Alias: nwtt
'''

# GLOBAL MODULES
import json
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import re
from dataclasses import dataclass, field, fields
from datetime import date, datetime, timedelta
from enum import StrEnum, auto
from matplotlib.dates import relativedelta
from numpy import uint
from numpy.typing import ArrayLike
from pandas import DataFrame, Series, NamedAgg
from pandas import Index
from pandas.io.formats.style import Styler
from re import Match
from types import SimpleNamespace
from typing import Any, Callable, Literal, Optional, Tuple, Union, cast
from nwshared import Formatter, FilePathManager, FileManager, LambdaProvider, MarkdownHelper, Displayer

# LOCAL MODULES
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
    EFFORTPERC = "Effort%"
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
    STARTDATE = "StartDate"
    ENDDATE = "EndDate"
    DURATION = "Duration"
    EFFORTH = "EffortH"
    SEQRANK = "SeqRank"
    HASHTAGSEQ = "HashtagSeq"
class TTID(StrEnum):
    
    '''Collects all the ids that identify the dataframes created by TTDataFrameFactory.'''

    TTSBYMONTH = "tts_by_month"
class DEFINITIONSCN(StrEnum):
    
    '''Collects all the column names used by definitions.'''

    TERM = "Term"
    DEFINITION = "Definition"
class OPTION(StrEnum):

    '''Represents a collection of options.'''

    display = auto()
    save = auto()
    log = auto()
    plot = auto()
class CRITERIA(StrEnum):

    '''Represents a collection of criterias.'''

    exclude = auto()
    include = auto()
    do_nothing = auto()
class COLORNAME(StrEnum):

    '''Represents a collection of color names.'''

    skyblue = auto()
    lightgreen = auto()
class EFFORTSTYLE(StrEnum):

    '''Represents a collection of highlight styles for EffortHighlighter.'''

    textual_highlight = auto()
    color_highlight = auto()
class EFFORTMODE(StrEnum):

    '''Represents a collection of modes for EffortHighlighter.'''

    top_one_effort_per_row = auto()
    top_three_efforts = auto()

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
    @staticmethod
    def something_failed_while_saving(file_path : str) -> str:
        return f"Something failed while saving '{file_path}'."

    @staticmethod
    def provided_df_invalid_bym_column_list(column_list : list[str]) -> str:
        return f"The provided df has an invalid BYM column list ('{column_list}')."

    @staticmethod
    def no_strategy_available_for_provided_criteria(criteria : CRITERIA) -> str:
        return f"No strategy available for the provided CRITERIA ('{criteria}')."
    @staticmethod
    def variable_cant_be_less_than_one(variable_name : str) -> str:
        return f"'{variable_name}' can't be < 1."

    @staticmethod
    def provided_df_has_duplicate_column_names(style : EFFORTSTYLE) -> str:
        return f"The provided df has duplicate column names, therefore '{style}' is not supported."
    @staticmethod
    def provided_mode_not_supported(mode : EFFORTMODE):
        return f"The provided mode is not supported: '{mode}'."
    @staticmethod
    def provided_style_not_supported(style : EFFORTSTYLE):
        return f"The provided style is not supported: '{style}'."    

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

    '''Collects all the dataframes, stylers and markdowns.'''

    tt_df : DataFrame
    tt_styler : Union[DataFrame, Styler]

    tts_by_month_tpl : Tuple[DataFrame, DataFrame]
    tts_by_month_styler : Union[DataFrame, Styler]
    tts_by_month_sub_dfs : list[DataFrame]
    tts_by_month_sub_md : str

    tts_by_year_df : DataFrame
    tts_by_year_styler : Union[DataFrame, Styler]

    tts_by_year_month_tpl : Tuple[DataFrame, DataFrame]
    tts_by_year_month_styler : Union[DataFrame, Styler]

    tts_by_year_month_spnv_tpl : Tuple[DataFrame, DataFrame]
    tts_by_year_month_spnv_styler : Union[DataFrame, Styler]

    tts_by_year_spnv_tpl : Tuple[DataFrame, DataFrame]
    tts_by_year_spnv_styler : Union[DataFrame, Styler]

    tts_by_spn_df : DataFrame
    tts_by_spn_styler : Union[DataFrame, Styler]

    tts_by_spn_spv_df : DataFrame
    tts_by_hashtag_df : DataFrame
    tts_by_hashtag_year_df : DataFrame
    tts_by_hashtag_year_styler : Union[DataFrame, Styler]

    tts_by_efs_tpl : Tuple[DataFrame, DataFrame]
    tts_by_efs_styler : Union[DataFrame, Styler]

    tts_by_tr_df : DataFrame
    tts_by_tr_styler : Union[DataFrame, Styler]
    
    tts_gantt_spnv_df : DataFrame
    tts_gantt_spnv_plot_function : Callable[[], None]

    tts_gantt_hseq_df : DataFrame
    tts_gantt_hseq_plot_function : Callable[[], None]

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
            "nwpackageversions"
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

    # WITHOUT DEFAULTS
    options_tt : list[Literal[OPTION.display]]
    options_tts_by_month : list[Literal[OPTION.display, OPTION.save]]
    options_tts_by_year : list[Literal[OPTION.display]]
    options_tts_by_year_month : list[Literal[OPTION.display]]
    options_tts_by_year_month_spnv : list[Literal[OPTION.display]]
    options_tts_by_year_spnv : list[Literal[OPTION.display]]    
    options_tts_by_spn : list[Literal[OPTION.display, OPTION.log]]
    options_tts_by_spn_spv : list[Literal[OPTION.display, OPTION.log]]
    options_tts_by_hashtag : list[Literal[OPTION.display, OPTION.log]]
    options_tts_by_hashtag_year : list[Literal[OPTION.display]]
    options_tts_by_efs : list[Literal[OPTION.display]]
    options_tts_by_tr : list[Literal[OPTION.display]]
    options_tts_gantt_spnv : list[Literal[OPTION.display, OPTION.plot, OPTION.log]]
    options_tts_gantt_hseq : list[Literal[OPTION.display, OPTION.plot, OPTION.log]]
    options_definitions : list[Literal[OPTION.display]]
    excel_nrows : int
    tts_by_year_month_spnv_display_only_spn : Optional[str]
    tts_by_year_spnv_display_only_spn : Optional[str]
    tts_by_spn_spv_display_only_spn : Optional[str]

    # WITH DEFAULTS
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
    tts_by_month_effort_highlight : bool = field(default = True)
    tts_by_month_effort_highlight_style : EFFORTSTYLE = field(default = EFFORTSTYLE.textual_highlight)
    tts_by_month_effort_highlight_mode : EFFORTMODE = field(default = EFFORTMODE.top_three_efforts)
    tts_by_year_effort_highlight : bool = field(default = True)
    tts_by_year_effort_highlight_column_names : list[str] = field(default_factory = lambda : [TTCN.EFFORT])
    tts_by_year_effort_highlight_style : EFFORTSTYLE = field(default = EFFORTSTYLE.color_highlight)
    tts_by_year_effort_highlight_mode : EFFORTMODE = field(default = EFFORTMODE.top_three_efforts)    
    tts_by_year_month_display_only_years : Optional[list[int]] = field(default_factory = lambda : YearProvider().get_most_recent_x_years(x = uint(1)))
    tts_by_year_month_spnv_formatters : dict = field(default_factory = lambda : { "%_DME" : "{:.2f}", "%_TME" : "{:.2f}" })
    tts_by_year_month_spnv_effort_highlight : bool = field(default = True)
    tts_by_year_month_spnv_effort_highlight_column_names : list[str] = field(default_factory = lambda : [TTCN.EFFORT])
    tts_by_year_month_spnv_effort_highlight_style : EFFORTSTYLE = field(default = EFFORTSTYLE.color_highlight)
    tts_by_year_month_spnv_effort_highlight_mode : EFFORTMODE = field(default = EFFORTMODE.top_three_efforts)    
    tts_by_year_spnv_formatters : dict = field(default_factory = lambda : { "%_DYE" : "{:.2f}", "%_TYE" : "{:.2f}" })
    tts_by_year_spnv_effort_highlight : bool = field(default = True)
    tts_by_year_spnv_effort_highlight_column_names : list[str] = field(default_factory = lambda : [TTCN.EFFORT])
    tts_by_year_spnv_effort_highlight_style : EFFORTSTYLE = field(default = EFFORTSTYLE.color_highlight)
    tts_by_year_spnv_effort_highlight_mode : EFFORTMODE = field(default = EFFORTMODE.top_three_efforts)    
    tts_by_spn_formatters : dict = field(default_factory = lambda : { "%_DE" : "{:.2f}", "%_TE" : "{:.2f}" })
    tts_by_spn_remove_untagged : bool = field(default = True)
    tts_by_spn_effort_highlight : bool = field(default = True)
    tts_by_spn_effort_highlight_column_names : list[str] = field(default_factory = lambda : [TTCN.EFFORT])
    tts_by_spn_effort_highlight_style : EFFORTSTYLE = field(default = EFFORTSTYLE.color_highlight)
    tts_by_spn_effort_highlight_mode : EFFORTMODE = field(default = EFFORTMODE.top_three_efforts)
    tts_by_hashtag_formatters : dict = field(default_factory = lambda : { "Effort%" : "{:.2f}" })
    tts_by_hashtag_year_enable_pivot : bool = field(default = True)
    tts_by_hashtag_year_effort_highlight : bool = field(default = True)
    tts_by_hashtag_year_effort_highlight_style : EFFORTSTYLE = field(default = EFFORTSTYLE.color_highlight)
    tts_by_hashtag_year_effort_highlight_mode : EFFORTMODE = field(default = EFFORTMODE.top_one_effort_per_row)
    tts_by_efs_is_correct : bool = field(default = False)
    tts_by_efs_n : uint = field(default = uint(25))
    tts_by_tr_unknown_id : str = field(default = "Unknown")
    tts_by_tr_remove_unknown_occurrences : bool = field(default = True)
    tts_by_tr_filter_by_top_n : Optional[uint] = field(default = uint(5))
    tts_by_tr_head_n : Optional[uint] = field(default = uint(10))
    tts_by_tr_display_head_n_with_tail : bool = field(default = False)
    tts_gantt_spnv_spns : Optional[list[str]] = field(default_factory = lambda : []) 
    tts_gantt_spnv_criteria : Literal[CRITERIA.do_nothing, CRITERIA.include, CRITERIA.exclude] = field(default = CRITERIA.do_nothing)
    tts_gantt_spnv_months : int = field(default = 4)
    tts_gantt_spnv_min_duration : int = field(default = 4)
    tts_gantt_spnv_fig_size : Tuple[int, int] = field(default = (10, 6))
    tts_gantt_spnv_title : Optional[str] = field(default = None)
    tts_gantt_spnv_x_label : Optional[str] = field(default = None)
    tts_gantt_spnv_y_label : Optional[str] = field(default = None)
    tts_gantt_spnv_formatters : dict = field(default_factory = lambda : { "StartDate": "{:%Y-%m-%d}", "EndDate": "{:%Y-%m-%d}" })
    tts_gantt_hseq_hashtags : Optional[list[str]] = field(default_factory = lambda : []) 
    tts_gantt_hseq_criteria : Literal[CRITERIA.do_nothing, CRITERIA.include, CRITERIA.exclude] = field(default = CRITERIA.do_nothing)
    tts_gantt_hseq_months : int = field(default = 4)
    tts_gantt_hseq_min_duration : int = field(default = 4)
    tts_gantt_hseq_fig_size : Tuple[int, int] = field(default = (10, 6))
    tts_gantt_hseq_title : Optional[str] = field(default = None)
    tts_gantt_hseq_x_label : Optional[str] = field(default = None)
    tts_gantt_hseq_y_label : Optional[str] = field(default = None)
    tts_gantt_hseq_formatters : dict = field(default_factory = lambda : { "StartDate": "{:%Y-%m-%d}", "EndDate": "{:%Y-%m-%d}" })
    md_infos : list[MDInfo] = field(default_factory = lambda : MDInfoProvider().get_all())
    md_last_update : datetime = field(default = datetime.now())
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
    def create_time_range_id(self, start_time : str, end_time : str, unknown_id : str) -> str:
            
        '''
            Creates a unique time range identifier out of the provided parameters.
            If parameters are empty, it returns unknown_id.
        '''

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
    def is_bym(self, column_list : list[str]) -> bool:
        
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

        if len(column_list) < 2 or column_list[0] != TTCN.MONTH:
            return False

        for i in range(1, len(column_list)):
            if i % 2 == 1:
                if not self.is_year(column_list[i]):
                    return False
            else:
                if column_list[i] != TTCN.TREND:
                    return False

        return self.is_even(number = len(column_list))
    def unbox_bym_column_list(self, df : DataFrame) -> DataFrame:
        
        '''
            Renames all "↕" column names by suffixing "↕" with a progressive number ["↕1", "↕2", "↕3", ...].

            BYM DataFrames must be 'unboxed' before being piped into certain processing tasks due to a Pandas limitation.
            Pandas does not support DataFrames with multiple columns sharing the same name.
        '''

        counter : int = 1
        new_columns : list[str] = []

        for col in df.columns:
            if col == TTCN.TREND:
                new_columns.append(f"{TTCN.TREND}{counter}")
                counter += 1
            else:
                new_columns.append(col)

        df.columns = Index(new_columns)
        
        return df
    def box_bym_column_list(self, df : DataFrame) -> DataFrame:
        
        '''
            Revert back ["↕1", "↕2", "↕3", ...] ('unboxed' column names) to "↕".
            
            BYM DataFrames must be 'boxed' before being displayed.
        '''
        
        new_columns : list[str] = [TTCN.TREND if col.startswith(TTCN.TREND) and col[1:].isdigit() else col for col in df.columns.to_list()]
        df.columns = Index(new_columns)
        
        return df
class BYMFactory():

    '''Encapsulates all the logic related to the creation of *_by_month_df dataframes.'''

    __df_helper : TTDataFrameHelper

    def __init__(self, df_helper : TTDataFrameHelper) -> None:

        self.__df_helper = df_helper

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
            tts_df[str(year)] = tts_df[str(year)].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))

        tts_df.rename(columns = (lambda x : self.__try_consolidate_trend_column_name(column_name = x)), inplace = True)
        tts_upd_df : DataFrame = self.__update_future_months_to_empty(tts_by_month_df = tts_df, now = now)

        return (tts_df, tts_upd_df)
class BYMSplitter():
    
    '''Encapsulates all the logic related to the splitting of *_by_month_df dataframes.'''

    __df_helper : TTDataFrameHelper

    def __init__(self, df_helper : TTDataFrameHelper) -> None:

        self.__df_helper = df_helper

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

        if self.__df_helper.is_even(index_lists[-1][-1]):
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

        if not self.__df_helper.is_bym(column_list = column_list):
            raise Exception(_MessageCollection.provided_df_invalid_bym_column_list(column_list))
        
        if len(column_list) == 2:
            return [df]

        column_numbers : list[int] = self.__create_column_numbers(df = df)
        index_lists : list[list[int]] = self.__create_index_lists(column_numbers = column_numbers)
        sub_dfs : list[DataFrame] = self.__filter_by_index_lists(df = df, index_lists = index_lists)

        return sub_dfs
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

    def __has_duplicate_column_names(self, df : DataFrame) -> bool:
        
        '''Return True if the DataFrame has duplicate column names.'''

        return bool(df.columns.duplicated().any())
    def __validate(self, df : DataFrame, style : EFFORTSTYLE) -> None: 

        '''
            | EFFORTSTYLE       | HAS_DUPLICATE_COLUMN_NAMES | OUTCOME   |
            |-------------------|----------------------------|-----------|
            | textual_highlight | True                       | OK        |
            | textual_highlight | False                      | OK        |
            | color_highlight   | True                       | EXCEPTION |
            | color_highlight   | FALSE                      | OK        |
        '''

        flag : bool = self.__has_duplicate_column_names(df = df)

        if flag == True and style == EFFORTSTYLE.color_highlight:
            raise Exception(_MessageCollection.provided_df_has_duplicate_column_names(style))

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

    def __apply_textual_highlights(self, df : DataFrame, effort_cells : list[EffortCell], tags : Tuple[str, str]) -> DataFrame:

        '''Adds two HTML tags around the content of the cells listed in effort_cells.'''

        styled_df : DataFrame = df.copy(deep = True)

        left_h : str = tags[0]
        right_h : str = tags[1]

        for effort_cell in effort_cells:

            row, col = effort_cell.coordinate_pair

            if row < len(df) and col < len(df.columns):
                styled_df.iloc[row, col] = f"{left_h}{str(df.iloc[row, col])}{right_h}"
            
        return styled_df
    def __apply_color_highlights(self, df : DataFrame, effort_cells : list[EffortCell], color : COLORNAME) -> Styler:
        
        '''Adds color as background color for the cells listed in effort_cells.'''

        styled_df : DataFrame = DataFrame('', index = df.index, columns = df.columns)
        
        for effort_cell in effort_cells:

            row, col = effort_cell.coordinate_pair

            if row < len(df) and col < len(df.columns):
                styled_df.iloc[row, col] = f"background-color: {color}"

        styler : Styler = df.style.apply(lambda _ : styled_df, axis = None)

        return styler

    def create_styler(
        self, 
        df : DataFrame, 
        style : EFFORTSTYLE, 
        mode : EFFORTMODE, 
        color : COLORNAME = COLORNAME.skyblue, 
        tags : Tuple[str, str] = ("<mark style='background-color: skyblue'>", "</mark>"),
        column_names : list[str] = []
        ) -> Union[Styler, DataFrame]:

        '''
            Expects a df containing efforts into cells - i.e. "45h 45m", "77h 45m".
            Returns a df with highlighted cells as per arguments. 
        '''

        self.__validate(df = df, style = style)

        tmp_df : DataFrame = df.copy(deep = True)

        if len(column_names) == 0:
            column_names = tmp_df.columns.to_list()

        effort_cells : list[EffortCell] = self.__calculate_effort_cells(
            df = tmp_df, 
            mode = mode,
            column_names = column_names
        )

        if style == EFFORTSTYLE.color_highlight:
            return self.__apply_color_highlights(df = tmp_df, effort_cells = effort_cells, color = color)
        elif style == EFFORTSTYLE.textual_highlight:
            return self.__apply_textual_highlights(df = tmp_df, effort_cells = effort_cells, tags = tags)
        else:
            raise Exception(_MessageCollection.provided_style_not_supported(style))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby(by = [TTCN.PROJECTNAME, TTCN.PROJECTVERSION])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.PROJECTNAME, TTCN.PROJECTVERSION]).reset_index(drop = True)

        condition_three : Series = (tts_df[TTCN.PROJECTNAME].isin(values = software_project_names))
        tts_df = tts_df.loc[condition_three]
        tts_df = tts_df.sort_values(by = [TTCN.PROJECTNAME, TTCN.PROJECTVERSION]).reset_index(drop = True)

        return tts_df
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby(by = [TTCN.HASHTAG])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)

        summarized : float = tts_df[TTCN.EFFORT].sum()
        tts_df[TTCN.EFFORTPERC] = tts_df.apply(lambda x : self.__df_helper.calculate_percentage(part = x[TTCN.EFFORT], whole = summarized), axis = 1)     

        return tts_df
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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby([TTCN.YEAR])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = TTCN.YEAR).reset_index(drop = True)

        tts_df[TTCN.YEARLYTARGET] = tts_df[TTCN.YEAR].apply(
            lambda x : cast(YearlyTarget, self.__df_helper.get_yearly_target(yearly_targets = yearly_targets, year = x)).hours)
        tts_df[TTCN.TARGETDIFF] = tts_df[TTCN.EFFORT] - tts_df[TTCN.YEARLYTARGET]
        tts_df[TTCN.ISTARGETMET] = tts_df.apply(
            lambda x : self.__df_helper.is_yearly_target_met(effort = x[TTCN.EFFORT], yearly_target = x[TTCN.YEARLYTARGET]), axis = 1)    

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))
        tts_df[TTCN.YEARLYTARGET] = tts_df[TTCN.YEARLYTARGET].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))
        tts_df[TTCN.TARGETDIFF] = tts_df[TTCN.TARGETDIFF].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = True))

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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.unbox_effort(effort_str = x))
        tts_df = tts_df.groupby(by = [TTCN.YEAR, TTCN.MONTH])[TTCN.EFFORT].sum().sort_values(ascending = [False]).reset_index(name = TTCN.EFFORT)
        tts_df = tts_df.sort_values(by = [TTCN.YEAR, TTCN.MONTH]).reset_index(drop = True)

        tts_df[TTCN.YEARLYTOTAL] = tts_df[TTCN.EFFORT].groupby(by = tts_df[TTCN.YEAR]).cumsum()

        tts_df[TTCN.YEARLYTARGET] = tts_df[TTCN.YEAR].apply(
            lambda x : cast(YearlyTarget, self.__df_helper.get_yearly_target(yearly_targets = yearly_targets, year = x)).hours)

        tts_df[TTCN.TOTARGET] = tts_df[TTCN.YEARLYTOTAL] - tts_df[TTCN.YEARLYTARGET]    
        tts_df.drop(columns = [TTCN.YEARLYTARGET], axis = 1, inplace = True)
        
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   
        tts_df[TTCN.YEARLYTOTAL] = tts_df[TTCN.YEARLYTOTAL].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))
        tts_df[TTCN.TOTARGET] = tts_df[TTCN.TOTARGET].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = True))

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
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   
        tts_df[TTCN.DME] = tts_df[TTCN.DME].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))
        tts_df[TTCN.TME] = tts_df[TTCN.TME].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))

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
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   
        tts_df[TTCN.DYE] = tts_df[TTCN.DYE].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))
        tts_df[TTCN.TYE] = tts_df[TTCN.TYE].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))

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

        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   
        tts_df[TTCN.DE] = tts_df[TTCN.DE].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))
        tts_df[TTCN.TE] = tts_df[TTCN.TE].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))

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
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   

        return tts_df
    def create_tts_by_hashtag_year_df(self, tt_df : DataFrame, years : list[int], enable_pivot : bool) -> DataFrame:

        '''
                Year	Hashtag	        Effort
            0   2023	#csharp	        67h 30m
            1   2023	#maintenance	51h 00m
            2   2023	#powershell	    04h 30m 
            ...    
        '''
    
        tts_df : DataFrame = self.__create_raw_tts_by_year_hashtag(tt_df = tt_df, years = years)
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   

        if enable_pivot:
            tts_df = tts_df.pivot(index = TTCN.HASHTAG, columns = TTCN.YEAR, values = TTCN.EFFORT).reset_index()
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
    
        tts_df : DataFrame = self.__create_raw_tts_by_hashtag(tt_df = tt_df)
        tts_df[TTCN.EFFORT] = tts_df[TTCN.EFFORT].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))   

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
class TTMarkdownFactory():

    '''Encapsulates all the logic related to Markdown creation out of Time Tracking dataframes.'''

    __markdown_helper : MarkdownHelper

    def __init__(self, markdown_helper : MarkdownHelper) -> None:

        self.__markdown_helper = markdown_helper

    def __convert_sub_dfs(self, sub_dfs : list[DataFrame]) -> str:

        '''Converts sub_dfs to sub_mds and joins them.'''

        sub_mds : list[str] = []

        for sub_df in sub_dfs:
            sub_md : str = sub_df.to_markdown(index = False)
            sub_mds.append(sub_md)

        return "\n\n".join(sub_mds)
    
    def create_tts_by_month_sub_md(self, paragraph_title : str, last_update : datetime, sub_dfs : list[DataFrame]) -> str:

        '''Creates the expected Markdown content for the provided arguments.'''

        markdown_header : str = self.__markdown_helper.get_markdown_header(last_update = last_update, paragraph_title = paragraph_title)
        tts_by_month_sub_md = self.__convert_sub_dfs(sub_dfs = sub_dfs)           

        md_content : str = markdown_header
        md_content += "\n"
        md_content += tts_by_month_sub_md
        md_content += "\n"

        return md_content
class TTSequencer():

    '''Encapsulates all the logic related to sequencing tt_df.'''

    __df_helper : TTDataFrameHelper

    def __init__(self, df_helper : TTDataFrameHelper) -> None:

        self.__df_helper = df_helper

    def __convert_criteria_to_value(self, criteria : Literal[CRITERIA.do_nothing, CRITERIA.include, CRITERIA.exclude]) -> Optional[bool]:

        if criteria == CRITERIA.do_nothing:
            return None
        elif criteria == CRITERIA.include:
            return True
        elif criteria == CRITERIA.exclude:
            return False
        else:
            raise Exception(_MessageCollection.no_strategy_available_for_provided_criteria(criteria = criteria))
    def __calculate_from_start_date(self, now : datetime, months : int) -> date:
        
        """Calculates from_start_date as 'now - months'."""

        from_start_date : datetime = now - relativedelta(months = months)

        return from_start_date.date()
    def __filter_by_from_start_date(self, df : DataFrame, from_start_date : date, sort_by : Literal[TTCN.DESCRIPTOR, TTCN.HASHTAGSEQ]) -> DataFrame:

        '''Filters out a df according to the condition: TTCN.STARTDATE > from_start_date.'''

        filtered_df : DataFrame = df.copy(deep = True)

        condition : Series = (filtered_df[TTCN.STARTDATE] > pd.Timestamp(from_start_date))
        filtered_df = cast(DataFrame, filtered_df.loc[condition])
        filtered_df = filtered_df.sort_values(by = [sort_by, TTCN.STARTDATE]).reset_index(drop = True)

        return filtered_df
    def __filter_by_is_software_project(self, df : DataFrame, spns : Optional[list[str]], value : Optional[bool]) -> DataFrame:
        
        '''
            Filters out a df according to the condition: TTCN.ISSOFTWAREPROJECT == <value>.

            If spns or value are None, df will be returned as-is.
        '''

        if not spns or not value:
            return df

        filtered_df : DataFrame = df.copy(deep = True)

        condition : Series = (filtered_df[TTCN.ISSOFTWAREPROJECT] == value)
        filtered_df = cast(DataFrame, filtered_df.loc[condition])

        if spns:
            filtered_df[TTCN.PROJECTNAME] = filtered_df[TTCN.DESCRIPTOR].apply(lambda x : self.__df_helper.extract_software_project_name(descriptor = x))
            condition = (filtered_df[TTCN.PROJECTNAME].isin(cast(list[str], spns)))
            filtered_df = cast(DataFrame, filtered_df.loc[condition])
            filtered_df.drop(columns = [TTCN.PROJECTNAME], inplace = True)

        filtered_df.reset_index(drop = True, inplace = True)

        return filtered_df
    def __filter_by_hashtag(self, df : DataFrame, hashtags : Optional[list[str]], value : Optional[bool]) -> DataFrame:
        
        '''
            Filters out a df according to the condition: TTCN.HASHTAG == <value>.

            If spns or value are None, df will be returned as-is.
        '''

        if not hashtags or not value:
            return df

        filtered_df : DataFrame = df.copy(deep = True)

        condition : Series = (filtered_df[TTCN.HASHTAG] == value)
        filtered_df = cast(DataFrame, filtered_df.loc[condition])

        if hashtags:
            condition = (filtered_df[TTCN.HASHTAG].isin(cast(list[str], hashtags)))
            filtered_df = cast(DataFrame, filtered_df.loc[condition])

        filtered_df.reset_index(drop = True, inplace = True)

        return filtered_df    
    def __filter_by_duration(self, df : DataFrame, min_duration : int) -> DataFrame:
        
        '''Filters out a df according to the condition: [TTCN.DURATION] >= min_duration.'''

        filtered_df : DataFrame = df.copy(deep = True)

        condition : Series = (filtered_df[TTCN.DURATION] >= min_duration)
        filtered_df = cast(DataFrame, filtered_df.loc[condition])

        filtered_df.reset_index(drop = True, inplace = True)

        return filtered_df
    def __round_effort(self, effort : str) -> int:

        '''
            14h 00m -> 14
            34h 15m -> 34
            13h 30m -> 13
            31h 45m -> 31 -> 32
        '''

        components : list[str] = effort.split()
        hour_str : str = components[0]
        minute_str : str = components[1]

        hours : int = int(hour_str.replace("h", ""))

        if "45m" in minute_str:
            hours += 1

        return hours

    def __add_seq_rank(self, df : DataFrame, group_by : Literal[TTCN.HASHTAG] = TTCN.HASHTAG) -> DataFrame:

        '''
            Assigns sequential ranks to hashtags sorted by Date.

            Steps:
                1 -> [ "Date", "StartTime", "EndTime", "Effort", "Hashtag", "Descriptor", "IsSoftwareProject", "IsReleaseDay", "Year", "Month" ]
                2 -> ["Date", "Effort", "Hashtag"]
                3 -> ["Date", "Effort", "Hashtag", "SeqRank"]
        '''

        ranked_df : DataFrame = cast(DataFrame, df[[TTCN.DATE, TTCN.EFFORT, group_by]].copy(deep = True))
        ranked_df = ranked_df.sort_values(by = TTCN.DATE).reset_index(drop = True)

        hashtag_rank : dict[str, int] = {}
        current_seqrank : int = 1
        previous_hashtag : Optional[str] = None
        
        seq_ranks : list[int] = []

        for _, row in ranked_df.iterrows():

            current_hashtag: str = str(row[group_by])
            
            if current_hashtag != previous_hashtag:
                if current_hashtag not in hashtag_rank:
                    hashtag_rank[current_hashtag] = current_seqrank
                else:
                    hashtag_rank[current_hashtag] += 1
            
            seq_ranks.append(hashtag_rank[current_hashtag])

            previous_hashtag = current_hashtag
        
        ranked_df[TTCN.SEQRANK] = seq_ranks

        return ranked_df
    def __add_hashtag_seq(self, df : DataFrame) -> DataFrame:

        '''
            Expects: ["Date", "Effort", "Hashtag", "SeqRank"]
            Returns: ["Date", "Effort", "Hashtag", "SeqRank", "HashtagSeq"]
        '''

        hseq_df : DataFrame = cast(DataFrame, df[[TTCN.DATE, TTCN.EFFORT, TTCN.HASHTAG, TTCN.SEQRANK]].copy(deep = True))

        hseq_df[TTCN.HASHTAGSEQ] = hseq_df[TTCN.HASHTAG].astype(str) + hseq_df[TTCN.SEQRANK].astype(str)

        return hseq_df

    def __create_gannt_df(self, df : DataFrame, group_by : Literal[TTCN.DESCRIPTOR, TTCN.HASHTAGSEQ]) -> DataFrame:

        '''

            
            Steps:
                1 -> [ "Date", "StartTime", "EndTime", "Effort", "Hashtag", "Descriptor", "IsSoftwareProject", "IsReleaseDay", "Year", "Month" ]
                2 -> ["Descriptor", "StartDate", "EndDate", "EffortH"] ("EffortH" as timedelta)
                3 -> ["Descriptor", "StartDate", "EndDate", "EffortH", "Duration"] ("EffortH" as timedelta)
                4 -> ["Descriptor", "StartDate", "EndDate", "EffortH", "Duration"] ("EffortH" as rounded int)
        '''

        gantt_df : DataFrame = df.copy(deep = True)
        gantt_df[TTCN.EFFORTH] = gantt_df[TTCN.EFFORT].apply(self.__df_helper.unbox_effort)
        
        gantt_df = (
            gantt_df
            .groupby(group_by)
            .agg(
                StartDate = (TTCN.DATE, 'min'), 
                EndDate = (TTCN.DATE, 'max'),
                EffortH = (TTCN.EFFORTH, 'sum'))
            .reset_index()
        )

        gantt_df[TTCN.STARTDATE] = pd.to_datetime(gantt_df[TTCN.STARTDATE])
        gantt_df[TTCN.ENDDATE] = pd.to_datetime(gantt_df[TTCN.ENDDATE])
        gantt_df[TTCN.DURATION] = (gantt_df[TTCN.ENDDATE] - gantt_df[TTCN.STARTDATE]).astype("timedelta64[ns]").dt.days

        gantt_df[TTCN.EFFORTH] = gantt_df[TTCN.EFFORTH].apply(lambda x : self.__df_helper.box_effort(effort_td = x, add_plus_sign = False))
        gantt_df[TTCN.EFFORTH] = gantt_df[TTCN.EFFORTH].apply(self.__round_effort)

        gantt_df.reset_index(drop = True, inplace = True)

        return gantt_df
    def __show_gantt_chart(
            self, 
            df : DataFrame, 
            fig_size : Tuple[int, int], 
            title : Optional[str], 
            x_label : Optional[str], 
            y_label : Optional[str],
            barh_y : Literal[TTCN.DESCRIPTOR, TTCN.HASHTAGSEQ]
            ) -> None:
        
        """
            Expects:
                - ["Descriptor", "StartDate", "EndDate", "Duration", "Effort"]
                - ["HashtagSeq", "StartDate", "EndDate", "Duration", "Effort"]

            It shows a gannt chart out of df.
        """

        fig, ax = plt.subplots(figsize = fig_size)

        x_min : float = cast(float, (mdates.date2num(df[TTCN.STARTDATE].min()) - 5))
        x_max : float = cast(float, (mdates.date2num(df[TTCN.ENDDATE].max()) + 5))
        ax.set_xlim(xmin = x_min, xmax = x_max)

        y_min : float = -2.5
        y_max : float = len(df) + 2.5
        ax.set_ylim(ymin = y_min, ymax = y_max)

        for row_number, row in enumerate(df.itertuples()):

            row_caller : Any = getattr(row, barh_y)
            ax.barh(row_caller, cast(ArrayLike, row.Duration), left = cast(ArrayLike, row.StartDate), color = "skyblue", edgecolor = "black")

            ax.plot(cast(ArrayLike, [row.EndDate, row.EndDate]), [row_number - 0.4, row_number + 0.8], linestyle = "dotted", color = "black")
            formatted_date : str = f"{cast(datetime, row.EndDate).strftime("%Y-%m-%d")}"
            ax.text(
                cast(float, mdates.date2num(row.EndDate)),
                row_number + 0.8, 
                formatted_date, 
                ha = "center", 
                va = "bottom", 
                fontsize = 6, 
                rotation = 90,
                clip_on = True
            )

            if barh_y == TTCN.HASHTAGSEQ:
                ax.plot(cast(ArrayLike, [row.StartDate, row.StartDate]), [row_number - 0.4, row_number + 0.8], linestyle = "dotted", color = "black")
                formatted_date = f"{cast(datetime, row.StartDate).strftime("%Y-%m-%d")}"
                ax.text(
                    cast(float, mdates.date2num(row.StartDate)), 
                    row_number + 0.8, 
                    formatted_date, 
                    ha = "center", 
                    va = "bottom", 
                    fontsize = 6, 
                    rotation = 90,
                    clip_on = True
                )


            mid_point : datetime = cast(datetime, row.StartDate) + timedelta(days = cast(float, row.Duration) / 2)
            ax.text(
                cast(float, mdates.date2num(mid_point)),
                row_number,
                str(row.EffortH),
                ha = "center",
                va = "center",
                fontsize = 9,
                color = "black"
            )

        clean_label : Callable[[Optional[str]], str] = lambda x : str(x) if x else ""

        ax.set_xlabel(xlabel = clean_label(x_label))
        ax.set_ylabel(ylabel = clean_label(y_label))
        ax.set_title(label = clean_label(title))
        ax.xaxis_date()
        plt.xticks(rotation = 45)
        plt.tight_layout()

        plt.show()

    def create_tts_gantt_spnv_df(
        self, 
        tt_df : DataFrame, 
        spns : Optional[list[str]],
        criteria : Literal[CRITERIA.do_nothing, CRITERIA.include, CRITERIA.exclude],
        now : datetime,
        months : int,
        min_duration : int
        ) -> DataFrame:

        '''
            Expects: [ "Date", "StartTime", "EndTime", "Effort", "Hashtag", "Descriptor", "IsSoftwareProject", "IsReleaseDay", "Year", "Month" ]
            Returns: ["Descriptor", "StartDate", "EndDate", "Duration", "EffortH"].
        '''

        if months < 1:
            raise Exception(_MessageCollection.variable_cant_be_less_than_one("months"))
        if cast(int, min_duration) < 1:
            raise Exception(_MessageCollection.variable_cant_be_less_than_one("min_duration"))

        df : DataFrame = tt_df.copy(deep = True)

        value : Optional[bool] = self.__convert_criteria_to_value(criteria = criteria)
        df = self.__filter_by_is_software_project(df = df, spns = spns, value = value)

        group_by : Literal[TTCN.DESCRIPTOR, TTCN.HASHTAGSEQ] = TTCN.DESCRIPTOR
        df  = self.__create_gannt_df(df = df, group_by = group_by)

        from_start_date : date = self.__calculate_from_start_date(now = now, months = months)
        df = self.__filter_by_from_start_date(df = df, from_start_date = from_start_date, sort_by = group_by)

        df = self.__filter_by_duration(df = df, min_duration = min_duration)        

        return df
    def create_tts_gantt_spnv_chart_function(
            self, 
            gantt_df : DataFrame,
            fig_size : Tuple[int, int], 
            title : Optional[str], 
            x_label : Optional[str], 
            y_label : Optional[str]
            ) -> Callable[[], None]:

        '''Returns a function that visualizes df as GANNT chart.'''

        func : Callable[[], None] = lambda : self.__show_gantt_chart(
            df = gantt_df,
            fig_size = fig_size,
            title = title,
            x_label = x_label,
            y_label = y_label,
            barh_y = TTCN.DESCRIPTOR
        )

        return func
    def create_tts_gantt_hseq_df(
            self, 
            tt_df : DataFrame,
            hashtags : Optional[list[str]],
            criteria : Literal[CRITERIA.do_nothing, CRITERIA.include, CRITERIA.exclude],
            now : datetime,
            months : int,
            min_duration : int
            ) -> DataFrame:

        '''
            Expects: [ "Date", "StartTime", "EndTime", "Effort", "Hashtag", "Descriptor", "IsSoftwareProject", "IsReleaseDay", "Year", "Month" ]
            Returns: [ "HashtagSeq", "StartDate", "EndDate", "EffortH", "Duration" ]
        '''

        if months < 1:
            raise Exception(_MessageCollection.variable_cant_be_less_than_one("months"))
        if cast(int, min_duration) < 1:
            raise Exception(_MessageCollection.variable_cant_be_less_than_one("min_duration"))

        df : DataFrame = tt_df.copy(deep = True)

        value : Optional[bool] = self.__convert_criteria_to_value(criteria = criteria)
        df = self.__filter_by_hashtag(df = df, hashtags = hashtags, value = value)

        df = self.__add_seq_rank(df = df)
        df = self.__add_hashtag_seq(df = df)

        group_by : Literal[TTCN.DESCRIPTOR, TTCN.HASHTAGSEQ] = TTCN.HASHTAGSEQ
        df  = self.__create_gannt_df(df = df, group_by = group_by)

        from_start_date : date = self.__calculate_from_start_date(now = now, months = months)
        df = self.__filter_by_from_start_date(df = df, from_start_date = from_start_date, sort_by = group_by)

        df = self.__filter_by_duration(df = df, min_duration = min_duration)

        return df    
    def create_tts_gantt_hseq_chart_function(
            self, 
            gantt_df : DataFrame,
            fig_size : Tuple[int, int], 
            title : Optional[str], 
            x_label : Optional[str], 
            y_label : Optional[str]
            ) -> Callable[[], None]:

        '''Returns a function that visualizes df as GANNT chart.'''

        func : Callable[[], None] = lambda : self.__show_gantt_chart(
            df = gantt_df,
            fig_size = fig_size,
            title = title,
            x_label = x_label,
            y_label = y_label,
            barh_y = TTCN.HASHTAGSEQ
        )

        return func
class TTAdapter():

    '''Adapts SettingBag properties for use in TT*Factory methods.'''

    __df_factory : TTDataFrameFactory
    __bym_factory : BYMFactory
    __bym_splitter : BYMSplitter
    __tt_sequencer : TTSequencer
    __md_factory : TTMarkdownFactory
    __effort_highlighter : EffortHighlighter

    def __init__(
            self, 
            df_factory : TTDataFrameFactory, 
            bym_factory : BYMFactory,
            bym_splitter : BYMSplitter,
            tt_sequencer : TTSequencer,
            md_factory : TTMarkdownFactory,
            effort_highlighter : EffortHighlighter
        ) -> None:
        
        self.__df_factory = df_factory
        self.__bym_factory = bym_factory
        self.__bym_splitter = bym_splitter
        self.__tt_sequencer = tt_sequencer
        self.__md_factory = md_factory
        self.__effort_highlighter = effort_highlighter

    def __orchestrate_head_n(self, df : DataFrame, head_n : Optional[uint], display_head_n_with_tail : bool) -> DataFrame:

        '''Orchestrates head()-related settings.'''

        if head_n is None:
            return df
        elif head_n is not None and display_head_n_with_tail == True:
            return df.tail(n = int(head_n))
        else:
            return df.head(n = int(head_n))

    def __create_tt_df(self, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tt_df : DataFrame = self.__df_factory.create_tt_df(
            excel_path = setting_bag.excel_path,
            excel_skiprows = setting_bag.excel_skiprows,
            excel_nrows = setting_bag.excel_nrows,
            excel_tabname = setting_bag.excel_tabname
            )

        return tt_df
    def __create_tt_styler(self, tt_df : DataFrame, setting_bag : SettingBag) -> Union[DataFrame, Styler]:

        tt_styler : Union[DataFrame, Styler] = self.__orchestrate_head_n(
            df = tt_df, 
            head_n = setting_bag.tt_head_n, 
            display_head_n_with_tail = setting_bag.tt_display_head_n_with_tail
        )

        return tt_styler

    def __create_tts_by_month_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_month_tpl : Tuple[DataFrame, DataFrame] = self.__bym_factory.create_tts_by_month_tpl(
            tt_df = tt_df,
            years = setting_bag.years,
            now = setting_bag.now
        )

        return tts_by_month_tpl
    def __create_tts_by_month_styler(self, tts_by_month_tpl : Tuple[DataFrame, DataFrame], setting_bag : SettingBag) -> Union[DataFrame, Styler]:
        
        '''Creates the expected Styler object out of the provided arguments.'''

        tts_by_month_df : DataFrame = tts_by_month_tpl[1]
        tts_by_month_styler : Union[DataFrame, Styler] = tts_by_month_df

        if setting_bag.tts_by_month_effort_highlight:
            tts_by_month_styler = self.__effort_highlighter.create_styler(
                df = tts_by_month_df,
                style = setting_bag.tts_by_month_effort_highlight_style,
                mode = setting_bag.tts_by_month_effort_highlight_mode
            )
        
        return tts_by_month_styler
    def __create_tts_by_month_sub_dfs(self, tts_by_month_styler : Union[DataFrame, Styler]) -> list[DataFrame]:

        '''Creates the expected collection of sub_dfs out of the provided arguments.'''

        tts_by_month_sub_dfs : list[DataFrame] = self.__bym_splitter.create_sub_dfs(df = cast(DataFrame, tts_by_month_styler))

        return tts_by_month_sub_dfs
    def __create_tts_by_month_sub_md(self, tts_by_month_sub_dfs : list[DataFrame], setting_bag : SettingBag) -> str:

        '''Creates the expected Markdown content out of the provided arguments.'''

        tts_by_month_sub_md : str = self.__md_factory.create_tts_by_month_sub_md(
            paragraph_title = self.extract_file_name_and_paragraph_title(id = TTID.TTSBYMONTH, setting_bag = setting_bag)[1],
            last_update = setting_bag.md_last_update,
            sub_dfs = tts_by_month_sub_dfs
        )

        return tts_by_month_sub_md

    def __create_tts_by_year_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_year_df : DataFrame = self.__df_factory.create_tts_by_year_df(
            tt_df = tt_df,
            years = setting_bag.years,
            yearly_targets = setting_bag.yearly_targets,
        )

        return tts_by_year_df
    def __create_tts_by_year_styler(self, tts_by_year_df : DataFrame, setting_bag : SettingBag) -> Union[DataFrame, Styler]:
        
        '''Creates the expected Styler object out of the provided arguments.'''

        tts_by_year_styler : Union[DataFrame, Styler] = tts_by_year_df

        if setting_bag.tts_by_year_effort_highlight:
            tts_by_year_styler = self.__effort_highlighter.create_styler(
                df = tts_by_year_df,
                style = setting_bag.tts_by_year_effort_highlight_style,
                mode = setting_bag.tts_by_year_effort_highlight_mode,
                column_names = setting_bag.tts_by_year_effort_highlight_column_names
            )
        
        return tts_by_year_styler    
    
    def __create_tts_by_year_month_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

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
    def __create_tts_by_year_month_styler(self, tts_by_year_month_tpl : Tuple[DataFrame, DataFrame], setting_bag : SettingBag) -> Union[DataFrame, Styler]:

        '''
            tts_by_year_month_tpl is made of (tts_by_year_month_df, tts_by_year_month_flt_df).

            This method decides which one of the two DataFrame is to be displayed according to setting_bag.tts_by_year_month_display_only_years.
        '''

        tts_by_year_month_styler : Union[DataFrame, Styler] = tts_by_year_month_tpl[0]

        if setting_bag.tts_by_year_month_display_only_years is not None:
            tts_by_year_month_styler = tts_by_year_month_tpl[1]

        return tts_by_year_month_styler
       
    def __create_tts_by_year_month_spnv_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_year_month_spnv_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_tts_by_year_month_spnv_tpl(
            tt_df = tt_df,
            years = setting_bag.years,
            software_project_names = setting_bag.software_project_names,
            software_project_name = setting_bag.tts_by_year_month_spnv_display_only_spn
        )

        return tts_by_year_month_spnv_tpl
    def __create_tts_by_year_month_spnv_styler(self, tts_by_year_month_spnv_tpl : Tuple[DataFrame, DataFrame], setting_bag : SettingBag) -> Union[DataFrame, Styler]:
        
        '''
            tts_by_year_month_spnv_tpl is made of (tts_by_year_month_spnv_df, tts_by_year_month_spnv_flt_df).

            This method decides which one of the two DataFrame is to be displayed according to setting_bag.tts_by_year_month_spnv_display_only_spn.
        '''

        tts_by_year_month_spnv_df : DataFrame = tts_by_year_month_spnv_tpl[0]

        if setting_bag.tts_by_year_month_spnv_display_only_spn is not None:
            tts_by_year_month_spnv_df = tts_by_year_month_spnv_tpl[1]

        tts_by_year_month_spnv_styler : Union[DataFrame, Styler] = tts_by_year_month_spnv_df

        if setting_bag.tts_by_year_month_spnv_effort_highlight:
            tts_by_year_month_spnv_styler = self.__effort_highlighter.create_styler(
                df = tts_by_year_month_spnv_df,
                style = setting_bag.tts_by_year_month_spnv_effort_highlight_style,
                mode = setting_bag.tts_by_year_month_spnv_effort_highlight_mode,
                column_names = setting_bag.tts_by_year_month_spnv_effort_highlight_column_names
            )
        
        return tts_by_year_month_spnv_styler
    
    def __create_tts_by_year_spnv_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_year_spnv_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_tts_by_year_spnv_tpl(
            tt_df = tt_df,
            years = setting_bag.years,
            software_project_names = setting_bag.software_project_names,
            software_project_name = setting_bag.tts_by_year_spnv_display_only_spn
        )

        return tts_by_year_spnv_tpl
    def __create_tts_by_year_spnv_styler(self, tts_by_year_spnv_tpl : Tuple[DataFrame, DataFrame], setting_bag : SettingBag) -> Union[DataFrame, Styler]:
        
        '''
            tts_by_year_spnv_tpl is made of (tts_by_year_spnv_df, tts_by_year_spnv_flt_df).

            This method decides which one of the two DataFrame is to be displayed according to setting_bag.tts_by_year_spnv_display_only_spn.
        '''

        tts_by_year_spnv_df : DataFrame = tts_by_year_spnv_tpl[0]

        if setting_bag.tts_by_year_spnv_display_only_spn is not None:
            tts_by_year_spnv_df = tts_by_year_spnv_tpl[1]

        tts_by_year_spnv_styler : Union[DataFrame, Styler] = tts_by_year_spnv_df

        if setting_bag.tts_by_year_spnv_effort_highlight:
            tts_by_year_spnv_styler = self.__effort_highlighter.create_styler(
                df = tts_by_year_spnv_df,
                style = setting_bag.tts_by_year_spnv_effort_highlight_style,
                mode = setting_bag.tts_by_year_spnv_effort_highlight_mode,
                column_names = setting_bag.tts_by_year_spnv_effort_highlight_column_names
            )
        
        return tts_by_year_spnv_styler
    
    def __create_tts_by_spn_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_spn_df : DataFrame = self.__df_factory.create_tts_by_spn_df(
            tt_df = tt_df,
            years = setting_bag.years,
            software_project_names = setting_bag.software_project_names,
            remove_untagged = setting_bag.tts_by_spn_remove_untagged
        )

        return tts_by_spn_df
    def __create_tts_by_spn_styler(self, tts_by_spn_df : DataFrame, setting_bag : SettingBag) -> Union[DataFrame, Styler]:
        
        '''Creates the expected Styler object out of the provided arguments.'''

        tts_by_spn_styler : Union[DataFrame, Styler] = tts_by_spn_df

        if setting_bag.tts_by_spn_effort_highlight:
            tts_by_spn_styler = self.__effort_highlighter.create_styler(
                df = tts_by_spn_df,
                style = setting_bag.tts_by_spn_effort_highlight_style,
                mode = setting_bag.tts_by_spn_effort_highlight_mode,
                column_names = setting_bag.tts_by_spn_effort_highlight_column_names
            )
        
        return tts_by_spn_styler
    
    def __create_tts_by_spn_spv_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_spn_spv_df : DataFrame = self.__df_factory.create_tts_by_spn_spv_df(
            tt_df = tt_df,
            years = setting_bag.years,
            software_project_names = setting_bag.software_project_names
        )

        return tts_by_spn_spv_df
    def __create_tts_by_hashtag_year_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_year_hashtag_df : DataFrame = self.__df_factory.create_tts_by_hashtag_year_df(
            tt_df = tt_df,
            years = setting_bag.years,
            enable_pivot = setting_bag.tts_by_hashtag_year_enable_pivot
        )

        return tts_by_year_hashtag_df
    def __create_tts_by_hashtag_year_styler(self, tts_by_hashtag_year_df : DataFrame, setting_bag : SettingBag) -> Union[DataFrame, Styler]:
        
        '''Creates the expected Styler object out of the provided arguments.'''

        tts_by_hashtag_year_styler : Union[DataFrame, Styler] = tts_by_hashtag_year_df

        if setting_bag.tts_by_hashtag_year_effort_highlight:
            tts_by_hashtag_year_styler = self.__effort_highlighter.create_styler(
                df = tts_by_hashtag_year_df,
                style = setting_bag.tts_by_hashtag_year_effort_highlight_style,
                mode = setting_bag.tts_by_hashtag_year_effort_highlight_mode
            )
        
        return tts_by_hashtag_year_styler    
    
    def __create_tts_by_efs_tpl(self, tt_df : DataFrame, setting_bag : SettingBag) -> Tuple[DataFrame, DataFrame]:

        '''Creates the expected dataframes out of the provided arguments.'''

        tts_by_efs_tpl : Tuple[DataFrame, DataFrame] = self.__df_factory.create_tts_by_efs_tpl(
            tt_df = tt_df,
            is_correct = setting_bag.tts_by_efs_is_correct
        )

        return tts_by_efs_tpl
    def __create_tts_by_tr_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        tts_by_tr_df : DataFrame = self.__df_factory.create_tts_by_tr_df(
            tt_df = tt_df,
            unknown_id = setting_bag.tts_by_tr_unknown_id,
            remove_unknown_occurrences = setting_bag.tts_by_tr_remove_unknown_occurrences
        )

        return tts_by_tr_df
    def __create_tts_by_tr_styler(self, tts_by_tr_df : DataFrame, setting_bag : SettingBag) -> Union[DataFrame, Styler]:

        tts_by_tr_styler : Union[DataFrame, Styler] = self.__orchestrate_head_n(
            df = tts_by_tr_df, 
            head_n = setting_bag.tts_by_tr_head_n, 
            display_head_n_with_tail = setting_bag.tts_by_tr_display_head_n_with_tail
        )    

        return tts_by_tr_styler

    def __create_tts_gantt_spnv_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        return self.__tt_sequencer.create_tts_gantt_spnv_df(
            tt_df = tt_df,
            spns = setting_bag.tts_gantt_spnv_spns,
            criteria = setting_bag.tts_gantt_spnv_criteria,
            now = setting_bag.now,
            months = setting_bag.tts_gantt_spnv_months,
            min_duration = setting_bag.tts_gantt_spnv_min_duration
        )
    def __create_tts_gantt_spnv_plot_function(self, gantt_df : DataFrame, setting_bag : SettingBag) -> Callable[[], None]:

        '''Creates the expected function out of the provided arguments.'''

        return self.__tt_sequencer.create_tts_gantt_spnv_chart_function(
            gantt_df = gantt_df,
            fig_size = setting_bag.tts_gantt_spnv_fig_size,
            title = setting_bag.tts_gantt_spnv_title,
            x_label = setting_bag.tts_gantt_spnv_x_label,
            y_label = setting_bag.tts_gantt_spnv_y_label
        )
    def __create_tts_gantt_hseq_df(self, tt_df : DataFrame, setting_bag : SettingBag) -> DataFrame:

        '''Creates the expected dataframe out of the provided arguments.'''

        return self.__tt_sequencer.create_tts_gantt_hseq_df(
            tt_df = tt_df,
            hashtags = setting_bag.tts_gantt_hseq_hashtags,
            criteria = setting_bag.tts_gantt_hseq_criteria,
            now = setting_bag.now,
            months = setting_bag.tts_gantt_hseq_months,
            min_duration = setting_bag.tts_gantt_hseq_min_duration
        )
    def __create_tts_gantt_hseq_plot_function(self, gantt_df : DataFrame, setting_bag : SettingBag) -> Callable[[], None]:

        '''Creates the expected function out of the provided arguments.'''

        return self.__tt_sequencer.create_tts_gantt_hseq_chart_function(
            gantt_df = gantt_df,
            fig_size = setting_bag.tts_gantt_hseq_fig_size,
            title = setting_bag.tts_gantt_hseq_title,
            x_label = setting_bag.tts_gantt_hseq_x_label,
            y_label = setting_bag.tts_gantt_hseq_y_label
        )   

    def create_summary(self, setting_bag : SettingBag) -> TTSummary:

        '''Creates a TTSummary object out of setting_bag.'''

        tt_df : DataFrame = self.__create_tt_df(setting_bag = setting_bag)
        tt_styler : Union[DataFrame, Styler] = self.__create_tt_styler(tt_df = tt_df, setting_bag = setting_bag)
        
        tts_by_month_tpl : Tuple[DataFrame, DataFrame] = self.__create_tts_by_month_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_month_styler : Union[DataFrame, Styler] = self.__create_tts_by_month_styler(tts_by_month_tpl = tts_by_month_tpl, setting_bag = setting_bag)
        tts_by_month_sub_dfs : list[DataFrame] = self.__create_tts_by_month_sub_dfs(tts_by_month_styler = tts_by_month_styler)
        tts_by_month_sub_md : str = self.__create_tts_by_month_sub_md(tts_by_month_sub_dfs = tts_by_month_sub_dfs, setting_bag = setting_bag)

        tts_by_year_df : DataFrame = self.__create_tts_by_year_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_styler : Union[DataFrame, Styler] = self.__create_tts_by_year_styler(tts_by_year_df = tts_by_year_df, setting_bag = setting_bag)
        
        tts_by_year_month_tpl : Tuple[DataFrame, DataFrame] = self.__create_tts_by_year_month_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_month_styler : Union[DataFrame, Styler] = self.__create_tts_by_year_month_styler(tts_by_year_month_tpl = tts_by_year_month_tpl, setting_bag = setting_bag)
        
        tts_by_year_month_spnv_tpl : Tuple[DataFrame, DataFrame] = self.__create_tts_by_year_month_spnv_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_month_spnv_styler : Union[DataFrame, Styler] = self.__create_tts_by_year_month_spnv_styler(tts_by_year_month_spnv_tpl = tts_by_year_month_spnv_tpl, setting_bag = setting_bag)
        
        tts_by_year_spnv_tpl : Tuple[DataFrame, DataFrame] = self.__create_tts_by_year_spnv_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_year_spnv_styler : Union[DataFrame, Styler] = self.__create_tts_by_year_spnv_styler(tts_by_year_spnv_tpl = tts_by_year_spnv_tpl, setting_bag = setting_bag)

        tts_by_spn_df : DataFrame = self.__create_tts_by_spn_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_spn_styler : Union[DataFrame, Styler] = self.__create_tts_by_spn_styler(tts_by_spn_df = tts_by_spn_df, setting_bag = setting_bag)

        tts_by_spn_spv_df : DataFrame = self.__create_tts_by_spn_spv_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_hashtag_df : DataFrame = self.__df_factory.create_tts_by_hashtag_df(tt_df = tt_df)
        tts_by_hashtag_year_df : DataFrame = self.__create_tts_by_hashtag_year_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_hashtag_year_styler : Union[DataFrame, Styler] = self.__create_tts_by_hashtag_year_styler(tts_by_hashtag_year_df = tts_by_hashtag_year_df, setting_bag = setting_bag)
        
        tts_by_efs_tpl : Tuple[DataFrame, DataFrame] = self.__create_tts_by_efs_tpl(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_efs_styler : Union[DataFrame, Styler] = tts_by_efs_tpl[1]

        tts_by_tr_df : DataFrame = self.__create_tts_by_tr_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_by_tr_styler : Union[DataFrame, Styler] = self.__create_tts_by_tr_styler(tts_by_tr_df = tts_by_tr_df, setting_bag = setting_bag)

        tts_gantt_spnv_df : DataFrame = self.__create_tts_gantt_spnv_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_gantt_spnv_plot_function : Callable[[], None] = self.__create_tts_gantt_spnv_plot_function(gantt_df = tts_gantt_spnv_df, setting_bag = setting_bag)
        tts_gantt_hseq_df : DataFrame = self.__create_tts_gantt_hseq_df(tt_df = tt_df, setting_bag = setting_bag)
        tts_gantt_hseq_plot_function : Callable[[], None] = self.__create_tts_gantt_hseq_plot_function(gantt_df = tts_gantt_hseq_df, setting_bag = setting_bag)       
        
        definitions_df : DataFrame = self.__df_factory.create_definitions_df()

        tt_summary : TTSummary = TTSummary(
            tt_df = tt_df,
            tt_styler = tt_styler,
            tts_by_month_tpl = tts_by_month_tpl,
            tts_by_month_styler = tts_by_month_styler,
            tts_by_month_sub_dfs = tts_by_month_sub_dfs,
            tts_by_month_sub_md = tts_by_month_sub_md,
            tts_by_year_df = tts_by_year_df,
            tts_by_year_styler = tts_by_year_styler,
            tts_by_year_month_tpl = tts_by_year_month_tpl,
            tts_by_year_month_styler = tts_by_year_month_styler,
            tts_by_year_month_spnv_tpl = tts_by_year_month_spnv_tpl,
            tts_by_year_month_spnv_styler = tts_by_year_month_spnv_styler,
            tts_by_year_spnv_tpl = tts_by_year_spnv_tpl,
            tts_by_year_spnv_styler = tts_by_year_spnv_styler,
            tts_by_spn_df = tts_by_spn_df,
            tts_by_spn_styler = tts_by_spn_styler,
            tts_by_spn_spv_df = tts_by_spn_spv_df,
            tts_by_hashtag_df = tts_by_hashtag_df,
            tts_by_hashtag_year_df = tts_by_hashtag_year_df,
            tts_by_hashtag_year_styler = tts_by_hashtag_year_styler,
            tts_by_efs_tpl = tts_by_efs_tpl,
            tts_by_efs_styler = tts_by_efs_styler,
            tts_by_tr_df = tts_by_tr_df,
            tts_by_tr_styler = tts_by_tr_styler,
            tts_gantt_spnv_df = tts_gantt_spnv_df,
            tts_gantt_spnv_plot_function = tts_gantt_spnv_plot_function,
            tts_gantt_hseq_df = tts_gantt_hseq_df,
            tts_gantt_hseq_plot_function = tts_gantt_hseq_plot_function,
            definitions_df = definitions_df
        )

        return tt_summary
    def extract_file_name_and_paragraph_title(self, id : TTID, setting_bag : SettingBag) -> Tuple[str, str]: 
    
        '''Returns (file_name, paragraph_title) for the provided id or raise an Exception.'''

        for md_info in setting_bag.md_infos:
            if md_info.id == id: 
                return (md_info.file_name, md_info.paragraph_title)

        raise Exception(_MessageCollection.no_mdinfo_found(id = id))
class SettingSubset(SimpleNamespace):

    '''A dynamically assigned subset of SettingBag properties with a custom __str__ method that returns them as JSON.'''

    def __str__(self):
        return json.dumps(
            {key: getattr(self, key) for key in self.__dict__}
        )

    def __repr__(self):
        return self.__str__()
class TTLogger():

    '''Collects all the logging logic.'''

    __logging_function : Callable[[str], None]

    def __init__(self, logging_function : Callable[[str], None]) -> None:
    
        self.__logging_function = logging_function

    def __create_setting_subset(self, setting_bag : SettingBag, setting_names : list[str]) -> SettingSubset:
        
        '''Extract all the SettingBag properties matching ids and returns a SettingSubset .'''

        matching_properties : dict = {}

        for field in fields(setting_bag):
            if field.name in setting_names:
                matching_properties[field.name] = getattr(setting_bag, field.name)
        
        return SettingSubset(**matching_properties)

    def try_log_column_definitions(self, df : DataFrame, definitions : DataFrame) -> None:
        
        """Logs the definitions for matching column names in the DataFrame."""

        definitions_dict : dict = definitions.set_index(DEFINITIONSCN.TERM)[DEFINITIONSCN.DEFINITION].to_dict()
        
        for column_name in df.columns:
            if column_name in definitions_dict:
                self.__logging_function(f"{column_name}: {definitions_dict[column_name]}")
    def try_log_term_definition(self, term : str, definitions : DataFrame) -> None:

        """Logs the definitions for matching term in the DataFrame."""

        definitions_dict : dict = definitions.set_index(DEFINITIONSCN.TERM)[DEFINITIONSCN.DEFINITION].to_dict()

        if term in definitions_dict:
            self.__logging_function(f"{term}: {definitions_dict[term]}")        
    def try_log_settings(self, setting_bag : SettingBag, setting_names : list[str]) -> None:
        
        """Logs only the settings with names contained in ids."""

        if len(setting_names) > 0:
            setting_subset : SettingSubset = self.__create_setting_subset(setting_bag = setting_bag, setting_names = setting_names)
            self.__logging_function(str(setting_subset))
    def log(self, msg : str) -> None:

        '''Logs the provided msg. Does nothing if msg is empty'''

        if len(msg) > 0:
            self.__logging_function(msg)
@dataclass(frozen=True)
class ComponentBag():

    '''Represents a collection of components.'''

    file_path_manager : FilePathManager = field(default = FilePathManager())
    file_manager : FileManager = field(default = FileManager(file_path_manager = FilePathManager()))
    displayer : Displayer = field(default = Displayer())
    
    tt_logger : TTLogger = field(default = TTLogger(logging_function = LambdaProvider().get_default_logging_function()))
    
    tt_adapter : TTAdapter = field(default = TTAdapter(
        df_factory = TTDataFrameFactory(df_helper = TTDataFrameHelper()), 
        bym_factory = BYMFactory(df_helper = TTDataFrameHelper()),
        bym_splitter = BYMSplitter(df_helper = TTDataFrameHelper()),
        tt_sequencer = TTSequencer(df_helper = TTDataFrameHelper()),
        md_factory = TTMarkdownFactory(markdown_helper = MarkdownHelper(formatter = Formatter())),
        effort_highlighter = EffortHighlighter(df_helper = TTDataFrameHelper())
        ))
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
    def __save_and_log(self, id : TTID, content : str, logging_function : Callable[[str], None]) -> None:

        '''Creates the provided Markdown content using __setting_bag.'''

        file_path : str = self.__component_bag.file_path_manager.create_file_path(
            folder_path = self.__setting_bag.working_folder_path,
            file_name = self.__component_bag.tt_adapter.extract_file_name_and_paragraph_title(id = id, setting_bag = self.__setting_bag)[0]
        )

        try:
           
            self.__component_bag.file_manager.save_content(content = content, file_path = file_path)
            logging_function(_MessageCollection.this_content_successfully_saved_as(id = id, file_path = file_path))

        except:
            logging_function(_MessageCollection.something_failed_while_saving(file_path = file_path))

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
        styler : Union[DataFrame, Styler] = self.__tt_summary.tt_styler
        hide_index : bool = self.__setting_bag.tt_hide_index

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler, hide_index = hide_index)
    def process_tts_by_month(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_month.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_month
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_month_styler
        content : str = self.__tt_summary.tts_by_month_sub_md
        id : TTID = TTID.TTSBYMONTH
        logging_function : Callable[[str], None] = lambda msg : self.__component_bag.tt_logger.log(msg)

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler)

        if OPTION.save in options:
            self.__save_and_log(id = id, content = content, logging_function = logging_function)
    def process_tts_by_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_year_styler

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler)
    def process_tts_by_year_month(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year_month.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year_month
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_year_month_styler

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler)
    def process_tts_by_year_month_spnv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year_month_spnv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year_month_spnv
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_year_month_spnv_styler
        formatters : dict = self.__setting_bag.tts_by_year_month_spnv_formatters

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler, formatters = formatters)
    def process_tts_by_year_spnv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_year_spnv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_year_spnv
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_year_spnv_styler
        formatters : dict = self.__setting_bag.tts_by_year_spnv_formatters

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler, formatters = formatters)
    def process_tts_by_spn(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_spn.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_spn
        df : DataFrame = self.__tt_summary.tts_by_spn_df
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_spn_styler
        formatters : dict = self.__setting_bag.tts_by_spn_formatters
        definitions_df : DataFrame = self.__tt_summary.definitions_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler, formatters = formatters)

        if OPTION.log in options:
            self.__component_bag.tt_logger.try_log_column_definitions(df = df, definitions = definitions_df)
    def process_tts_by_spn_spv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_spn_spv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_spn_spv
        df : DataFrame = self.__tt_summary.tts_by_spn_spv_df
        definitions_df : DataFrame = self.__tt_summary.definitions_df        

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df)

        if OPTION.log in options:
            self.__component_bag.tt_logger.try_log_column_definitions(df = df, definitions = definitions_df)
    def process_tts_by_hashtag(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_hashtag.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_hashtag
        df : DataFrame = self.__tt_summary.tts_by_hashtag_df
        formatters : dict = self.__setting_bag.tts_by_hashtag_formatters
        definitions_df : DataFrame = self.__tt_summary.definitions_df

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df, formatters = formatters)

        if OPTION.log in options:
            self.__component_bag.tt_logger.try_log_column_definitions(df = df, definitions = definitions_df)
    def process_tts_by_hashtag_year(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_hashtag_year.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_hashtag_year
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_hashtag_year_styler

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler)
    def process_tts_by_efs(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_efs.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_efs
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_efs_styler

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler)
    def process_tts_by_tr(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_by_tr.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_by_tr
        styler : Union[DataFrame, Styler] = self.__tt_summary.tts_by_tr_styler

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = styler)
    def process_tts_gantt_spnv(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_gantt_spnv.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_gantt_spnv
        df : DataFrame = self.__tt_summary.tts_gantt_spnv_df
        formatters : dict = self.__setting_bag.tts_gantt_spnv_formatters
        definitions_df : DataFrame = self.__tt_summary.definitions_df
        term : str = "tts_gantt_spnv"
        setting_names : list[str] = [ "tts_gantt_spnv_months", "tts_gantt_spnv_min_duration" ]

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df, formatters = formatters)

        if OPTION.plot in options:
            self.__tt_summary.tts_gantt_spnv_plot_function()

        if OPTION.log in options:
            self.__component_bag.tt_logger.try_log_term_definition(term = term, definitions = definitions_df)
            self.__component_bag.tt_logger.try_log_column_definitions(df = df, definitions = definitions_df)
            self.__component_bag.tt_logger.try_log_settings(setting_bag = self.__setting_bag, setting_names = setting_names)
    def process_tts_gantt_hseq(self) -> None:

        '''
            Performs all the actions listed in __setting_bag.options_tts_gantt_hseq.
            
            It raises an exception if the 'initialize' method has not been run yet.
        '''

        self.__validate_summary()

        options : list = self.__setting_bag.options_tts_gantt_hseq
        df : DataFrame = self.__tt_summary.tts_gantt_hseq_df
        formatters : dict = self.__setting_bag.tts_gantt_hseq_formatters
        definitions_df : DataFrame = self.__tt_summary.definitions_df   
        term : str = "tts_gantt_hseq"
        setting_names : list[str] = [ "tts_gantt_hseq_months", "tts_gantt_hseq_min_duration" ]

        if OPTION.display in options:
            self.__component_bag.displayer.display(obj = df, formatters = formatters)

        if OPTION.plot in options:
            self.__tt_summary.tts_gantt_hseq_plot_function()

        if OPTION.log in options:
            self.__component_bag.tt_logger.try_log_term_definition(term = term, definitions = definitions_df)
            self.__component_bag.tt_logger.try_log_column_definitions(df = df, definitions = definitions_df)
            self.__component_bag.tt_logger.try_log_settings(setting_bag = self.__setting_bag, setting_names = setting_names)
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

# MAIN
if __name__ == "__main__":
    pass