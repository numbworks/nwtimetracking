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
    remove_untagged_from_de : bool
    definitions : dict[str, str]
    show_sessions_df : bool
    show_tt_by_year_df : bool
    show_tt_by_year_month_df : bool
    show_tt_by_year_month_spnv_df : bool
    show_tt_by_year_spnv_df : bool
    show_tt_by_spn_df : bool
    show_tts_by_month_df : bool
    show_future_values_in_tts_by_month : bool    

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
        remove_untagged_from_de : bool,
        definitions : dict[str, str],
        show_sessions_df : bool,
        show_tt_by_year_df : bool,
        show_tt_by_year_month_df : bool,
        show_tt_by_year_month_spnv_df : bool,
        show_tt_by_year_spnv_df : bool,
        show_tt_by_spn_df : bool,
        show_tts_by_month_df : bool,
        show_future_values_in_tts_by_month : bool
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
        self.remove_untagged_from_de = remove_untagged_from_de
        self.definitions = definitions
        self.show_sessions_df = show_sessions_df
        self.show_tt_by_year_df = show_tt_by_year_df
        self.show_tt_by_year_month_df = show_tt_by_year_month_df
        self.show_tt_by_year_month_spnv_df = show_tt_by_year_month_spnv_df
        self.show_tt_by_year_spnv_df = show_tt_by_year_spnv_df
        self.show_tt_by_spn_df = show_tt_by_spn_df
        self.show_tts_by_month_df = show_tts_by_month_df
        self.show_future_values_in_tts_by_month = show_future_values_in_tts_by_month      

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
    column_names.append("Effort")               # [3], str
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
def is_yearly_target_met(effort : timedelta, yearly_target : timedelta) -> bool:

    if effort >= yearly_target:
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
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby([cn_year])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = cn_year).reset_index(drop = True)

    cn_yearly_target : str = "YearlyTarget"
    cn_target_diff : str = "TargetDiff"
    cn_is_target_met : str = "IsTargetMet"

    tt_df[cn_yearly_target] = tt_df[cn_year].apply(
        lambda x : get_yearly_target(yearly_targets = yearly_targets, year = x).hours)
    tt_df[cn_target_diff] = tt_df[cn_effort] - tt_df[cn_yearly_target]
    tt_df[cn_is_target_met] = tt_df.apply(
        lambda x : is_yearly_target_met(effort = x[cn_effort], yearly_target = x[cn_yearly_target]), axis = 1)    

    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))
    tt_df[cn_yearly_target] = tt_df[cn_yearly_target].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))
    tt_df[cn_target_diff] = tt_df[cn_target_diff].apply(lambda x : format_timedelta(td = x, add_plus_sign = True))

    return tt_df
def get_tt_by_year_month(sessions_df : DataFrame, years : list[int], yearly_targets : list[YearlyTarget]) -> DataFrame:

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
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)

    cn_yearly_total : str = "YearlyTotal"
    tt_df[cn_yearly_total] = tt_df[cn_effort].groupby(by = tt_df[cn_year]).cumsum()

    cn_yearly_target : str = "YearlyTarget"
    tt_df[cn_yearly_target] = tt_df[cn_year].apply(
        lambda x : get_yearly_target(yearly_targets = yearly_targets, year = x).hours)

    cn_to_target : str  = "ToTarget"
    tt_df[cn_to_target] = tt_df[cn_yearly_total] - tt_df[cn_yearly_target]    

    tt_df.drop(columns = [cn_yearly_target], axis = 1, inplace = True)
    
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))   
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
def get_raw_tt_by_year_month_spnv(sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:
    
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
    cn_effort : str = "Effort"
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_month, cn_project_name, cn_project_version])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = [cn_year, cn_month, cn_project_name, cn_project_version]).reset_index(drop = True)
  
    condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
    tt_df = tt_df.loc[condition_three]

    return tt_df
def get_raw_dme(sessions_df : DataFrame, years : list[int]) -> DataFrame:
    
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

    cn_month : str = "Month"
    cn_effort : str = "Effort"
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)
  
    cn_dme : str = "DME"
    tt_df.rename(columns = {cn_effort : cn_dme}, inplace = True)

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
    cn_effort : str = "Effort"
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_month])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = [cn_year, cn_month]).reset_index(drop = True)
  
    cn_tme : str = "TME"
    tt_df.rename(columns = {cn_effort : cn_tme}, inplace = True)

    return tt_df
