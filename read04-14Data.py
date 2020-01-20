import pandas as pd
import logging
from fullWellList import fullWellList
from xAndClassFailures import xAndClassFailures
from customErrors import NoWellsFoundError
from procFailSeries import procFailSeries
# from pg_pandas import closeSeries, compFillna
# from datetime import datetime
# from openpyxl import load_workbook
# import os
# import re

failTypeCode = {'subs': -1,
                'surf': 0,
                'uncl': -2,
                'op': 1}

logging.basicConfig(filename='log1.log', level=logging.DEBUG, format='%(asctime)s:%(funcName)s:%(message)s',
                    filemode='w')

logging.info('----------------------- Start of Script.')
rawData = pd.read_csv('2004-2014_rawFailureData2_prep.csv', engine='python', index_col='Date', parse_dates=True).dropna()
rawData2 = pd.read_csv('rawData2_2014-2019.csv', engine='python', index_col=0, parse_dates=True, header=None).dropna()

rawData2.index.name = 'Date'
rawData2.columns = ['Comments']

rawData = rawData.append(rawData2)

dateList = pd.date_range(rawData.index[0], rawData2.index[-1], freq='D')

actMatFull = pd.DataFrame(index=dateList, columns=fullWellList)

for date, failInfo in rawData.itertuples():
    try:
        surfList, subsList, unclassList = xAndClassFailures(failInfo)
    except NoWellsFoundError:
        logging.info('No wells found in the failInfo. Date: {}, failInfo: {}'.format(date, failInfo))
        continue

    actMatFull.loc[date, :] = failTypeCode['op']
    actMatFull.loc[date, surfList] = failTypeCode['surf']
    actMatFull.loc[date, subsList] = failTypeCode['subs']
    actMatFull.loc[date, unclassList] = failTypeCode['uncl']

# ------------ Processing
# -- Remove injectors
actMatFull = actMatFull.drop(columns=['1408', '752'])

# Fill in missing data with 1 for the initial few years. The missing data in this period of the data typically means
# all the wells are running.
actMatFull.iloc[0:1354] = actMatFull.iloc[0:1354].fillna(1)

# Automatic resolution of unclassified errors
actMatFull = actMatFull.apply(procFailSeries)



# Manual corrections
# actMatFull.loc['2004-12-15', ['814', '812', '1302']] =
# actMatFull.loc['2004-12-15', '814'] =
# actMatFull.loc['2005-02-16':'2005-02-18', ['405', '1303']] =
# actMatFull.loc['2005-02-16':'2005-02-18', '405'] =
subs = -1
surf = 0
op = 1
uncl = -2
actMatFull.loc['2009-12-24', actMatFull.columns] = surf # CRU down due to electrical issues
actMatFull.loc['2009-12-24', ['204','806','813','1007','107','1419']] = subs # to correct the previous line
actMatFull.loc['2010-08-16':'2010-08-18', '108'] = surf
actMatFull.loc['2010-08-13':'2010-08-18', '606'] = subs
actMatFull.loc['2009-12-25':'2009-12-29', '106'] = surf
actMatFull.loc['2009-12-25':'2009-12-31', ['104', '105', '108', '203']] = surf
actMatFull.loc['2009-11-23', ['1304', '1415']] = surf
actMatFull.loc['2009-11-21':'2009-11-23', '801'] = subs # acidized
actMatFull.loc['2009-11-22', ['1418', '1415', '1409', '1304', '1303', '1306']] = surf
actMatFull.loc['2009-10-05', '1303'] = surf
actMatFull.loc['2008-05-21':'2008-05-22', '1412'] = subs
actMatFull.loc['2008-06-11':'2008-06-12', '708'] = subs
actMatFull.loc['2009-08-26':'2009-08-27', '803'] = subs
actMatFull.loc['2009-2-18', ['1304','1303','1306','1418','1409']] = surf # cause before well id
actMatFull.loc['2008-12-1':'2009-1-27', '806'] = subs
actMatFull.loc['2008-7-14', ['405', '204', '206', '208', '1004', '1005', '1006', '1007', '1010', '910', '106']] = surf
actMatFull.loc['2008-7-15', ['910', '104', '1006', '1007', '405']] = surf # Cause before well number
actMatFull.loc['2008-4-9', '605'] = surf
actMatFull.loc['2008-1-2':'2008-1-4', '807'] = op
actMatFull.loc['2008-04-09', '605'] = op
actMatFull.loc['2008-03-21', ['105', '505']] = op
actMatFull.loc['2008-03-19':'2008-03-20', ['105', '505']] = subs    # roh - rig on hole?
actMatFull.loc['2008-03-03', '801'] = surf
actMatFull.loc['2008-01-09', '605'] = op
actMatFull.loc['2007-10-22', '1406'] = subs
actMatFull.loc['2007-06-02':'2007-06-04', '206'] = surf
actMatFull.loc['2007-04-04', '813'] = surf
actMatFull.loc['2007-04-03':'2007-04-04', ['503', '405']] = surf
actMatFull.loc['2007-01-28':'2007-01-29', '1306'] = surf
actMatFull.loc['2006-09-28':'2006-09-30', '808'] = op
actMatFull.loc['2006-08-01', '108'] = op
actMatFull.loc['2006-05-22', '108'] = surf
actMatFull.loc['2006-05-22', '608'] = op
actMatFull.loc['2006-03-27':'2006-03-28', '1416'] = surf
actMatFull.loc['2005-02-16':'2005-02-18', ['405', '1303']] = op
actMatFull.loc['2005-01-06', '605'] = surf
actMatFull.loc['2004-12-27':'2004-12-31', '608'] = surf
actMatFull.loc['2004-12-15', ['814', '812', '1302']] = surf
actMatFull.loc['2004-10-22', ['105','901','107']] = surf
actMatFull.loc['2004-8-4', '1104'] = surf
actMatFull.loc['2010-05-17': '2010-05-18', '1305'] = surf
actMatFull.loc['2010-11-18': '2010-11-22', '1104'] = subs # not sure, reported "E/L"?
actMatFull.loc['2010-11-25', ['1104', '1302', '1006']] = surf # circulation against bugs
actMatFull.loc['2011-09-19':'2011-09-21', '808'] = subs # actually both surf and subs. Resolved for more major.
actMatFull.loc['2012-2-3':'2012-2-7', '206'] = surf # actually both surf and subs. Resolved for more major.
actMatFull.loc['2012-3-21':'2012-3-28', '808'] = op # "running".

actMatFull.to_csv('actMatFull_0.csv')
