import numpy as np
from padasip import padasip as pa


class AdapTuner(object):
    """
    Adaptive filter for signal tuning
    """
    def __init__(self, model: 'str'="lms", f_init: 'ndarray or str'=None):
        self.filter = pa.filters.AdaptiveFilter(model=model)
        self._initialize(f_init)

    def _initialize(self, f_init):
        """Initialize this filter
        
        Arguments:
            f_init {ndarray or str} -- initial filter-weights
        
        Raises:
            ValueError: 'type(f_init)' is not suitable
        """
        if f_init is None:
            pass
        elif f_init is np.ndarray:
            self.filter.init_weights(f_init)
        elif f_init is str:
            self.filter.init_weights(np.load(file=f_init))
        else:
            raise ValueError(
                "'f_init' seems unlike filter-weights or true-filename.")

    def _reconfigure(self, other_model: 'str'):
        """Reconfigure filter-model
        
        Arguments:
            other_model {str} -- other model-type
        """
        self.filter = pa.filters.AdaptiveFilter(model=other_model)

    def tune(self, desired: 'ndarray', input: 'ndarray', other_model: 'str'=None)->'tuple':
        """Tune filter for fitting outputs closer to 'desired'
        
        Arguments:
            desired {ndarray} -- desired data (1-dimension matrix)
            input {ndarray} -- input data (2-dimension matrix)
        
        Keyword Arguments:
            other_model {str} -- other filter-model-type (default: {None})
        
        Returns:
            tuple -- matrixes returned by running 'AdapTuner'
        """
        if other_model is not None:
            self._reconfigure(other_model)
        return self.filter.run(desired, input)

    def get_filter_parameters(self)->'ndarray':
        """Get current filter-weights
        
        Returns:
            ndarray -- current filter-weights
        """
        return self.filter.w

    def save(self, filename: 'str'):
        """Save current filter to file
        
        Arguments:
            filename {str} -- filename or path/to/file
        """
        np.savez(filename, self.get_filter_parameters())
