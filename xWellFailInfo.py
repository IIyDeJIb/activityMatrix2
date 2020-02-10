import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def xWellFailInfo(ser):

    cols = ['failDate', 'fixDate', 'TTR', 'TTF',
               'TTFadj',
               'AFE#',
               'WOcost']

    serBin = (ser == -1)*1

    failEventDay = (serBin.index[serBin.diff() == 1]).to_list()
    fixEventDay = (serBin.index[serBin.diff() == -1] - timedelta(days=1)).to_list()


    try:
        if failEventDay[0] > fixEventDay[0]: # Begins with failure streak
            failEventDay.insert(0, np.nan)
    except IndexError:
        print(ser.name, ': No failures found. Return empty DataFrame')
        return pd.DataFrame(columns=cols)  # return empty DataFrame

    try:
        if failEventDay[-1] > fixEventDay[-1]:  # Ends with failure streak
            fixEventDay.append(np.nan)
    except IndexError:
        print(ser.name, ': No repair found. Return empty DataFrame')
        return pd.DataFrame(columns=cols) # return empty DataFrame

    failInfoDf = pd.DataFrame(index=range(len(fixEventDay)), columns=cols)

    failInfoDf['failDate'] = failEventDay
    failInfoDf['fixDate'] = fixEventDay
    failInfoDf['TTR'] = (failInfoDf['fixDate'] - failInfoDf['failDate']+timedelta(days=1)).apply(lambda x: x.days)
    failInfoDf['TTF'] = (failInfoDf['failDate'].shift(-1)-failInfoDf['fixDate']+timedelta(days=1)).apply(lambda x: x.days)

    # Find adjusted Time To Failure
    ii=0
    for streakStart, streakEnd in zip(failInfoDf['fixDate'].to_list(), failInfoDf['failDate'].shift(-1).to_list()):
        if pd.isnull(streakStart) or pd.isnull(streakEnd):
            continue
        failInfoDf.loc[ii,'TTFadj'] = sum(ser[streakStart:streakEnd] == 1)
        ii+=1

    failInfoDf['TTFadj'] = failInfoDf['TTFadj'].astype('float')

    return failInfoDf