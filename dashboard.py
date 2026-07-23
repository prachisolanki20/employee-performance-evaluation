"""Dashboard page with summary cards and charts."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from tkinter import ttk

try:
    import ttkbootstrap as tb
except ImportError:
    from tkinter import ttk as tb  # type: ignore

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from database import DB
from employee import EmployeeFrame
from evaluation import EvaluationFrame
from reports import ReportsFrame
from department import DepartmentFrame
from attendance import AttendanceFrame
from database import BASE_DIR
from theme import CHINESE_BLACK, WATERMELON_PINK, Toast


class DashboardFrame(tb.Frame):
    """Main authenticated area with navigation sidebar."""

    def __init__(self, master: tk.Misc, username: str, role: str) -> None:
        """Initialize dashboard for a logged-in user."""
        super().__init__(master)
        self.username = username
        self.role = role
        self.dark_mode = True
        self.content = tb.Frame(self, padding=18)
        self._build_layout()
        self.show_home()

    def _build_layout(self) -> None:
        """Create sidebar and content container."""
        sidebar = tb.Frame(self, padding=16)
        sidebar.pack(side="left", fill="y")
        tb.Label(sidebar, text="HR System", font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))
        tb.Label(sidebar, text=f"{self.username} ({self.role})").pack(pady=(0, 20))
        for text, command in (
            ("Dashboard", self.show_home),
            ("Employees", self.show_employees),
            ("Evaluations", self.show_evaluations),
            ("Departments", self.show_departments),
            ("Attendance", self.show_attendance),
            ("Reports", self.show_reports),
            ("Backup DB", self.backup_database),
            ("Restore DB", self.restore_database),
            ("Toggle Theme", self.toggle_theme),
            ("Reports", self.show_reports),
        ):
            tb.Button(sidebar, text=text, command=command).pack(fill="x", pady=6)
        self.content.pack(side="right", fill="both", expand=True)

    def _clear_content(self) -> None:
        """Remove current page widgets."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_home(self) -> None:
        """Display dashboard cards and matplotlib charts."""
        self._clear_content()
        hero = tb.Frame(self.content, padding=18)
        hero.pack(fill="x", pady=(0, 12))
        tk.Label(hero, text="🍉 HR Analytics Command Center", bg=CHINESE_BLACK, fg=WATERMELON_PINK, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(hero, text="Premium Chinese Black × Watermelon Pink performance insights", bg=CHINESE_BLACK, fg="white", font=("Segoe UI", 11)).pack(anchor="w")
        tb.Label(self.content, text="Dashboard", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        stats = self._stats()
        cards = tb.Frame(self.content)
        cards.pack(fill="x", pady=15)
        for title, value in stats.items():
            card = tb.Frame(cards, padding=18)
            card.pack(side="left", fill="x", expand=True, padx=6)
            tb.Label(card, text=title, font=("Segoe UI", 11)).pack()
            tb.Label(card, text=str(value), font=("Segoe UI", 24, "bold")).pack()
        self._draw_charts()

    def _stats(self) -> dict[str, object]:
        """Calculate dashboard metrics from the database."""
        employees = DB.fetch_one("SELECT COUNT(*) AS total FROM employees") or {"total": 0}
        evaluations = DB.fetch_one("SELECT COUNT(*) AS total FROM evaluations") or {"total": 0}
        avg = DB.fetch_one("SELECT ROUND(AVG(total_score), 2) AS score FROM evaluations")
        top = DB.fetch_one(
            """
            SELECT e.name AS name, ROUND(AVG(v.total_score), 2) AS score
        avg = DB.fetch_one("SELECT ROUND(AVG((ratings+attendance+productivity+teamwork)/4), 2) AS score FROM evaluations")
        top = DB.fetch_one(
            """
            SELECT e.name AS name, ROUND(AVG((v.ratings+v.attendance+v.productivity+v.teamwork)/4), 2) AS score
            FROM evaluations v JOIN employees e ON e.employee_id = v.employee_id
            GROUP BY e.employee_id, e.name ORDER BY score DESC LIMIT 1
            """
        )
        return {
            "Employees": employees["total"],
            "Evaluations": evaluations["total"],
            "Average Score": (avg or {}).get("score") or 0,
            "Top Performer": f"{top['name']} ({top['score']})" if top else "Pending",
        }

    def _draw_charts(self) -> None:
        """Draw department and score distribution charts."""
        rows = DB.fetch_all("SELECT department, COUNT(*) AS total FROM employees GROUP BY department")
        fig = Figure(figsize=(9, 4), dpi=100)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        if rows:
            ax1.pie([row["total"] for row in rows], labels=[row["department"] for row in rows], autopct="%1.0f%%")
        ax1.set_title("Employees by Department")
        scores = DB.fetch_all(
            "SELECT e.name, ROUND(AVG(v.total_score), 2) AS score FROM evaluations v JOIN employees e ON e.employee_id = v.employee_id GROUP BY e.name"
            "SELECT e.name, ROUND(AVG((v.ratings+v.attendance+v.productivity+v.teamwork)/4), 2) AS score FROM evaluations v JOIN employees e ON e.employee_id = v.employee_id GROUP BY e.name"
        )
        ax2.bar([row["name"].split()[0] for row in scores], [row["score"] for row in scores])
        ax2.set_ylim(0, 10)
        ax2.set_title("Average Performance")
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=12)

    def show_employees(self) -> None:
        """Open employee management page."""
        self._clear_content()
        EmployeeFrame(self.content).pack(fill="both", expand=True)

    def show_evaluations(self) -> None:
        """Open performance evaluation page."""
        self._clear_content()
        EvaluationFrame(self.content).pack(fill="both", expand=True)

    def show_departments(self) -> None:
        """Open department and designation management page."""
        self._clear_content()
        DepartmentFrame(self.content).pack(fill="both", expand=True)

    def show_attendance(self) -> None:
        """Open attendance tracking page."""
        self._clear_content()
        AttendanceFrame(self.content).pack(fill="both", expand=True)

    def show_reports(self) -> None:
        """Open reports page."""
        self._clear_content()
        ReportsFrame(self.content).pack(fill="both", expand=True)

    def backup_database(self) -> None:
        """Create a timestamped database backup."""
        from datetime import datetime

        path = DB.backup(BASE_DIR / "backups" / f"employee_performance_{datetime.now():%Y%m%d_%H%M%S}.db")
        Toast.show(self, f"Database backup created: {path.name}")

    def restore_database(self) -> None:
        """Restore database from a selected backup file."""
        source = filedialog.askopenfilename(filetypes=[("SQLite Backup", "*.db"), ("All Files", "*.*")])
        if not source:
            return
        DB.restore(Path(source))
        Toast.show(self, "Database restored successfully")
        self.show_home()

    def toggle_theme(self) -> None:
        """Toggle between dark presentation mode and light mode."""
        self.dark_mode = not self.dark_mode
        color = CHINESE_BLACK if self.dark_mode else "#fff5f8"
        self.configure(style="TFrame")
        self.content.configure(style="TFrame")
        Toast.show(self, f"{'Dark' if self.dark_mode else 'Light'} mode enabled")
