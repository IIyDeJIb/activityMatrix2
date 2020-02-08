import scipy.optimize

def xnpv(rate, values, dates):
    '''Equivalent of Excel's XNPV function.
    # >>> from datetime import date
    # >>> dates = [date(2010, 12, 29), date(2012, 1, 25), date(2012, 3, 8)]
    # >>> values = [-10000, 20, 10100]
    # >>> xnpv(0.1, values, dates)
    -966.4345...
    '''
    if rate <= -1.0:
        return float('inf')
    d0 = dates[0]    # or min(dates)
    return sum([ vi / (1.0 + rate)**((di - d0).days / 365.0) for vi, di in zip(values, dates)])

def xirr(values, dates):
    '''Equivalent of Excel's XIRR function.
    # >>> from datetime import date
    # >>> dates = [date(2010, 12, 29), date(2012, 1, 25), date(2012, 3, 8)]
    # >>> values = [-10000, 20, 10100]
    # >>> xirr(values, dates)
    0.0100612...
    '''
    try:
        return scipy.optimize.newton(lambda r: xnpv(r, values, dates), 0.0)
    except RuntimeError:    # Failed to converge?
        return scipy.optimize.brentq(lambda r: xnpv(r, values, dates), -1.0, 1e10)
