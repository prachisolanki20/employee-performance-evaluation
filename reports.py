"""Report generation page for Excel and PDF exports."""

from __future__ import annotations

import csv
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

try:
    import ttkbootstrap as tb
except ImportError:
    from tkinter import ttk as tb  # type: ignore

try:
    from openpyxl import Workbook
except ImportError:
    Workbook = None  # type: ignore[assignment]

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
except ImportError:
    colors = None  # type: ignore[assignment]
    A4 = None  # type: ignore[assignment]
    getSampleStyleSheet = None  # type: ignore[assignment]
    Paragraph = SimpleDocTemplate = Spacer = Table = TableStyle = None  # type: ignore[assignment]
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from database import BASE_DIR, DB

REPORT_DIR = BASE_DIR / "reports_output"


class ReportsFrame(tb.Frame):
    """Displays consolidated performance reports and exports them."""

    def __init__(self, master: tk.Misc) -> None:
        """Create report table and export buttons."""
        super().__init__(master)
        REPORT_DIR.mkdir(exist_ok=True)
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Render report controls."""
        tb.Label(self, text="Reports", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 10))
        actions = tb.Frame(self)
        actions.pack(fill="x", pady=8)
        tb.Button(actions, text="Refresh", command=self.refresh).pack(side="left", padx=4)
        tb.Button(actions, text="Export Excel", command=self.export_excel).pack(side="left", padx=4)
        tb.Button(actions, text="Export PDF", command=self.export_pdf).pack(side="left", padx=4)
        self.columns = ("employee_id", "name", "department", "designation", "evaluations", "average_score", "grade", "recommendation")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings")
        for column in self.columns:
            self.tree.heading(column, text=column.replace("_", " ").title())
            self.tree.column(column, width=135)
        self.tree.pack(fill="both", expand=True)

    def _rows(self) -> list[dict[str, object]]:
        """Return report rows with grade and recommendation."""
        rows = DB.fetch_all(
            """
            SELECT e.employee_id, e.name, e.department, e.designation,
                   COUNT(v.evaluation_id) AS evaluations,
                   ROUND(AVG(v.total_score), 2) AS average_score
                   ROUND(AVG((v.ratings+v.attendance+v.productivity+v.teamwork)/4), 2) AS average_score
            FROM employees e LEFT JOIN evaluations v ON v.employee_id = e.employee_id
            GROUP BY e.employee_id, e.name, e.department, e.designation
            ORDER BY average_score DESC
            """
        )
        for row in rows:
            score = row["average_score"] or 0
            row["grade"] = self.grade(float(score))
            row["recommendation"] = "Recommended" if float(score) >= 8 else "Not Recommended"
        return rows

    @staticmethod
    def grade(score: float) -> str:
        """Convert a 10-point score into a readable HR grade."""
        if score >= 9:
            return "A+"
        if score >= 8:
            return "A"
        if score >= 7:
            return "B+"
        if score >= 6:
            return "B"
        return "C"
        percentage = score * 10
        if percentage >= 90:
            return "Outstanding"
        if percentage >= 80:
            return "Excellent"
        if percentage >= 70:
            return "Very Good"
        if percentage >= 60:
            return "Good"
        if percentage >= 50:
            return "Average"
        return "Needs Improvement"

    def refresh(self) -> None:
        """Reload report table."""
        self.tree.delete(*self.tree.get_children())
        for row in self._rows():
            self.tree.insert("", "end", values=tuple(row[column] for column in self.columns))

    def export_excel(self) -> None:
        """Export report data to Excel, or CSV if openpyxl is unavailable."""
        if Workbook is None:
            path = self._timestamped_path("employee_report", "csv")
            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([column.replace("_", " ").title() for column in self.columns])
                writer.writerows([[row[column] for column in self.columns] for row in self._rows()])
            messagebox.showinfo("CSV Export", f"openpyxl is not installed. CSV report exported to {path}")
            return
        """Export report data to an Excel workbook."""
        path = self._timestamped_path("employee_report", "xlsx")
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Performance Report"
        sheet.append([column.replace("_", " ").title() for column in self.columns])
        for row in self._rows():
            sheet.append([row[column] for column in self.columns])
        for column_cells in sheet.columns:
            sheet.column_dimensions[column_cells[0].column_letter].width = 18
        workbook.save(path)
        messagebox.showinfo("Excel Export", f"Report exported to {path}")

    def export_pdf(self) -> None:
        """Export report data to PDF, with a text fallback when ReportLab is unavailable."""
        if SimpleDocTemplate is None or Table is None or getSampleStyleSheet is None:
            path = self._timestamped_path("employee_report", "txt")
            rows = self._rows()
            with path.open("w", encoding="utf-8") as file:
                file.write("Employee Performance Evaluation Report\n")
                file.write("Premium HR Analytics - Chinese Black x Watermelon Pink\n\n")
                for row in rows:
                    file.write(" | ".join(str(row[column]) for column in self.columns) + "\n")
            messagebox.showinfo("Text Export", f"ReportLab is not installed. Text report exported to {path}")
            return
        """Export report data to a PDF document."""
        path = self._timestamped_path("employee_report", "pdf")
        doc = SimpleDocTemplate(str(path), pagesize=A4)
        styles = getSampleStyleSheet()
        data = [[column.replace("_", " ").title() for column in self.columns]]
        data.extend([[str(row[column]) for column in self.columns] for row in self._rows()])
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ff4f81")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                ]
            )
        )
        title = Paragraph("Employee Performance Evaluation Report", styles["Title"])
        subtitle = Paragraph("Premium HR Analytics • Chinese Black × Watermelon Pink", styles["Normal"])
        grade_note = Paragraph("Grades: A+ (9-10), A (8-8.99), B+ (7-7.99), B (6-6.99), C (below 6).", styles["Normal"])
        doc.build([title, subtitle, Spacer(1, 10), grade_note, Spacer(1, 12), table])
        title = Paragraph("🍉 Employee Performance Evaluation Report", styles["Title"])
        subtitle = Paragraph("Premium HR Analytics • Chinese Black × Watermelon Pink", styles["Normal"])
        table_style_note = Paragraph("Grades: A+ (9-10), A (8-8.99), B+ (7-7.99), B (6-6.99), C (below 6).", styles["Normal"])
        doc.build([title, subtitle, Spacer(1, 10), table_style_note, Spacer(1, 12), table])
        doc.build([Paragraph("Employee Performance Evaluation Report", styles["Title"]), Spacer(1, 12), table])
        messagebox.showinfo("PDF Export", f"Report exported to {path}")

    @staticmethod
    def _timestamped_path(prefix: str, suffix: str) -> Path:
        """Build a unique report filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return REPORT_DIR / f"{prefix}_{timestamp}.{suffix}"
