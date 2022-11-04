# Automated characterization of noise distributions in diffusion MRI data

[miccai]: https://arxiv.org/abs/1805.12071
[miccai_publisher]: https://link.springer.com/chapter/10.1007%2F978-3-030-00928-1_35
[media]: https://www.sciencedirect.com/science/article/pii/S1361841520301225

###  The example and documentation

The latest version can be installed with
~~~
pip install autodmri
~~~

You can find a quick example and datasets over [here](example) and the full documentation at http://autodmri.rtfd.io/.

An example, super basic call to the script would be

~~~bash
autodmri_get_distribution dwi.nii.gz sigma.nii.gz N.nii.gz mask.nii.gz
~~~

Be sure to check the options by passing `--help` to the script.

###  The manuscript and references

You can read the [journal version][media] in Medical Image Analysis and the datasets are available here https://zenodo.org/record/2483105.

The conference version of the manuscript (as published in MICCAI 2018) is available [here][miccai] for free
and from the [publisher][miccai_publisher].

Here is a bibtex entry for the journal version

~~~
@article{St-jean2020_media,
author = {St-Jean, Samuel and {De Luca}, Alberto and Tax, Chantal M.W. and Viergever, Max A. and Leemans, Alexander},
doi = {10.1016/j.media.2020.101758},
eprint = {1906.12121},
issn = {13618415},
journal = {Medical Image Analysis},
month = {jun},
pages = {101758},
title = {{Automated characterization of noise distributions in diffusion MRI data}},
url = {https://linkinghub.elsevier.com/retrieve/pii/S1361841520301225},
year = {2020}
}
~~~

and for the conference manuscript in MICCAI

~~~
@InProceedings{St-jean2018_miccai,
author="St-Jean, Samuel
and De Luca, Alberto
and Viergever, Max A.
and Leemans, Alexander",
editor="Frangi, Alejandro F.
and Schnabel, Julia A.
and Davatzikos, Christos
and Alberola-L{\'o}pez, Carlos
and Fichtinger, Gabor",
title="Automatic, Fast and Robust Characterization of Noise Distributions for Diffusion MRI",
booktitle="Medical Image Computing and Computer Assisted Intervention -- MICCAI 2018",
year="2018",
publisher="Springer International Publishing",
address="Cham",
pages="304--312",
isbn="978-3-030-00928-1"
}
~~~

###  Referencing the code itself

The code is also autoarchived on zenodo for those wanting to refer to a specific version over here

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3339157.svg)](https://doi.org/10.5281/zenodo.3339157)
