import pathlib as _pathlib
from typing import Optional

from typing_extensions import NoReturn


def init(name: Optional[str] = None, path: Optional[str, _pathlib.Path] = '.') -> NoReturn:
    """
    Initialize audapter project.

    Args:
        name (str, optional): Project name to profile.
        path (str or 'pathlib.Path', optional): Path to generate configuration.
    """
    path = _pathlib.Path(path)
    name = name or path.parent.name
