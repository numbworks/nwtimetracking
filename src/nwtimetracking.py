'''
A collection of components to handle "Time Tracking.xlsx".

Alias: nwtt
'''

# GLOBAL MODULES
import numpy as np
import os
import pandas as pd
import re
import openpyxl
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from pandas import DataFrame
from pandas import Series
from typing import Optional

# LOCAL MODULES
# CONSTANTS
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

# DTOs
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

# CLASSES
class SettingBag():

    '''Represents a collection of settings.'''

    years : list[int]
    yearly_targets : list[YearlyTarget]
    excel_path : str
    excel_books_nrows : int
    software_project_names : list[str]
    software_project_names_by_spv : list[str]
    tt_by_year_hashtag_years : list[int]

    show_sessions_df : bool
    show_tt_by_year_df : bool
    show_tt_by_year_month_df : bool
    show_tt_by_year_month_spnv_df : bool
    show_tt_by_year_spnv_df : bool
    show_tt_by_spn_df : bool
    show_tt_by_spn_spv_df : bool
    show_tt_by_year_hashtag : bool
    show_tt_by_hashtag : bool
    show_tts_by_month_df : bool
    show_effort_status_df : bool
    show_time_ranges_df : bool
    excel_books_skiprows : int
    excel_books_tabname : str
    n_generic : int
    n_by_month : int
    now : datetime
    remove_untagged_from_de : bool
    definitions : dict[str, str]
    effort_status_n : int
    effort_status_is_correct : bool
    tts_by_month_update_future_values_to_empty : bool
    time_ranges_unknown_id : str
    time_ranges_top_n : int
    time_ranges_remove_unknown_id : bool
    time_ranges_filter_by_top_n : bool

    def __init__(
        self, 
        years : list[int],
        yearly_targets : list[YearlyTarget],
        excel_path : str,
        excel_books_nrows : int,
        software_project_names : list[str],
        software_project_names_by_spv : list[str],
        tt_by_year_hashtag_years : list[int],

        show_sessions_df : bool = False,
        show_tt_by_year_df : bool = True,
        show_tt_by_year_month_df : bool = True,
        show_tt_by_year_month_spnv_df : bool = False,
        show_tt_by_year_spnv_df : bool = False,
        show_tt_by_spn_df : bool = True,
        show_tt_by_spn_spv_df : bool = True,
        show_tt_by_year_hashtag : bool = True,
        show_tt_by_hashtag : bool = True,
        show_tts_by_month_df : bool = True,
        show_effort_status_df : bool = True,
        show_time_ranges_df : bool = True,
        excel_books_skiprows : int = 0,
        excel_books_tabname : str = "Sessions",
        n_generic : int = 5,
        n_by_month : int = 12,
        now : datetime = datetime.now(),
        remove_untagged_from_de : bool = True,
        definitions : dict[str, str] = { 
            "DME": "Development Monthly Effort",
            "TME": "Total Monthly Effort",
            "DYE": "Development Yearly Effort",
            "TYE": "Total Yearly Effort",
            "DE": "Development Effort",
            "TE": "Total Effort"
        },
        effort_status_n : int = 25,
        effort_status_is_correct : bool = False,
        tts_by_month_update_future_values_to_empty : bool = True,
        time_ranges_unknown_id : str = "Unknown",
        time_ranges_top_n : int = 5,
        time_ranges_remove_unknown_id : bool = True,
        time_ranges_filter_by_top_n : bool  = True       
        ) -> None:
        
        self.years = years
        self.yearly_targets = yearly_targets
        self.excel_path = excel_path
        self.excel_books_nrows = excel_books_nrows
        self.software_project_names = software_project_names
        self.software_project_names_by_spv = software_project_names_by_spv
        self.tt_by_year_hashtag_years = tt_by_year_hashtag_years

        self.show_sessions_df = show_sessions_df
        self.show_tt_by_year_df = show_tt_by_year_df
        self.show_tt_by_year_month_df = show_tt_by_year_month_df
        self.show_tt_by_year_month_spnv_df = show_tt_by_year_month_spnv_df
        self.show_tt_by_year_spnv_df = show_tt_by_year_spnv_df
        self.show_tt_by_spn_df = show_tt_by_spn_df
        self.show_tt_by_spn_spv_df = show_tt_by_spn_spv_df
        self.show_tt_by_year_hashtag = show_tt_by_year_hashtag
        self.show_tt_by_hashtag = show_tt_by_hashtag
        self.show_tts_by_month_df = show_tts_by_month_df
        self.show_effort_status_df = show_effort_status_df
        self.show_time_ranges_df = show_time_ranges_df
        self.excel_books_skiprows = excel_books_skiprows
        self.excel_books_tabname = excel_books_tabname
        self.n_generic = n_generic
        self.n_by_month = n_by_month
        self.now = now
        self.remove_untagged_from_de = remove_untagged_from_de
        self.definitions = definitions
        self.effort_status_n = effort_status_n
        self.effort_status_is_correct = effort_status_is_correct
        self.tts_by_month_update_future_values_to_empty = tts_by_month_update_future_values_to_empty
        self.time_ranges_unknown_id = time_ranges_unknown_id
        self.time_ranges_top_n = time_ranges_top_n
        self.time_ranges_remove_unknown_id = time_ranges_remove_unknown_id
        self.time_ranges_filter_by_top_n = time_ranges_filter_by_top_n
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
            YearlyTarget(year = 2024, hours = timedelta(hours = 250))
        ]

        return yearly_targets    
