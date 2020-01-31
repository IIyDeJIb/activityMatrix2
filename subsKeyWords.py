# List of keywords which are common for subsurface problem reports
import re

# subsKW = r'p/r p\r rdp prt tbg hit h/t h\t part rp r.p p.r tubing csg cg casing shut joint wor h.i s\i s/i'
#
# subsRx = re.compile(r'(' + '|'.join(subsKW.split(' ')) + r'|ht |pump |si )')

subsRx = re.compile(r'(p/r|p\\r|r\\p|r/p|rdp|prt|tbg|hit|h/t|h\\t|part|rp|r\.p|p\.r|p\\u|p/u|tubing|[^a-z]hic|csg|cg'
                    r'|casing|not pumping'
                    r'|shut(\s|-)?in|trash|trsh|h\\c|h/c|h\.i\.c|reent'
                    r'|rig|w/o|w\\o|p/t|p\\t|(?:[^a-z]|^)pt'
                    r'|frac|joint|wor(?![a-z])|h\.i|s\\i|h/i/t'
                    r'|s/i|(?:[^a-z]|^)ht(?:[^a-z]|$)|pump(?!\sja)(?:[^a-z]|$)|(?:[^a-z]|^)si(?:[^a-z]|$))')
