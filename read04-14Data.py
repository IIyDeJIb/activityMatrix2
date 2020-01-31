import pandas as pd
import logging
from fullWellList import fullWellList
from xAndClassFailures import xAndClassFailures
from customErrors import NoWellsFoundError
from procFailSeries import procFailSeries
# from pg_pandas import closeSeries, compFillna
from datetime import datetime
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

# --- Preprocessing
# Remove some faulty data
rawData = rawData.drop(index=[datetime(2016,10,2), datetime(2016,10,3), datetime(2016,10,4), datetime(2016,10,5),
                              datetime(2016,10,6)])
rawData = rawData.drop(index=[datetime(2016,4,2), datetime(2016,4,3), datetime(2016,4,4), datetime(2016,4,5),
                              datetime(2016,4,6)])
rawData = rawData.drop(index=[datetime(2013,4,2)])
rawData = rawData.drop(index=pd.date_range(start=datetime(2008,1,2), end=datetime(2008,1,4)))
rawData = rawData.drop(index=[datetime(2009,10,4)])
rawData = rawData.drop(index=[datetime(2011,8,14)])

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
# -- Remove wells which are of no interest
actMatFull = actMatFull.drop(columns=['1408', '752', '1307'])

# Fill in missing data with 1 for the initial few years. The missing data in this period of the data typically means
# all the wells are running.
actMatFull.iloc[0:1354] = actMatFull.iloc[0:1354].fillna(1)

# Save the data before processing
actMatFull.to_csv('actMatFull_0_before_proc.csv')

# Upload unprocessed version
# actMatFull = pd.read_csv('actMatFull_0_before_proc.csv', parse_dates=['Unnamed: 0']).rename(columns={'Unnamed: 0':
#                                                                                                          'Date'}).set_index('Date')


# Automatic resolution of unclassified errors
actMatFull = actMatFull.apply(procFailSeries)



# --- Post-processing - Manual corrections of data which does not fit the rules
actMatFull.loc['2010-12-25', '1404'] = failTypeCode['surf']
actMatFull.loc['2004-06-21', '503'] = failTypeCode['subs'] # interference by tract 14
actMatFull.loc['2011-08-11':'2011-08-21', '1105'] = failTypeCode['subs']
actMatFull.loc['2011-08-14':'2011-08-18', '803'] = failTypeCode['surf']
actMatFull.loc['2011-08-12':'2011-08-15', ['809', '813']] = failTypeCode['surf']
actMatFull.loc['2011-06-12':'2011-06-14', '810'] = failTypeCode['surf'] # bad distributor
actMatFull.loc['2011-05-31':'2011-06-02', ['104', '105', '106', '107', '201', '202', '205', '206', '1106']] = \
    failTypeCode['surf']