class TimeTrackingManager():

    '''Collects all the logic related to the management of "Time Tracking.xlsx".'''

    def __enforce_dataframe_definition_for_sessions_df(self, sessions_df : DataFrame) -> DataFrame:

        '''Enforces definition for the provided dataframe.'''

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

        sessions_df = sessions_df[column_names]
    
        sessions_df[column_names[0]] = pd.to_datetime(sessions_df[column_names[0]], format="%Y-%m-%d") 
        sessions_df[column_names[0]] = sessions_df[column_names[0]].apply(lambda x: x.date())

        sessions_df = sessions_df.astype({column_names[1]: str})
        sessions_df = sessions_df.astype({column_names[2]: str})
        sessions_df = sessions_df.astype({column_names[3]: str})
        sessions_df = sessions_df.astype({column_names[4]: str})
        sessions_df = sessions_df.astype({column_names[5]: str})
        sessions_df = sessions_df.astype({column_names[6]: bool})
        sessions_df = sessions_df.astype({column_names[7]: bool})
        sessions_df = sessions_df.astype({column_names[8]: int})
        sessions_df = sessions_df.astype({column_names[9]: int})

        sessions_df[column_names[1]] = sessions_df[column_names[1]].replace('nan', '')
        sessions_df[column_names[2]] = sessions_df[column_names[2]].replace('nan', '')
        sessions_df[column_names[5]] = sessions_df[column_names[5]].replace('nan', '')

        return sessions_df    
    def __enforce_dataframe_definition_for_raw_ttm_df(self, df : DataFrame) -> DataFrame:

        '''Ensures that the columns of the provided dataframe have the expected data types.'''

        cn_month : str = "Month" 

        df = df.astype({cn_month: int})
        # can't enforce the year column as "timedelta"

        return df 
    def __convert_string_to_timedelta(self, td_str : str) -> timedelta:

        '''"5h 30m" => 5:30:00'''

        td : timedelta = pd.Timedelta(value = td_str).to_pytimedelta()

        return td
    def __get_yearly_target(self, yearly_targets : list[YearlyTarget], year : int) -> Optional[YearlyTarget]:

        '''Retrieves the YearlyTarget object for the provided "year" or None.'''

        for yearly_target in yearly_targets:
            if yearly_target.year == year:
                return yearly_target
            
        return None
    def __is_yearly_target_met(self, effort : timedelta, yearly_target : timedelta) -> bool:

        if effort >= yearly_target:
            return True

        return False
    def __format_timedelta(self, td : timedelta, add_plus_sign : bool) -> str:

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
    def __extract_software_project_name(self, descriptor : str) -> str:

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
    def __extract_software_project_version(self, descriptor : str) -> str: 

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
    def __calculate_percentage(self, part : float, whole : float, rounding_digits : int = 2) -> float:

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
    def __get_raw_tt_by_year_month_spnv(self, sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:
        
        '''
                Year	Month	ProjectName	        ProjectVersion	Effort
            0	2023	4	    nwtraderaanalytics	2.0.0	        0 days 09:15:00
            1	2023	5	    NW.AutoProffLibrary	1.0.0	        0 days 09:30:00
            ...
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        cn_is_software_project : str = "IsSoftwareProject"
        condition_one : Series = (sessions_df[cn_year].isin(values = years))
        condition_two : Series = (sessions_df[cn_is_software_project] == True)
        tt_df = tt_df.loc[condition_one & condition_two]

        cn_descriptor : str = "Descriptor"
        cn_project_name : str = "ProjectName"
        cn_project_version : str = "ProjectVersion"
        tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_name(descriptor = x))
        tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_version(descriptor = x))

        cn_month : str = "Month"
        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_year, cn_month, cn_project_name, cn_project_version])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_year, cn_month, cn_project_name, cn_project_version]).reset_index(drop = True)
    
        condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
        tt_df = tt_df.loc[condition_three]

        return tt_df
    def __get_raw_dme(self, sessions_df : DataFrame, years : list[int]) -> DataFrame:
        
        '''
                Year	Month	DME
            0	2023	4	    0 days 09:15:00
            1	2023	6	    0 days 06:45:00
            ...

            DME = DevelopmentMonthlyEffort
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        cn_is_software_project : str = "IsSoftwareProject"
        condition_one : Series = (sessions_df[cn_year].isin(values = years))
        condition_two : Series = (sessions_df[cn_is_software_project] == True)
        tt_df = tt_df.loc[condition_one & condition_two]

        cn_descriptor : str = "Descriptor"
        cn_project_name : str = "ProjectName"
        cn_project_version : str = "ProjectVersion"
        tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_name(descriptor = x))
        tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_version(descriptor = x))

        cn_month : str = "Month"
        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)
    
        cn_dme : str = "DME"
        tt_df.rename(columns = {cn_effort : cn_dme}, inplace = True)

        return tt_df
    def __get_raw_tme(self, sessions_df : DataFrame, years : list[int]) -> DataFrame:
        
        '''
                Year	Month	TME
            0	2023	4	    0 days 09:15:00
            1	2023	6	    0 days 06:45:00
            ...

            TME = TotalMonthlyEffort
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        condition : Series = (sessions_df[cn_year].isin(values = years))
        tt_df = tt_df.loc[condition]

        cn_month : str = "Month"
        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)
    
        cn_tme : str = "TME"
        tt_df.rename(columns = {cn_effort : cn_tme}, inplace = True)

        return tt_df
    def __get_raw_tt_by_year_spnv(self, sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:
        
        '''
                Year	ProjectName	        ProjectVersion	Effort
            0	2023	nwtraderaanalytics	2.0.0	        0 days 09:15:00
            1	2023	NW.AutoProffLibrary	1.0.0	        0 days 09:30:00
            ...
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        cn_is_software_project : str = "IsSoftwareProject"
        condition_one : Series = (sessions_df[cn_year].isin(values = years))
        condition_two : Series = (sessions_df[cn_is_software_project] == True)
        tt_df = tt_df.loc[condition_one & condition_two]

        cn_descriptor : str = "Descriptor"
        cn_project_name : str = "ProjectName"
        cn_project_version : str = "ProjectVersion"
        tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_name(descriptor = x))
        tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_version(descriptor = x))

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_year, cn_project_name, cn_project_version])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_year, cn_project_name, cn_project_version]).reset_index(drop = True)
    
        condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
        tt_df = tt_df.loc[condition_three]
        tt_df = tt_df.sort_values(by = [cn_year, cn_project_name, cn_project_version]).reset_index(drop = True)

        return tt_df
    def __get_raw_dye(self, sessions_df : DataFrame, years : list[int]) -> DataFrame:
        
        '''
                Year	DYE
            0	2023	0 days 09:15:00
            1	2023	0 days 06:45:00
            ...

            DYE = DevelopmentYearlyEffort
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        cn_is_software_project : str = "IsSoftwareProject"
        condition_one : Series = (sessions_df[cn_year].isin(values = years))
        condition_two : Series = (sessions_df[cn_is_software_project] == True)
        tt_df = tt_df.loc[condition_one & condition_two]

        cn_descriptor : str = "Descriptor"
        cn_project_name : str = "ProjectName"
        cn_project_version : str = "ProjectVersion"
        tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_name(descriptor = x))
        tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_version(descriptor = x))

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_year])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_year]).reset_index(drop = True)
    
        cn_dye : str = "DYE"
        tt_df.rename(columns = {cn_effort : cn_dye}, inplace = True)

        return tt_df
    def __get_raw_tye(self, sessions_df : DataFrame, years : list[int]) -> DataFrame:
        
        '''
                Year	TYE
            0	2023	0 days 09:15:00
            1	2023	0 days 06:45:00
            ...

            TYE = TotalYearlyEffort
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        condition : Series = (sessions_df[cn_year].isin(values = years))
        tt_df = tt_df.loc[condition]

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_year])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_year]).reset_index(drop = True)
    
        cn_tye : str = "TYE"
        tt_df.rename(columns = {cn_effort : cn_tye}, inplace = True)

        return tt_df
    def __get_raw_tt_by_spn(self, sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame: 
        
        '''
                Hashtag	ProjectName	            Effort
            0	#python	nwtraderaanalytics	    72h 00m
            1	#python	nwreadinglistmanager	66h 30m
            2	#python	nwtimetrackingmanager	18h 45m
            3	#csharp	NW.WIDJobs	            430h 00m
            ...
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        cn_is_software_project : str = "IsSoftwareProject"
        condition_one : Series = (sessions_df[cn_year].isin(values = years))
        condition_two : Series = (sessions_df[cn_is_software_project] == True)
        tt_df = tt_df.loc[condition_one & condition_two]

        cn_descriptor : str = "Descriptor"
        cn_project_name : str = "ProjectName"
        tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_name(descriptor = x))

        cn_effort : str = "Effort"
        cn_hashtag : str = "Hashtag"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_project_name, cn_hashtag])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_project_name]).reset_index(drop = True)

        condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
        tt_df = tt_df.loc[condition_three] 
        tt_df = tt_df.sort_values(by = [cn_hashtag, cn_effort], ascending = [False, False]).reset_index(drop = True)

        tt_df = tt_df[[cn_hashtag, cn_project_name, cn_effort]]

        return tt_df
    def __get_raw_de(self, sessions_df : DataFrame, years : list[int]) -> timedelta:
        
        '''3 days 21:15:00'''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        cn_is_software_project : str = "IsSoftwareProject"
        condition_one : Series = (sessions_df[cn_year].isin(values = years))
        condition_two : Series = (sessions_df[cn_is_software_project] == True)
        tt_df = tt_df.loc[condition_one & condition_two]

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        summarized : timedelta = tt_df[cn_effort].sum()

        return summarized
    def __get_raw_te(self, sessions_df : DataFrame, years : list[int], remove_untagged : bool) -> timedelta:

        '''186 days 11:15:00'''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        condition_one : Series = (sessions_df[cn_year].isin(values = years))
        tt_df = tt_df.loc[condition_one]

        if remove_untagged:
            cn_hashtag : str = "Hashtag"
            condition_two : Series = (sessions_df[cn_hashtag] != "#untagged")
            tt_df = tt_df.loc[condition_two]

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        summarized : timedelta = tt_df[cn_effort].sum()

        return summarized    
    def __get_raw_tt_by_spn_spv(self, sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

        '''
                ProjectName	                ProjectVersion	Effort
            0	NW.MarkdownTables	        1.0.0	        0 days 15:15:00
            1	NW.MarkdownTables	        1.0.1	        0 days 02:30:00
            2	NW.NGramTextClassification	1.0.0	        3 days 02:15:00
            ...
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        cn_is_software_project : str = "IsSoftwareProject"
        condition_one : Series = (sessions_df[cn_year].isin(values = years))
        condition_two : Series = (sessions_df[cn_is_software_project] == True)
        tt_df = tt_df.loc[condition_one & condition_two]

        cn_descriptor : str = "Descriptor"
        cn_project_name : str = "ProjectName"
        cn_project_version : str = "ProjectVersion"
        tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_name(descriptor = x))
        tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : self.__extract_software_project_version(descriptor = x))

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_project_name, cn_project_version])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_project_name, cn_project_version]).reset_index(drop = True)

        condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
        tt_df = tt_df.loc[condition_three]
        tt_df = tt_df.sort_values(by = [cn_project_name, cn_project_version]).reset_index(drop = True)

        return tt_df
    def __get_default_raw_ttm(self, year : int) -> DataFrame:

        '''
            default_df:

                    Month	2019
                0	1	    0 days
                ...
        '''

        cn_month : str = "Month"
        td : timedelta = self.__convert_string_to_timedelta(td_str = "0h 00m")

        default_df : DataFrame = pd.DataFrame(
            {
                f"{cn_month}": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
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

        cn_month : str = "Month"

        if ttm_df[cn_month].count() != 12:

            default_df : DataFrame = self.__get_default_raw_ttm(year = year)
            missing_df : DataFrame = default_df.loc[~default_df[cn_month].astype(str).isin(ttm_df[cn_month].astype(str))]

            completed_df : DataFrame = pd.concat([ttm_df, missing_df], ignore_index = True)
            completed_df = completed_df.sort_values(by = cn_month, ascending = [True])
            completed_df = completed_df.reset_index(drop = True)

            return completed_df

        return ttm_df
    def __get_raw_ttm(self, sessions_df : DataFrame, year : int) -> DataFrame:
        
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

        cn_year : str = "Year"
        cn_month : str = "Month" 
        cn_effort : str = "Effort"

        ttm_df : DataFrame = sessions_df.copy(deep=True)
        ttm_df = ttm_df[[cn_year, cn_month, cn_effort]]

        condition : Series = (sessions_df[cn_year] == year)
        ttm_df = ttm_df.loc[condition]

        ttm_df[cn_effort] = ttm_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        ttm_df[str(year)] = ttm_df[cn_effort]
        cn_effort = str(year)    

        ttm_df = ttm_df.groupby([cn_month])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        ttm_df = ttm_df.sort_values(by = cn_month).reset_index(drop = True)

        ttm_df = self.__try_complete_raw_ttm(ttm_df = ttm_df, year = year)
        ttm_df = self.__enforce_dataframe_definition_for_raw_ttm_df(df = ttm_df)

        return ttm_df
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
    def __expand_raw_ttm_by_year(self, sessions_df : DataFrame, years : list, tts_by_month_df : DataFrame, i : int, add_trend : bool) -> DataFrame:

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
        ttm_df : DataFrame = self.__get_raw_ttm(sessions_df = sessions_df, year = years[i])

        cn_month : str = "Month"      
        expansion_df = pd.merge(
            left = actual_df, 
            right = ttm_df, 
            how = "inner", 
            left_on = cn_month, 
            right_on = cn_month)

        if add_trend == True:

            cn_trend : str = f"↕{i}"
            cn_trend_1 : str = str(years[i-1])   # for ex. "2016"
            cn_trend_2 : str = str(years[i])     # for ex. "2017"
            
            expansion_df[cn_trend] = expansion_df.apply(lambda x : self.__get_trend_by_timedelta(td_1 = x[cn_trend_1], td_2 = x[cn_trend_2]), axis = 1) 

            new_column_names : list = [cn_month, cn_trend_1, cn_trend, cn_trend_2]   # for ex. ["Month", "2016", "↕", "2017"]
            expansion_df = expansion_df.reindex(columns = new_column_names)

            shared_columns : list = [cn_month, str(years[i-1])] # ["Month", "2016"]
            actual_df = pd.merge(
                left = actual_df, 
                right = expansion_df, 
                how = "inner", 
                left_on = shared_columns, 
                right_on = shared_columns)

        else:
            actual_df = expansion_df

        return actual_df
    def __try_consolidate_trend_column_name(self, column_name : str) -> str:

        '''
            "2016"  => "2016"
            "↕1"    => "↕"
        '''

        cn_trend : str = "↕"

        if column_name.startswith(cn_trend):
            return cn_trend
        
        return column_name
    def __create_effort_status_for_none_values(self, idx : int, effort_str : str) -> EffortStatus:

        actual_str : str = effort_str
        actual_td : timedelta = self.__convert_string_to_timedelta(td_str = effort_str)
        is_correct : bool = True
        message : str = "''start_time' and/or 'end_time' are empty, 'effort' can't be verified. We assume that it's correct."

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
            message = message
            )    

        return effort_status
    def __create_time_object(self, time : str) -> datetime:

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
    def __create_effort_status(self, idx : int, start_time_str : str, end_time_str : str, effort_str : str) -> EffortStatus:

        '''
            start_time_str, end_time_str:
                - Expects time values in the "%H:%M" format - for ex. 20:00.

            is_correct:
                start_time_str = "20:00", end_time_str = "00:00", effort_str = "4h 00m" => True
                start_time_str = "20:00", end_time_str = "00:00", effort_str = "5h 00m" => False
        '''

        try:

            if len(start_time_str) == 0 or len(end_time_str) == 0:
                return self.__create_effort_status_for_none_values(idx = idx, effort_str = effort_str)

            start_time_dt : datetime = self.__create_time_object(time = start_time_str)
            end_time_dt : datetime = self.__create_time_object(time = end_time_str)

            actual_str : str = effort_str
            actual_td : timedelta = self.__convert_string_to_timedelta(td_str = effort_str)

            expected_td : timedelta = (end_time_dt - start_time_dt)
            expected_str : str = self.__format_timedelta(td = expected_td, add_plus_sign = False)
            
            is_correct : bool = True
            if actual_td != expected_td:
                is_correct = False
            
            message : str = "The effort is correct."
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

            message : str = _MessageCollection.effort_status_not_possible_to_create(
                idx = idx, start_time_str = start_time_str, end_time_str = end_time_str, effort_str = effort_str)

            raise ValueError(message)
    def __create_time_range_id(self, start_time : str, end_time : str, unknown_id : str) -> str:
            
            '''
                Creates a unique time range identifier out of the provided parameters.
                If parameters are empty, it returns unknown_id.
            '''

            time_range_id : str = f"{start_time}-{end_time}"

            if len(start_time) == 0 or len(end_time) == 0:
                time_range_id = unknown_id

            return time_range_id
    def __get_raw_tt_by_year_hashtag(self, sessions_df : DataFrame, years : list[int]) -> DataFrame:

        '''
                Year	Hashtag	        Effort
            0   2023	#csharp	        0 days 15:15:00
            1   2023	#maintenance	0 days 02:30:00
            2   2023	#powershell	    3 days 02:15:00
            ...   
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        condition : Series = (sessions_df[cn_year].isin(values = years))
        tt_df = tt_df.loc[condition]

        cn_hashtag: str = "Hashtag"
        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_year, cn_hashtag])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_hashtag, cn_year]).reset_index(drop = True)

        return tt_df
    def __get_raw_tt_by_hashtag(self, sessions_df : DataFrame) -> DataFrame:

        '''
                Hashtag	        Effort          Effort%
            0   #csharp	        0 days 15:15:00 56.49
            1   #maintenance	0 days 02:30:00 23.97
            2   #powershell	    3 days 02:15:00 6.43
            ...   
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_hashtag: str = "Hashtag"
        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_hashtag])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)

        cn_effort_prc : str = "Effort%"
        summarized : float = tt_df[cn_effort].sum()
        tt_df[cn_effort_prc] = tt_df.apply(lambda x : self.__calculate_percentage(part = x[cn_effort], whole = summarized), axis = 1)     

        return tt_df

    def get_sessions_dataset(self, setting_bag : SettingBag) -> DataFrame:
        
        '''
            Retrieves the content of the "Sessions" tab and returns it as a Dataframe. 
        '''

        sessions_df : DataFrame = pd.read_excel(
            io = setting_bag.excel_path, 	
            skiprows = setting_bag.excel_books_skiprows,
            nrows = setting_bag.excel_books_nrows,
            sheet_name = setting_bag.excel_books_tabname, 
            engine = 'openpyxl'
            )      
        sessions_df = self.__enforce_dataframe_definition_for_sessions_df(sessions_df = sessions_df)

        return sessions_df
    def get_tt_by_year(self, sessions_df : DataFrame, years : list[int], yearly_targets : list[YearlyTarget]) -> DataFrame:

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

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        condition : Series = (sessions_df[cn_year].isin(values = years))
        tt_df = tt_df.loc[condition]

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby([cn_year])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = cn_year).reset_index(drop = True)

        cn_yearly_target : str = "YearlyTarget"
        cn_target_diff : str = "TargetDiff"
        cn_is_target_met : str = "IsTargetMet"

        tt_df[cn_yearly_target] = tt_df[cn_year].apply(
            lambda x : self.__get_yearly_target(yearly_targets = yearly_targets, year = x).hours)
        tt_df[cn_target_diff] = tt_df[cn_effort] - tt_df[cn_yearly_target]
        tt_df[cn_is_target_met] = tt_df.apply(
            lambda x : self.__is_yearly_target_met(effort = x[cn_effort], yearly_target = x[cn_yearly_target]), axis = 1)    

        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))
        tt_df[cn_yearly_target] = tt_df[cn_yearly_target].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))
        tt_df[cn_target_diff] = tt_df[cn_target_diff].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = True))

        return tt_df
    def get_tt_by_year_month(self, sessions_df : DataFrame, years : list[int], yearly_targets : list[YearlyTarget]) -> DataFrame:

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
        '''

        tt_df : DataFrame = sessions_df.copy(deep = True)

        cn_year : str = "Year"
        condition : Series = (sessions_df[cn_year].isin(values = years))
        tt_df = tt_df.loc[condition]

        cn_month : str = "Month"
        cn_effort : str = "Effort"   
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__convert_string_to_timedelta(td_str = x))
        tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
        tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)

        cn_yearly_total : str = "YearlyTotal"
        tt_df[cn_yearly_total] = tt_df[cn_effort].groupby(by = tt_df[cn_year]).cumsum()

        cn_yearly_target : str = "YearlyTarget"
        tt_df[cn_yearly_target] = tt_df[cn_year].apply(
            lambda x : self.__get_yearly_target(yearly_targets = yearly_targets, year = x).hours)

        cn_to_target : str  = "ToTarget"
        tt_df[cn_to_target] = tt_df[cn_yearly_total] - tt_df[cn_yearly_target]    

        tt_df.drop(columns = [cn_yearly_target], axis = 1, inplace = True)
        
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))   
        tt_df[cn_yearly_total] = tt_df[cn_yearly_total].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))
        tt_df[cn_to_target] = tt_df[cn_to_target].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = True))

        return tt_df
    def get_tt_by_year_month_spnv(self, sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

        '''
            [0] ...
            [1]

                    Year	Month	ProjectName     	    ProjectVersion	Effort	DME	    %_DME	TME	    %_TME
                0	2023	4	    nwtraderaanalytics	    2.0.0	        09h 15m	09h 15m	100.00	19h 00m	48.68
                1	2023	6	    nwreadinglistmanager	1.0.0	        06h 45m	06h 45m	100.00	24h 45m	27.27
                ...
        '''

        spnv_df : DataFrame = self.__get_raw_tt_by_year_month_spnv(sessions_df = sessions_df, years = years, software_project_names = software_project_names)
        dme_df : DataFrame = self.__get_raw_dme(sessions_df = sessions_df, years = years)
        tme_df : DataFrame = self.__get_raw_tme(sessions_df = sessions_df, years = years)

        cn_year : str = "Year"
        cn_month : str = "Month"

        tt_df : DataFrame = pd.merge(
            left = spnv_df, 
            right = dme_df, 
            how = "inner", 
            left_on = [cn_year, cn_month], 
            right_on = [cn_year, cn_month]
            )
        
        cn_effort : str = "Effort"
        cn_dme : str = "DME"
        cn_percentage_dme : str = "%_DME"
        tt_df[cn_percentage_dme] = tt_df.apply(lambda x : self.__calculate_percentage(part = x[cn_effort], whole = x[cn_dme]), axis = 1)        

        tt_df = pd.merge(
            left = tt_df, 
            right = tme_df, 
            how = "inner", 
            left_on = [cn_year, cn_month], 
            right_on = [cn_year, cn_month]
            )   
    
        cn_tme : str = "TME"
        cn_percentage_tme : str = "%_TME"
        tt_df[cn_percentage_tme] = tt_df.apply(lambda x : self.__calculate_percentage(part = x[cn_effort], whole = x[cn_tme]), axis = 1)    

        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))   
        tt_df[cn_dme] = tt_df[cn_dme].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))
        tt_df[cn_tme] = tt_df[cn_tme].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))

        return tt_df
    def get_tt_by_year_spnv(self, sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

        '''
            [0] ...
            [1]

                    Year	ProjectName     	    ProjectVersion	Effort	DYE	    %_DYE	TYE	    %_TYE
                0	2023	nwtraderaanalytics	    2.0.0	        09h 15m	09h 15m	100.00	19h 00m	48.68
                1	2023	nwreadinglistmanager	1.0.0	        06h 45m	06h 45m	100.00	24h 45m	27.27
                ...
        '''

        spnv_df : DataFrame = self.__get_raw_tt_by_year_spnv(sessions_df = sessions_df, years = years, software_project_names = software_project_names)
        dye_df : DataFrame = self.__get_raw_dye(sessions_df = sessions_df, years = years)
        tye_df : DataFrame = self.__get_raw_tye(sessions_df = sessions_df, years = years)

        cn_year : str = "Year"

        tt_df : DataFrame = pd.merge(
            left = spnv_df, 
            right = dye_df, 
            how = "inner", 
            left_on = [cn_year], 
            right_on = [cn_year]
            )
        
        cn_effort : str = "Effort"
        cn_dye : str = "DYE"
        cn_percentage_dye : str = "%_DYE"
        tt_df[cn_percentage_dye] = tt_df.apply(lambda x : self.__calculate_percentage(part = x[cn_effort], whole = x[cn_dye]), axis = 1)        

        tt_df = pd.merge(
            left = tt_df, 
            right = tye_df, 
            how = "inner", 
            left_on = [cn_year], 
            right_on = [cn_year]
            )   
    
        cn_tye : str = "TYE"
        cn_percentage_tye : str = "%_TYE"
        tt_df[cn_percentage_tye] = tt_df.apply(lambda x : self.__calculate_percentage(part = x[cn_effort], whole = x[cn_tye]), axis = 1)    

        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))   
        tt_df[cn_dye] = tt_df[cn_dye].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))
        tt_df[cn_tye] = tt_df[cn_tye].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))

        return tt_df
    def get_tt_by_spn(self, sessions_df : DataFrame, years : list[int], software_project_names : list[str], remove_untagged : bool) -> DataFrame:

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

        tt_df : DataFrame = self.__get_raw_tt_by_spn(sessions_df = sessions_df, years = years, software_project_names = software_project_names)
        de : timedelta = self.__get_raw_de(sessions_df = sessions_df, years = years)
        te : timedelta = self.__get_raw_te(sessions_df = sessions_df, years = years, remove_untagged = remove_untagged)    

        cn_de : str = "DE"
        tt_df[cn_de] = de

        cn_effort : str = "Effort"
        cn_percentage_de : str = "%_DE"
        tt_df[cn_percentage_de] = tt_df.apply(lambda x : self.__calculate_percentage(part = x[cn_effort], whole = x[cn_de]), axis = 1)      

        cn_te : str = "TE"
        tt_df[cn_te] = te

        cn_percentage_te : str = "%_TE"
        tt_df[cn_percentage_te] = tt_df.apply(lambda x : self.__calculate_percentage(part = x[cn_effort], whole = x[cn_te]), axis = 1)     

        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))   
        tt_df[cn_de] = tt_df[cn_de].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))
        tt_df[cn_te] = tt_df[cn_te].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))

        return tt_df
    def get_tt_by_spn_spv(self, sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

        '''
                ProjectName	                ProjectVersion	Effort
            0	NW.MarkdownTables	        1.0.0	        15h 15m
            1	NW.MarkdownTables	        1.0.1	        02h 30m
            2	NW.NGramTextClassification	1.0.0	        74h 15m
            ...    
        '''

        tt_df : DataFrame = self.__get_raw_tt_by_spn_spv(sessions_df = sessions_df, years = years, software_project_names = software_project_names)

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))   

        return tt_df
    def get_tts_by_month(self, sessions_df : DataFrame, years : list) -> DataFrame:

        '''
                Month	2016	↕   2017	    ↕	2018    ...
            0	1	    0h 00m	↑	13h 00m		↓	0h 00m
            1	2	    0h 00m	↑	1h 00m	    ↓	0h 00m
            ...
        '''

        tts_by_month_df : DataFrame = None
        for i in range(len(years)):

            if i == 0:
                tts_by_month_df = self.__get_raw_ttm(sessions_df = sessions_df, year = years[i])
            else:
                tts_by_month_df = self.__expand_raw_ttm_by_year(
                    sessions_df = sessions_df, 
                    years = years, 
                    tts_by_month_df = tts_by_month_df, 
                    i = i, 
                    add_trend = True)
                
        for year in years:
            tts_by_month_df[str(year)] = tts_by_month_df[str(year)].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))

        tts_by_month_df.rename(columns = (lambda x : self.__try_consolidate_trend_column_name(column_name = x)), inplace = True)

        return tts_by_month_df
    def get_tt_by_year_hashtag(self, sessions_df : DataFrame, years : list[int]) -> DataFrame:

        '''
                Year	Hashtag	        Effort
            0   2023	#csharp	        67h 30m
            1   2023	#maintenance	51h 00m
            2   2023	#powershell	    04h 30m 
            ...    
        '''
    
        tt_df : DataFrame = self.__get_raw_tt_by_year_hashtag(sessions_df = sessions_df, years = years)

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))   

        return tt_df
    def get_tt_by_hashtag(self, sessions_df : DataFrame) -> DataFrame:

        '''
                Hashtag	        Effort  Effort%
            0   #csharp	        67h 30m 56.49
            1   #maintenance	51h 00m 23.97
            2   #powershell	    04h 30m 6.43
            ...    
        '''
    
        tt_df : DataFrame = self.__get_raw_tt_by_hashtag(sessions_df = sessions_df)

        cn_effort : str = "Effort"
        tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : self.__format_timedelta(td = x, add_plus_sign = False))   

        return tt_df

    def try_print_definitions(self, df : DataFrame, definitions : dict[str, str]) -> None:
        
        '''
            "DE"    => print("DE: Development Effort")
            "Year"  => do nothing
        '''
        
        for column_name in df.columns:
            if definitions.get(column_name) != None:
                print(f"{column_name}: {definitions[column_name]}")
    def update_future_months_to_empty(self, tts_by_month_df : DataFrame, now : datetime) -> DataFrame:

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
        cn_month : str = "Month"
        new_value : str = ""

        condition : Series = (tts_by_month_upd_df[cn_month] > now_month)
        tts_by_month_upd_df[cn_year] = np.where(condition, new_value, tts_by_month_upd_df[cn_year])
            
        idx_year : int = tts_by_month_upd_df.columns.get_loc(cn_year)
        idx_trend : int = (idx_year - 1)
        tts_by_month_upd_df.iloc[:, idx_trend] = np.where(condition, new_value, tts_by_month_upd_df.iloc[:, idx_trend])

        return tts_by_month_upd_df
    def add_effort_status(self, sessions_df : DataFrame) -> DataFrame:

        '''
            StartTime	EndTime	Effort	ES_IsCorrect	ES_Expected	ES_Message
            21:00       23:00   1h 00m  False           2h 00m      ...
            ...        
        '''

        es_df : DataFrame = sessions_df.copy(deep = True)
        
        cn_start_time : str = "StartTime"
        cn_end_time : str = "EndTime"
        cn_effort : str = "Effort"
        cn_effort_status : str = "EffortStatus"

        es_df[cn_effort_status] = es_df.apply(
            lambda x : self.__create_effort_status(
                idx = x.name, 
                start_time_str = x[cn_start_time],
                end_time_str = x[cn_end_time],
                effort_str = x[cn_effort]),
                axis = 1)
        
        cn_es_is_correct : str = "ES_IsCorrect"
        cn_es_expected : str = "ES_Expected"
        cn_es_message : str = "ES_Message"

        es_df[cn_es_is_correct] = es_df[cn_effort_status].apply(lambda x : x.is_correct)
        es_df[cn_es_expected] = es_df[cn_effort_status].apply(lambda x : x.expected_str)
        es_df[cn_es_message] = es_df[cn_effort_status].apply(lambda x : x.message)

        es_df = es_df[[cn_start_time, cn_end_time, cn_effort, cn_es_is_correct, cn_es_expected, cn_es_message]]

        return es_df
    def filter_by_is_correct(self, es_df : DataFrame, is_correct : bool) -> DataFrame:

        '''Returns a DataFrame that contains only rows that match the provided is_correct.'''

        filtered_df : DataFrame = es_df.copy(deep = True)

        cn_es_is_correct : str = "ES_IsCorrect"

        condition : Series = (filtered_df[cn_es_is_correct] == is_correct)
        filtered_df = es_df.loc[condition]

        return filtered_df
    def create_time_ranges_df(self, sessions_df : DataFrame, unknown_id : str) -> DataFrame:

            '''
                    TimeRangeId	Occurrences
                0	Unknown		44
                1	18:00-20:00	19
                2	08:00-08:30	16
                ...
            '''

            time_ranges_df : DataFrame = sessions_df.copy(deep = True)
            
            cn_start_time : str = "StartTime"
            cn_end_time : str = "EndTime"
            cn_time_range_id : str = "TimeRangeId"

            time_ranges_df = time_ranges_df[[cn_start_time, cn_end_time]]
            time_ranges_df[cn_time_range_id] = time_ranges_df.apply(
                lambda x : self.__create_time_range_id(
                    start_time = x[cn_start_time], 
                    end_time = x[cn_end_time], 
                    unknown_id = unknown_id), axis = 1)

            cn_occurrences : str = "Occurrences"

            time_ranges_df = time_ranges_df[[cn_time_range_id]].groupby(by = [cn_time_range_id], as_index=False).agg(
                    count = pd.NamedAgg(column = cn_time_range_id, aggfunc = "count"))
            time_ranges_df.rename(columns={"count" : cn_occurrences}, inplace = True)
            time_ranges_df = time_ranges_df.sort_values(by = [cn_occurrences], ascending = False).reset_index(drop = True)
            
            return time_ranges_df
    def remove_unknown_id(self, time_ranges_df : DataFrame, unknown_id : str) -> DataFrame:

        '''Removes the provided uknown_id from the "TimeRangeId" column of the provided DataFrame.'''

        cn_time_range_id : str = "TimeRangeId"

        condition : Series = (time_ranges_df[cn_time_range_id] != unknown_id)
        time_ranges_df = time_ranges_df.loc[condition]	
        time_ranges_df.reset_index(drop = True, inplace = True)

        return time_ranges_df
    def filter_by_top_n_occurrences(self, time_ranges_df : DataFrame, n : int, ascending : bool = False) -> DataFrame:

        '''Returns only the top n rows by "Occurrences" of the provided DataFrame.'''

        cn_occurrences : str = "Occurrences"

        time_ranges_df.sort_values(by = cn_occurrences, ascending = [ascending], inplace = True)
        time_ranges_df = time_ranges_df.iloc[0:n]
        time_ranges_df.reset_index(drop = True, inplace = True)

        return time_ranges_df

# MAIN
if __name__ == "__main__":
    pass