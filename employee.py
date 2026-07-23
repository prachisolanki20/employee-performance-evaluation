"""Employee management page supporting add, update, delete, and search."""

from __future__ import annotations

import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    import ttkbootstrap as tb
except ImportError:
    from tkinter import ttk as tb  # type: ignore

from database import BASE_DIR, DB
from theme import Toast


class EmployeeFrame(tb.Frame):
    """CRUD interface for employee records."""

    def __init__(self, master: tk.Misc) -> None:
        """Create employee form and table."""
        super().__init__(master)
        self.selected_id: int | None = None
        self.photo_path = tk.StringVar()
        self.fields = {name: tk.StringVar() for name in ("name", "department", "designation", "email", "phone", "joining_date", "status", "search")}
        self.fields["status"].set("Active")
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Render form controls and employee grid."""
        tb.Label(self, text="Employee Management", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 10))
        form = tb.Frame(self)
        form.pack(fill="x")
        labels = ["name", "department", "designation", "email", "phone", "joining_date", "status"]
        for index, key in enumerate(labels):
            tb.Label(form, text=key.replace("_", " ").title()).grid(row=index // 4 * 2, column=index % 4, sticky="w", padx=5)
            tb.Entry(form, textvariable=self.fields[key], width=24).grid(row=index // 4 * 2 + 1, column=index % 4, padx=5, pady=4)
        buttons = tb.Frame(self)
        buttons.pack(fill="x", pady=10)
        for text, command in (("Add", self.add_employee), ("Update", self.update_employee), ("Delete", self.delete_employee), ("Clear", self.clear_form)):
            tb.Button(buttons, text=text, command=command).pack(side="left", padx=4)
        tb.Entry(buttons, textvariable=self.fields["search"], width=28).pack(side="right", padx=4)
        tb.Button(buttons, text="Search", command=self.refresh).pack(side="right")
        tb.Button(buttons, text="Upload Photo", command=self.upload_photo).pack(side="left", padx=4)
        columns = ("employee_id", "name", "department", "designation", "email", "phone", "joining_date", "status", "photo_path")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for column in columns:
            self.tree.heading(column, text=column.replace("_", " ").title(), command=lambda c=column: self.sort_by(c, False))
            self.tree.column(column, width=130)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _validate(self) -> bool:
        """Validate required employee input fields."""
        required = ["name", "department", "designation", "email", "phone", "joining_date"]
        if any(not self.fields[key].get().strip() for key in required):
            messagebox.showwarning("Validation", "Please fill all required employee fields.")
            return False
        if "@" not in self.fields["email"].get():
            messagebox.showwarning("Validation", "Please enter a valid email address.")
            return False
        return True

    def upload_photo(self) -> None:
        """Copy a selected employee photo into the assets folder."""
        source = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if not source:
            return
        photo_dir = BASE_DIR / "assets" / "employee_photos"
        photo_dir.mkdir(parents=True, exist_ok=True)
        destination = photo_dir / Path(source).name
        shutil.copy2(source, destination)
        self.photo_path.set(str(destination.relative_to(BASE_DIR)))
        Toast.show(self, "Employee photo uploaded")

    def add_employee(self) -> None:
        """Insert a new employee record."""
        if not self._validate():
            return
        try:
            DB.execute(
                "INSERT INTO employees (name, department, designation, email, phone, joining_date, status, photo_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                tuple(self.fields[key].get().strip() for key in ("name", "department", "designation", "email", "phone", "joining_date", "status")) + (self.photo_path.get(),),
            )
            self.clear_form()
            self.refresh()
            Toast.show(self, "Employee added successfully")
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))

    def update_employee(self) -> None:
        """Update the selected employee record."""
        if self.selected_id is None or not self._validate():
            return
        DB.execute(
            "UPDATE employees SET name=?, department=?, designation=?, email=?, phone=?, joining_date=?, status=?, photo_path=? WHERE employee_id=?",
            tuple(self.fields[key].get().strip() for key in ("name", "department", "designation", "email", "phone", "joining_date", "status")) + (self.photo_path.get(), self.selected_id),
        )
        self.clear_form()
        self.refresh()
        Toast.show(self, "Employee updated successfully")

    def delete_employee(self) -> None:
        """Delete the selected employee record."""
        if self.selected_id is None:
            messagebox.showinfo("Delete", "Select an employee first.")
            return
        if messagebox.askyesno("Confirm", "Delete selected employee?"):
            DB.execute("DELETE FROM employees WHERE employee_id=?", (self.selected_id,))
            self.clear_form()
            self.refresh()
            Toast.show(self, "Employee deleted successfully")

    def refresh(self) -> None:
        """Reload employee table using optional search text."""
        query = "%" + self.fields["search"].get().strip() + "%"
        rows = DB.fetch_all(
            "SELECT * FROM employees WHERE name LIKE ? OR department LIKE ? OR email LIKE ? ORDER BY employee_id DESC",
            (query, query, query),
        )
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=tuple(row[column] for column in self.tree["columns"]))

    def sort_by(self, column: str, descending: bool) -> None:
        """Sort the employee table by a selected column."""
        rows = [(self.tree.set(item, column), item) for item in self.tree.get_children("")]
        rows.sort(reverse=descending)
        for index, (_value, item) in enumerate(rows):
            self.tree.move(item, "", index)
        self.tree.heading(column, command=lambda: self.sort_by(column, not descending))

    def clear_form(self) -> None:
        """Clear form fields and selection."""
        self.selected_id = None
        self.photo_path.set("")
        for key, variable in self.fields.items():
            if key != "search":
                variable.set("Active" if key == "status" else "")

    def _on_select(self, _event: tk.Event) -> None:
        """Load selected tree row into the form."""
        item = self.tree.focus()
        if not item:
            return
        values = self.tree.item(item, "values")
        self.selected_id = int(values[0])
        for key, value in zip(("name", "department", "designation", "email", "phone", "joining_date", "status"), values[1:8]):
            self.fields[key].set(value)
        self.photo_path.set(values[8] if len(values) > 8 else "")
