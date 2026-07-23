# Employee Performance Evaluation System

A professional Python desktop mini project for managing employees, recording performance evaluations, viewing analytics dashboards, and exporting reports.

## Features

- Premium Chinese Black and Watermelon Pink theme with splash screen, animated login logo, toast notifications, and dark/light mode toggle.
- Role-based login for Admin, HR, and Manager users.
- Employee management with add, update, delete, search, filters, sorting-ready table columns, and employee photo upload.
- Department/designation management and attendance tracking.
- Performance evaluation using ratings, attendance, productivity, teamwork, automatic weighted score calculation, A+/A/B+/B/C grades, and AI-style suggestions.
- Dashboard cards and charts using Matplotlib.
- Attractive PDF report generation using ReportLab with branded title and grade notes.
- Excel export using openpyxl.
- SQLite demo database with Oracle driver dependency retained for college environments that require Oracle connectivity discussion.
- Database backup support for safer demonstrations.

## Folder Structure

```text
main.py
 database.py
 login.py
 dashboard.py
 employee.py
 evaluation.py
 reports.py
 department.py
 attendance.py
 theme.py
 assets/
 requirements.txt
 README.md
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

## Demo Login

| Role | Username | Password |
| --- | --- | --- |
| Admin | admin | admin123 |
| HR | hr | hr123 |
| Manager | manager | manager123 |

## Oracle Configuration

The application works with SQLite by default. To use Oracle Database 21c XE or 23c, set these environment variables before running the app:

```bash
export ORACLE_USER=your_user
export ORACLE_PASSWORD=your_password
export ORACLE_DSN=localhost:1521/XEPDB1
```

If these variables are missing, the app creates `employee_performance.db` automatically.

## Viva Explanation

The project follows a simple layered structure. GUI modules call the centralized `DatabaseManager` in `database.py`, which performs all database operations. This keeps SQL away from button-handling logic and makes the code easier to explain, test, and maintain. The enhanced version adds HR analytics, attendance, department/designation administration, automatic grades, AI-style suggestions, backup support, and exportable reports for a polished viva demonstration.
