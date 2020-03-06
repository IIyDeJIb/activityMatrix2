import pandas as pd
import numpy as np
import scipy.stats as stats
from datetime import timedelta, datetime
from xWellFailInfo import xWellFailInfo
from reliability.Fitters import Fit_Everything, Fit_Weibull_3P
from genRiskCurve import genRiskCurve
from activeWellList import activeWellList

# Import the activity matrix
actMatFull = pd.read_csv('actMatFull_0.csv', index_col=0, parse_dates=True)
actMatFull.columns = actMatFull.columns.astype('int')

# Initialize the failInfo DataFrame
failInfoDf = xWellFailInfo(actMatFull[actMatFull.columns[0]])
failInfoDf.insert(2, 'Well_ID', actMatFull.columns[0])

for wellID in actMatFull.columns[1:]:
    failInfoDf = failInfoDf.append(
        xWellFailInfo(actMatFull[wellID]).assign(Well_ID=wellID), sort=False)

# Number of failures and datapoints by well
failInfoByWell = failInfoDf.groupby('Well_ID').count()[['failDate', 'TTF']]
failInfoByWell.index = failInfoByWell.index.astype('int')
failInfoByWell = failInfoByWell.sort_index()

# Mean Time To Failure (MTTF)
failInfoByWell['MTTF'] = (actMatFull == 1).sum() / failInfoByWell['failDate']

# Number of active wells
actMatFull['actWellCount'] = (actMatFull == 1).sum(axis=1)

# Number of failures daily
actMatFull['failCount'] = ((((actMatFull == -1) * 1).diff()) == 1).sum(axis=1)

# Rolling failure rate
# The left label of the window is assigned the failure rate. The number of active
# wells is taken from the same left label of the window. Say there are 90 wells on
# 2004-01-01, then the rolling failure rate on that day is calculated as the
# number of failures which happened between ( 2004-01-01 and 2004-01-01 + <window
# size> )/Number of active wells on 2004-01-01. Such an approach seems to help to
# better track correlation between failure rate and certain events. Say if we
# change the chemical vendor on 2004-01-01, on that same date we
# will see how this may have affected the failure rate one <window size> ahead.
actMatFull['rollingFailureRate'] = actMatFull['failCount'].rolling(
    '365D').sum().shift(-364) / actMatFull[
                                       'actWellCount']

# Failure model for all wells
out = Fit_Weibull_3P(failures=failInfoDf['TTFadj'].dropna().values,
                     show_probability_plot=False)

# Failure model for currently active wells (data: 2004-2019)
out_active = Fit_Weibull_3P(failures=failInfoDf[['Well_ID', 'TTFadj']][
    failInfoDf['Well_ID'].astype('str').isin(
        pd.Index(activeWellList).astype('str'))][
    'TTFadj'].dropna().values, show_probability_plot=False)

# Failure model for currently active wells (>=Jun 2017). Failure data - before
# June 2017
afterJun2017 = actMatFull.columns[(actMatFull.loc['2017-06-01':] == 1).any()].drop(
    'failCount')
afterJun2017TTFadj = failInfoDf[failInfoDf['failDate'] < '2017-06-01'][
    ['Well_ID', 'TTFadj']]
afterJun2017TTFadj = afterJun2017TTFadj[
    afterJun2017TTFadj['Well_ID'].astype('str').isin(afterJun2017.astype('str'))]

outAfterJun2017 = Fit_Weibull_3P(
    failures=afterJun2017TTFadj['TTFadj'].dropna().values,
    show_probability_plot=False)

# Failure model for currently inactive wells (>=Jun 2017). Failure data - before
# June 2017
afterJun2017_inact = actMatFull.columns[~(actMatFull.loc['2017-06-01':] == 1).any()]
afterJun2017TTFadj_inact = failInfoDf[failInfoDf['failDate'] < '2017-06-01'][
    ['Well_ID', 'TTFadj']]
afterJun2017TTFadj_inact = afterJun2017TTFadj_inact[
    afterJun2017TTFadj_inact['Well_ID'].astype('str').isin(
        afterJun2017_inact.astype('str'))]
