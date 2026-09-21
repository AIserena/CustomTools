"""Controller package with lazy imports for optional desktop dependencies."""

__all__ = ["DesktopController", "WebController"]


def __getattr__(name):
	if name == "DesktopController":
		from .desktop_controller import DesktopController

		return DesktopController
	if name == "WebController":
		from .web_controller import WebController

		return WebController
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
