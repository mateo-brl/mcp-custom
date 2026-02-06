"""Shim de retrocompatibilite. Utilisez mon_mcp.platform_api a la place."""

import warnings

warnings.warn(
    "mon_mcp.win_api est deprecie. Utilisez mon_mcp.platform_api a la place.",
    DeprecationWarning,
    stacklevel=2,
)

from mon_mcp._platform_windows import *  # noqa: F401,F403
