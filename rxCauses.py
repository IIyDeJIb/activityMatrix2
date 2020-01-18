from fullWellList import fullWellList
import re

<<<<<<< HEAD
# Special treatment for 105 not to confuse it with 1105 (actually not necessary anymore since 1105 was added to the full
# well list)
=======
# Special treatment for 105 not to confuse it with 1105
>>>>>>> c91fe7e... extract, classify, some manual corrections
fullWellStr = '(104|(?<!1)105|106|107|108|109|201(?![0-9])|202(?![0-9])|' + '|'.join(fullWellList[8:]) + ')'
rxCauses = re.compile(fullWellStr + r'(.+?)(?=' + fullWellStr + r'|$)')