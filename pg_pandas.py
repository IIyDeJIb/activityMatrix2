# Collection of my pandas functions
import pandas as pd

def compFillna(dfOld):
    # fill in nan values using a combination of backward and forward fill (i.e. compromise)
    # Input:    {Series}
    # Output:   {Series}
    # by Peyruz Gasimov, 11-28-2019

    notConverged = True
    while notConverged:
        dfNew = dfOld.fillna(method='bfill', limit=1)
        dfNew = dfNew.fillna(method='ffill', limit=1)
        if dfNew.isna().any().any():
            dfOld = dfNew
        else:
            notConverged = False

    return dfNew