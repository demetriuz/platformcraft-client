from setuptools import setup, find_packages, os


setup(
    name='Platformcraft client',
    version='0.0.1',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'requests'
    ]
)
