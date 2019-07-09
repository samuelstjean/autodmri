import numpy as np

from scipy.special import digamma
from autodmri.gamma import inv_digamma


def test_inv_digamma():
    values = np.random.uniform(0.1, 100, 1000)
    gam = digamma(values)
    invgam = [inv_digamma(g) for g in gam]
    np.testing.assert_allclose(invgam, values)
