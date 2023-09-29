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
    software_project_names : list[str]
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
        software_project_names : list[str],
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
        self.software_project_names = software_project_names  
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
def format_timedelta(td : timedelta, add_plus_sign : bool) -> str:

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

    tt_df : DataFrame = sessions_df.copy(deep = True)

    cn_year : str = "Year"
    condition : Series = (sessions_df[cn_year].isin(values = years))
    tt_df = tt_df.loc[condition]

    cn_duration : str = "Duration"
    tt_df[cn_duration] = tt_df[cn_duration].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby([cn_year])[cn_duration].sum().sort_values(ascending = [False]).reset_index(name = cn_duration)
    tt_df = tt_df.sort_values(by = cn_year).reset_index(drop = True)

    cn_yearly_target : str = "YearlyTarget"
    cn_target_diff : str = "TargetDiff"
    cn_is_target_met : str = "IsTargetMet"

    tt_df[cn_yearly_target] = tt_df[cn_year].apply(
        lambda x : get_yearly_target(yearly_targets = yearly_targets, year = x).hours)
    tt_df[cn_target_diff] = tt_df[cn_duration] - tt_df[cn_yearly_target]
    tt_df[cn_is_target_met] = tt_df.apply(
        lambda x : is_yearly_target_met(duration = x[cn_duration], yearly_target = x[cn_yearly_target]), axis = 1)    

    tt_df[cn_duration] = tt_df[cn_duration].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))
    tt_df[cn_yearly_target] = tt_df[cn_yearly_target].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))
    tt_df[cn_target_diff] = tt_df[cn_target_diff].apply(lambda x : format_timedelta(td = x, add_plus_sign = True))

    return tt_df
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

    tt_df : DataFrame = sessions_df.copy(deep = True)

    cn_year : str = "Year"
    condition : Series = (sessions_df[cn_year].isin(values = years))
    tt_df = tt_df.loc[condition]

    cn_month : str = "Month"
    cn_duration : str = "Duration"   
    tt_df[cn_duration] = tt_df[cn_duration].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_duration].sum().sort_values(ascending = [False]).reset_index(name = cn_duration)
    tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)

    cn_yearly_total : str = "YearlyTotal"
    tt_df[cn_yearly_total] = tt_df[cn_duration].groupby(by = tt_df[cn_year]).cumsum()

    cn_yearly_target : str = "YearlyTarget"
    tt_df[cn_yearly_target] = tt_df[cn_year].apply(
        lambda x : get_yearly_target(yearly_targets = yearly_targets, year = x).hours)

    cn_to_target : str  = "ToTarget"
    tt_df[cn_to_target] = tt_df[cn_yearly_total] - tt_df[cn_yearly_target]    

    tt_df.drop(columns = [cn_yearly_target], axis = 1, inplace = True)
    
    tt_df[cn_duration] = tt_df[cn_duration].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))   
    tt_df[cn_yearly_total] = tt_df[cn_yearly_total].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))
    tt_df[cn_to_target] = tt_df[cn_to_target].apply(lambda x : format_timedelta(td = x, add_plus_sign = True))

    return tt_df

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
def calculate_percentage(part : float, whole : float, rounding_digits : int = 2) -> float:

    '''Calculates a percentage.'''

    prct : float = None

    if part == 0:
        prct = 0
    else:
        prct = (100 * part) / whole

    prct = round(number = prct, ndigits = rounding_digits)

    return prct
def get_raw_tt_by_year_month_sp(sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:
    
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
    tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_name(descriptor = x))
    tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_version(descriptor = x))

    cn_month : str = "Month"
    cn_duration : str = "Duration"
    tt_df[cn_duration] = tt_df[cn_duration].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_month, cn_project_name, cn_project_version])[cn_duration].sum().sort_values(ascending = [False]).reset_index(name = cn_duration)
    tt_df = tt_df.sort_values(by = [cn_year, cn_month, cn_project_name, cn_project_version]).reset_index(drop = True)
  
    cn_effort : str = "Effort"
    tt_df.rename(columns = {cn_duration : cn_effort}, inplace = True)

    condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
    tt_df = tt_df.loc[condition_three]

    return tt_df
def get_raw_dme(sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:
    
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
    tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_name(descriptor = x))
    tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_version(descriptor = x))

    condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
    tt_df = tt_df.loc[condition_three]

    cn_month : str = "Month"
    cn_duration : str = "Duration"
    tt_df[cn_duration] = tt_df[cn_duration].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_duration].sum().sort_values(ascending = [False]).reset_index(name = cn_duration)
    tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)
  
    cn_dme : str = "DME"
    tt_df.rename(columns = {cn_duration : cn_dme}, inplace = True)

    return tt_df
def get_raw_tme(sessions_df : DataFrame, years : list[int]) -> DataFrame:
    
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
    cn_duration : str = "Duration"
    tt_df[cn_duration] = tt_df[cn_duration].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_duration].sum().sort_values(ascending = [False]).reset_index(name = cn_duration)
    tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)
  
    cn_dme : str = "TME"
    tt_df.rename(columns = {cn_duration : cn_dme}, inplace = True)

    return tt_df
def get_tt_by_year_month_sp(sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

    '''
        [0]

                Year	Month	ProjectName	            ProjectVersion	Effort	        DME	            %_DME	TME	            %_TME
            0	2023	4	    nwtraderaanalytics	    2.0.0	        0 days 09:15:00	0 days 09:15:00	100.00	0 days 19:00:00	48.68
            1	2023	6	    nwreadinglistmanager	1.0.0	        0 days 06:45:00	0 days 06:45:00	100.00	1 days 00:45:00	27.27
            ...

        [1]

                Year	Month	ProjectName     	    ProjectVersion	Effort	DME	    %_DME	TME	    %_TME
            0	2023	4	    nwtraderaanalytics	    2.0.0	        09h 15m	09h 15m	100.00	19h 00m	48.68
            1	2023	6	    nwreadinglistmanager	1.0.0	        06h 45m	06h 45m	100.00	24h 45m	27.27
            ...
    '''

    sp_df : DataFrame = get_raw_tt_by_year_month_sp(sessions_df = sessions_df, years = years, software_project_names = software_project_names)
    dme_df : DataFrame = get_raw_dme(sessions_df = sessions_df, years = years, software_project_names = software_project_names)
    tme_df : DataFrame = get_raw_tme(sessions_df = sessions_df, years = years)

    cn_year : str = "Year"
    cn_month : str = "Month"

    tt_df : DataFrame = pd.merge(
        left = sp_df, 
        right = dme_df, 
        how = "inner", 
        left_on = [cn_year, cn_month], 
        right_on = [cn_year, cn_month]
        )
    
    cn_effort : str = "Effort"
    cn_dme : str = "DME"
    cn_percentage_dme : str = "%_DME"
    tt_df[cn_percentage_dme] = tt_df.apply(lambda x : calculate_percentage(part = x[cn_effort], whole = x[cn_dme]), axis = 1)        

    tt_df = pd.merge(
        left = tt_df, 
        right = tme_df, 
        how = "inner", 
        left_on = [cn_year, cn_month], 
        right_on = [cn_year, cn_month]
        )   
   
    cn_tme : str = "TME"
    cn_percentage_tme : str = "%_TME"
    tt_df[cn_percentage_tme] = tt_df.apply(lambda x : calculate_percentage(part = x[cn_effort], whole = x[cn_tme]), axis = 1)    

    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))   
    tt_df[cn_dme] = tt_df[cn_dme].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))
    tt_df[cn_tme] = tt_df[cn_tme].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))

    return tt_df

# MAIN
if __name__ == "__main__":
    pass