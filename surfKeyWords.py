# List of keywords which are common for surface problem reports.
import re

# surfKW = 'elec line flow belt gear grbox rrc reset resset tee brdl bridle jack power rail saddle brg bearing motor ' \
#          'meter mtr ' \
#          'fuse pin wrist timer unit lock brok puley pulley fl voltage stuffi stufi sheav'
#
# surfRx = re.compile(r'(' + '|'.join(surfKW.split(' ')) + r')')

surfRx = re.compile(r'((?:[^a-z]|^)el[ei]c|(?<!on)lin{1,2}e|flowl|belt|grbox|gear|rrc|reset|resset|tee|brdl|brid{1,2}'
                    r'le|jack|power'
                    r'|rail'
                    r'|saddle|transformer|bridel|starter'
                    r'|brg|wellhead|well head|bullwheel'
                    r'|bearing|s\\b|panel|contact|pipe' #|pump jack'
                    r'|motor|meter|mtr|fuse|pin[^g]|wrist|tim{1,2}'
                    r'er|unit|lock|brok|puley|pulley|voltage|stuffi|stufi|sheav)')