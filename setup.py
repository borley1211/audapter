import os
import pip
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from pathlib import Path
from six import iteritems


PACKAGE_NAME = "audapter"

SOURCES = {"apps": "microlibs/apps_module", "core": "microlibs/core_module"}


def install_microlibs(sources: dict, is_devmode: bool):
    print(
        "installing microlibs in {} mode".format(
            "development" if is_devmode else "normal"
        )
    )

    wd = os.getcwd()

    for k, v in iteritems(sources):
        pass
        try:
            # 作業ディレクトリを各 microlibs のルートに移動.
            os.chdir(Path(wd) / v)

            if develop:
                pip.main(["install", "-e", "."])
            else:
                pip.main(["install", "."])
        except Exception as e:
            print(f"Oops, something went wrong installing {PACKAGE_NAME}.{k}")
            print(e)
        finally:
            os.chdir(wd)


class DevelopCommand(develop):
    pass


class InstallCommand(install):
    pass


setup(cmdclass={"install": InstallCommand, "develop": DevelopCommand})
