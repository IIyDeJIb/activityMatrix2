import pandas as pd
import numpy as np
from datetime import timedelta
from xWellFailInfo import xWellFailInfo
from reliability.Fitters import Weibull_plot

actMatFull = pd.read_csv('actMatFull_0.csv', index_col='Date', parse_dates = ['Date'])


data = xWellFailInfo(actMatFull['606'])['TTFadj'].dropna().values.astype('int')
Weibull_plot(failures=data)