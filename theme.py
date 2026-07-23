"""Theme constants and reusable UI helpers for the premium HR application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

CHINESE_BLACK = "#101014"
WATERMELON_PINK = "#ff4f81"
SOFT_PINK = "#ff86a8"
CARD_DARK = "#191922"
TEXT_LIGHT = "#f8f7fb"
TEXT_MUTED = "#b9b4c7"
LIGHT_BG = "#fff5f8"
LIGHT_CARD = "#ffffff"


class Toast:
    """Small temporary notification window."""

    @staticmethod
    def show(master: tk.Misc, message: str, success: bool = True) -> None:
        """Display a toast notification near the top-right of the app."""
        root = master.winfo_toplevel()
        toast = tk.Toplevel(root)
        toast.overrideredirect(True)
        toast.configure(bg=WATERMELON_PINK if success else "#d64545")
        x = root.winfo_x() + root.winfo_width() - 360
        y = root.winfo_y() + 80
        toast.geometry(f"320x48+{max(x, 50)}+{max(y, 50)}")
        tk.Label(
            toast,
            text=message,
            bg=toast["bg"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=14,
        ).pack(fill="both", expand=True)
        toast.after(2400, toast.destroy)


def configure_tree_style() -> None:
    """Apply readable Treeview styling for dark and light mode."""
    style = ttk.Style()
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
