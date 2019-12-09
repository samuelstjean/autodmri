# Automated characterization of noise distributions in diffusion MRI data

[preprint]: https://doi.org/10.1101/686436
[miccai]: https://arxiv.org/abs/1805.12071
[miccai_publisher]: https://link.springer.com/chapter/10.1007%2F978-3-030-00928-1_35

###  The example and documentation

The latest version can be installed with
~~~
pip install autodmri
~~~

You can find a quick example and datasets over [here](example) and the full documentation at http://autodmri.rtfd.io/.

### Using Docker

If you have docker, you do not need to install anything else and can use the Dockerfile to get everything.
You can then mount your data folder to run the script and get the results into the same folder like this.

~~~
docker build -t autodmri:v0.2 .
docker run -it -v /home/samuel/git/autodmri/datasets:/mnt autodmri:v0.2 get_distribution /mnt/data_SENSE3_MB3_dwi.nii.gz /mnt/sigma.nii.gz /mnt/N.nii.gz /mnt/mask.nii.gz
~~~

Just be sure to adapt the path and filename of your data or add more options as needed.


###  The manuscript and references

The conference version of the manuscript (as published in MICCAI 2018) is available [here][miccai]
and from the [publisher][miccai_publisher].

You can find the [preprint of the journal version][preprint]
and the datasets are available here https://zenodo.org/record/2483105


Here is a bibtex entry for the conference manuscript and the preprint to the journal version

<details>
      <summary>Bibtex for the manuscript</summary>

~~~
@InProceedings{10.1007/978-3-030-00928-1_35,
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

</details>


<details>
      <summary>Bibtex for the preprint</summary>

~~~
@article {St-Jean686436,
    author = {St-Jean, Samuel and De Luca, Alberto and Tax, Chantal M. W. and Viergever, Max A. and Leemans, Alexander},
    title = {Automated characterization of noise distributions in diffusion MRI data},
    elocation-id = {686436},
    year = {2019},
    doi = {10.1101/686436},
    publisher = {Cold Spring Harbor Laboratory},
    URL = {https://www.biorxiv.org/content/early/2019/08/15/686436},
    eprint = {https://www.biorxiv.org/content/early/2019/08/15/686436.full.pdf},
    journal = {bioRxiv}
}
~~~

</details>


###  Referencing the code itself

The code is also autoarchived on zenodo for those wanting to refer to a specific version over here

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3339157.svg)](https://doi.org/10.5281/zenodo.3339157)
