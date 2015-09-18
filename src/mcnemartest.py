"""
True -> Ture: a
True -> False: b
False -> True: c
False -> False: d
"""

from scipy import stats
 
def mcnemar_t(a,b,c,d):
    """
    Input args:
       a, b, c, d- frequencies
    Output:
       pvalue of test.
    """
    # chi2testval = 1.0 * (abs(c-b)-1)**2 / (c + b)
    # print (abs(c-b)-1)**2
    # print chi2testval
    chi2testval = 1.0 * (abs(c-b))**2 / (c + b)

    # print chi2testval
    # chi2testval = 6.6349
    
    df = 1
    pvalue = 1 - stats.chi2.cdf(chi2testval, df)
    return pvalue
 
if __name__ == "__main__":
    a, b, c, d = 10, 25, 33, 10
 
    print mcnemar_t(a,b,c,d)
