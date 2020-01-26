# List of keywords which are common for surface problem reports.
import re

# surfKW = 'elec line flow belt gear grbox rrc reset resset tee brdl bridle jack power rail saddle brg bearing motor ' \
#          'meter mtr ' \
#          'fuse pin wrist timer unit lock brok puley pulley fl voltage stuffi stufi sheav'
#
# surfRx = re.compile(r'(' + '|'.join(surfKW.split(' ')) + r')')

surfRx = re.compile(r'([^a-zA-Z]ele|(?<!on)line|flowl|belt|grbox|gear|rrc|reset|resset|tee|brdl|bridle|jack|power|rail'
                    r'|saddle|transformer|bridel'
                    r'|brg|wellhead|well head|bullwheel'
                    r'|bearing|s\\b|panel|contact|pipe|pump jack'
                    r'|motor|meter|mtr|fuse|pin[^g]|wrist|timer|unit|lock|brok|puley|pulley|voltage|stuffi|stufi|sheav)', flags=re.IGNORECASE)