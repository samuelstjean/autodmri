# Changelog

## [v0.2.4] - 2021-03-09

- Fix an indexing bug for noise maps when going over the full data (the default).
- Pad 3D noise maps to 4D automatically in the main script.

## [v0.2.3] - 2020-06-22

- Add new option **--fast_median** to reduce time and memory usage for large datasets such as the HCP datasets.
- Add journal manuscript reference.

## [v0.2.2] - 2020-01-13

- Bugfix: Remove non ascii char in get_distribution for python 2.

## [v0.2.1] - 2019-12-13

- Bugfix: Use io.open for backward compatibility in python 2.7 for setup.py.

## [v0.2] - 2019-12-09

- Now using joblib for the multiprocessing backend
- When selecting overlapping noise maps measurements without subsampling (option **--noise_maps**), values are now averaged for each overlapping voxel.
- New fancy example available at https://github.com/samuelstjean/autodmri/tree/master/example


## [v0.1] - 2019-05-17

The first release.

To install, download the file and run in your favorite terminal

~~~bash
pip install autodmri-0.1.tar.gz
~~~
