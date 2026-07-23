"""Performance evaluation page for employee scoring."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

try:
    import ttkbootstrap as tb
except ImportError:
    from tkinter import ttk as tb  # type: ignore

from database import DB
from theme import Toast


class EvaluationFrame(tb.Frame):
    """Records ratings, attendance, productivity, and teamwork scores."""

    def __init__(self, master: tk.Misc) -> None:
        """Create evaluation input form."""
        super().__init__(master)
        self.employee_lookup: dict[str, int] = {}
        self.vars = {key: tk.StringVar() for key in ("employee", "period", "ratings", "attendance", "productivity", "teamwork", "remarks")}
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Render evaluation controls and history table."""
        tb.Label(self, text="Performance Evaluation", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 12))
        form = tb.Frame(self)
        form.pack(fill="x")
        tb.Label(form, text="Employee").grid(row=0, column=0, sticky="w")
        self.employee_combo = ttk.Combobox(form, textvariable=self.vars["employee"], width=28, state="readonly")
        self.employee_combo.grid(row=1, column=0, padx=5, pady=4)
        labels = ["period", "ratings", "attendance", "productivity", "teamwork", "remarks"]
        for index, key in enumerate(labels, start=1):
            tb.Label(form, text=key.title()).grid(row=(index // 4) * 2, column=index % 4, sticky="w", padx=5)
            tb.Entry(form, textvariable=self.vars[key], width=24).grid(row=(index // 4) * 2 + 1, column=index % 4, padx=5, pady=4)
        tb.Button(self, text="Save Evaluation", command=self.save).pack(anchor="w", pady=10)
        columns = ("evaluation_id", "employee", "period", "ratings", "attendance", "productivity", "teamwork", "total_score", "grade", "suggestion", "remarks")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            self.tree.heading(column, text=column.title())
            self.tree.column(column, width=120)
        self.tree.pack(fill="both", expand=True)

    def refresh(self) -> None:
        """Reload employee combo and evaluation table."""
        employees = DB.fetch_all("SELECT employee_id, name FROM employees ORDER BY name")
        self.employee_lookup = {row["name"]: row["employee_id"] for row in employees}
        self.employee_combo["values"] = list(self.employee_lookup.keys())
        rows = DB.fetch_all(
            """
            SELECT v.evaluation_id, e.name AS employee, v.period, v.ratings, v.attendance,
                   v.productivity, v.teamwork,
                   v.total_score, v.grade, v.suggestion, COALESCE(v.remarks, '') AS remarks
            FROM evaluations v JOIN employees e ON e.employee_id = v.employee_id
            ORDER BY v.evaluation_id DESC
            """
        )
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=tuple(row[column] for column in self.tree["columns"]))

    def save(self) -> None:
        """Validate and save an evaluation."""
        employee = self.vars["employee"].get()
        if employee not in self.employee_lookup:
            messagebox.showwarning("Validation", "Please select an employee.")
            return
        try:
            scores = [float(self.vars[key].get()) for key in ("ratings", "attendance", "productivity", "teamwork")]
        except ValueError:
            messagebox.showwarning("Validation", "Scores must be numeric values from 0 to 10.")
            return
        if not self.vars["period"].get().strip() or any(score < 0 or score > 10 for score in scores):
            messagebox.showwarning("Validation", "Enter period and scores between 0 and 10.")
            return
        total_score = self.calculate_score(*scores)
        grade = self.grade_for_score(total_score)
        suggestion = self.ai_suggestion(total_score, scores)
        try:
            DB.execute(
                "INSERT INTO evaluations (employee_id, period, ratings, attendance, productivity, teamwork, total_score, grade, suggestion, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.employee_lookup[employee], self.vars["period"].get().strip(), *scores, total_score, grade, suggestion, self.vars["remarks"].get().strip()),
            )
            for variable in self.vars.values():
                variable.set("")
            self.refresh()
            Toast.show(self, f"Evaluation saved: {grade} grade, score {total_score}/10")
        except Exception as exc:
            messagebox.showerror("Database Error", f"Unable to save evaluation. {exc}")

    @staticmethod
    def calculate_score(ratings: float, attendance: float, productivity: float, teamwork: float) -> float:
        """Calculate weighted automatic performance score out of 10."""
        return round((ratings * 0.30) + (attendance * 0.20) + (productivity * 0.30) + (teamwork * 0.20), 2)

    @staticmethod
    def grade_for_score(score: float) -> str:
        """Return A+, A, B+, B, or C grade for a 10-point score."""
        if score >= 9:
            return "A+"
        if score >= 8:
            return "A"
        if score >= 7:
            return "B+"
        if score >= 6:
            return "B"
        return "C"

    @staticmethod
    def ai_suggestion(score: float, scores: list[float]) -> str:
        """Generate simple AI-style performance suggestions from score patterns."""
        labels = ["ratings", "attendance", "productivity", "teamwork"]
        weakest = labels[scores.index(min(scores))]
        if score >= 9:
            return "Outstanding performer. Consider leadership tasks and promotion readiness."
        if score >= 8:
            return f"Strong performance. Improve {weakest} to reach A+ level."
        if score >= 7:
            return f"Good contributor. Provide mentoring and a focused {weakest} improvement plan."
        if score >= 6:
            return f"Average performance. Schedule monthly coaching for {weakest}."
        return f"Needs immediate support. Create a 30-day improvement plan for {weakest}."
