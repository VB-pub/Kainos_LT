from setuptools import setup, find_packages

setup(
    name='Kainos_LT_scraper',
    version='1.0.0',
    author='VB_pub',
    long_description=open('README.md').read(),
    url='https://github.com/VB-pub/Kainos_LT',  # Replace with the URL to your package's repo
    packages=find_packages(),
    install_requires=[
    ],
    classifiers=[
        # Choose classifiers from the list at https://pypi.org/classifiers/
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify compatible Python versions
)
