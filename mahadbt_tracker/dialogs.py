"""CRUD dialogs for students, schemes, applications, and documents."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from .database import APP_STATUSES, APP_TYPES, CATEGORIES, DEPARTMENTS, SCHEME_TYPES, Database


def _date_edit(iso: Optional[str]) -> QDateEdit:
    widget = QDateEdit()
    widget.setCalendarPopup(True)
    widget.setDisplayFormat("yyyy-MM-dd")
    if iso:
        widget.setDate(QDate.fromString(iso[:10], "yyyy-MM-dd"))
    else:
        widget.setDate(QDate.currentDate())
    return widget


def _iso(widget: QDateEdit) -> str:
    return widget.date().toString("yyyy-MM-dd")


class StudentDialog(QDialog):
    def __init__(self, parent=None, row=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Student profile")
        self.setMinimumWidth(460)
        self.name = QLineEdit()
        self.gender = QComboBox()
        self.gender.addItems(["Female", "Male", "Other"])
        self.category = QComboBox()
        self.category.addItems(CATEGORIES)
        self.aadhaar = QLineEdit()
        self.aadhaar.setMaxLength(4)
        self.aadhaar.setPlaceholderText("Last 4 digits only")
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.college = QLineEdit()
        self.course = QLineEdit()
        self.year = QComboBox()
        self.year.addItems(
            ["First Year", "Second Year", "Third Year", "Final Year", "PG First Year", "PG Second Year"]
        )
        self.income = QSpinBox()
        self.income.setRange(0, 20000000)
        self.income.setSingleStep(10000)
        self.district = QLineEdit()

        form = QFormLayout()
        form.addRow("Full name *", self.name)
        form.addRow("Gender", self.gender)
        form.addRow("Category *", self.category)
        form.addRow("Aadhaar (last 4)", self.aadhaar)
        form.addRow("Email", self.email)
        form.addRow("Phone", self.phone)
        form.addRow("College / Institute", self.college)
        form.addRow("Course", self.course)
        form.addRow("Year of study", self.year)
        form.addRow("Annual income (₹)", self.income)
        form.addRow("District", self.district)

        if row is not None:
            self.name.setText(row["full_name"])
            self.gender.setCurrentText(row["gender"] or "Female")
            self.category.setCurrentText(row["category"])
            self.aadhaar.setText(row["aadhaar_last4"] or "")
            self.email.setText(row["email"] or "")
            self.phone.setText(row["phone"] or "")
            self.college.setText(row["college"] or "")
            self.course.setText(row["course"] or "")
            self.year.setCurrentText(row["year_of_study"] or "First Year")
            self.income.setValue(int(row["annual_income"] or 0))
            self.district.setText(row["district"] or "")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        if not self.name.text().strip():
            QMessageBox.warning(self, "Required", "Student name is required.")
            return
        self.accept()

    def data(self) -> dict:
        return {
            "full_name": self.name.text().strip(),
            "gender": self.gender.currentText(),
            "category": self.category.currentText(),
            "aadhaar_last4": self.aadhaar.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "college": self.college.text().strip(),
            "course": self.course.text().strip(),
            "year_of_study": self.year.currentText(),
            "annual_income": self.income.value(),
            "district": self.district.text().strip(),
        }


class ScholarshipDialog(QDialog):
    def __init__(self, parent=None, row=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("MahaDBT scheme")
        self.setMinimumWidth(520)
        self.name = QLineEdit()
        self.department = QComboBox()
        self.department.addItems(DEPARTMENTS)
        self.department.setEditable(True)
        self.category = QComboBox()
        self.category.addItems(CATEGORIES)
        self.year = QLineEdit("2026-27")
        self.open_date = _date_edit("2026-06-01")
        self.close_date = _date_edit("2026-09-30")
        self.income_limit = QSpinBox()
        self.income_limit.setRange(0, 20000000)
        self.income_limit.setSingleStep(50000)
        self.max_amount = QSpinBox()
        self.max_amount.setRange(0, 5000000)
        self.max_amount.setSingleStep(1000)
        self.scheme_type = QComboBox()
        self.scheme_type.addItems(SCHEME_TYPES)
        self.eligibility = QTextEdit()
        self.eligibility.setFixedHeight(80)
        self.portal = QLineEdit("https://mahadbt2.maharashtra.gov.in")
        self.active = QCheckBox("Scheme is open for applications")
        self.active.setChecked(True)

        form = QFormLayout()
        form.addRow("Scheme name *", self.name)
        form.addRow("Department", self.department)
        form.addRow("Target category", self.category)
        form.addRow("Academic year", self.year)
        form.addRow("Open date", self.open_date)
        form.addRow("Close date / deadline", self.close_date)
        form.addRow("Income limit (₹)", self.income_limit)
        form.addRow("Typical max amount (₹)", self.max_amount)
        form.addRow("Scheme type", self.scheme_type)
        form.addRow("Eligibility notes", self.eligibility)
        form.addRow("Portal URL", self.portal)
        form.addRow("", self.active)

        if row is not None:
            self.name.setText(row["name"])
            self.department.setCurrentText(row["department"])
            self.category.setCurrentText(row["category"] or "Open")
            self.year.setText(row["academic_year"] or "2026-27")
            self.open_date.setDate(QDate.fromString(row["open_date"] or "2026-06-01", "yyyy-MM-dd"))
            self.close_date.setDate(QDate.fromString(row["close_date"] or "2026-09-30", "yyyy-MM-dd"))
            self.income_limit.setValue(int(row["income_limit"] or 0))
            self.max_amount.setValue(int(row["max_amount"] or 0))
            self.scheme_type.setCurrentText(row["scheme_type"] or "Post-Matric")
            self.eligibility.setPlainText(row["eligibility"] or "")
            self.portal.setText(row["portal_url"] or "")
            self.active.setChecked(bool(row["is_active"]))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        if not self.name.text().strip():
            QMessageBox.warning(self, "Required", "Scheme name is required.")
            return
        self.accept()

    def data(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "department": self.department.currentText().strip(),
            "category": self.category.currentText(),
            "academic_year": self.year.text().strip(),
            "open_date": _iso(self.open_date),
            "close_date": _iso(self.close_date),
            "income_limit": self.income_limit.value(),
            "max_amount": self.max_amount.value(),
            "scheme_type": self.scheme_type.currentText(),
            "eligibility": self.eligibility.toPlainText().strip(),
            "portal_url": self.portal.text().strip(),
            "is_active": 1 if self.active.isChecked() else 0,
        }


class ApplicationDialog(QDialog):
    def __init__(self, db: Database, parent=None, row=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Scholarship application")
        self.setMinimumWidth(520)
        self.students = db.list_students()
        self.scholarships = db.list_scholarships()
        self.student = QComboBox()
        for s in self.students:
            self.student.addItem(f"{s['full_name']} ({s['category']})", s["id"])
        self.scholarship = QComboBox()
        for sc in self.scholarships:
            self.scholarship.addItem(f"{sc['name'][:70]}", sc["id"])
        self.app_number = QLineEdit()
        self.app_number.setPlaceholderText("e.g. MDBT-2026-DTE-10021")
        self.app_type = QComboBox()
        self.app_type.addItems(APP_TYPES)
        self.status = QComboBox()
        self.status.addItems(APP_STATUSES)
        self.submitted = _date_edit(None)
        self.no_submit = QCheckBox("Not submitted yet")
        self.amount = QSpinBox()
        self.amount.setRange(0, 5000000)
        self.amount.setSingleStep(500)
        self.remarks = QTextEdit()
        self.remarks.setFixedHeight(70)

        form = QFormLayout()
        form.addRow("Student *", self.student)
        form.addRow("Scheme *", self.scholarship)
        form.addRow("Application number", self.app_number)
        form.addRow("Fresh / Renewal", self.app_type)
        form.addRow("Status", self.status)
        form.addRow("Submitted on", self.submitted)
        form.addRow("", self.no_submit)
        form.addRow("Claimed amount (₹)", self.amount)
        form.addRow("Remarks", self.remarks)

        if row is not None:
            self.student.setCurrentIndex(self.student.findData(row["student_id"]))
            self.scholarship.setCurrentIndex(self.scholarship.findData(row["scholarship_id"]))
            self.app_number.setText(row["app_number"] or "")
            self.app_type.setCurrentText(row["app_type"] or "Fresh")
            self.status.setCurrentText(row["status"])
            if row["submitted_on"]:
                self.submitted.setDate(QDate.fromString(row["submitted_on"][:10], "yyyy-MM-dd"))
                self.no_submit.setChecked(False)
            else:
                self.no_submit.setChecked(True)
            self.amount.setValue(int(row["claimed_amount"] or 0))
            self.remarks.setPlainText(row["remarks"] or "")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        if self.student.currentData() is None or self.scholarship.currentData() is None:
            QMessageBox.warning(self, "Required", "Add at least one student and one scheme first.")
            return
        self.accept()

    def data(self) -> dict:
        return {
            "student_id": self.student.currentData(),
            "scholarship_id": self.scholarship.currentData(),
            "app_number": self.app_number.text().strip() or None,
            "app_type": self.app_type.currentText(),
            "status": self.status.currentText(),
            "submitted_on": None if self.no_submit.isChecked() else _iso(self.submitted),
            "claimed_amount": self.amount.value(),
            "remarks": self.remarks.toPlainText().strip(),
        }


class DocumentDialog(QDialog):
    def __init__(self, db: Database, parent=None, row=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Document checklist item")
        self.setMinimumWidth(480)
        self.apps = db.list_applications()
        self.application = QComboBox()
        for a in self.apps:
            label = f"{a['student_name']} — {a['scholarship_name'][:40]}"
            self.application.addItem(label, a["id"])
        self.doc_name = QLineEdit()
        self.uploaded = QCheckBox("Uploaded to MahaDBT portal")
        self.uploaded_on = _date_edit(None)
        self.notes = QLineEdit()

        form = QFormLayout()
        form.addRow("Application", self.application)
        form.addRow("Document name *", self.doc_name)
        form.addRow("", self.uploaded)
        form.addRow("Uploaded on", self.uploaded_on)
        form.addRow("Notes", self.notes)

        if row is not None:
            self.application.setCurrentIndex(self.application.findData(row["application_id"]))
            self.doc_name.setText(row["doc_name"])
            self.uploaded.setChecked(bool(row["is_uploaded"]))
            if row["uploaded_on"]:
                self.uploaded_on.setDate(QDate.fromString(row["uploaded_on"][:10], "yyyy-MM-dd"))
            self.notes.setText(row["notes"] or "")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        if not self.doc_name.text().strip():
            QMessageBox.warning(self, "Required", "Document name is required.")
            return
        self.accept()

    def data(self) -> dict:
        uploaded = self.uploaded.isChecked()
        return {
            "application_id": self.application.currentData(),
            "doc_name": self.doc_name.text().strip(),
            "is_uploaded": 1 if uploaded else 0,
            "uploaded_on": _iso(self.uploaded_on) if uploaded else None,
            "notes": self.notes.text().strip(),
        }
