from dataclasses import dataclass as _dataclass

from padasip.filters import AdaptiveFilter as _AdaptiveFilter
from padasip.filters.base_filter import AdaptiveFilter as _AdaptiveFilterCls


@_dataclass(frozen=True)
class FilterModel(object):
    adaptive_filter : _AdaptiveFilterCls
    
    def __init__(self, model : str):
        self.adaptive_filter = _AdaptiveFilter(model=model)
