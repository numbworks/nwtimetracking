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
 
# FUNCTIONS

# MAIN
if __name__ == "__main__":
    pass