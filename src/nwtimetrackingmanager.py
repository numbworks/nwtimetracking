'''
A collection of components to handle "Time Tracking.xlsx".

Alias: nwttm
'''

# GLOBAL MODULES
import os
import re
import pandas as pd
import numpy as np
import openpyxl
import copy
from pandas import DataFrame
from datetime import datetime
from datetime import date
from datetime import timedelta
from pandas import Series
from numpy import float64

# LOCAL MODULES
# CLASSES
class YearlyTarget():
    
    '''Represents an amount of hours for a given year.'''

    year : int
    hours : timedelta

    def __init__(self, year : int, hours : timedelta):
        
        self.year = year
        self.hours = hours
class SettingCollection():

    '''Represents a collection of settings.'''

    years : list[int]
    yearly_targets : list[YearlyTarget]
    excel_path : str
    excel_books_skiprows : int
    excel_books_nrows : int
    excel_books_tabname : str
    n_generic : int
    n_by_month : int
    now : datetime
    show_sessions_df : bool
    show_tt_by_year_df : bool
    show_tt_by_year_month_df : bool

    def __init__(
        self,
        years : list[int],
        yearly_targets : list[YearlyTarget],
        excel_path : str,
        excel_books_skiprows : int,
        excel_books_nrows : int,
        excel_books_tabname : str,
        n_generic : int,
        n_by_month : int,
        now : datetime,
        show_sessions_df : bool,
        show_tt_by_year_df : bool,
        show_tt_by_year_month_df : bool
        ):

        self.years = years
        self.yearly_targets = yearly_targets
        self.excel_path = excel_path
        self.excel_books_skiprows = excel_books_skiprows
        self.excel_books_nrows = excel_books_nrows
        self.excel_books_tabname = excel_books_tabname
        self.n_generic = n_generic
        self.n_by_month = n_by_month
        self.now = now         
        self.show_sessions_df = show_sessions_df
        self.show_tt_by_year_df = show_tt_by_year_df
        self.show_tt_by_year_month_df = show_tt_by_year_month_df

# FUNCTIONS
def get_default_time_tracking_path()-> str:

    '''
        "c:\...\nwtimetrackingmanager\data\Time Tracking.xlsx"
    '''
    
    path : str = os.getcwd().replace("src", "data")
    path = os.path.join(path, "Time Tracking.xlsx")

    return path
def get_sessions_dataset(setting_collection : SettingCollection) -> DataFrame:
    
    '''
        Retrieves the content of the "Sessions" tab and returns it as a Dataframe. 
    '''

    column_names : list[str] = []
    column_names.append("Date")                 # [0], date
    column_names.append("StartTime")            # [1], str
    column_names.append("EndTime")              # [2], str
    column_names.append("Duration")             # [3], str
    column_names.append("Hashtag")              # [4], str
    column_names.append("Descriptor")           # [5], str
    column_names.append("IsSoftwareProject")    # [6], bool
    column_names.append("IsReleaseDay")         # [7], bool
    column_names.append("Year")                 # [8], int
    column_names.append("Month")                # [9], int

    dataset_df = pd.read_excel(
	    io = setting_collection.excel_path, 	
        skiprows = setting_collection.excel_books_skiprows,
        nrows = setting_collection.excel_books_nrows,
	    sheet_name = setting_collection.excel_books_tabname, 
        engine = 'openpyxl'
        )
    
    dataset_df = dataset_df[column_names]
  
    dataset_df[column_names[0]] = pd.to_datetime(dataset_df[column_names[0]], format="%Y-%m-%d") 
    dataset_df[column_names[0]] = dataset_df[column_names[0]].apply(lambda x: x.date())

    dataset_df = dataset_df.astype({column_names[1]: str})
    dataset_df = dataset_df.astype({column_names[2]: str})
    dataset_df = dataset_df.astype({column_names[3]: str})
    dataset_df = dataset_df.astype({column_names[4]: str})
    dataset_df = dataset_df.astype({column_names[5]: str})
    dataset_df = dataset_df.astype({column_names[6]: bool})
    dataset_df = dataset_df.astype({column_names[7]: bool})
    dataset_df = dataset_df.astype({column_names[8]: int})
    dataset_df = dataset_df.astype({column_names[9]: int})

    return dataset_df