actMatFull.loc['2011-05-03', '1106'] = failTypeCode['op'] # Cover the hole
actMatFull.loc['2011-05-01':'2011-05-02', '1105'] = failTypeCode['op'] # Cover the hole
actMatFull.loc['2015-03-27':'2015-02-13', '1411'] = failTypeCode['subs'] # Cover the hole
actMatFull.loc['2011-03-27':'2011-03-28', '505'] = failTypeCode['subs'] # "hole in tuber"..
actMatFull.loc['2011-03-17', ['604', '608']] = failTypeCode['op'] # no well issue
actMatFull.loc['2011-03-14', '606'] = failTypeCode['surf'] # Reason not indicated. Guessed.
actMatFull.loc['2011-03-12':'2011-03-15', '1412'] = failTypeCode['subs'] # Reason not indicated. Guessed.
actMatFull.loc['2011-01-03', ['405', '407']] = failTypeCode['op'] # chem circulation
actMatFull.loc['2011-01-02', ['405', '407', '910']] = failTypeCode['op'] # chem circulation
actMatFull.loc['2010-12-27', '1418'] = failTypeCode['surf']
actMatFull.loc['2010-12-25', ['1303', '1304', '1414']] = failTypeCode['surf']
actMatFull.loc['2010-12-17', '807'] = failTypeCode['surf']
actMatFull.loc['2010-12-04', ['603', '403']] = failTypeCode['surf']
actMatFull.loc['2010-10-31':'2010-11-04', '106'] = failTypeCode['subs'] # detected correctly, but better be joined
actMatFull.loc['2010-10-18':'2010-10-19', '1306'] = failTypeCode['surf']
actMatFull.loc['2010-03-27':'2010-03-29', '409'] = failTypeCode['surf']
actMatFull.loc['2010-03-27':'2010-03-29', '409'] = failTypeCode['surf'] # 1307 masking
actMatFull.loc['2009-10-03', '1412'] = failTypeCode['subs']
actMatFull.loc['2009-10-09':'2009-10-10', '1412'] = failTypeCode['op']
actMatFull.loc['2008-07-31', '1418'] = failTypeCode['surf']
actMatFull.loc['2008-01-09', ['708', '1105']] = failTypeCode['subs']
actMatFull.loc['2004-11-17':'2004-11-26', ['401', '406']] = failTypeCode['subs']
actMatFull.loc['2012-07-12':'2012-08-23', '807'] = failTypeCode['op']
actMatFull.loc['2012-08-13', '508'] = failTypeCode['surf']
actMatFull.loc['2012-08-21', '1419'] = failTypeCode['surf']
actMatFull.loc['2012-08-23':'2012-08-23', '1410'] = failTypeCode['op']
actMatFull.loc['2012-07-16':'2012-07-18', '1410'] = failTypeCode['subs']
actMatFull.loc['2012-09-13':'2012-09-19', '1006'] = failTypeCode['subs']
actMatFull.loc['2013-10-22', '208'] = failTypeCode['surf']
actMatFull.loc['2013-10-22':'2013-10-23', '1002'] = failTypeCode['surf']
actMatFull.loc['2013-01-22':'2013-01-23', '812'] = failTypeCode['surf']
actMatFull.loc['2013-02-03':'2013-02-08', '813'] = failTypeCode['surf']
actMatFull.loc['2013-05-24':'2013-05-28', '1410'] = failTypeCode['op']
actMatFull.loc['2013-06-18':'2013-06-19', ['812', '816', '1305']] = failTypeCode['surf']
actMatFull.loc['2013-07-12', '708'] = failTypeCode['surf']
actMatFull.loc['2013-07-13':'2013-07-28', '818'] = failTypeCode['subs'] # masked by ws well
actMatFull.loc['2013-09-12', ['1302', '817', '1416', '901']] = failTypeCode['surf']
actMatFull.loc['2014-09-22', '704'] = failTypeCode['surf'] # masked by LM
actMatFull.loc['2014-09-28':'2014-09-29', '1306'] = failTypeCode['surf'] # masked by LM
actMatFull.loc['2015-01-29', '508'] = failTypeCode['surf'] # repaired same day
actMatFull.loc['2015-04-07', '203'] = failTypeCode['op']
actMatFull.loc['2015-12-15':'2016-1-04', '506'] = failTypeCode['subs'] # "beltys"
actMatFull.loc['2016-09-22', '606'] = failTypeCode['subs']
actMatFull.loc['2016-03-19', '807'] = failTypeCode['op']
actMatFull.loc['2016-05-02':'2016-05-08', '1409'] = failTypeCode['surf'] # "beltys"
actMatFull.loc['2013-09-12', ['817', '1109', '1416']] = failTypeCode['op'] # reset
actMatFull.loc['2013-10-08', '1305'] = failTypeCode['surf'] # masked by injector..
actMatFull.loc['2014-01-23', ['201', '403', '404', '406', '503', '504', '906', '1002', '1004', '1005', '1006',
                              '1007', '1008', '1010']] = failTypeCode['op'] # no failure, just rebuilding header 10
actMatFull.loc['2014-01-23':'2014-03-25', '1005'] = failTypeCode['op']
actMatFull.loc['2014-01-30':'2014-01-31', '1409'] = failTypeCode['op']
actMatFull.loc['2014-05-27', ['201', '202']] = failTypeCode['surf'] # fuse
actMatFull.loc['2014-06-15', '813'] = failTypeCode['surf'] # overload tripper
actMatFull.loc['2014-06-29':'2014-07-01', '1410'] = failTypeCode['surf']
actMatFull.loc['2014-12-24':'2014-12-29', ['1414', '1419']] = failTypeCode['surf']
actMatFull.loc['2015-01-15', '508'] = failTypeCode['op']
actMatFull.loc['2015-12-30':'2015-12-31', ['205', '104']] = failTypeCode['op']
actMatFull.loc['2016-04-02':'2016-04-03', '1409'] = failTypeCode['op']
actMatFull.loc['2016-03-24':'2016-04-01', '1409'] = failTypeCode['surf']
actMatFull.loc['2016-05-01':'2016-05-04', '1404'] = failTypeCode['subs']
actMatFull.loc['2016-05-01', '1409'] = failTypeCode['surf']
actMatFull.loc['2017-01-18':'2017-01-21', '204'] = failTypeCode['subs']
actMatFull.loc['2017-08-05':'2017-08-08', '603'] = failTypeCode['surf'] # h/o/a? Seriously? No AFE found for this,
# so must me a minor surface issue.
actMatFull.loc['2018-01-02':'2018-01-03', ['201', '202', '504', '503', '606', '806', '1002', '1103', '1006', '1418',
                                           '1009']] = failTypeCode['op']
actMatFull.loc['2018-01-04', '405'] = 0
actMatFull.loc['2018-07-05', ['201', '202', '504', '704', '807', '809', '812', '814', '1006', '1007', '1008', '1009',
                              '1106']] = failTypeCode['op']
