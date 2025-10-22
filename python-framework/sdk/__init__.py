"""Deprecated SDK shim.

This legacy package path is deprecated. Please use:

    from reasonops_sdk import ReasonOpsClient

This module re-exports the public API from `reasonops_sdk` and emits a DeprecationWarning.
"""
import warnings

warnings.warn(
    "Importing 'sdk' from 'python-framework/sdk' is deprecated. Use 'reasonops_sdk' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from reasonops_sdk import (  # type: ignore F401
    ReasonOpsClient,
    Dashboard,
    MonthlySummary,
    SLMMetrics,
    ReasonOpsError,
)

__all__ = [
    "ReasonOpsClient",
    "Dashboard",
    "MonthlySummary",
    "SLMMetrics",
    "ReasonOpsError",
]