def convert_string_to_timedelta(td_str : str) -> timedelta:

    '''"5h 30m" => 5:30:00'''

    td : timedelta = pd.Timedelta(value = td_str).to_pytimedelta()

    return td
def get_yearly_target(yearly_targets : list[YearlyTarget], year : int) -> YearlyTarget:

    '''Retrieves the YearlyTarget object for the provided "year" or None.'''

    for yearly_target in yearly_targets:
        if yearly_target.year == year:
            return yearly_target
        
    return None
def is_yearly_target_met(duration : timedelta, yearly_target : timedelta) -> bool:

    if duration >= yearly_target:
        return True

    return False
def format_timedelta(td : timedelta, is_target_diff : bool) -> str:

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

    if (is_target_diff == True and td.days >= 0):
        formatted = f"+{formatted}"

    return formatted
def get_tt_by_year(sessions_df : DataFrame, years : list[int], yearly_targets : list[YearlyTarget]) -> DataFrame:

    '''
        [0]
                Date	    StartTime	EndTime	Duration	Hashtag	    Descriptor IsSoftwareProject    IsReleaseDay	Year	Month
            0	2015-10-31	nan	        nan	    8h 00m	    #untagged	nan	       nan	                nan	            2015	10
            1	2015-11-30	nan	        nan	    10h 00m	    #untagged	nan	       nan	                nan	            2015	11            
            ...

        [1]
                Year	Duration
            0	2016	25 days 15:15:00

        [2] 
                Year	Duration	        YearlyTarget        TargetDiff	    IsTargetMet	
            0	2015	0 days 18:00:00	    0 days 00:00:00	    0 days 18:00:00 True
            1	2016	25 days 15:15:00	20 days 20:00:00	4 days 19:15:00 True
            ...

        [3]
                Year	Duration	YearlyTarget	TargetDiff	IsTargetMet
            0	2015	18h 00m	    00h 00m	        +18h 00m	True
            1	2016	615h 15m	500h 00m	    +115h 15m	True
            ...
    '''

    cn_year : str = "Year"
    cn_duration : str = "Duration"

    tt_by_year_df : DataFrame = sessions_df.copy(deep = True)

    condition : Series = (sessions_df[cn_year].isin(values = years))
    tt_by_year_df = tt_by_year_df.loc[condition]

    tt_by_year_df[cn_duration] = tt_by_year_df[cn_duration].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_by_year_df : DataFrame = tt_by_year_df.groupby([cn_year])[cn_duration].sum().sort_values(ascending = [False]).reset_index(name = cn_duration)
    tt_by_year_df = tt_by_year_df.sort_values(by = cn_year).reset_index(drop = True)

    cn_yearly_target : str = "YearlyTarget"
    cn_target_diff : str = "TargetDiff"
    cn_is_target_met : str = "IsTargetMet"

    tt_by_year_df[cn_yearly_target] = tt_by_year_df[cn_year].apply(
        lambda x : get_yearly_target(yearly_targets = yearly_targets, year = x).hours)
    tt_by_year_df[cn_target_diff] = tt_by_year_df[cn_duration] - tt_by_year_df[cn_yearly_target]
    tt_by_year_df[cn_is_target_met] = tt_by_year_df.apply(
        lambda x : is_yearly_target_met(duration = x[cn_duration], yearly_target = x[cn_yearly_target]), axis = 1)    

    tt_by_year_df[cn_duration] = tt_by_year_df[cn_duration].apply(lambda x : format_timedelta(td = x, is_target_diff = False))
    tt_by_year_df[cn_yearly_target] = tt_by_year_df[cn_yearly_target].apply(lambda x : format_timedelta(td = x, is_target_diff = False))
    tt_by_year_df[cn_target_diff] = tt_by_year_df[cn_target_diff].apply(lambda x : format_timedelta(td = x, is_target_diff = True))

    return tt_by_year_df