actMatFull.loc['2018-07-05', '109'] = failTypeCode['subs']
actMatFull.loc['2018-09-03', '817'] = failTypeCode['surf']
actMatFull.loc['2018-09-03', ['1005', '1002', '910', '606', '109']] = failTypeCode['op']
actMatFull.loc['2004-02-06':'2018-08-13', '410'] = 'tbd' # 8-13-2018 taken as the completion date of 410.
actMatFull.loc['2019-09-29':'2019-11-21', '906'] = failTypeCode['op']
actMatFull.loc['2009-12-24', actMatFull.columns] = failTypeCode['surf'] # CRU down due to electrical issues
actMatFull.loc['2009-12-24', ['204', '806', '813', '1007', '107', '1419']] = failTypeCode['subs'] # to correct the
# previous line
actMatFull.loc['2010-08-16':'2010-08-18', '108'] = failTypeCode['surf']
actMatFull.loc['2010-08-13':'2010-08-18', '606'] = failTypeCode['subs']
actMatFull.loc['2009-12-25':'2009-12-29', '106'] = failTypeCode['surf']
actMatFull.loc['2009-12-25':'2009-12-31', ['104', '105', '108', '203']] = failTypeCode['surf']
actMatFull.loc['2009-11-23', ['1304', '1415']] = failTypeCode['surf']
actMatFull.loc['2009-11-21':'2009-11-23', '801'] = failTypeCode['subs'] # acidized
actMatFull.loc['2009-11-22', ['1418', '1415', '1409', '1304', '1303', '1306']] = failTypeCode['surf']
actMatFull.loc['2009-10-05', '1303'] = failTypeCode['surf']
actMatFull.loc['2008-05-21':'2008-05-22', '1412'] = failTypeCode['subs']
actMatFull.loc['2008-06-11':'2008-06-12', '708'] = failTypeCode['subs']
actMatFull.loc['2009-08-26':'2009-08-27', '803'] = failTypeCode['subs']
actMatFull.loc['2009-2-18', ['1304','1303','1306','1418','1409']] = failTypeCode['surf'] # cause before well id
actMatFull.loc['2008-12-1':'2009-1-27', '806'] = failTypeCode['subs']
actMatFull.loc['2008-7-14', ['405', '204', '206', '208', '1004', '1005', '1006', '1007', '1010', '910', '106']] = failTypeCode['surf']
actMatFull.loc['2008-7-15', ['910', '104', '1006', '1007', '405']] = failTypeCode['surf'] # Cause before well number
actMatFull.loc['2008-4-9', '605'] = failTypeCode['surf']
actMatFull.loc['2008-1-2':'2008-1-4', '807'] = failTypeCode['op']
actMatFull.loc['2008-04-09', '605'] = failTypeCode['op']
actMatFull.loc['2008-03-21', ['105', '505']] = failTypeCode['op']
actMatFull.loc['2008-03-19':'2008-03-20', ['105', '505']] = failTypeCode['subs']    # roh - rig on hole?
actMatFull.loc['2008-03-03', '801'] = failTypeCode['surf']
actMatFull.loc['2008-01-09', '605'] = failTypeCode['op']
actMatFull.loc['2007-10-22', '1406'] = failTypeCode['subs']
actMatFull.loc['2007-06-02':'2007-06-04', '206'] = failTypeCode['surf']
actMatFull.loc['2007-04-04', '813'] = failTypeCode['surf']
actMatFull.loc['2007-04-03':'2007-04-04', ['503', '405']] = failTypeCode['surf']
actMatFull.loc['2007-01-28':'2007-01-29', '1306'] = failTypeCode['surf']
actMatFull.loc['2006-09-28':'2006-09-30', '808'] = failTypeCode['op']
actMatFull.loc['2006-08-01', '108'] = failTypeCode['op']
actMatFull.loc['2006-05-22', '108'] = failTypeCode['surf']
actMatFull.loc['2006-05-22', '608'] = failTypeCode['op']
actMatFull.loc['2006-03-27':'2006-03-28', '1416'] = failTypeCode['surf']
actMatFull.loc['2005-02-16':'2005-02-18', ['405', '1303']] = failTypeCode['op']
actMatFull.loc['2005-01-06', '605'] = failTypeCode['surf']
actMatFull.loc['2004-12-27':'2004-12-31', '608'] = failTypeCode['surf']
actMatFull.loc['2004-12-15', ['814', '812', '1302']] = failTypeCode['surf']
actMatFull.loc['2004-10-22', ['105','901','107']] = failTypeCode['surf']
actMatFull.loc['2004-8-4', '1104'] = failTypeCode['surf']
actMatFull.loc['2010-05-17': '2010-05-18', '1305'] = failTypeCode['surf']
actMatFull.loc['2010-11-18': '2010-11-22', '1104'] = failTypeCode['subs'] # not sure, reported "E/L"?
actMatFull.loc['2010-11-25', ['1104', '1302', '1006']] = failTypeCode['surf'] # circulation against bugs
actMatFull.loc['2011-09-19':'2011-09-21', '808'] = failTypeCode['subs'] # actually both surf and subs. Resolved for more major.
actMatFull.loc['2012-2-3':'2012-2-7', '206'] = failTypeCode['surf'] # actually both surf and subs. Resolved for more major.
actMatFull.loc['2012-3-21':'2012-3-28', '808'] = failTypeCode['op'] # "running".

actMatFull.to_csv('actMatFull_0.csv')
