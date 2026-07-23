# Employee Performance Evaluation System

A professional Python desktop mini project for managing employees, recording performance evaluations, viewing analytics dashboards, and exporting reports.

## Features

- Role-based login for Admin, HR, and Manager users.
- Employee management with add, update, delete, and search.
- Performance evaluation using ratings, attendance, productivity, and teamwork scores.
- Dashboard cards and charts using Matplotlib.
- PDF report generation using ReportLab.
- Excel export using openpyxl.
- Oracle-ready database layer with automatic SQLite fallback for easy college demonstration.

## Folder Structure

```text
main.py
 database.py
 login.py
 dashboard.py
 employee.py
 evaluation.py
 reports.py
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

The project follows a simple layered structure. GUI modules call the centralized `DatabaseManager` in `database.py`, which performs all database operations. This keeps SQL away from button-handling logic and makes the code easier to explain, test, and maintain.
