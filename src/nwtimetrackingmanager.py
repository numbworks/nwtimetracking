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
from pandas import Series
from numpy import float64

# LOCAL MODULES
# CLASSES
class YearlyTarget():
    
    '''Represents an amount of hours for a given year.'''

    year : str
    hours : int

    def __init__(self, year : str, hours : int):
        
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
    excel_null_value : str
    n_generic : int
    n_by_month : int
    show_sessions_df : bool
    show_tts_by_month_upd_df : bool
    show_cumulative_df : bool
    now : datetime

    def __init__(
        self,
        read_years : list[int],
        yearly_targets : list[YearlyTarget],
        excel_path : str,
        excel_books_skiprows : int,
        excel_books_nrows : int,
        excel_books_tabname : str,
        excel_null_value : str,
        n_generic : int,
        n_by_month : int,
        show_sessions_df : bool,
        show_tts_by_month_upd_df : bool,
        show_cumulative_df : bool,
        now : datetime
        ):

        self.read_years = read_years
        self.yearly_targets = yearly_targets
        self.excel_path = excel_path
        self.excel_books_skiprows = excel_books_skiprows
        self.excel_books_nrows = excel_books_nrows
        self.excel_books_tabname = excel_books_tabname
        self.excel_null_value = excel_null_value
        self.n_generic = n_generic
        self.n_by_month = n_by_month
        self.show_sessions_df = show_sessions_df
        self.show_tts_by_month_upd_df = show_tts_by_month_upd_df
        self.show_cumulative_df = show_cumulative_df
        self.now = now 

# FUNCTIONS
def get_default_time_tracking_path()-> str:

    '''
        "c:\...\nwtimetrackingmanager\data\Time Tracking.xlsx"
    '''
    
    path : str = os.getcwd().replace("src", "data")
    path = os.path.join(path, "Time Tracking.xlsx")

    return path


# MAIN
if __name__ == "__main__":
    pass