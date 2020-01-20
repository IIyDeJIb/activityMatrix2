# Extract well IDs from the down wells' section of the CRU Daily report
#
# Input:
#   fullStr         - {str} the extracted string from the daily report containing the down well numbers
#   fullWellList    - {list} the list of wells to search for in the list
#
# Output:
#   exdWells        - {list} - list of wells from fullWellList found in the fullStr
#
# by Peyruz Gasimov
# 11-18-19

import re

def DRdownWellExtractor(dataStr, fullWellList):
    exdWells = []
    for wellQ in fullWellList:
        wellQrx = re.compile(r'(\D|^)('+wellQ+r')(\D|$)')
        g = wellQrx.findall(dataStr)
        if g != []:
            exdWells.append(g[0][1])

    return exdWells