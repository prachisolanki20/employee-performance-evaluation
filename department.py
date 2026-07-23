"""Department and designation management page."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

try:
    import ttkbootstrap as tb
except ImportError:
    from tkinter import ttk as tb  # type: ignore

from database import DB
from theme import Toast


class DepartmentFrame(tb.Frame):
    """Manage departments, managers, and designations."""

    def __init__(self, master: tk.Misc) -> None:
        """Initialize department management form."""
        super().__init__(master)
        self.department = tk.StringVar()
        self.manager = tk.StringVar()
        self.designation = tk.StringVar()
        self.designation_department = tk.StringVar()
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Build department and designation controls."""
        tb.Label(self, text="Department & Designation Management", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 12))
        form = tb.Frame(self)
        form.pack(fill="x", pady=8)
        tb.Label(form, text="Department").grid(row=0, column=0, sticky="w")
        tb.Entry(form, textvariable=self.department, width=24).grid(row=1, column=0, padx=5)
        tb.Label(form, text="Manager").grid(row=0, column=1, sticky="w")
        tb.Entry(form, textvariable=self.manager, width=24).grid(row=1, column=1, padx=5)
        tb.Button(form, text="Save Department", command=self.save_department).grid(row=1, column=2, padx=8)
        tb.Label(form, text="Designation").grid(row=2, column=0, sticky="w", pady=(12, 0))
        tb.Entry(form, textvariable=self.designation, width=24).grid(row=3, column=0, padx=5)
        tb.Label(form, text="Department Name").grid(row=2, column=1, sticky="w", pady=(12, 0))
        tb.Entry(form, textvariable=self.designation_department, width=24).grid(row=3, column=1, padx=5)
        tb.Button(form, text="Save Designation", command=self.save_designation).grid(row=3, column=2, padx=8)
        self.dept_tree = ttk.Treeview(self, columns=("department_id", "department_name", "manager_name"), show="headings", height=7)
        for col in self.dept_tree["columns"]:
            self.dept_tree.heading(col, text=col.replace("_", " ").title())
        self.dept_tree.pack(fill="x", pady=10)
        self.desig_tree = ttk.Treeview(self, columns=("designation_id", "designation_name", "department_name"), show="headings", height=7)
        for col in self.desig_tree["columns"]:
            self.desig_tree.heading(col, text=col.replace("_", " ").title())
        self.desig_tree.pack(fill="both", expand=True)

    def save_department(self) -> None:
        """Insert or update a department."""
        if not self.department.get().strip():
            messagebox.showwarning("Validation", "Department name is required.")
            return
        DB.execute(
            "INSERT OR REPLACE INTO departments (department_name, manager_name) VALUES (?, ?)",
            (self.department.get().strip(), self.manager.get().strip() or "Not Assigned"),
        )
        self.department.set("")
        self.manager.set("")
        self.refresh()
        Toast.show(self, "Department saved successfully")

    def save_designation(self) -> None:
        """Insert or update a designation."""
        if not self.designation.get().strip() or not self.designation_department.get().strip():
            messagebox.showwarning("Validation", "Designation and department are required.")
            return
        DB.execute(
            "INSERT OR REPLACE INTO designations (designation_name, department_name) VALUES (?, ?)",
            (self.designation.get().strip(), self.designation_department.get().strip()),
        )
        self.designation.set("")
        self.designation_department.set("")
        self.refresh()
        Toast.show(self, "Designation saved successfully")

    def refresh(self) -> None:
        """Reload both management tables."""
        self.dept_tree.delete(*self.dept_tree.get_children())
        for row in DB.fetch_all("SELECT * FROM departments ORDER BY department_name"):
            self.dept_tree.insert("", "end", values=(row["department_id"], row["department_name"], row["manager_name"]))
        self.desig_tree.delete(*self.desig_tree.get_children())
        for row in DB.fetch_all("SELECT * FROM designations ORDER BY designation_name"):
            self.desig_tree.insert("", "end", values=(row["designation_id"], row["designation_name"], row["department_name"]))
