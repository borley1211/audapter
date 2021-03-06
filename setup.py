#################### Maintained by Hatch ####################
# This file is auto-generated by hatch. If you'd like to customize this file
# please add your changes near the bottom marked for 'USER OVERRIDES'.
# EVERYTHING ELSE WILL BE OVERWRITTEN by hatch.
#############################################################
from io import open

from setuptools import find_packages, setup

with open("audapter/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        version = "0.0.1"

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

REQUIRES = []

kwargs = {
    "name": "audapter",
    "version": version,
    "description": "",
    "long_description": readme,
    "author": "Kazuma Miebori",
    "author_email": "km.isetan@gmail.com",
    "maintainer": "Kazuma Miebori",
    "maintainer_email": "km.isetan@gmail.com",
    "url": "https://github.com/borley1211/audapter",
    "license": "MIT",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    "install_requires": REQUIRES,
    "tests_require": ["coverage", "pytest"],
    "packages": find_packages(exclude=("tests", "tests.*")),
}

# ################## BEGIN USER OVERRIDES ################## #
# Add your customizations in this section.

# ################### END USER OVERRIDES ################### #

setup(**kwargs)
