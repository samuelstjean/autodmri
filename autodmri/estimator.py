from __future__ import division

import numpy as np

from scipy.ndimage.interpolation import zoom
from scipy.special import gammaincinv

from autodmri.gamma import get_noise_distribution
from autodmri.blocks import extract_patches

from joblib import Parallel, delayed

###########################################
# These functions are for over dwis
###########################################


def estimate_from_dwis(data, axis=-2, return_mask=False, exclude_mask=None, ncores=-1, method='moments', verbose=0, fast_median=False):
    '''Given the data, splits over each slice to compute parameters of the gamma distribution

    input
    ------
        data : array, input volume used to identify noise voxels and estimate the noise distribution

    optional
    --------
        axis : (0, 1 or 2) the axis to consider as a slab of uniform noise profile

        return_mask : bool, if True returns the identified noise voxels as a mask

        exclude_mask : array, mask indicating voxels to remove from all the computations, such as those containing huge artifacts.

        ncores : int, number of cores to use for multiprocessing

        method='moments' or method='maxlk' : which algorithm to use to estimate sigma and N

        verbose : print progress for joblib, can be an integer to increase verbosity

        fast_median : Computes the median of medians from each volume.
        Useful for large datasets with many volumes (e.g. HCP) since the median requires a full copy of the data and sorting.

    output
    -------
    sigma, N, mask (optional)
    '''

    # guess a gross upper bound of sigma
    # if it's masked, median can be zero, so use the nonzero data
    if fast_median:
        medians = np.zeros(data.shape[-1])

        for idx in range(data.shape[-1]):
            chunk = data[..., idx]
            median = np.median(chunk)

            if median == 0:
                median = np.median(chunk[chunk > 0])

            medians[idx] = median

        median = np.median(medians)
    else:
        median = np.median(data)

        if median == 0:
            median = np.median(data[data > 0])

    if axis < 0:
        axis = data.ndim + axis

    ranger = range(data.shape[axis])
    swapped_data = data.swapaxes(0, axis)

    if exclude_mask is None:
        exclude_mask = [None] * swapped_data.shape[0]
    else:
        exclude_mask = exclude_mask.swapaxes(0, axis)

    output = Parallel(n_jobs=ncores, verbose=verbose)(delayed(_inner)(swapped_data[i], median, exclude_mask[i], method) for i in ranger)

    # output is each slice we took along axis, so the mask might be reversed
    sigma = np.zeros(len(output))
    N = np.zeros(len(output))
    mask = np.zeros(data.shape[:-1], dtype=np.int16).swapaxes(0, axis)

    for i, s in enumerate(output):
        sigma[i] = s[0]
        N[i] = s[1]
        mask[i] = s[2]

    if return_mask:
        return sigma, N, mask.swapaxes(0, axis)
    return sigma, N


def _inner(data, median, exclude_mask=None, method='moments', l=50, N_min=1, N_max=12, max_iter=100, eps=1e-3):

    def lambda_cdf(N, alpha_prob):
        out = gammaincinv(N, alpha_prob)
        out = np.nan_to_num(out).clip(min=1e-7)
        return out

    def get_mask(data, N_min, N_max, phi, alpha_prob=0.05):
        K = data.shape[-1]
        sum_data2 = np.sum(data**2, axis=-1)

        data[data == 0] = np.nan
        sum_data2 = np.nansum(data**2, axis=-1)
        K = np.sum(np.isfinite(data), axis=-1)
        data[np.isnan(data)] = 0

        lambda_minus = lambda_cdf(N_min*K, alpha_prob/2)
        lambda_plus = lambda_cdf(N_max*K, 1 - alpha_prob/2)

        mask_current = np.zeros(data.shape[:-1], dtype=np.bool)
        mask_loop = np.zeros(data.shape[:-1], dtype=np.bool)

        for sigma in phi:
            s = sum_data2 / (2*sigma**2)
            mask_current[:] = np.logical_and(lambda_minus < s, s < lambda_plus)

            if mask_current.sum() > mask_loop.sum():
                mask_loop[:] = mask_current
        return mask_loop

    # Explicitly remove known artifacts
    if exclude_mask is None:
        exclude_mask = np.zeros(data.shape[:-1], dtype=np.bool)

    # we don't know N, so guess parameters iteratively
    data = data.astype(np.float64)  # prevent data**4 overflow
    sigma_prev = -1
    N_prev = -1
    sigma_init = median / np.sqrt(2 * lambda_cdf(N_max, 0.5))
    phi = np.arange(1, l+1) * sigma_init / l

    for _ in range(max_iter):

        mask = get_mask(data, N_min, N_max, phi)
        mask *= np.logical_not(exclude_mask)

        # empty slice -> mask is zero
        if mask.sum() == 0:
            return 0, 0, np.zeros_like(mask)

        datam = data[np.broadcast_to(mask[..., None], data.shape)]
        sigma, N = get_noise_distribution(datam, method=method)

        if sigma == 0 or N == 0:
            return 0, 0, np.zeros_like(mask)

        # abs error is small?
        if (np.abs(N - N_prev) < eps) and (np.abs(sigma - sigma_prev) < eps):
            break

        # relative error is small?
        if ((np.abs(N - N_prev) / N) < eps) and ((np.abs(sigma - sigma_prev) / sigma) < eps):
            break

        N_prev = N
        sigma_prev = sigma

        N_min = N
        N_max = N

        phi = np.linspace(.95, 1.05, num=11) * sigma

    return sigma, N, mask


