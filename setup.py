# Copyright (c) 2025 Scott Russell
# SPDX-License-Identifier: MIT

from setuptools import find_packages, setup

setup(
    name='meatball',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['pyyaml', 'sexpdata'],
    entry_points={
        'console_scripts': [
            'meatball = meatball.cli:main'
        ]
    },
    extras_require={
        'test': ['pytest']
    },
)
