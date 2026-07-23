"""Application entry point for the Employee Performance Evaluation System."""

from __future__ import annotations

import logging

try:
    import ttkbootstrap as tb
except ImportError:  # graceful fallback for systems before dependency install
    import tkinter as tb  # type: ignore

from database import DB
from login import LoginFrame

logging.basicConfig(
    filename="employee_performance.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


class EmployeePerformanceApp(tb.Window):
    """Root desktop application window."""

    def __init__(self) -> None:
        """Initialize the root window and show the login page."""
        super().__init__(themename="darkly") if hasattr(tb, "Window") else super().__init__()
        self.title("Employee Performance Evaluation System")
        self.geometry("1180x720")
        self.minsize(1024, 650)
        DB.initialize()
        LoginFrame(self).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = EmployeePerformanceApp()
    app.mainloop()
