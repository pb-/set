from setuptools import setup, find_packages

setup(
    name='set',
    packages=find_packages(),
    install_requires=[
        'tornado',
    ],
    entry_points={
        'console_scripts': [
            'setd = set.server:run',
        ],
    },
)
