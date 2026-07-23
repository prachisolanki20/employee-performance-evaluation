"""Application entry point for the Employee Performance Evaluation System."""

from __future__ import annotations

import logging
import tkinter as tk

try:
    import ttkbootstrap as tb
except ImportError:  # graceful fallback for systems before dependency install
    from tkinter import ttk as tb  # type: ignore

from database import DB
from login import LoginFrame
from theme import CHINESE_BLACK, WATERMELON_PINK, configure_tree_style

logging.basicConfig(
    filename="employee_performance.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


class SplashScreen(tk.Toplevel):
    """Animated splash screen shown while the application initializes."""

    def __init__(self, master: tk.Misc) -> None:
        """Create the premium project splash window."""
        super().__init__(master)
        self.overrideredirect(True)
        self.geometry("520x300+360+180")
        self.configure(bg=CHINESE_BLACK)
        self.progress = 0
        tk.Label(self, text="🍉", bg=CHINESE_BLACK, fg=WATERMELON_PINK, font=("Segoe UI Emoji", 46)).pack(pady=(32, 5))
        tk.Label(self, text="HR Analytics Suite", bg=CHINESE_BLACK, fg="white", font=("Segoe UI", 25, "bold")).pack()
        tk.Label(self, text="Chinese Black × Watermelon Pink", bg=CHINESE_BLACK, fg=WATERMELON_PINK, font=("Segoe UI", 11)).pack(pady=8)
        self.bar = tk.Canvas(self, width=360, height=12, bg="#2a2a35", highlightthickness=0)
        self.bar.pack(pady=24)
        self.after(40, self.animate)

    def animate(self) -> None:
        """Animate splash progress bar."""
        self.progress += 8
        self.bar.delete("all")
        self.bar.create_rectangle(0, 0, min(self.progress, 360), 12, fill=WATERMELON_PINK, outline="")
        if self.progress < 360:
            self.after(35, self.animate)
        else:
            self.destroy()


WindowBase = tb.Window if hasattr(tb, "Window") else tk.Tk


class EmployeePerformanceApp(WindowBase):
    """Root desktop application window."""

    def __init__(self) -> None:
        """Initialize the root window and show the login page."""
        super().__init__(themename="darkly") if hasattr(tb, "Window") else super().__init__()
        self.withdraw()
        configure_tree_style()
        splash = SplashScreen(self)
        self.after(1700, lambda: self._show_login(splash))

    def _show_login(self, splash: SplashScreen) -> None:
        """Finish initialization and display the login page."""
        if splash.winfo_exists():
            splash.destroy()
        self.title("Employee Performance Evaluation System")
        self.geometry("1180x720")
        self.minsize(1024, 650)
        DB.initialize()
        self.deiconify()
        LoginFrame(self).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = EmployeePerformanceApp()
    app.mainloop()
