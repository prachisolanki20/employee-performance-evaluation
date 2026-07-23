"""Dashboard page with summary cards and charts."""

from __future__ import annotations

import tkinter as tk
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


class DashboardFrame(tb.Frame):
    """Main authenticated area with navigation sidebar."""

    def __init__(self, master: tk.Misc, username: str, role: str) -> None:
        """Initialize dashboard for a logged-in user."""
        super().__init__(master)
        self.username = username
        self.role = role
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

    def show_reports(self) -> None:
        """Open reports page."""
        self._clear_content()
        ReportsFrame(self.content).pack(fill="both", expand=True)
