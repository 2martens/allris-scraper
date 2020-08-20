# -*- coding: utf-8 -*-

#   Copyright 2020 Jim Martens
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""setup.py for allris scraper"""

from setuptools import find_packages
from setuptools import setup

with open("README.rst", "rb") as f:
    long_desc = f.read().decode()

setup(
    name="twomartens.allrisscraper",
    description="Scraper for ALLRIS",
    long_description=long_desc,
    long_description_content_type="text/x-rst; charset=UTF-8",
    author="Jim Martens",
    author_email="github@2martens.de",
    url="https://git.2martens.de/2martens/allris-scraper",
    version="0.4.1",
    namespace_packages=["twomartens"],
    packages=find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={'': 'src'},
    package_data={},
    entry_points={
        "console_scripts": ["tm-allrisscraper = twomartens.allrisscraper.main:main"]
    },
    python_requires="~=3.7",
    install_requires=["selenium"],
    license="Apache License 2.0",
    include_package_data=True,
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Environment :: Console",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
