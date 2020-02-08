import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def xWellFailInfo(ser):

    serBin = (ser == -1)*1

    try:
        failEventDay = (serBin.index[serBin.diff() == 1]).to_list()
    except TypeError:
        print('No failures found: ', ser.name)
        return -1

    try:
        fixEventDay = (serBin.index[serBin.diff() == -1] - timedelta(days=1)).to_list()
    except TypeError:
        print('No repairs found: ', ser.name)
        return -1

    if failEventDay[0] > fixEventDay[0]: # Begins with failure streak
        failEventDay.insert(0, np.nan)

    if failEventDay[-1] > fixEventDay[-1]:  # Ends with failure streak
        fixEventDay.append(np.nan)



    failInfoDf = pd.DataFrame(index=range(len(fixEventDay)), columns=['failDate', 'fixDate', 'TTR', 'TTF',
                                                                      'TTFadj',
                                                                      'AFE#',
                                                                      'WOcost'])

    failInfoDf['failDate'] = failEventDay
    failInfoDf['fixDate'] = fixEventDay
    failInfoDf['TTR'] = failInfoDf['fixDate'] - failInfoDf['failDate']+timedelta(days=1)
    failInfoDf['TTF'] = failInfoDf['failDate'].shift(-1)-failInfoDf['fixDate']+timedelta(days=1)

    # Find adjusted Time To Failure
    ii=0
    for streakStart, streakEnd in zip(failInfoDf['fixDate'].to_list(), failInfoDf['failDate'].shift(-1).to_list()):
        if pd.isnull(streakStart) or pd.isnull(streakEnd):
            continue
        failInfoDf.loc[ii,'TTFadj'] = sum(ser[streakStart:streakEnd] == 1)
        ii+=1

    return failInfoDf