"""
A setuptools based setup module.
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

description = 'High Dimensional Algorithm Tester: A tool for manually verifying high-dimensionality algorithms.'

setup(
    name='hdat',
    version='0.1.0',
    description=description,
    long_description=description,
    url='https://github.com/innolitics/hdat',
    author='Innolitics, LLC',
    author_email='info@innolitics.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',

        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='scientific image',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['gitpython'],

    extras_require={
        'dev': ['check-manifest', 'sphinx', 'sphinx-autobuild', 'mock'],
        'test': ['coverage', 'numpy'],
    },

    package_data={},
    data_files=[('/etc/bash_completion.d/', ['hdat/hdat_completion'])],
    entry_points={
        'console_scripts': [
            'hdat = hdat.main:main'
        ]
    },
)
