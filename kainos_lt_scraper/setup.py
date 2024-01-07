#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="VB_pub",
    author_email='audreyr@example.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Scraper",
    entry_points={
        'console_scripts': [
            'kainos_lt_scraper=kainos_lt_scraper.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='kainos_lt_scraper',
    name='kainos_lt_scraper',
    packages=find_packages(include=['kainos_lt_scraper', 'kainos_lt_scraper.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/VB_pub/kainos_lt_scraper',
    version='1.0.0',
    zip_safe=False,
)