from __future__ import division

import numpy as np

from scipy.special import digamma, polygamma


def get_noise_distribution(data, method='moments'):
    '''Computes sigma and N from an array of gamma distributed data

    input
    -----
    data
        A numpy array of gamma distributed values
    method='moments' or method='maxlk'
        Use either the moments or maximum likelihood equations to estimate the parameters.

    output
    ------
    sigma, N
        parameters related to the original Gaussian noise distribution
    '''

    data = data[data > 0]

    # If we have no voxel or only the same value
    # it leads to a divide by 0 as an edge case
    if data.size == 0 or np.std(data) == 0:
        return 0, 0

    # First get sigma
    if method == 'moments':
        mdata2 = np.mean(data**2)
        mdata4 = np.mean(data**4)

        p1 = mdata4 / mdata2
        p2 = mdata2
        sigma = np.sqrt(p1 - p2) / np.sqrt(2)
    elif method == 'maxlk':
            sigma = maxlk_sigma(data)
    else:
        raise ValueError('Invalid method name {}'.format(method))

    t = data**2 / (2*sigma**2)

    # Now compute N
    if method == 'moments':
        N = np.mean(t)
    elif method == 'maxlk':
            y = np.mean(np.log(t))
            N = inv_digamma(y)
    else:
        raise ValueError('Invalid method name {}'.format(method))

    return sigma, N


def maxlk_sigma(m, xold=None, eps=1e-8, max_iter=100):
    '''Maximum likelihood equation to estimate sigma from gamma distributed values'''

    sum_m2 = np.sum(m**2)
    K = m.size
    sum_log_m2 = np.sum(np.log(m**2))

    def f(sigma):
        return digamma(sum_m2/(2*K*sigma**2)) - sum_log_m2/K + np.log(2*sigma**2)

    def fprime(sigma):
        return -sum_m2 * polygamma(1, sum_m2/(2*K*sigma**2)) / (K*sigma**3) + 2/sigma

    if xold is None:
        xold = m.std()

    for _ in range(max_iter):

        xnew = xold - f(xold) / fprime(xold)

        if np.abs(xold - xnew) < eps:
            break

        xold = xnew

    return xnew


def inv_digamma(y, eps=1e-8, max_iter=100):
    '''Numerical inverse to the digamma function by root finding'''

    if y >= -2.22:
        xold = np.exp(y) + 0.5
    else:
        xold = -1 / (y - digamma(1))

    for _ in range(max_iter):

        xnew = xold - (digamma(xold) - y) / polygamma(1, xold)

        if np.abs(xold - xnew) < eps:
            break

        xold = xnew

    return xnew
