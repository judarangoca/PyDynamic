# -*- coding: utf-8 -*-

"""
The :mod:`PyDynamic.uncertainty.propagate_DWT` module implements methods for
the propagation of uncertainties in the application of the discrete wavelet
transform (DWT).
"""

import pywt
import numpy as np
import scipy.signal as scs
from PyDynamic.uncertainty.propagate_filter import FIRuncFilter


__all__ = ["dwt", "wave_dec", "idwt", "wave_rec", "filter_design"]


def dwt(x, Ux, l, h, kind):
    """
    Apply low-pass `l` and high-pass `h` to time-series data `x`.
    The uncertainty is propgated through the transformation by using 
    PyDynamic.uncertainty.FIRuncFilter. and propagate

    Return the subsampled results.

    Parameters
    ----------
        x: np.ndarray
            filter input signal
        Ux: float or np.ndarray
            float:    standard deviation of white noise in x
            1D-array: interpretation depends on kind
        l: np.ndarray
            FIR filter coefficients
            representing a low-pass for decomposition
        h: np.ndarray
            FIR filter coefficients
            representing a high-pass for decomposition
        kind: string
            only meaningfull in combination with isinstance(Ux, numpy.ndarray)
            "diag": point-wise standard uncertainties of non-stationary white noise
            "corr": single sided autocovariance of stationary (colored/corrlated) noise (default)
    
    Returns
    -------
        y_approx: np.ndarray
            subsampled low-pass output signal
        U_approx: np.ndarray
            subsampled low-pass output uncertainty
        y_detail: np.ndarray
            subsampled high-pass output signal
        U_detail: np.ndarray
            subsampled high-pass output uncertainty
    """

    # propagate uncertainty through FIR-filter
    y_approx, U_approx = FIRuncFilter(x, Ux, l, Utheta=None, kind=kind)
    y_detail, U_detail = FIRuncFilter(x, Ux, h, Utheta=None, kind=kind)

    # subsample to half the length
    y_approx = y_approx[::2] 
    U_approx = U_approx[::2] 
    y_detail = y_detail[::2] 
    U_detail = U_detail[::2] 

    return y_approx, U_approx, y_detail, U_detail


def wave_dec(x, Ux, l, h, max_depth=-1, kind="corr"):
    """
    Multilevel discrete wavelet transformation of time-series x with uncertainty Ux.

    Parameters:
    -----------
        x: np.ndarray
            ...
        Ux: float or np.ndarray
            ...
        l: np.ndarray
            lowpass for wavelet_block
        h: np.ndarray
            high-pass for wavelet_block
        max_depth: int
            maximum consecutive repetitions of wavelet_block
            user is warned, if it is not possible to reach the specified maximum depth
            ignored if set to -1 (default)
        kind: string
            only meaningfull in combination with isinstance(Ux, numpy.ndarray)
            "diag": point-wise standard uncertainties of non-stationary white noise
            "corr": single sided autocovariance of stationary (colored/corrlated) noise (default)

    Returns:
    --------
        tbd, currently just a list of tuples with results of each level.
    """

    y_detail = x
    U_detail = Ux
    
    results = []
    counter = 0

    while True:
        
        # execute wavelet bloc
        y_approx, U_approx, y_detail, U_detail = dwt(y_detail, U_detail, l, h, kind)

        results.append(((y_approx, U_approx),(y_detail, U_detail)))

        # if max_depth was specified, check if it is reached
        if (max_depth != -1) and (counter >= max_depth):
            print("reached max depth")
            break
    
        # check if another iteration is possible
        if y_detail.size <= 1:

            # warn user if specified depth is deeper than achieved depth
            if counter < max_depth:
                raise UserWarning("Reached only depth of {COUNTER}, but you specified {MAX_DEPTH}".format(COUNTER=counter, MAX_DEPTH=max_depth))
            break

        counter += 1
    
    return results


def idwt(y_approx, U_approx, y_detail, U_detail, l, h, kind):
    """
    Single step of inverse discrete wavelet transform

    Parameters
    ----------
        y_approx: np.ndarray
            low-pass output signal
        U_approx: np.ndarray
            low-pass output uncertainty
        y_detail: np.ndarray
            high-pass output signal
        U_detail: np.ndarray
            high-pass output uncertainty
        l: np.ndarray
            FIR filter coefficients
            representing a low-pass for reconstruction
        h: np.ndarray
            FIR filter coefficients
            representing a high-pass for reconstruction
        kind: string
            only meaningfull in combination with isinstance(Ux, numpy.ndarray)
            "diag": point-wise standard uncertainties of non-stationary white noise
            "corr": single sided autocovariance of stationary (colored/corrlated) noise (default)
    
    Returns
    -------
        x: np.ndarray
            upsampled reconstructed signal
        Ux: np.ndarray
            upsampled uncertainty of reconstructed signal
    """

    # upsample to half the length
    indices = np.linspace(1,y_detail.size,y_detail.size)
    y_approx = np.insert(y_approx, indices, 0) 
    U_approx = np.insert(U_approx, indices, 0) 
    y_detail = np.insert(y_detail, indices, 0) 
    U_detail = np.insert(U_detail, indices, 0) 

    # propagate uncertainty through FIR-filter
    x_approx, Ux_approx = FIRuncFilter(y_approx, U_approx, l, Utheta=None, kind=kind)
    x_detail, Ux_detail = FIRuncFilter(y_detail, U_detail, h, Utheta=None, kind=kind)

    # add both parts
    x = x_detail + x_approx
    Ux = Ux_detail + Ux_approx

    return x, Ux


def wave_rec():
    pass


def filter_design(kind):
    """
    Provide low- and highpass filters suitable for discrete wavelet transformation.
    
    Parameters:
    -----------
        kind: string
            filter name, i.e. db4, coif6, gaus9, rbio3.3, ...
            supported families: pywt.families(short=False)
            supported wavelets: pywt.wavelist()

    Returns:
    --------
        ld: np.ndarray
            low-pass filter for decomposition
        hd: np.ndarray
            high-pass filter for decomposition
        lr: np.ndarray
            low-pass filter for reconstruction
        hr: np.ndarray
            high-pass filter for reconstruction
    """

    if kind in pywt.wavelist():
        w = pywt.Wavelet(kind)
        ld = np.array(w.dec_lo)
        hd = np.array(w.dec_hi)
        lr = np.array(w.rec_lo)
        hr = np.array(w.rec_hi)

        return ld, hd, lr, hr

    else:
        raise NotImplementedError("The specified wavelet-kind \"{KIND}\" is not implemented.".format(KIND=kind))
        