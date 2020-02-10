import pandas as pd
import numpy as np
from datetime import timedelta
from xWellFailInfo import xWellFailInfo
from reliability.Fitters import Fit_Everything, Fit_Weibull_3P

# Import the activity matrix
actMatFull = pd.read_csv('actMatFull_0.csv', index_col=0, parse_dates=True)
actMatFull.columns = actMatFull.columns.astype('int')

# Initialize the failInfo DataFrame
failInfoDf = xWellFailInfo(actMatFull[actMatFull.columns[0]])
failInfoDf.insert(2, 'Well_ID', actMatFull.columns[0])

for wellID in actMatFull.columns[1:]:
    failInfoDf = failInfoDf.append(xWellFailInfo(actMatFull[wellID]).assign(Well_ID=wellID), sort=False)


# Weibull_plot(failures=data)
# out = Fit_Weibull_2P(failures=data)
#
# out = Fit_Weibull_3P(failures=failInfoDf['TTFadj'].dropna().values)

# Number of failures and datapoints by well
failInfoByWell = failInfoDf.groupby('Well_ID').count()[['failDate', 'TTF']]
failInfoByWell.index = failInfoByWell.index.astype('int')
failInfoByWell = failInfoByWell.sort_index()

# MTTF
failInfoByWell['MTTF'] = (actMatFull==1).sum()/failInfoByWell['failDate']
failInfoByWell['MTTF'].plot('bar')

# Number of active wells
actMatFull['actWellCount'] = (actMatFull == 1).sum(axis=1)

# Number of failures daily
actMatFull['failCount'] = ((((actMatFull == -1)*1).diff())==1).sum(axis=1)

# Rolling failure rate
actMatFull['rollingFailureRate'] = actMatFull['failCount'].rolling('365D').sum() / actMatFull['actWellCount'].rolling(
    '360D').mean()

# TODO: Failure model for all wells (2004-2019) - Done
# Failure model for all wells
out = Fit_Weibull_3P(failures=failInfoDf['TTFadj'].dropna().values)


# TODO: Failure model for currently active wells (>=2018)
afterJun2017 = actMatFull.columns[(actMatFull.loc['2017-06-01':] == 1).any()].drop('failCount')
afterJun2017TTFadj = failInfoDf['TTFadj'][failInfoDf['Well_ID'].astype('str').isin(afterJun2017.astype('str'))]
outAfterJun2017 = Fit_Weibull_3P(failures=afterJun2017TTFadj.dropna().values)

# TODO: Use the active well model to generate the risk curve
# TODO: Failure model for currently inactive wells
# TODO: Compare the alphas of the groups
# TODO: Check hypothesis that current wells are more reliable





