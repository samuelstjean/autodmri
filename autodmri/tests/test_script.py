import os.path
import subprocess

import autodmri
import pytest

commands = ['autodmri_get_distribution data_SENSE3_MB3_noisemap.nii.gz sigma_maxlk_nmaps.nii.gz N_maxlk_nmaps.nii.gz mask_maxlk_nmaps.nii.gz -m maxlk --noise_maps',
            'autodmri_get_distribution data_SENSE3_MB3_noisemap.nii.gz sigma_nmaps.nii.gz N_nmaps.nii.gz mask_nmaps.nii.gz --noise_maps',
            'autodmri_get_distribution data_SENSE3_MB3_noisemap.nii.gz sigma_nmaps.nii.gz N_nmaps.nii.gz mask_nmaps.nii.gz --noise_maps -f --subsample',
            'autodmri_get_distribution data_SENSE3_MB3_noisemap.nii.gz sigma_nmaps.nii.gz N_nmaps.nii.gz mask_nmaps.nii.gz --noise_maps -f --fast_median -m maxlk',
            'autodmri_get_distribution dwi_1_8.nii.gz sigma.nii.gz N.nii.gz mask.nii.gz -v',
            'autodmri_get_distribution dwi_1_8.nii.gz sigma.nii.gz N.nii.gz mask.nii.gz -m maxlk -f --ncores 4',
            'autodmri_get_distribution dwi_1_8.nii.gz sigma_maxlk.nii.gz N_maxlk.nii.gz mask_maxlk.nii.gz -m maxlk --size 3 -f -v --axis 0']

cwd = os.path.join(os.path.dirname(autodmri.__file__), '../datasets')

@pytest.mark.parametrize('command', commands)
def test_script(command):
    subprocess.run([command], shell=True, cwd=cwd, check=True)
