# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='Python Password',
    version='0.1.2',
    description='Simple password storing app.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AnonymousX86/Python-Password',
    author='Jakub Suchenek',
    author_email='jakub.suchenek.25@gmail.com',
    license='GNU GPL v3',
    classifiers=[
        'Development status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.8',
        'Topic :: Security :: Cryptography'
    ],
    keywords='password storing security cryptography',
    project_urls={
        'Source': 'https://github.com/AnonymousX86/Python-Password',
        'Tracker': 'https://github.com/AnonymousX86/Python-Password/issues'
    },
    packages=find_packages(),
    # py_modules=[],
    install_requires=requirements,
    python_requires='~=3.8',
    # package_data={},
    # data_files=(),
    # scripts=(),
    # entry_points={}
)
