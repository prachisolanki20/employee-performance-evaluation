"""Login screen with role-based authentication."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

try:
    import ttkbootstrap as tb
except ImportError:
    from tkinter import ttk as tb  # type: ignore

from dashboard import DashboardFrame
from theme import CHINESE_BLACK, SOFT_PINK, WATERMELON_PINK
from database import DB


class LoginFrame(tb.Frame):
    """Login form that validates users from the database."""

    def __init__(self, master: tk.Misc) -> None:
        """Create username and password controls."""
        super().__init__(master, padding=40)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self._build_ui()

    def _build_ui(self) -> None:
        """Render login widgets."""
        self.configure(style="TFrame")
        logo = tk.Canvas(self, width=130, height=130, bg=CHINESE_BLACK, highlightthickness=0)
        logo.place(relx=0.5, rely=0.15, anchor="center")
        logo.create_oval(15, 15, 115, 115, fill=WATERMELON_PINK, outline=SOFT_PINK, width=4)
        logo.create_text(65, 65, text="HR", fill="white", font=("Segoe UI", 28, "bold"))
        self._pulse_logo(logo, 0)
        card = tb.Frame(self, padding=34)
        card.place(relx=0.5, rely=0.58, anchor="center")
        tb.Label(card, text="Employee Performance Evaluation", font=("Segoe UI", 22, "bold")).pack(pady=(0, 8))
        tb.Label(card, text="Premium HR Analytics Login", font=("Segoe UI", 12)).pack(pady=(0, 25))
        card = tb.Frame(self, padding=30)
        card.place(relx=0.5, rely=0.5, anchor="center")
        tb.Label(card, text="Employee Performance Evaluation", font=("Segoe UI", 22, "bold")).pack(pady=(0, 8))
        tb.Label(card, text="College Mini Project Login", font=("Segoe UI", 12)).pack(pady=(0, 25))
        tb.Label(card, text="Username").pack(anchor="w")
        tb.Entry(card, textvariable=self.username, width=35).pack(pady=(3, 12))
        tb.Label(card, text="Password").pack(anchor="w")
        tb.Entry(card, textvariable=self.password, show="*", width=35).pack(pady=(3, 20))
        tb.Button(card, text="Login", command=self._login).pack(fill="x")
        tb.Label(card, text="Demo: admin/admin123 | hr/hr123 | manager/manager123").pack(pady=(18, 0))

    def _login(self) -> None:
        """Validate credentials and open the dashboard."""
        user = DB.fetch_one(
            "SELECT username, role FROM users WHERE username = ? AND password = ?",
            (self.username.get().strip(), self.password.get().strip()),
        )
        if not user:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return
        self.destroy()
        DashboardFrame(self.master, user["username"], user["role"]).pack(fill="both", expand=True)


    def _pulse_logo(self, logo: tk.Canvas, step: int) -> None:
        """Animate the login logo with a gentle pulse."""
        radius = 48 + (step % 12)
        logo.delete("pulse")
        logo.create_oval(65 - radius, 65 - radius, 65 + radius, 65 + radius, outline=SOFT_PINK, width=2, tags="pulse")
        logo.after(120, lambda: self._pulse_logo(logo, step + 1))