outAfterJun2017_inact = Fit_Weibull_3P(
    failures=afterJun2017TTFadj_inact['TTFadj'].dropna().values,
    show_probability_plot=False)

# -----  Risk curves
# Use the 'all CRU wells' model to generate the risk curve
weibulParam = {
    'alpha': out.alpha,
    'beta': out.beta,
    'gamma': out.gamma,
}

caseDetails = {
    'startDate': datetime(2020, 1, 11),
    'endDate': 'from MC trials',
    'qini': 3,
    'decline': 0.05,
    'discRate': 0.1,
    'investment': 30000,
    'oilPrice': 50,  # less differential
    'NRI': 0.875,
    'fixedCost': 350
}

RiskCurve_all, P_all = genRiskCurve(weibulParam, caseDetails, Ntrials=1000)

# Use the 'active wells' model to generate the risk curve

weibulParam = {
    'alpha': out_active.alpha,
    'beta': out_active.beta,
    'gamma': out_active.gamma
}

RiskCurve_active, P_active = genRiskCurve(weibulParam, caseDetails, Ntrials=1000)

# ------ Failure by month - is there a statistically significant trend?
# Calculate mean number of failures by month
failInfoDf['failMonth'] = failInfoDf['failDate'].apply(lambda x: x.month_name())
failInfoDf['failYear'] = failInfoDf['failDate'].apply(lambda x: x.year)

# Distribution of failure count by month and year
failByMonth = pd.DataFrame(data=[failInfoDf[failInfoDf['failYear'] == year][
    'failMonth'].value_counts().sort_index(
) for year in failInfoDf['failYear'].unique()],
    index=failInfoDf['failYear'].unique()).sort_index().fillna(0).drop(
    index=np.nan)

# ANOVA F-test shows no statistically significant difference between the mean
# failure count every month
stats.f_oneway(*[failByMonth[month] for month in failByMonth.columns])

# ------ Failure by season
failInfoDf['failSeason'] = failInfoDf['failMonth'].map({'January': 'Winter',
                                                        'February': 'Winter',
                                                        'March': 'Spring',
                                                        'April': 'Spring',
                                                        'May': 'Spring',
                                                        'June': 'Summer',
                                                        'July': 'Summer',
                                                        'August': 'Summer',
                                                        'September': 'Fall',
                                                        'October': 'Fall',
                                                        'November': 'Fall',
                                                        'December': 'Winter'})
# ANOVA F-test
failBySeason = pd.DataFrame(data=[failInfoDf[failInfoDf['failYear'] == year][
    'failSeason'].value_counts().sort_index(
) for year in failInfoDf['failYear'].unique()],
    index=failInfoDf['failYear'].unique()).sort_index().fillna(0).drop(
    index=np.nan)

stats.f_oneway(*[failBySeason[season] for season in failBySeason.columns])

# # ----- Weibull fit with right-censored data
# # Wells which were active at the end of the data timespan are have censored TTF.
# These can be incorporated into the
# # Weibull model.
# # The fit is worse than without censored data because gamma is then fit to 1 and
# does not capure a lot of the
# # early-time data. Not Recommended.
# # Extract the censored data
# right_cens_all = (actMatFull.index[-1]-failInfoDf.set_index('failDate')[
# 'fixDate'][failInfoDf.set_index('failDate')[
#     'TTFadj'].isnull()].dropna()).apply(lambda x: x.days).values
#
# out_cens = Fit_Weibull_3P(failures=failInfoDf['TTFadj'].dropna().values,
# show_probability_plot=False,
#                           right_censored=right_cens_all)

# ----------------------------- Analyze the chemical program
chemLog = pd.read_csv('chemLog.csv', parse_dates=['EffDate']).set_index('EffDate')

# Rolling chemical expense (left)
rollingChemExp90D_left = (chemLog['Amount'].groupby(by='EffDate').sum().reindex(
    actMatFull.index).rolling('90D'). \
                          sum().shift(-89) / actMatFull['actWellCount'])

# Correlation between failure rate and chemical expenses
chemCorr = pd.DataFrame(
    data=[rollingChemExp90D_left, actMatFull['rollingFailureRate']]).transpose()

