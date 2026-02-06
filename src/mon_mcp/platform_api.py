"""Couche d'abstraction plateforme - route vers le bon backend."""

import sys

if sys.platform == "win32":
    from mon_mcp._platform_windows import *  # noqa: F401,F403
elif sys.platform == "linux":
    from mon_mcp._platform_linux import *  # noqa: F401,F403
else:
    from mon_mcp._platform_stub import *  # noqa: F401,F403