def get_tt_by_year_month(sessions_df : DataFrame, years : list[int], yearly_targets : list[YearlyTarget]) -> DataFrame:

    '''
        [0]

                    Year	Month	Duration
            0	    2015	11	    0 days 10:00:00
            1	    2015	10	    0 days 08:00:00
            ...

        [1]

                    Year	Month	Duration	    YearlyTotal
            0	    2015	10	    0 days 08:00:00	0 days 08:00:00
            1	    2015	11	    0 days 10:00:00	0 days 18:00:00
            ...

        [2] 

                Year	Month	Duration	    YearlyTotal	    YearlyTarget
            0	2015	10	    0 days 08:00:00	0 days 08:00:00	0 days 00:00:00
            1	2015	11	    0 days 10:00:00	0 days 18:00:00	0 days 00:00:00
            ...
        
        [3]

                Year	Month	Duration	    YearlyTotal	    YearlyTarget	ToTarget
            0	2015	10	    0 days 08:00:00	0 days 08:00:00	0 days 00:00:00	0 days 08:00:00
            1	2015	11	    0 days 10:00:00	0 days 18:00:00	0 days 00:00:00	0 days 10:00:00        
            ...

        [4] 
                Year	Month	Duration	YearlyTotal	ToTarget
            ...
            87	2023	1	    06h 00m	    06h 00m	    -394h 00m
            88	2023	2	    23h 00m	    29h 00m	    -371h 00m
            89	2023	3	    50h 15m	    79h 15m	    -321h 15m   
            ...
    '''

    cn_year : str = "Year"
    cn_month : str = "Month"
    cn_duration : str = "Duration"    

    tt_by_year_month_df : DataFrame = sessions_df.copy(deep = True)

    condition : Series = (sessions_df[cn_year].isin(values = years))
    tt_by_year_month_df = tt_by_year_month_df.loc[condition]

    tt_by_year_month_df[cn_duration] = tt_by_year_month_df[cn_duration].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_by_year_month_df : DataFrame = tt_by_year_month_df.groupby(by = [cn_year, cn_month])[cn_duration].sum().sort_values(ascending = [False]).reset_index(name = cn_duration)
    tt_by_year_month_df = tt_by_year_month_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)

    cn_yearly_total : str = "YearlyTotal"
    tt_by_year_month_df[cn_yearly_total] = tt_by_year_month_df[cn_duration].groupby(by = tt_by_year_month_df[cn_year]).cumsum()

    cn_yearly_target : str = "YearlyTarget"
    tt_by_year_month_df[cn_yearly_target] = tt_by_year_month_df[cn_year].apply(
        lambda x : get_yearly_target(yearly_targets = yearly_targets, year = x).hours)

    cn_to_target : str  = "ToTarget"
    tt_by_year_month_df[cn_to_target] = tt_by_year_month_df[cn_yearly_total] - tt_by_year_month_df[cn_yearly_target]    

    tt_by_year_month_df.drop(columns = [cn_yearly_target], axis = 1, inplace = True)
    
    tt_by_year_month_df[cn_duration] = tt_by_year_month_df[cn_duration].apply(lambda x : format_timedelta(td = x, is_target_diff = False))   
    tt_by_year_month_df[cn_yearly_total] = tt_by_year_month_df[cn_yearly_total].apply(lambda x : format_timedelta(td = x, is_target_diff = False))
    tt_by_year_month_df[cn_to_target] = tt_by_year_month_df[cn_to_target].apply(lambda x : format_timedelta(td = x, is_target_diff = True))

    return tt_by_year_month_df

def extract_software_project_name(descriptor : str) -> str:

    '''
        "NW.AutoProffLibrary v1.0.0"    => "NW.AutoProffLibrary"
        "nwreadinglistmanager v1.5.0"   => "nwreadinglistmanager"

        Returns "ERROR" is parsing goes wrong.
    '''

    pattern : str = r"^[a-zA-Z\.]{2,}"
    matches : list = re.findall(pattern = pattern, string = descriptor, flags = re.MULTILINE)

    if len(matches) == 1:
        return matches[0]

    return "ERROR"
def extract_software_project_version(descriptor : str) -> str: 

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


# MAIN
if __name__ == "__main__":
    pass