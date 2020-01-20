# Collection of my pandas functions
import pandas as pd
import numpy as np
from scipy import ndimage

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


def closeSeries(seriesIn, maxHole):
    indSave = seriesIn.index # preserve the index

    return pd.Series(ndimage.binary_closing(seriesIn, structure=[1]*maxHole), index=indSave)

    # return pd.Series(np.abs(ndimage.binary_closing(np.abs(seriesIn - 1), structure=[1]*maxHole) * 1 - 1), index=indSave)