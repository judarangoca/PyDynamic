# -*- coding: utf-8 -*-
"""
.. deprecated:: 2.0.0
    The module *identification* is combined with the module *deconvolution* and
    renamed to :mod:`PyDynamic.model_estimation` since the last major release 2.0.0.
    *identification* might be removed any time. Please switch to the current module
    immediately.
"""

import warnings


warning = (
    "The module *identification* is combined with the module *deconvolution* and "
    "renamed to :mod:`PyDynamic.model_estimation` since the last major release 2.0.0. "
    "*identification* might be removed any time. Please switch to the current module "
    "immediately. Please use the current function name "
)

__all__ = ["fit_sos"]


def fit_sos(**kwargs):
    """.. deprecated:: 1.4.1 Please use :func:`PyDynamic.model_estimation.fit_som`"""
    warnings.warn(
        f"{warning}:func:`PyDynamic.model_estimation.fit_som`.", DeprecationWarning
    )
