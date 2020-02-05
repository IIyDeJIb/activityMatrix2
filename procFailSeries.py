from pg_pandas import compFillna, closeSeries
import numpy as np
from datetime import timedelta

def procFailSeries(seriesIn, tipover0=0.1, tipover1=0.5, failTypeCode=None):
    # Process fail series
    #
    # The following steps are undertaken here:
    # 1. Fill nan values
    # 2. Convert the series into binary "well on/off" format
    # 3. Fix the holes in the binary series
    # 4. Detect the failure streaks (from fail event to fix event) and process each assigning fail type to each where
    # known with reasonable probability (see the if correspondent if statements for more information)
    #
    # The methodology used here correctly solved many unclassified datapoints. However it also has a backside of
    # sometimes poor estimate of failure type on one day will trump the days where error was unclassified. Erroneous
    # fail typing mainly comes from additional comments pumpers sometimes leave after the daily failure report.
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
    try:
        fixEventDay = seriesInBin.index[seriesInBin.diff() == -1]-timedelta(days=1)
    except TypeError:
        print(seriesIn.name)
        pass

    try:    # Well may have no failures on record. This will throw an IndexError.
        if failEventDay[0]>fixEventDay[0]:
            failEventDay = np.insert(fixEventDay,failEventDay.index[0],seriesInBin.index[0])
    except IndexError:
        return seriesIn

    try:  # Well may have no repairs on record. This will throw an IndexError.
        if failEventDay[-1]>fixEventDay[-1]:
            fixEventDay = np.append(fixEventDay,seriesInBin.index[-1])
    except IndexError:
        return seriesIn

    for failStart, failEnd in zip(failEventDay, fixEventDay):
        failStreak = seriesIn[failStart: failEnd]

        # Remove single-day downhole failures (improbable)
        if failStreak.size == 1:
            if failStreak[0] == -1:
                seriesIn[failStart: failEnd] = 1
                continue

        if sum(failStreak == failTypeCode['uncl'])!=0 or sum(failStreak == failTypeCode['op'])!=0:
            subsFrac = sum(failStreak == -1)/len(failStreak)
            surfFrac = sum(failStreak == 0)/len(failStreak)
            # if subsFrac >= tipover and surfFrac < 0.1:
            #     seriesIn[failStart: failEnd] = failTypeCode['subs']
            # elif subsFrac < 0.2 and surfFrac >= tipover:
            #     seriesIn[failStart: failEnd] = failTypeCode['surf']
            # else:
            #     pass
            if subsFrac == 0 or surfFrac == 0:
                if subsFrac >= tipover0:
                    seriesIn[failStart: failEnd] = failTypeCode['subs']
                elif surfFrac >= tipover0:
                    seriesIn[failStart: failEnd] = failTypeCode['surf']
                else:
                    pass
            else:
                if subsFrac >= tipover1 and surfFrac < 0.1:
                    seriesIn[failStart: failEnd] = failTypeCode['subs']
                elif subsFrac < 0.1 and surfFrac >= tipover1:
                    seriesIn[failStart: failEnd] = failTypeCode['surf']
                else:
                    pass

    # --- Second pass, treat the subsurface failure portion of the series
    # Larger holes are closed between the subsurface streaks
    seriesInBinSubs = (seriesIn == failTypeCode['subs'])
    seriesInBinSubs = closeSeries(seriesInBinSubs, maxHole=12)
    seriesIn[seriesInBinSubs] = failTypeCode['subs']

    return seriesIn
