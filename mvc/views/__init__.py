"""View package with lazy imports for optional Tkinter dependencies."""

__all__ = ["DashboardView"]


def __getattr__(name):
	if name == "DashboardView":
		from .dashboard_view import DashboardView

		return DashboardView
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