def get_tt_by_year_month_spnv(sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

    '''
        [0] ...
        [1]

                Year	Month	ProjectName     	    ProjectVersion	Effort	DME	    %_DME	TME	    %_TME
            0	2023	4	    nwtraderaanalytics	    2.0.0	        09h 15m	09h 15m	100.00	19h 00m	48.68
            1	2023	6	    nwreadinglistmanager	1.0.0	        06h 45m	06h 45m	100.00	24h 45m	27.27
            ...
    '''

    spnv_df : DataFrame = get_raw_tt_by_year_month_spnv(sessions_df = sessions_df, years = years, software_project_names = software_project_names)
    dme_df : DataFrame = get_raw_dme(sessions_df = sessions_df, years = years)
    tme_df : DataFrame = get_raw_tme(sessions_df = sessions_df, years = years)

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

def get_raw_tt_by_year_spnv(sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:
    
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
    tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_name(descriptor = x))
    tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_version(descriptor = x))

    cn_effort : str = "Effort"
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year, cn_project_name, cn_project_version])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = [cn_year, cn_project_name, cn_project_version]).reset_index(drop = True)
  
    condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
    tt_df = tt_df.loc[condition_three]
    tt_df = tt_df.sort_values(by = [cn_year, cn_project_name, cn_project_version]).reset_index(drop = True)

    return tt_df
def get_raw_dye(sessions_df : DataFrame, years : list[int]) -> DataFrame:
    
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
    tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_name(descriptor = x))
    tt_df[cn_project_version] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_version(descriptor = x))

    cn_effort : str = "Effort"
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = [cn_year]).reset_index(drop = True)
  
    cn_dye : str = "DYE"
    tt_df.rename(columns = {cn_effort : cn_dye}, inplace = True)

    return tt_df
def get_raw_tye(sessions_df : DataFrame, years : list[int]) -> DataFrame:
    
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
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_year])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = [cn_year]).reset_index(drop = True)
  
    cn_tye : str = "TYE"
    tt_df.rename(columns = {cn_effort : cn_tye}, inplace = True)

    return tt_df
def get_tt_by_year_spnv(sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame:

    '''
        [0] ...
        [1]

                Year	ProjectName     	    ProjectVersion	Effort	DYE	    %_DYE	TYE	    %_TYE
            0	2023	nwtraderaanalytics	    2.0.0	        09h 15m	09h 15m	100.00	19h 00m	48.68
            1	2023	nwreadinglistmanager	1.0.0	        06h 45m	06h 45m	100.00	24h 45m	27.27
            ...
    '''

    spnv_df : DataFrame = get_raw_tt_by_year_spnv(sessions_df = sessions_df, years = years, software_project_names = software_project_names)
    dye_df : DataFrame = get_raw_dye(sessions_df = sessions_df, years = years)
    tye_df : DataFrame = get_raw_tye(sessions_df = sessions_df, years = years)

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
    tt_df[cn_percentage_dye] = tt_df.apply(lambda x : calculate_percentage(part = x[cn_effort], whole = x[cn_dye]), axis = 1)        

    tt_df = pd.merge(
        left = tt_df, 
        right = tye_df, 
        how = "inner", 
        left_on = [cn_year], 
        right_on = [cn_year]
        )   
   
    cn_tye : str = "TYE"
    cn_percentage_tye : str = "%_TYE"
    tt_df[cn_percentage_tye] = tt_df.apply(lambda x : calculate_percentage(part = x[cn_effort], whole = x[cn_tye]), axis = 1)    

    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))   
    tt_df[cn_dye] = tt_df[cn_dye].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))
    tt_df[cn_tye] = tt_df[cn_tye].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))

    return tt_df

