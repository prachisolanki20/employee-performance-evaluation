"""Dashboard page with summary cards and charts."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

try:
    import ttkbootstrap as tb
except ImportError:
    from tkinter import ttk as tb  # type: ignore

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    Figure = None  # type: ignore[assignment]
    FigureCanvasTkAgg = None  # type: ignore[assignment]

from attendance import AttendanceFrame
from database import BASE_DIR, DB
from department import DepartmentFrame
from employee import EmployeeFrame
from evaluation import EvaluationFrame
from reports import ReportsFrame
from theme import CHINESE_BLACK, LIGHT_BG, WATERMELON_PINK, Toast


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
        ):
            tb.Button(sidebar, text=text, command=command).pack(fill="x", pady=6)
        self.content.pack(side="right", fill="both", expand=True)

    def _clear_content(self) -> None:
        """Remove current page widgets."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_home(self) -> None:
        """Display dashboard cards and charts."""
        self._clear_content()
        hero = tk.Frame(self.content, bg=CHINESE_BLACK, padx=18, pady=18)
        hero.pack(fill="x", pady=(0, 12))
        tk.Label(hero, text="🍉 HR Analytics Command Center", bg=CHINESE_BLACK, fg=WATERMELON_PINK, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(hero, text="Premium Chinese Black × Watermelon Pink performance insights", bg=CHINESE_BLACK, fg="white", font=("Segoe UI", 11)).pack(anchor="w")
        cards = tb.Frame(self.content)
        cards.pack(fill="x", pady=15)
        for title, value in self._stats().items():
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
        """Draw charts, or a helpful message when Matplotlib is unavailable."""
        if Figure is None or FigureCanvasTkAgg is None:
            tb.Label(self.content, text="Install matplotlib to view dashboard charts.", font=("Segoe UI", 12)).pack(pady=20)
            return
        department_rows = DB.fetch_all("SELECT department, COUNT(*) AS total FROM employees GROUP BY department")
        score_rows = DB.fetch_all(
            """
            SELECT e.name, ROUND(AVG(v.total_score), 2) AS score
            FROM evaluations v JOIN employees e ON e.employee_id = v.employee_id
            GROUP BY e.name
            """
        )
        fig = Figure(figsize=(9, 4), dpi=100)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        if department_rows:
            ax1.pie([row["total"] for row in department_rows], labels=[row["department"] for row in department_rows], autopct="%1.0f%%")
        ax1.set_title("Employees by Department")
        ax2.bar([row["name"].split()[0] for row in score_rows], [row["score"] for row in score_rows])
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
        self.content.configure(style="TFrame")
        background = CHINESE_BLACK if self.dark_mode else LIGHT_BG
        self.winfo_toplevel().configure(bg=background)
        Toast.show(self, f"{'Dark' if self.dark_mode else 'Light'} mode enabled")
