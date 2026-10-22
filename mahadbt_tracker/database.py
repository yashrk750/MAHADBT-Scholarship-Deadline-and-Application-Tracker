"""SQLite persistence for students, schemes, applications, and documents."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

APP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = APP_ROOT / "data"
DB_PATH = DATA_DIR / "mahadbt.db"

CATEGORIES = [
    "SC",
    "ST",
    "OBC",
    "VJNT",
    "SBC",
    "SEBC",
    "EBC",
    "EWS",
    "Minority",
    "Open",
    "PwD",
]

APP_STATUSES = [
    "Draft",
    "Submitted",
    "Under Scrutiny",
    "Document Pending",
    "Approved",
    "Rejected",
    "Disbursed",
]

APP_TYPES = ["Fresh", "Renewal"]

SCHEME_TYPES = ["Post-Matric", "Pre-Matric", "Freeship", "Hostel", "Merit"]

DEPARTMENTS = [
    "Social Justice and Special Assistance",
    "Tribal Development",
    "Directorate of Higher Education",
    "Directorate of Technical Education",
    "VJNT, OBC and SBC Welfare",
    "Directorate of Medical Education and Research",
    "Minority Development",
    "Skill Development and Entrepreneurship",
]

DEFAULT_DOCUMENTS = [
    "Aadhaar Card",
    "Domicile Certificate",
    "Caste Certificate",
    "Income Certificate",
    "Previous Year Marksheet",
    "College Bonafide / Fee Receipt",
    "Bank Passbook (Aadhaar-seeded)",
    "CAP / Admission Letter",
]


def today_iso() -> str:
    return date.today().isoformat()


def days_until(close_date: Optional[str]) -> Optional[int]:
    if not close_date:
        return None
    try:
        close = date.fromisoformat(close_date[:10])
    except ValueError:
        return None
    return (close - date.today()).days


class Database:
    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()
        self._seed_if_empty()

    def close(self) -> None:
        self.conn.close()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                gender TEXT,
                category TEXT NOT NULL,
                aadhaar_last4 TEXT,
                email TEXT,
                phone TEXT,
                college TEXT,
                course TEXT,
                year_of_study TEXT,
                annual_income INTEGER,
                district TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS scholarships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                category TEXT,
                academic_year TEXT,
                open_date TEXT,
                close_date TEXT,
                income_limit INTEGER,
                max_amount INTEGER,
                scheme_type TEXT,
                eligibility TEXT,
                portal_url TEXT,
                is_active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                scholarship_id INTEGER NOT NULL,
                app_number TEXT,
                app_type TEXT,
                status TEXT NOT NULL,
                submitted_on TEXT,
                last_updated TEXT,
                claimed_amount INTEGER,
                remarks TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (scholarship_id) REFERENCES scholarships(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                doc_name TEXT NOT NULL,
                is_uploaded INTEGER DEFAULT 0,
                uploaded_on TEXT,
                notes TEXT,
                FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def _seed_if_empty(self) -> None:
        count = self.conn.execute("SELECT COUNT(*) FROM scholarships").fetchone()[0]
        if count:
            return
        self._seed()

    def _seed(self) -> None:
        portal = "https://mahadbt2.maharashtra.gov.in"
        year = "2026-27"
        scholarships = [
            (
                "Government of India Post-Matric Scholarship (SC)",
                "Social Justice and Special Assistance",
                "SC",
                year,
                "2026-06-01",
                "2026-09-30",
                250000,
                120000,
                "Post-Matric",
                "Maharashtra domicile, SC / Neo-Buddhist, family income up to ₹2.5 lakh, studying in a post-matric course.",
                portal,
                1,
            ),
            (
                "Post-Matric Tuition Fee and Examination Fee (Freeship)",
                "Social Justice and Special Assistance",
                "SC",
                year,
                "2026-06-01",
                "2026-09-30",
                800000,
                90000,
                "Freeship",
                "SC students whose family income is above the PMS limit; tuition and exam fee reimbursement.",
                portal,
                1,
            ),
            (
                "Post Matric Scholarship Scheme (ST) – Government of India",
                "Tribal Development",
                "ST",
                year,
                "2026-06-01",
                "2026-09-30",
                250000,
                120000,
                "Post-Matric",
                "ST students with Maharashtra domicile; maintenance allowance and fee reimbursement.",
                portal,
                1,
            ),
            (
                "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti (EBC – DHE)",
                "Directorate of Higher Education",
                "EBC",
                year,
                "2026-06-01",
                "2026-09-30",
                800000,
                50000,
                "Post-Matric",
                "Open / EBC students in non-professional UG/PG courses; income up to ₹8 lakh; 50–100% tuition and exam fee.",
                portal,
                1,
            ),
            (
                "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti (EBC – DTE)",
                "Directorate of Technical Education",
                "EBC",
                year,
                "2026-06-01",
                "2026-09-30",
                800000,
                100000,
                "Post-Matric",
                "EBC students in diploma/degree/PG technical courses admitted via CAP.",
                portal,
                1,
            ),
            (
                "Dr. Punjabrao Deshmukh Vasatigruh Nirvah Bhatta Yojna (DTE)",
                "Directorate of Technical Education",
                "EWS",
                year,
                "2026-06-01",
                "2026-10-15",
                800000,
                32000,
                "Hostel",
                "EWS/SEBC hostellers in technical courses; priority to children of marginal farmers and registered labourers.",
                portal,
                1,
            ),
            (
                "Post Matric Scholarship to OBC Students",
                "VJNT, OBC and SBC Welfare",
                "OBC",
                year,
                "2026-06-01",
                "2026-09-30",
                150000,
                60000,
                "Post-Matric",
                "OBC students, Maharashtra domicile, income ceiling as per GR; maintenance and fee support.",
                portal,
                1,
            ),
            (
                "Post Matric Scholarship to VJNT Students",
                "VJNT, OBC and SBC Welfare",
                "VJNT",
                year,
                "2026-06-01",
                "2026-09-30",
                150000,
                60000,
                "Post-Matric",
                "VJNT category students in recognised post-matric institutions.",
                portal,
                1,
            ),
            (
                "Post Matric Scholarship to SBC Students",
                "VJNT, OBC and SBC Welfare",
                "SBC",
                year,
                "2026-06-01",
                "2026-09-30",
                150000,
                60000,
                "Post-Matric",
                "SBC category students; tuition/exam support as per department GR.",
                portal,
                1,
            ),
            (
                "State Minority Scholarship Part II (DHE)",
                "Minority Development",
                "Minority",
                year,
                "2026-06-01",
                "2026-10-31",
                600000,
                5000,
                "Post-Matric",
                "Minority students in Arts/Commerce/Science/Law/Education; income up to ₹6 lakh.",
                portal,
                1,
            ),
            (
                "Scholarship for Minority Students – Higher and Professional Courses (DTE)",
                "Minority Development",
                "Minority",
                year,
                "2026-06-01",
                "2026-10-31",
                800000,
                25000,
                "Post-Matric",
                "Minority students in professional/technical courses through DTE.",
                portal,
                1,
            ),
            (
                "Post-Matric Scholarship for Persons with Disability",
                "Social Justice and Special Assistance",
                "PwD",
                year,
                "2026-06-01",
                "2026-11-15",
                800000,
                80000,
                "Post-Matric",
                "Students with benchmark disability; maintenance, fees, and disability allowances.",
                portal,
                1,
            ),
        ]
        self.conn.executemany(
            """
            INSERT INTO scholarships (
                name, department, category, academic_year, open_date, close_date,
                income_limit, max_amount, scheme_type, eligibility, portal_url, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            scholarships,
        )

        students = [
            (
                "Aarav Patil",
                "Male",
                "EBC",
                "4521",
                "aarav.patil@email.com",
                "9876543210",
                "COEP Technological University, Pune",
                "B.Tech Computer Engineering",
                "Second Year",
                420000,
                "Pune",
            ),
            (
                "Sneha Jadhav",
                "Female",
                "OBC",
                "8834",
                "sneha.jadhav@email.com",
                "9823123456",
                "Savitribai Phule Pune University",
                "B.Com",
                "Third Year",
                128000,
                "Nashik",
            ),
            (
                "Rohit Gaikwad",
                "Male",
                "SC",
                "1109",
                "rohit.gaikwad@email.com",
                "9765432109",
                "Dr. Babasaheb Ambedkar Marathwada University",
                "B.A. Political Science",
                "First Year",
                180000,
                "Chhatrapati Sambhajinagar",
            ),
            (
                "Fatima Shaikh",
                "Female",
                "Minority",
                "6672",
                "fatima.shaikh@email.com",
                "9890123456",
                "Mumbai University",
                "B.Sc. Chemistry",
                "Second Year",
                310000,
                "Mumbai",
            ),
            (
                "Aditya Pawar",
                "Male",
                "ST",
                "3340",
                "aditya.pawar@email.com",
                "9812345678",
                "Government Polytechnic, Nashik",
                "Diploma in Mechanical Engineering",
                "Third Year",
                95000,
                "Nandurbar",
            ),
            (
                "Meera Kamble",
                "Female",
                "SBC",
                "2298",
                "meera.kamble@email.com",
                "9900112233",
                "Shivaji University, Kolhapur",
                "B.Sc. Nursing",
                "First Year",
                140000,
                "Kolhapur",
            ),
        ]
        self.conn.executemany(
            """
            INSERT INTO students (
                full_name, gender, category, aadhaar_last4, email, phone,
                college, course, year_of_study, annual_income, district
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            students,
        )

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        applications = [
            (1, 5, "MDBT-2026-DTE-10021", "Renewal", "Under Scrutiny", "2026-07-12", now, 78000, "Institute scrutiny in progress"),
            (1, 6, "MDBT-2026-DTE-10088", "Fresh", "Submitted", "2026-08-02", now, 30000, "Hostel allowance claimed"),
            (2, 7, "MDBT-2026-OBC-20411", "Renewal", "Approved", "2026-07-01", now, 18500, "College verified"),
            (3, 1, "MDBT-2026-SC-33002", "Fresh", "Document Pending", "2026-08-20", now, 0, "Income certificate expired"),
            (3, 2, None, "Fresh", "Draft", None, now, 0, "Freeship form not submitted"),
            (4, 10, "MDBT-2026-MIN-44190", "Fresh", "Submitted", "2026-08-15", now, 5000, "Awaiting DHE confirmation"),
            (5, 3, "MDBT-2026-ST-55017", "Renewal", "Disbursed", "2026-06-18", now, 42000, "Amount credited to Aadhaar-seeded account"),
            (6, 9, "MDBT-2026-SBC-61204", "Fresh", "Rejected", "2026-07-28", now, 0, "Course not mapped to institute AISHE code"),
        ]
        self.conn.executemany(
            """
            INSERT INTO applications (
                student_id, scholarship_id, app_number, app_type, status,
                submitted_on, last_updated, claimed_amount, remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            applications,
        )

        docs = []
        app_ids = [row[0] for row in self.conn.execute("SELECT id FROM applications").fetchall()]
        for app_id in app_ids:
            status = self.conn.execute(
                "SELECT status FROM applications WHERE id = ?", (app_id,)
            ).fetchone()[0]
            for i, name in enumerate(DEFAULT_DOCUMENTS):
                uploaded = 1
                if status in ("Draft", "Document Pending") and i >= 4:
                    uploaded = 0
                if status == "Rejected" and i == 3:
                    uploaded = 0
                docs.append(
                    (
                        app_id,
                        name,
                        uploaded,
                        "2026-07-15" if uploaded else None,
                        "",
                    )
                )
        self.conn.executemany(
            """
            INSERT INTO documents (application_id, doc_name, is_uploaded, uploaded_on, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            docs,
        )
        self.conn.commit()

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def fetchall(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchall()

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchone()

    def list_students(self, search: str = "") -> list[sqlite3.Row]:
        if search:
            q = f"%{search.strip()}%"
            return self.fetchall(
                """
                SELECT * FROM students
                WHERE full_name LIKE ? OR college LIKE ? OR course LIKE ?
                      OR category LIKE ? OR district LIKE ?
                ORDER BY full_name
                """,
                (q, q, q, q, q),
            )
        return self.fetchall("SELECT * FROM students ORDER BY full_name")

    def add_student(self, data: dict[str, Any]) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO students (
                full_name, gender, category, aadhaar_last4, email, phone,
                college, course, year_of_study, annual_income, district
            ) VALUES (:full_name, :gender, :category, :aadhaar_last4, :email, :phone,
                      :college, :course, :year_of_study, :annual_income, :district)
            """,
            data,
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def update_student(self, student_id: int, data: dict[str, Any]) -> None:
        payload = dict(data)
        payload["id"] = student_id
        self.conn.execute(
            """
            UPDATE students SET
                full_name=:full_name, gender=:gender, category=:category,
                aadhaar_last4=:aadhaar_last4, email=:email, phone=:phone,
                college=:college, course=:course, year_of_study=:year_of_study,
                annual_income=:annual_income, district=:district
            WHERE id=:id
            """,
            payload,
        )
        self.conn.commit()

    def delete_student(self, student_id: int) -> None:
        self.execute("DELETE FROM students WHERE id = ?", (student_id,))

    def list_scholarships(self, search: str = "", active_only: bool = False) -> list[sqlite3.Row]:
        clauses = []
        params: list[Any] = []
        if search:
            q = f"%{search.strip()}%"
            clauses.append(
                "(name LIKE ? OR department LIKE ? OR category LIKE ? OR scheme_type LIKE ?)"
            )
            params.extend([q, q, q, q])
        if active_only:
            clauses.append("is_active = 1")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        return self.fetchall(
            f"SELECT * FROM scholarships {where} ORDER BY close_date, name",
            tuple(params),
        )

    def add_scholarship(self, data: dict[str, Any]) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO scholarships (
                name, department, category, academic_year, open_date, close_date,
                income_limit, max_amount, scheme_type, eligibility, portal_url, is_active
            ) VALUES (
                :name, :department, :category, :academic_year, :open_date, :close_date,
                :income_limit, :max_amount, :scheme_type, :eligibility, :portal_url, :is_active
            )
            """,
            data,
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def update_scholarship(self, scholarship_id: int, data: dict[str, Any]) -> None:
        payload = dict(data)
        payload["id"] = scholarship_id
        self.conn.execute(
            """
            UPDATE scholarships SET
                name=:name, department=:department, category=:category,
                academic_year=:academic_year, open_date=:open_date, close_date=:close_date,
                income_limit=:income_limit, max_amount=:max_amount, scheme_type=:scheme_type,
                eligibility=:eligibility, portal_url=:portal_url, is_active=:is_active
            WHERE id=:id
            """,
            payload,
        )
        self.conn.commit()

    def delete_scholarship(self, scholarship_id: int) -> None:
        self.execute("DELETE FROM scholarships WHERE id = ?", (scholarship_id,))

    def list_applications(self, search: str = "", status: str = "All") -> list[sqlite3.Row]:
        clauses = []
        params: list[Any] = []
        if search:
            q = f"%{search.strip()}%"
            clauses.append(
                "(s.full_name LIKE ? OR sc.name LIKE ? OR a.app_number LIKE ? OR a.status LIKE ?)"
            )
            params.extend([q, q, q, q])
        if status and status != "All":
            clauses.append("a.status = ?")
            params.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        return self.fetchall(
            f"""
            SELECT a.*, s.full_name AS student_name, s.category AS student_category,
                   sc.name AS scholarship_name, sc.department, sc.close_date, sc.academic_year
            FROM applications a
            JOIN students s ON s.id = a.student_id
            JOIN scholarships sc ON sc.id = a.scholarship_id
            {where}
            ORDER BY sc.close_date, s.full_name
            """,
            tuple(params),
        )

    def add_application(self, data: dict[str, Any]) -> int:
        payload = dict(data)
        payload.setdefault("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M"))
        cur = self.conn.execute(
            """
            INSERT INTO applications (
                student_id, scholarship_id, app_number, app_type, status,
                submitted_on, last_updated, claimed_amount, remarks
            ) VALUES (
                :student_id, :scholarship_id, :app_number, :app_type, :status,
                :submitted_on, :last_updated, :claimed_amount, :remarks
            )
            """,
            payload,
        )
        self.conn.commit()
        app_id = int(cur.lastrowid)
        for name in DEFAULT_DOCUMENTS:
            self.conn.execute(
                "INSERT INTO documents (application_id, doc_name, is_uploaded) VALUES (?, ?, 0)",
                (app_id, name),
            )
        self.conn.commit()
        return app_id

    def update_application(self, application_id: int, data: dict[str, Any]) -> None:
        payload = dict(data)
        payload["id"] = application_id
        payload["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.conn.execute(
            """
            UPDATE applications SET
                student_id=:student_id, scholarship_id=:scholarship_id,
                app_number=:app_number, app_type=:app_type, status=:status,
                submitted_on=:submitted_on, last_updated=:last_updated,
                claimed_amount=:claimed_amount, remarks=:remarks
            WHERE id=:id
            """,
            payload,
        )
        self.conn.commit()

    def delete_application(self, application_id: int) -> None:
        self.execute("DELETE FROM applications WHERE id = ?", (application_id,))

    def list_documents(self, application_id: Optional[int] = None, search: str = "") -> list[sqlite3.Row]:
        clauses = []
        params: list[Any] = []
        if application_id:
            clauses.append("d.application_id = ?")
            params.append(application_id)
        if search:
            q = f"%{search.strip()}%"
            clauses.append("(d.doc_name LIKE ? OR s.full_name LIKE ? OR sc.name LIKE ?)")
            params.extend([q, q, q])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        return self.fetchall(
            f"""
            SELECT d.*, s.full_name AS student_name, sc.name AS scholarship_name, a.app_number
            FROM documents d
            JOIN applications a ON a.id = d.application_id
            JOIN students s ON s.id = a.student_id
            JOIN scholarships sc ON sc.id = a.scholarship_id
            {where}
            ORDER BY s.full_name, d.doc_name
            """,
            tuple(params),
        )

    def add_document(self, data: dict[str, Any]) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO documents (application_id, doc_name, is_uploaded, uploaded_on, notes)
            VALUES (:application_id, :doc_name, :is_uploaded, :uploaded_on, :notes)
            """,
            data,
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def update_document(self, document_id: int, data: dict[str, Any]) -> None:
        payload = dict(data)
        payload["id"] = document_id
        self.conn.execute(
            """
            UPDATE documents SET
                application_id=:application_id, doc_name=:doc_name,
                is_uploaded=:is_uploaded, uploaded_on=:uploaded_on, notes=:notes
            WHERE id=:id
            """,
            payload,
        )
        self.conn.commit()

    def toggle_document(self, document_id: int, uploaded: bool) -> None:
        self.execute(
            "UPDATE documents SET is_uploaded = ?, uploaded_on = ? WHERE id = ?",
            (1 if uploaded else 0, today_iso() if uploaded else None, document_id),
        )

    def delete_document(self, document_id: int) -> None:
        self.execute("DELETE FROM documents WHERE id = ?", (document_id,))

    def dashboard_kpis(self) -> dict[str, int]:
        active = self.fetchone("SELECT COUNT(*) c FROM scholarships WHERE is_active = 1")["c"]
        apps = self.fetchone("SELECT COUNT(*) c FROM applications")["c"]
        pending = self.fetchone(
            """
            SELECT COUNT(*) c FROM applications
            WHERE status IN ('Draft', 'Submitted', 'Under Scrutiny', 'Document Pending')
            """
        )["c"]
        due = 0
        overdue = 0
        for row in self.list_applications():
            remaining = days_until(row["close_date"])
            if remaining is None:
                continue
            if row["status"] in ("Approved", "Rejected", "Disbursed"):
                continue
            if remaining < 0:
                overdue += 1
            elif remaining <= 15:
                due += 1
        missing_docs = self.fetchone("SELECT COUNT(*) c FROM documents WHERE is_uploaded = 0")["c"]
        return {
            "active_schemes": active,
            "applications": apps,
            "pending": pending,
            "due_soon": due,
            "overdue": overdue,
            "missing_docs": missing_docs,
        }

    def status_counts(self) -> list[tuple[str, int]]:
        rows = self.fetchall(
            "SELECT status, COUNT(*) c FROM applications GROUP BY status ORDER BY c DESC"
        )
        return [(r["status"], r["c"]) for r in rows]

    def department_counts(self) -> list[tuple[str, int]]:
        rows = self.fetchall(
            """
            SELECT sc.department, COUNT(*) c
            FROM applications a
            JOIN scholarships sc ON sc.id = a.scholarship_id
            GROUP BY sc.department
            ORDER BY c DESC
            """
        )
        return [(r["department"], r["c"]) for r in rows]

    def amount_by_scholarship(self) -> list[tuple[str, int]]:
        rows = self.fetchall(
            """
            SELECT sc.name, COALESCE(SUM(a.claimed_amount), 0) total
            FROM applications a
            JOIN scholarships sc ON sc.id = a.scholarship_id
            GROUP BY sc.id
            HAVING total > 0
            ORDER BY total DESC
            LIMIT 8
            """
        )
        return [(r["name"], r["total"]) for r in rows]

    def upcoming_deadlines(self, limit: int = 12) -> list[sqlite3.Row]:
        return self.fetchall(
            """
            SELECT a.id, s.full_name, sc.name AS scholarship_name, sc.close_date,
                   a.status, a.app_number, sc.department
            FROM applications a
            JOIN students s ON s.id = a.student_id
            JOIN scholarships sc ON sc.id = a.scholarship_id
            WHERE a.status NOT IN ('Approved', 'Rejected', 'Disbursed')
            ORDER BY sc.close_date
            LIMIT ?
            """,
            (limit,),
        )

    def urgent_alerts(self, within_days: int = 15) -> list[dict[str, Any]]:
        alerts = []
        for row in self.upcoming_deadlines(50):
            remaining = days_until(row["close_date"])
            if remaining is None:
                continue
            if remaining <= within_days:
                alerts.append(
                    {
                        "student": row["full_name"],
                        "scheme": row["scholarship_name"],
                        "close_date": row["close_date"],
                        "days": remaining,
                        "status": row["status"],
                    }
                )
        return alerts
