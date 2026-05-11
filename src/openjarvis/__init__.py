"""OpenJarvis — modular AI assistant backend with composable intelligence primitives."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openjarvis.sdk import Jarvis, JarvisSystem, MemoryHandle, SystemBuilder

try:
    __version__ = _pkg_version("openjarvis")
except PackageNotFoundError:  # pragma: no cover — uninstalled source tree
    __version__ = "0.0.0+unknown"

def __getattr__(name: str):
    if name in {"Jarvis", "JarvisSystem", "MemoryHandle", "SystemBuilder"}:
        from openjarvis.sdk import Jarvis, JarvisSystem, MemoryHandle, SystemBuilder

        exports = {
            "Jarvis": Jarvis,
            "JarvisSystem": JarvisSystem,
            "MemoryHandle": MemoryHandle,
            "SystemBuilder": SystemBuilder,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["Jarvis", "JarvisSystem", "MemoryHandle", "SystemBuilder", "__version__"]