###########################################
# These functions are for over noise maps
###########################################


def estimate_from_nmaps(data, size=5, return_mask=True, method='moments', full=False, ncores=-1, use_rejection=False, verbose=0):
    '''Given the data, estimates parameters of the gamma distribution in small 3D windows.

    input
    ------
        data : noise maps to use for parameter estimation.

    optional
    --------
        size : size of the 3D windows (default 5)

        return_mask : bool, if True returns the identified noise voxels as a mask

        method='moments' or method='maxlk' : which algorithm to use to estimate sigma and N

        full : bool, if True estimates are made in overlapping windows

        ncores : int, number of cores to use for multiprocessing

        use_rejection : if True, iterate to reject voxels in each estimated window, but this is much slower than just using all of the data.

        verbose : print progress for joblib, can be an integer to increase verbosity

    output
    -------
    sigma, N, mask (optional)
    '''
    m_out = np.zeros(data.shape[:-1], dtype=np.bool)
    median = np.median(data)

    if median == 0:
        median = np.median(data[data > 0])

    if full:
        reshaped_maps = extract_patches(data, (size, size, size, data.shape[-1]), (1, 1, 1, data.shape[-1]), flatten=False)

        sigma = np.zeros(data.shape[:-1], dtype=np.float32)
        N = np.zeros(data.shape[:-1], dtype=np.float32)
        count = np.zeros(data.shape[:-1], dtype=np.int16)
        mask = np.zeros(data.shape[:-1], dtype=np.int16)

        indexer = list(np.ndindex(reshaped_maps.shape[:reshaped_maps.ndim//2 - 1]))

        output = Parallel(n_jobs=ncores,
                          verbose=verbose)(delayed(proc_inner)(reshaped_maps[i], median, size, method, use_rejection) for i in indexer)

        # Account for padding on each side
        indexer = (tuple(np.array(idx) + size//2) for idx in indexer)
        indexer = (np.index_exp[idx[0]:idx[0] + size, idx[1]:idx[1] + size, idx[2]:idx[2] + size] for idx in indexer)

        # We accumulate the value at each voxel then take the average over the overlap
        for idx, (s, n, m) in zip(indexer, output):
            sigma[idx] += s
            N[idx] += n

            mask[idx] = m.sum()
            count[idx] += 1

        sigma /= count
        N /= count

        if return_mask:
            return sigma, N, mask
        return sigma, N

    else:
        reshaped_maps = extract_patches(data, (size, size, size, data.shape[-1]), (size, size, size, data.shape[-1]))

        sigma = np.zeros(reshaped_maps.shape[0], dtype=np.float32)
        N = np.zeros(reshaped_maps.shape[0], dtype=np.float32)
        mask = np.zeros((reshaped_maps.shape[0], size**3), dtype=np.bool)

        output = Parallel(n_jobs=ncores,
                          verbose=verbose)(delayed(proc_inner)(reshaped_maps[i], median, size, method, use_rejection) for i in range(reshaped_maps.shape[0]))

        for i, (s, n, m) in enumerate(output):
            sigma[i] = s
            N[i] = n
            mask[i] = np.squeeze(m).sum(axis=-1)

        s_out = sigma.reshape(data.shape[0] // size, data.shape[1] // size, data.shape[2] // size)
        N_out = N.reshape(data.shape[0] // size, data.shape[1] // size, data.shape[2] // size)

        for n, i in enumerate(np.ndindex(s_out.shape)):
            i = np.array(i) * size
            j = i + size
            m_out[i[0]:j[0], i[1]:j[1], i[2]:j[2]] = mask[n].reshape(size, size, size)

        x, y, z = np.array(s_out.shape) * size
        interpolated_sigma = np.zeros_like(data[..., 0], dtype=np.float32)
        interpolated_N = np.zeros_like(data[..., 0], dtype=np.float32)

        interpolated_sigma[:x, :y, :z] = zoom(s_out, size, order=1)
        interpolated_N[:x, :y, :z] = zoom(N_out, size, order=1)

        if return_mask:
            return interpolated_sigma, interpolated_N, m_out
        return interpolated_sigma, interpolated_N


def proc_inner(cur_map, median, size, method, use_rejection):

    if use_rejection:
        cur_map = cur_map.reshape(-1, 1, 1)
        output = _inner(cur_map, median, method=method)
    else:
        cur_map = cur_map.reshape(size**3, 1, -1)
        sigma, N = get_noise_distribution(cur_map, method=method)
        mask = np.ones_like(cur_map, dtype=np.bool)
        output = sigma, N, mask
    return output
