from setuptools import setup, find_packages

setup(
    name='autodmri',
    version='0.2',
    author='Samuel St-Jean',
    author_email='samuel@isi.uu.nl',
    packages=find_packages(),
    scripts=['scripts/get_distribution'],
    url='https://github.com/samuelstjean/autodmri',
    license='LICENSE',
    description='Implementation of "Automated characterization of noise distributions in diffusion MRI data".',
    long_description=open('README.md').read(),
    install_requires=['numpy>=1.10',
                      'scipy>=0.19',
                      'joblib>=0.12',
                      'nibabel>=2.2'],
)
