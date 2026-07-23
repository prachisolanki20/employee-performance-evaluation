"""Attendance tracking page."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

try:
    import ttkbootstrap as tb
except ImportError:
    from tkinter import ttk as tb  # type: ignore

from database import DB
from theme import Toast


class AttendanceFrame(tb.Frame):
    """Record daily attendance for employees."""

    def __init__(self, master: tk.Misc) -> None:
        """Create attendance form and grid."""
        super().__init__(master)
        self.employee_lookup: dict[str, int] = {}
        self.employee = tk.StringVar()
        self.attendance_date = tk.StringVar(value=date.today().isoformat())
        self.status = tk.StringVar(value="Present")
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Render attendance controls."""
        tb.Label(self, text="Attendance Tracking", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 12))
        form = tb.Frame(self)
        form.pack(fill="x", pady=8)
        self.employee_combo = ttk.Combobox(form, textvariable=self.employee, width=28, state="readonly")
        self.employee_combo.grid(row=1, column=0, padx=5)
        tb.Label(form, text="Employee").grid(row=0, column=0, sticky="w")
        tb.Label(form, text="Date (YYYY-MM-DD)").grid(row=0, column=1, sticky="w")
        tb.Entry(form, textvariable=self.attendance_date, width=18).grid(row=1, column=1, padx=5)
        tb.Label(form, text="Status").grid(row=0, column=2, sticky="w")
        ttk.Combobox(form, textvariable=self.status, values=("Present", "Absent", "Half Day", "Leave"), state="readonly", width=16).grid(row=1, column=2, padx=5)
        tb.Button(form, text="Save Attendance", command=self.save).grid(row=1, column=3, padx=8)
        columns = ("attendance_id", "employee", "attendance_date", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
        self.tree.pack(fill="both", expand=True, pady=10)

    def save(self) -> None:
        """Save or update attendance for one employee/date."""
        if self.employee.get() not in self.employee_lookup:
            messagebox.showwarning("Validation", "Please select an employee.")
            return
        DB.execute(
            "INSERT OR REPLACE INTO attendance (employee_id, attendance_date, status) VALUES (?, ?, ?)",
            (self.employee_lookup[self.employee.get()], self.attendance_date.get().strip(), self.status.get()),
        )
        self.refresh()
        Toast.show(self, "Attendance saved")

    def refresh(self) -> None:
        """Reload employee combo and attendance history."""
        employees = DB.fetch_all("SELECT employee_id, name FROM employees ORDER BY name")
        self.employee_lookup = {row["name"]: row["employee_id"] for row in employees}
        self.employee_combo["values"] = list(self.employee_lookup.keys())
        self.tree.delete(*self.tree.get_children())
        rows = DB.fetch_all(
            """
            SELECT a.attendance_id, e.name AS employee, a.attendance_date, a.status
            FROM attendance a JOIN employees e ON e.employee_id = a.employee_id
            ORDER BY a.attendance_date DESC, e.name
            """
        )
        for row in rows:
            self.tree.insert("", "end", values=tuple(row[column] for column in self.tree["columns"]))
