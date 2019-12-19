# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = {"": "src"}

packages = ["audapter", "audapter.driver", "audapter.helper", "audapter.interface"]

package_data = {"": ["*"], "audapter": ["domain/*"], "audapter.interface": ["driver/*"]}

install_requires = [
    "adasigpy",
    "bashplotlib>=0.6.5,<0.7.0",
    "dynaconf>=2.2,<3.0",
    "numpy>=1.17,<2.0",
    "pydocstyle>=5.0.1,<6.0.0",
    "pysoundfile>=0.9.0,<0.10.0",
    "scipy",
    "sounddevice>=0.3.14,<0.4.0",
    "stft>=0.5.2,<0.6.0",
]

setup_kwargs = {
    "name": "audapter",
    "version": "0.1.0",
    "description": "Adaptive Sound Processing",
    "long_description": None,
    "author": "borley1211",
    "author_email": "km.isetan@gmail.com",
    "maintainer": None,
    "maintainer_email": None,
    "url": None,
    "package_dir": package_dir,
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.6,<4.0",
}


setup(**setup_kwargs)
