import shutil as _shutil
from dynaconf import settings as _SYSCONF
from ..helper.config import load_settings
import typer as _typer
import pathlib as _plib

__all__ = ["config"]


USERCONF = _plib.Path(_SYSCONF.get("USERCONFPATH")).absolute()
DEFAULTS = _plib.Path(_SYSCONF.get("DEFAULTSPATH")).absolute()


def config(
    restore: bool = _typer.Option(False, prompt="Restore the config file to default.")
):
    """
    Manage config files.
    """
    if restore:
        _shutil.copy(DEFAULTS, USERCONF)
    
    settings = load_settings()
    _typer.echo_via_pager(settings.values())
