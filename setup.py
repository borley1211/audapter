# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['audapter',
 'audapter.domain',
 'audapter.driver',
 'audapter.helper',
 'audapter.interface',
 'audapter.interface.driver']

package_data = \
{'': ['*']}

install_requires = \
['adasigpy>=0.1.7-beta.0,<0.2.0',
 'dynaconf>=2.2,<3.0',
 'fire>=0.2.1,<0.3.0',
 'nptyping>=0.3.1,<0.4.0',
 'numpy>=1.17,<2.0',
 'pyroomacoustics>=0.3.1,<0.4.0',
 'pysoundfile>=0.9.0,<0.10.0',
 'scipy>=1.4.0,<2.0.0',
 'sounddevice>=0.3.14,<0.4.0',
 'stft>=0.5.2,<0.6.0',
 'syncsweptsine @ git+https://github.com/SiggiGue/syncsweptsine.git@master']

entry_points = \
{'console_scripts': ['audapter = audapter:shell']}

setup_kwargs = {
    'name': 'audapter',
    'version': '0.1.1',
    'description': 'Adaptive Sound Processing',
    'long_description': None,
    'author': 'borley1211',
    'author_email': 'km.isetan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
