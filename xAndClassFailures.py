# Use the failure info string and the list of the wells detected in the string to classify the well failures.
# Peyruz Gasimov, 12-18-2019

import re
import pandas as pd
import numpy as np
from rxCauses import rxCauses
from surfKeyWords import surfRx
from subsKeyWords import subsRx
from onlineRx import onlineRx
from customErrors import NoWellsFoundError

def xAndClassFailures(failInfo):

    failDf = pd.DataFrame(columns=['Surface', 'Subsurface', 'Online', 'Unclassified'])

    allCauses = rxCauses.findall(failInfo)

    if allCauses==[]:
        raise NoWellsFoundError(failInfo)

    # Comma check: Detect whether all there is in what was detected is a coma. In that case the failure for that well
    # needs to be read from the next well (and so on). E.g. 801, 101,606 hit will assign hit to all the listed wells.
    # Same logic goes for "&" and " ".
    comRx = re.compile(r'(^\s?,\s?$|^\s? \s?$|^\s?&\s?$)')
    # comRx = re.compile(r'^\s?,\s?$')

    for failTup in allCauses:
        # Check whether only failure cause is indicated for this well (comma check)
        if comRx.findall(failTup[1].lower())!=[]:
            failDf.loc[failTup[0],'Surface'] = np.nan
            failDf.loc[failTup[0],'Subsurface'] = np.nan
            failDf.loc[failTup[0], 'Online'] = np.nan
            continue

        failDf.loc[failTup[0], 'Subsurface'] = subsRx.findall(failTup[1].lower()) != []
        failDf.loc[failTup[0], 'Surface'] = surfRx.findall(failTup[1].lower()) != []
        failDf.loc[failTup[0], 'Online'] = onlineRx.findall(failTup[1].lower()) != []

    # Two steps of filling the missing values. The first steps takes care of the wells which only had coma after them
    # (we skip those first). Here we backfill the data so in the string (see "Comma check" comment). The second one is
    # when comas were detected, however no causes were. All the wells are marked as unclassified in this case.
    failDf[['Surface', 'Subsurface','Online']] = failDf[['Surface', 'Subsurface','Online']].fillna(method='bfill').fillna(False)

    failDf['Unclassified'] = False
    failDf.loc[np.sum(failDf[['Surface', 'Subsurface', 'Online']], axis=1) != 1, 'Unclassified'] = True

    # failDf['Unclassified'] = np.logical_not(np.logical_xor(failDf['Surface'].values.astype('bool'),
    #                                                            failDf['Subsurface'].values.astype('bool')))

    # return lists to keep consistency
    return failDf.index[failDf['Surface']].tolist(), failDf.index[failDf['Subsurface']].tolist(), \
           failDf.index[failDf['Unclassified']].tolist()






