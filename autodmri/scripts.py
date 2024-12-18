import numpy as np
import nibabel as nib

import os
import argparse
import logging

from autodmri.estimator import estimate_from_dwis, estimate_from_nmaps


DESCRIPTION = """
Main script for automatically characterizing noise distributions.
"""

EPILOG = """
Reference:

MICCAI version
---------------
St-Jean S., De Luca A., Viergever M.A., Leemans A. (2018)
Automatic, Fast and Robust Characterization of Noise Distributions for Diffusion MRI, MICCAI 2018.
Springer International Publishing, pp. 304-312. doi: 10.1007/978-3-030-00928-1_35.
Available at: https://arxiv.org/abs/1805.12071

Journal version
-----------------
Samuel St-Jean, Alberto De Luca, Chantal M.W. Tax, Max A. Viergever, Alexander Leemans,
Automated characterization of noise distributions in diffusion MRI data,
Medical Image Analysis, 2020, 101758, ISSN 1361-8415,
doi: 10.1016/j.media.2020.101758
Available at: http://www.sciencedirect.com/science/article/pii/S1361841520301225
"""


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass


def buildArgsParser():

    p = argparse.ArgumentParser(description=DESCRIPTION,
                                epilog=EPILOG,
                                formatter_class=CustomFormatter)

    p.add_argument('data', metavar='input',
                   help='Path of the input data.')

    p.add_argument('sigma', metavar='sigma',
                   help='Path of the output sigma volume.')

    p.add_argument('N', metavar='N',
                   help='Path of the output N volume.')

    p.add_argument('mask', metavar='mask',
                   help='Path of the output mask for voxels identified as noise.')

    p.add_argument('-a', '--axis', type=int, default=-2, choices=[0, 1, 2],
                   help='Axis (0, 1 or 2 typically) which is assumed to contain uniform noise.')

    p.add_argument('-m', '--method', default='moments', choices=['moments', 'maxlk'], metavar='string',
                   help='Method to use for estimating parameters, either "moments" or "maxlk".')

    p.add_argument('--ncores', metavar='int', type=int, default=-1,
                   help='Number of cores to use for multithreading.')

    p.add_argument('--exclude', metavar='file',
                   help='Mask indicating which voxels to exclude from the computation. Useful to remove gross artifacts.')

    p.add_argument('--noise_maps', action='store_true',
                   help='Estimate in small windows instead of whole slices over the input volume. Only valid in theory for noise maps.')

    p.add_argument('--subsample', action='store_true',
                   help='If supplied, estimate in non-overlapping windows with option --noise_maps.')

    p.add_argument('--fast_median', action='store_true',
                   help='If supplied, computes the median of medians from each volume instead of one median value.\n'
                      'Useful for large datasets with many volumes (e.g. HCP) since the median requires a full copy of the data and sorting.')

    p.add_argument('--size', metavar='int', type=int, default=5,
                   help='Size of the window for local noise maps estimation.')

    p.add_argument('-f', '--force', action='store_true', dest='overwrite',
                   help='If set, overwrites the output text file if it already exists.')

    p.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                   help='If set, shows a progress bar during processing and prints useful information.')

    p.add_argument('-l', '--log', dest='logfile', metavar='file',
                   help='Save the logging output to this file. Implies verbose output.')

    return p


def main():
    parser = buildArgsParser()
    args = parser.parse_args()

    logger = logging.getLogger('autodmri')

    if args.logfile is not None:
        handler = logging.FileHandler(args.logfile)
        args.verbose = True
    else:
        handler = logging.StreamHandler(args.logfile)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if args.verbose:
        logger.setLevel(logging.INFO)
        logger.info('Verbosity is on')

    overwritable_files = [args.sigma,
                          args.N,
                          args.mask]

    for f in overwritable_files:
        if f is not None and os.path.isfile(f):
            if args.overwrite:
                logger.warning(f'Overwriting {os.path.realpath(f)}')
            else:
                parser.error(f'{f} already exists! Use -f or --force to overwrite it.')

    vol = nib.load(args.data)
    data = vol.get_fdata(dtype=np.float32)
    aff = vol.affine
    # hdr = vol.header

    ncores = args.ncores
    method = args.method
    axis = args.axis
    full = not args.subsample
    size = args.size
    noise_maps = args.noise_maps

    if args.exclude is not None:
        exclude_mask = nib.load(args.exclude).get_fdata().astype(bool)
        logger.info(f'Excluding voxels from file {args.exclude}')
    else:
        exclude_mask = None

    logger.info(f'Now estimating over file {args.data} with method = {method} and axis = {axis}')

    if noise_maps:
        if full:
            overlap = 'overlapping windows'
        else:
            overlap = 'non-overlapping windows'

        if data.ndim == 3:
            data = data[..., None]

        logger.info(f'Estimation will be done over noise maps with a window of size {size} and {overlap}')
        sigma, N, mask = estimate_from_nmaps(data, size=size, return_mask=True, method=method, full=full, ncores=ncores, use_rejection=False, verbose=args.verbose)

    else:
        if axis < 0:
            axis = data.ndim + axis

        if args.fast_median:
            logger.info('Estimation of the medians will be done over each volume, then on the median of the medians.')
        elif data.shape[-1] > 100:
            logger.warning(f'Estimation of the median will be done over the whole volume, but you have {data.shape[-1]} volumes.\n' +
                           '\tConsider the option --fast_median if memory usage is high and startup time is too long.')

        sigma, N, mask = estimate_from_dwis(data, axis=axis, return_mask=True, exclude_mask=exclude_mask, ncores=ncores,
                                            method=method, verbose=args.verbose, fast_median=args.fast_median)

        # Broadcast the 1D arrays to full 3D
        if axis == 0:
            sigma = sigma[:, None, None]
            N = N[:, None, None]
        elif axis == 1:
            sigma = sigma[None, :, None]
            N = N[None, :, None]
        elif axis == 2:
            sigma = sigma[None, None, :]
            N = N[None, None, :]
        else:
            raise ValueError(f'axis = {axis} is not 0, 1 or 2, but that should never happen!')

        sigma = np.ones(mask.shape) * sigma
        N = np.ones(mask.shape) * N

    # Save the data
    logger.info(f'Output files are {args.sigma}, {args.N} and {args.mask}')
    mask = mask.astype(np.int16)
    sigma = sigma.astype(np.float32)
    N = N.astype(np.float32)

    nib.Nifti1Image(sigma, aff).to_filename(args.sigma)
    nib.Nifti1Image(N, aff).to_filename(args.N)
    nib.Nifti1Image(mask, aff).to_filename(args.mask)


if __name__ == "__main__":
    main()
