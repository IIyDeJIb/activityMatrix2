# List of keywords which are common for online well reports
import re

# onlineRx = re.compile(r'back|pumping(?! (un|te|ja))|rtp|return|repaired|flowback|flowing back') # rtp - returned to
onlineRx = re.compile(r'back|pumping(?! (un|te|ja))|rtp|return|repaired|level') # rtp - returned to

# production