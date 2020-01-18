# Use the failure info string and the list of the wells detected in the string to classify the well failures.
# Peyruz Gasimov, 12-18-2019

import re
import pandas as pd
import numpy as np
from surfKeyWords import surfRx
from subsKeyWords import subsRx

def classifyFailures(failInfo, downWellList):

    failDf = pd.DataFrame(index=downWellList, columns=['Surface', 'Subsurface', 'Unclassified'])
    downWellStr = '(' + '|'.join(downWellList) + ')'
    rxCauses = re.compile(downWellStr + r'(.+?)(?=' + downWellStr + r'|$)')

    allCauses = rxCauses.findall(failInfo.lower())

    # Comma check: Detect whether all there is in what was detected is a coma. In that case the failure for that well
    # needs to be read from the next well (and so on). E.g. 801, 101,606 hit will assign hit to all the listed wells.


    for failTup in allCauses:
        # Check whether only failure cause is indicated for this well (comma check)
        if not comRx.findall(failTup[1])==[]:
            continue

        failDf.loc[failTup[0], 'Subsurface'] = subsRx.findall(failTup[1]) != []
        failDf.loc[failTup[0], 'Surface'] = surfRx.findall(failTup[1]) != []

    failDf[['Surface', 'Subsurface']] = failDf[['Surface','Subsurface']].fillna(method='bfill')

    failDf['Unclassified'] = np.logical_not(np.logical_xor(failDf['Surface'].values.astype('bool'),
                                                               failDf['Subsurface'].values.astype('bool')))
    # return lists to keep consistency
    return np.array(downWellList)[failDf['Surface']].tolist(), np.array(downWellList)[failDf['Subsurface']].tolist(),\
           np.array(downWellList)[failDf['Unclassified']].tolist()






