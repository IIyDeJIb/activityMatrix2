import numpy as np
import pandas as pd
from wellCashFlow import well_moDCF
from datetime import datetime, timedelta
from reliability.Distributions import Weibull_Distribution


def genRiskCurve(weibulParam=None, caseDetails=None, Ntrials=None):

    """
    :param weibulParam: <dict> see default below
    :param caseDetails: <dict> see default below
    :return: RiskCurve: <Series> Cumulative probability -> NPV,
                    P:  <dict> P10, 50 and 90 of the trial
    """

    # number of Monte-Carlo trials
    if Ntrials==None:
        Ntrials = 1000

    if weibulParam == None: # Default: model for all CRU wells
        weibulParam = {
            'alpha': 306.528315,
            'beta': 0.763063,
            'gamma': 11.991000,
        }

    if caseDetails == None:
        caseDetails = {
            'startDate': datetime(2020, 1, 11),
            'endDate': datetime(2021, 1, 1),
            'qini': 3,
            'decline': 0.05,
            'discRate': 0.1,
            'investment': 30000,
            'oilPrice': 50, # less differential
            'NRI': 0.875,
            'fixedCost': 350
        }


    dist = Weibull_Distribution(weibulParam['alpha'], weibulParam['beta'], weibulParam['gamma'])

    TTF_all = dist.random_samples(Ntrials)

    CumDCF = []

    for TTF in TTF_all:
        caseDetails['endDate'] = caseDetails['startDate'] + timedelta(days=TTF)
        CumDCF.append(well_moDCF(caseDetails)['Cum DCF'].iloc[-1])

    RiskCurve = pd.Series(data=CumDCF).sort_values(ascending=False)
    RiskCurve.index = np.arange(len(RiskCurve))/len(RiskCurve)

    P = {'P10': RiskCurve.iloc[RiskCurve.index.get_loc(0.1)],
         'P50': RiskCurve.iloc[RiskCurve.index.get_loc(0.5)],
         'P90': RiskCurve.iloc[RiskCurve.index.get_loc(0.9)]}

    return RiskCurve, P


