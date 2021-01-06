# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='AutosarModeller',
    version='0.1.0',
    description='Python module for reading autosar module configuration arxml files',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Girish Chandran',
    author_email='girishchandran.tpm@gmail.com',
    url='https://github.com/girishchandranc/autosarmodeller',
    license="MIT",
    packages=find_packages(exclude=('tests')),
    include_package_data=True,
    install_requires=["lxml>=4.6.1"],
    python_requires='>=3.6',
)
