import setuptools
from distutils.core import setup

setuptools.setup(
    name='iocachesim',
    version='0.1',
    author='Jean-Baptiste BESNARD',
    description='This is a trivial IO cache simulator.',
    entry_points = {
        'console_scripts': ['iosim=lib.iocli:cli_entry'],
    },
    packages=["lib.iosim", "lib.iocli"],
    install_requires=[
        'matplotlib',
        'wheel'
    ],
    python_requires='>=3.5'
)