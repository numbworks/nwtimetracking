'''
A collection of components to handle "Time Tracking.xlsx".

Alias: nwttm
'''

# GLOBAL MODULES
import os
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

    read_years : list[int]
    yearly_targets : list[YearlyTarget]
    excel_path : str
    excel_books_skiprows : int
    excel_books_nrows : int
    excel_books_tabname : str
    n_generic : int
    n_by_month : int
    now : datetime
    show_sessions_df : bool

    def __init__(
        self,
        read_years : list[int],
        yearly_targets : list[YearlyTarget],
        excel_path : str,
        excel_books_skiprows : int,
        excel_books_nrows : int,
        excel_books_tabname : str,
        n_generic : int,
        n_by_month : int,
        now : datetime,
        show_sessions_df : bool
        ):

        self.read_years = read_years
        self.yearly_targets = yearly_targets
        self.excel_path = excel_path
        self.excel_books_skiprows = excel_books_skiprows
        self.excel_books_nrows = excel_books_nrows
        self.excel_books_tabname = excel_books_tabname
        self.n_generic = n_generic
        self.n_by_month = n_by_month
        self.now = now         
        self.show_sessions_df = show_sessions_df

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
    column_names.append("Description")          # [5], str
    column_names.append("ProjectName")          # [6], str
    column_names.append("ProjectVersion")       # [7], str
    column_names.append("IsReleaseDate")        # [8], str - not bool because it can be Yes/No/null
    column_names.append("Year")                 # [9], int
    column_names.append("Month")                # [10], int

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
    dataset_df = dataset_df.astype({column_names[7]: str})
    dataset_df = dataset_df.astype({column_names[8]: str})
    dataset_df = dataset_df.astype({column_names[9]: int})
    dataset_df = dataset_df.astype({column_names[10]: int})

    return dataset_df

def convert_string_to_timedelta(td_str : str) -> timedelta:

    '''"5h 30m" => 5:30:00'''

    td : timedelta = pd.Timedelta(value = td_str).to_pytimedelta()

    return td
def add_timedeltas(td_1 : timedelta, td_2 : timedelta) -> timedelta:

    '''Performs td_1 + td_2. '''

    td : timedelta = td_1 + td_2

    return td
def substract_timedeltas(td_1 : timedelta, td_2 : timedelta) -> timedelta:

    '''Performs td_1 - td_2. '''

    td : timedelta = td_1 - td_2

    return td


# MAIN
if __name__ == "__main__":
    pass