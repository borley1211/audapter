import numpy as np


def gen_input_from_history(desired : np.ndarray, n : int):
    d_arr = np.array(desired, dtype="float64")
    x_arr = np.array([d_arr[i:i+n] for i in range(len(d_arr)-n+1)])
    return x_arr