chemCorr = chemCorr[chemCorr != np.inf]
chemCorr = chemCorr.dropna().rename(columns={'Unnamed 0': 'chemExp90D'})

print('Correlation between Failure Rate and Chemical Expenses: ',
      stats.pearsonr(chemCorr.iloc[:, 1], chemCorr.iloc[:, 0]))

chemCorr['Description'] = chemLog['Description'][
    ~chemLog['Description'].index.duplicated()].reindex(chemCorr.index).fillna(
    method='ffill')

# Break down by types of treatment where possible

# Since the Wolfpacke data is incomplete when it comes to the components of the
# treatment, we can refer to PO log instead. The details of the treatmetns in the
# Wolfpacke source ceases to specify types of treatments at 3-31-2017 mark. For
# that time on we will use the PO log data.
# Import the chemical PO log
chemPOLog = pd.read_csv('CRUChemPO_2014-2019.csv',
                        usecols=['Date', 'Description of Work',
                                 'Remark Actual Rcvd'], parse_dates=['Date'],
                        engine='python').rename(
    columns={'Date': 'EffDate', 'Remark Actual Rcvd': 'Amount', 'Description of Work': 'Description'}).set_index('EffDate')['4-01-2017':]

# Merge the chemLog with chemPOLog for further processing
chemLog = chemLog[:'4-01-2017'].append(chemPOLog)

treatmentTypesKW = ['corr', 'scal', 'acid', 'surf', 'iron', 'scav', 'cide', 'bio',
                    'emul', 'paraf', 'truck']

mask = pd.Series(index=chemLog.index)
unknownMask = pd.Series(data=1, index=chemLog.index)

for ttype in treatmentTypesKW:
    mask = chemLog['Description'].apply(lambda x: ttype in x.lower())

    # aggregated version of 'any'
    unknownMask = unknownMask * ((unknownMask.astype('bool') | mask) * 1 - (
            unknownMask.astype('bool') & mask) * 1)

    chemCorr[ttype + '90D'] = chemLog['Amount'][mask].groupby(
        by='EffDate').sum().reindex(actMatFull.index).rolling('90D'). \
                                  sum().shift(-89) / actMatFull['actWellCount']

chemCorr['unknown90D'] = chemLog['Amount'][unknownMask.astype('bool')].groupby(
    by='EffDate').sum().reindex(actMatFull.index).rolling('90D'). \
                             sum().shift(-89) / actMatFull['actWellCount']

chemCorr = chemCorr.fillna(0)

# Looking at the treatment proposal from Endura (1/1/2019), we allocate the truck
# treatment cost as follows:
chemCorr['corr90D'] = chemCorr['corr90D'] + 0.92 * chemCorr['truck90D']
chemCorr['paraf90D'] = chemCorr['paraf90D'] + 0.01 * chemCorr['truck90D']
chemCorr['bio90D'] = chemCorr['bio90D'] + 0.01 * chemCorr['truck90D']
chemCorr['iron90D'] = chemCorr['iron90D'] + 0.06 * chemCorr['truck90D']

# Combine some treatment cost with different keywords
chemCorr['iron90D'] = chemCorr['iron90D'] + chemCorr['scav90D']
chemCorr['bio90D'] = chemCorr['bio90D'] + chemCorr['cide90D']
chemCorr['scal90D'] = chemCorr['scal90D'] + chemCorr['surf90D'] + chemCorr['acid90D']

chemCorr.drop(columns=['truck90D', 'scav90D', 'cide90D', 'surf90D', 'acid90D'],
              inplace=True)

# Add active well count to the chemCorr
chemCorr['actWellCount'] = actMatFull['actWellCount'].reindex(chemCorr)

# ------ Output
chemCorr.to_csv('chemCorr.csv')
rollingChemExp90D_left.to_csv('rollingChemExp90D_left.csv')
failBySeason.to_csv('failBySeason.csv')
failByMonth.to_csv('failByMonth.csv')
RiskCurve_active.to_csv('RiskCurve_active.csv')
RiskCurve_all.to_csv('RiskCurve_all.csv')
failInfoByWell.to_csv('failInfoByWell.csv')
actMatFull.to_csv('calc_actMatFull.csv')
