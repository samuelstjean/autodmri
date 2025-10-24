from __future__ import annotations # Needed for | annotations on python 3.9

import numpy as np
import numpy.typing as npt
import pytest

from autodmri.estimator import estimate_from_dwis, estimate_from_nmaps
from itertools import product


sigma = 1, 10, 50, 100, 200
N = 1, 4, 8, 12, 24
methods = ['moments', 'maxlk']

all_items = product(sigma, N, methods)

@pytest.mark.parametrize('sigma, N, method', all_items)
def test_estimators(sigma, N, method):
    data = np.zeros([25,25,25,30])
    data[10:20, 10:20, 10:20] = 1000
    empty = np.zeros_like(data)

    noisy = _make_noise(data, sigma, N)
    noise_maps = _make_noise(empty, sigma, N)

    dwis_sigma, dwis_N = estimate_from_dwis(noisy, method=method)
    nmaps_sigma, nmaps_N = estimate_from_nmaps(noise_maps, method=method, return_mask=False, full=False)
    nmaps_sigma_full, nmaps_N_full = estimate_from_nmaps(noise_maps, method=method, return_mask=False, full=True)

    for (estimated_sigma, estimated_N) in zip([dwis_sigma, nmaps_sigma, nmaps_sigma_full],
                                              [dwis_N, nmaps_N, nmaps_N_full]):
        # less than 5% error on average estimate?
        assert np.abs(sigma - estimated_sigma.mean()) / sigma < 0.05
        assert np.abs(N - estimated_N.mean()) / N < 0.05


def _make_noise(data: npt.NDArray, sigma: float, N: int, seed: int | None = None) -> np.ndarray:
    size = data.shape[:-1]
    out = np.zeros_like(data, dtype=np.float32)
    n1 = np.zeros(size, dtype=np.float32)
    n2 = np.zeros(size, dtype=np.float32)

    rng = np.random.RandomState(seed)

    for _ in range(N):
        for i in range(data.shape[-1]):
            n1[:] = rng.normal(0, sigma, size)
            n2[:] = rng.normal(0, sigma, size)
            out[..., i] += (data[..., i] + n1)**2 + n2**2

    return np.sqrt(out)