def get_raw_tt_by_spn(sessions_df : DataFrame, years : list[int], software_project_names : list[str]) -> DataFrame: 
    
    '''
            ProjectName	        Effort
        0	nwtraderaanalytics	0 days 09:15:00
        1	NW.AutoProffLibrary	0 days 09:30:00
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
    tt_df[cn_project_name] = tt_df[cn_descriptor].apply(lambda x : extract_software_project_name(descriptor = x))

    cn_effort : str = "Effort"
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    tt_df = tt_df.groupby(by = [cn_project_name])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    tt_df = tt_df.sort_values(by = [cn_project_name]).reset_index(drop = True)

    condition_three : Series = (tt_df[cn_project_name].isin(values = software_project_names))
    tt_df = tt_df.loc[condition_three] 
    tt_df = tt_df.sort_values(by = [cn_effort], ascending = [False]).reset_index(drop = True)

    return tt_df
def get_raw_de(sessions_df : DataFrame, years : list[int]) -> timedelta:
    
    '''3 days 21:15:00'''

    tt_df : DataFrame = sessions_df.copy(deep = True)

    cn_year : str = "Year"
    cn_is_software_project : str = "IsSoftwareProject"
    condition_one : Series = (sessions_df[cn_year].isin(values = years))
    condition_two : Series = (sessions_df[cn_is_software_project] == True)
    tt_df = tt_df.loc[condition_one & condition_two]

    cn_effort : str = "Effort"
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    summarized : timedelta = tt_df[cn_effort].sum()

    return summarized
def get_raw_te(sessions_df : DataFrame, years : list[int], remove_untagged : bool) -> timedelta:

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
    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    summarized : timedelta = tt_df[cn_effort].sum()

    return summarized    
def get_tt_by_spn(sessions_df : DataFrame, years : list[int], software_project_names : list[str], remove_untagged : bool) -> DataFrame:

    '''
            ProjectName	            Effort	    DE	%_DE	TE	        %_TE
        0	nwreadinglistmanager	66h 30m	93h 15m	71.31	4475h 15m	1.49
        1	nwtraderaanalytics	    09h 15m	93h 15m	9.92	4475h 15m	0.21
        ...

        With remove_untagged = True:

            ProjectName	            Effort	DE	    %_DE	TE	        %_TE
        0	nwreadinglistmanager	66h 30m	93h 15m	71.31	174h 15m	38.16
        1	nwtraderaanalytics	    09h 15m	93h 15m	9.92	174h 15m	5.31
        ...
    '''

    tt_df : DataFrame = get_raw_tt_by_spn(sessions_df = sessions_df, years = years, software_project_names = software_project_names)
    de : timedelta = get_raw_de(sessions_df = sessions_df, years = years)
    te : timedelta = get_raw_te(sessions_df = sessions_df, years = years, remove_untagged = remove_untagged)    

    cn_de : str = "DE"
    tt_df[cn_de] = de

    cn_effort : str = "Effort"
    cn_percentage_de : str = "%_DE"
    tt_df[cn_percentage_de] = tt_df.apply(lambda x : calculate_percentage(part = x[cn_effort], whole = x[cn_de]), axis = 1)      

    cn_te : str = "TE"
    tt_df[cn_te] = te

    cn_percentage_te : str = "%_TE"
    tt_df[cn_percentage_te] = tt_df.apply(lambda x : calculate_percentage(part = x[cn_effort], whole = x[cn_te]), axis = 1)     

    tt_df[cn_effort] = tt_df[cn_effort].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))   
    tt_df[cn_de] = tt_df[cn_de].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))
    tt_df[cn_te] = tt_df[cn_te].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))

    return tt_df

def try_print_definitions(df : DataFrame, definitions : dict[str, str]) -> None:
    
    '''
	    "DE"    => print("DE: Development Effort")
        "Year"  => do nothing
	'''
    
    for column_name in df.columns:
        if definitions.get(column_name) != None:
            print(f"{column_name}: {definitions[column_name]}")

def enforce_raw_ttm_schema(df : DataFrame) -> DataFrame:

    '''Ensures that the columns of the provided dataframe have the expected data types.'''

    cn_month : str = "Month" 

    df = df.astype({cn_month: int})
    # can't enforce the year column as "timedelta"

    return df 
def get_default_raw_ttm(year : int) -> DataFrame:

    '''
        default_df:

                Month	2019
            0	1	    0 days
            ...
    '''

    cn_month : str = "Month"
    td : timedelta = convert_string_to_timedelta(td_str = "0h 00m")

    default_df : DataFrame = pd.DataFrame(
        {
            f"{cn_month}": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            f"{str(year)}": [td, td, td, td, td, td, td, td, td, td, td, td]
        },
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    )

    default_df = enforce_raw_ttm_schema(df = default_df)

    return default_df
def try_complete_raw_ttm(ttm_df : DataFrame, year : int) -> DataFrame:

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

        default_df : DataFrame = get_default_raw_ttm(year = year)
        missing_df : DataFrame = default_df.loc[~default_df[cn_month].astype(str).isin(ttm_df[cn_month].astype(str))]

        completed_df : DataFrame = pd.concat([ttm_df, missing_df], ignore_index = True)
        completed_df = completed_df.sort_values(by = cn_month, ascending = [True])
        completed_df = completed_df.reset_index(drop = True)

        return completed_df

    return ttm_df
def get_raw_ttm(sessions_df : DataFrame, year : int) -> DataFrame:
    
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

    ttm_df[cn_effort] = ttm_df[cn_effort].apply(lambda x : convert_string_to_timedelta(td_str = x))
    ttm_df[str(year)] = ttm_df[cn_effort]
    cn_effort = str(year)    

    ttm_df = ttm_df.groupby([cn_month])[cn_effort].sum().sort_values(ascending = [False]).reset_index(name = cn_effort)
    ttm_df = ttm_df.sort_values(by = cn_month).reset_index(drop = True)

    ttm_df = try_complete_raw_ttm(ttm_df = ttm_df, year = year)
    ttm_df = enforce_raw_ttm_schema(df = ttm_df)

    return ttm_df

def get_trend_by_timedelta(td_1 : timedelta, td_2 : timedelta) -> str:

    '''
        0h 30m, 1h 00m => "↑"
        1h 00m, 0h 30m => "↓"
        0, 0 => "="
    '''
    trend : str = None

    if td_1 < td_2:
        trend = "↑"
    elif td_1 > td_2:
        trend = "↓"
    else:
        trend = "="

    return trend
def expand_raw_ttm_by_year(sessions_df : DataFrame, years : list, tts_by_month_df : DataFrame, i : int, add_trend : bool) -> DataFrame:

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
    ttm_df : DataFrame = get_raw_ttm(sessions_df = sessions_df, year = years[i])

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
        
        expansion_df[cn_trend] = expansion_df.apply(lambda x : get_trend_by_timedelta(td_1 = x[cn_trend_1], td_2 = x[cn_trend_2]), axis = 1) 

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
def try_consolidate_trend_column_name(column_name : str) -> str:

    '''
        "2016"  => "2016"
        "↕1"    => "↕"
    '''

    cn_trend : str = "↕"

    if column_name.startswith(cn_trend):
        return cn_trend
    
    return column_name
def get_tts_by_month(sessions_df : DataFrame, years : list) -> DataFrame:

    '''
            Month	2016	↕   2017	    ↕	2018    ...
        0	1	    0h 00m	↑	13h 00m		↓	0h 00m
        1	2	    0h 00m	↑	1h 00m	    ↓	0h 00m
        ...
    '''

    tts_by_month_df : DataFrame = None
    for i in range(len(years)):

        if i == 0:
            tts_by_month_df = get_raw_ttm(sessions_df = sessions_df, year = years[i])
        else:
            tts_by_month_df = expand_raw_ttm_by_year(
                sessions_df = sessions_df, 
                years = years, 
                tts_by_month_df = tts_by_month_df, 
                i = i, 
                add_trend = True)
            
    for year in years:
        tts_by_month_df[str(year)] = tts_by_month_df[str(year)].apply(lambda x : format_timedelta(td = x, add_plus_sign = False))

    tts_by_month_df.rename(columns = (lambda x : try_consolidate_trend_column_name(column_name = x)), inplace = True)

    return tts_by_month_df

def update_future_months_to_empty(tts_by_month_df : DataFrame, now : datetime) -> DataFrame:

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

# MAIN
if __name__ == "__main__":
    pass