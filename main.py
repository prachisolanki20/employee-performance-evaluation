"""Application entry point for the Employee Performance Evaluation System.

This module owns only the startup lifecycle: logging, theme setup, splash
screen, database preflight, and transition to the login view. Functional pages
live in the GUI package (preferred for the final project structure) or in the
legacy flat modules that are still present during incremental migration.
"""

from __future__ import annotations

import importlib
import logging
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from types import ModuleType
from typing import Callable, TypeAlias, cast

try:
    import ttkbootstrap as ttkb
except ImportError:  # pragma: no cover - exercised only before dependencies install.
    from tkinter import ttk as ttkb  # type: ignore[assignment]

APP_NAME = "Employee Performance Evaluation System"
APP_VERSION = "1.0.0"
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "employee_performance.log"

FrameFactory: TypeAlias = Callable[[tk.Misc], tk.Widget]


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)


class SplashScreen(tk.Toplevel):
    """Small animated splash screen shown while the app initializes."""

    def __init__(self, master: tk.Misc) -> None:
        """Create the splash window and start its progress animation."""
        super().__init__(master)
        self._progress = 0
        self._max_width = 380
        self.overrideredirect(True)
        self.configure(bg="#111827")
        self.geometry(self._center_geometry(width=560, height=320))

        tk.Label(
            self,
            text="Employee Performance\nEvaluation System",
            bg="#111827",
            fg="#f8fafc",
            font=("Segoe UI", 24, "bold"),
            justify="center",
        ).pack(pady=(44, 8))
        tk.Label(
            self,
            text="Python • Tkinter • Oracle SQL/PLSQL • Analytics",
            bg="#111827",
            fg="#60a5fa",
            font=("Segoe UI", 11),
        ).pack(pady=(0, 28))

        self._bar = tk.Canvas(
            self,
            width=self._max_width,
            height=12,
            bg="#1f2937",
            highlightthickness=0,
        )
        self._bar.pack()
        tk.Label(
            self,
            text="Loading application modules...",
            bg="#111827",
            fg="#cbd5e1",
            font=("Segoe UI", 10),
        ).pack(pady=(16, 0))
        self.after(35, self._animate)

    def _center_geometry(self, width: int, height: int) -> str:
        """Return a Tk geometry string centered on the primary display."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = max((screen_width - width) // 2, 0)
        y_position = max((screen_height - height) // 2, 0)
        return f"{width}x{height}+{x_position}+{y_position}"

    def _animate(self) -> None:
        """Advance the splash progress bar until startup is complete."""
        self._progress = min(self._progress + 10, self._max_width)
        self._bar.delete("all")
        self._bar.create_rectangle(0, 0, self._progress, 12, fill="#3b82f6", outline="")
        if self._progress < self._max_width and self.winfo_exists():
            self.after(35, self._animate)


class StartupErrorFrame(tk.Frame):
    """Friendly error screen displayed when required modules or Oracle fail."""

    def __init__(self, master: tk.Misc, title: str, details: str) -> None:
        """Render a recoverable startup error instead of crashing."""
        super().__init__(master, bg="#111827", padx=36, pady=36)
        tk.Label(
            self,
            text=title,
            bg="#111827",
            fg="#f87171",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w", pady=(0, 12))
        tk.Label(
            self,
            text=details,
            bg="#111827",
            fg="#e5e7eb",
            font=("Segoe UI", 11),
            justify="left",
            wraplength=760,
        ).pack(anchor="w")
        tk.Button(self, text="Close", command=master.destroy).pack(anchor="e", pady=(28, 0))


WindowBase = cast(type[tk.Tk], getattr(ttkb, "Window", tk.Tk))


class EmployeePerformanceApp(WindowBase):
    """Root desktop application window for the HR evaluation system."""

    def __init__(self) -> None:
        """Initialize the application shell, then load the login screen."""
        if hasattr(ttkb, "Window"):
            super().__init__(themename="darkly")
        else:
            super().__init__()
        self.withdraw()
        self.title(APP_NAME)
        self.geometry("1200x760")
        self.minsize(1024, 650)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._configure_ttk_style()
        self._splash = SplashScreen(self)
        self.after(1200, self._finish_startup)

    def _configure_ttk_style(self) -> None:
        """Apply a professional dark theme to standard ttk widgets."""
        style = ttkb.Style() if hasattr(ttkb, "Style") else None
        if style is None:
            return
        try:
            style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
            style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        except tk.TclError:
            LOGGER.debug("Unable to apply optional Treeview styling", exc_info=True)

    def _finish_startup(self) -> None:
        """Complete startup checks and mount the login frame."""
        self._destroy_splash()
        self.deiconify()
        try:
            self._initialize_database_if_available()
            login_factory = self._resolve_login_frame()
            login_factory(self).pack(fill="both", expand=True)
        except Exception as exc:  # noqa: BLE001 - startup must never crash to console.
            LOGGER.exception("Application startup failed")
            StartupErrorFrame(
                self,
                "Application could not start",
                self._format_startup_error(exc),
            ).pack(fill="both", expand=True)

    def _destroy_splash(self) -> None:
        """Close the splash window when it still exists."""
        if getattr(self, "_splash", None) is not None and self._splash.winfo_exists():
            self._splash.destroy()

    def _initialize_database_if_available(self) -> None:
        """Run the project database initializer when the database module exposes it."""
        database_module = self._import_first_available(("config.database", "database"))
        database_object = getattr(database_module, "DB", None)
        initializer = getattr(database_object, "initialize", None)
        if callable(initializer):
            initializer()

    def _resolve_login_frame(self) -> FrameFactory:
        """Return the LoginFrame class from the modular or legacy location."""
        login_module = self._import_first_available(("gui.login", "login"))
        login_frame = getattr(login_module, "LoginFrame", None)
        if login_frame is None:
            raise ImportError("LoginFrame class was not found in gui.login or login.py.")
        return cast(FrameFactory, login_frame)

    @staticmethod
    def _import_first_available(module_names: tuple[str, ...]) -> ModuleType:
        """Import the first module that exists from a list of compatible paths."""
        last_error: Exception | None = None
        for module_name in module_names:
            try:
                return importlib.import_module(module_name)
            except ModuleNotFoundError as exc:
                if exc.name != module_name:
                    raise
                last_error = exc
        searched = ", ".join(module_names)
        raise ImportError(f"None of these required modules could be imported: {searched}.") from last_error

    @staticmethod
    def _format_startup_error(error: Exception) -> str:
        """Create a user-friendly startup error message with Oracle guidance."""
        message = str(error).strip() or error.__class__.__name__
        return (
            f"Reason: {message}\n\n"
            "Please verify that all Python dependencies from requirements.txt are installed, "
            "Oracle Database is running, and the connection settings in config/database.py "
            "or database.py are correct. The application does not silently switch to another "
            "database; Oracle connection issues are shown here so they can be fixed."
        )

    def _on_close(self) -> None:
        """Ask for confirmation before closing the desktop application."""
        if messagebox.askokcancel("Exit", "Close the Employee Performance Evaluation System?"):
            LOGGER.info("Application closed by user")
            self.destroy()


def main() -> int:
    """Start the Tkinter event loop and return a process exit status."""
    try:
        app = EmployeePerformanceApp()
        app.mainloop()
        return 0
    except tk.TclError as exc:
        LOGGER.exception("Tkinter could not create the application window")
        print(f"Unable to start the graphical interface: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
