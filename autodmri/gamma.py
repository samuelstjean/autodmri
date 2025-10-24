from __future__ import annotations # Needed for | annotations on python 3.9

import numpy as np
import numpy.typing as npt

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
        sigma = np.sqrt(mdata4 / mdata2 - mdata2) / np.sqrt(2)
    elif method == 'maxlk':
        sigma = maxlk_sigma(data)
    else:
        raise ValueError(f'Invalid method name {method}')

    t = 1/2 * (data / sigma)**2

    # Now compute N
    if method == 'moments':
        N = np.mean(t)
    elif method == 'maxlk':
        y = np.mean(np.log(t))
        N = inv_digamma(y)
    else:
        raise ValueError(f'Invalid method name {method}')

    return sigma, N


def maxlk_sigma(m: npt.NDArray, xold: float | None = None, eps: float=1e-8, max_iter: int=100):
    '''Maximum likelihood equation to estimate sigma from gamma distributed values'''

    mean_m2 = np.mean(m**2)
    mean_log_m2 = 2 * np.mean(np.log(m))

    def f(sigma):
        return digamma(mean_m2 / (2*sigma**2)) - mean_log_m2 + np.log(2*sigma**2)

    def fprime(sigma):
        return -mean_m2 * polygamma(1, mean_m2 / (2*sigma**2)) / sigma**3 + 2/sigma

    if xold is None:
        xold = m.std()

    for _ in range(max_iter):

        xnew = xold - f(xold) / fprime(xold)

        if np.abs(xold - xnew) < eps:
            break

        xold = xnew

    return xnew


def inv_digamma(y: float, eps: float=1e-8, max_iter: int=100) -> float:
    '''Numerical inverse to the digamma function by root finding'''

    if y >= -2.22:
        xold = np.exp(y) + 1/2
    else:
        xold = -1 / (y + np.euler_gamma)

    for _ in range(max_iter):

        xnew = xold - (digamma(xold) - y) / polygamma(1, xold)

        if np.abs(xold - xnew) < eps:
            break

        xold = xnew

    return xnew
