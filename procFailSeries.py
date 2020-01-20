from pg_pandas import compFillna, closeSeries
import numpy as np
from datetime import timedelta

def procFailSeries(seriesIn, tipover=0.75, failTypeCode=None):
    # Process fail series
    #
    # The following steps are undertaken here:
    # 1. Fill nan values
    # 2. Convert the series into binary "well on/off" format
    # 3. Fix the holes in the binary series
    # 4. Detect the failure streaks (from fail event to fix event) and process each assigning fail type to each where
    # known with reasonable probability (controlled by 'tipover')
    #
    # Headnote 1
    # sufficient fraction of the streak needs to be initially classified as 'X' to classify the whole streak as 'X'.
    # 'X' here is ['subs', 'surf', 'uncl']. Second condition for the streak to be classified as 'X' is that
    # the other category must initially have fraction of zero. E.g. the streak will be classified as subsurface failure only
    # if more than 'tipover' fraction of the streak is initially classified as subsurface and if no part of the
    # streak is initially classified as surface.
    #
    # by Peyruz Gasimov, Jan 2020

    if failTypeCode==None:
        failTypeCode = {'subs': -1,
                        'surf': 0,
                        'uncl': -2,
                        'op': 1}
    # Step 1
    seriesIn = compFillna(seriesIn)

    # Step 2
    seriesInBin = (seriesIn!=failTypeCode['op'])

    # Step 3
    seriesInBin = closeSeries(seriesInBin, maxHole=5)*1

    # Step 4
    failEventDay = seriesInBin.index[seriesInBin.diff() == 1]
    fixEventDay = seriesInBin.index[seriesInBin.diff() == -1]-timedelta(days=1)

    if failEventDay[0]>fixEventDay[0]:
        failEventDay = np.insert(fixEventDay,failEventDay.index[0],seriesInBin.index[0])

    if failEventDay[-1]>fixEventDay[-1]:
        fixEventDay = np.append(fixEventDay,seriesInBin.index[-1])

    for failStart, failEnd in zip(failEventDay, fixEventDay):
        failStreak = seriesIn[failStart: failEnd]
        if sum(failStreak==-2)!=0:
            subsFrac = sum(failStreak == -1)/len(failStreak)
            surfFrac = sum(failStreak == 0)/len(failStreak)
            if subsFrac > tipover and surfFrac == 0:
                seriesIn[failStart: failEnd] = failTypeCode['subs']
            elif subsFrac == 0 and surfFrac > tipover:
                seriesIn[failStart: failEnd] = failTypeCode['surf']
            else:
                pass

    return seriesIn
