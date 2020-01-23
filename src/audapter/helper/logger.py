import logging as _log

from .. import LOGGERNAME

_log.basicConfig(format="%(levelname)s: %(message)s", level=_log.INFO)
logger = _log.getLogger(LOGGERNAME)
