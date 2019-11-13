import os
import pip
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from six import iteritems


def install_microlibs(sources: dict, is_devmode: bool):
    print("installing microlibs in {} mode".format("development" if is_devmode else "normal"))
    
    for k, v in iteritems(sources):
        pass


setup()
