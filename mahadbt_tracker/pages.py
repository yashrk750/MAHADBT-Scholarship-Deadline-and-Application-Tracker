"""Main pages: dashboard, students, schemes, applications, documents, reports."""

from __future__ import annotations

import csv
from typing import Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .database import APP_STATUSES, Database, days_until
from .dialogs import ApplicationDialog, DocumentDialog, ScholarshipDialog, StudentDialog


def inr(value) -> str:
    try:
        n = int(value or 0)
    except (TypeError, ValueError):
        return "₹0"
    return f"₹{n:,}"


def card(title: str, widget: QWidget) -> QFrame:
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    heading = QLabel(title)
    heading.setStyleSheet("font-weight: 700; color: #0B3D3A; font-size: 14px;")
    layout.addWidget(heading)
    layout.addWidget(widget)
    return frame


def kpi_card(label: str, value: str, accent: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    value_lbl = QLabel(value)
    value_lbl.setObjectName("KpiValue")
    value_lbl.setStyleSheet(f"color: {accent};")
    caption = QLabel(label)
    caption.setObjectName("KpiLabel")
    layout.addWidget(value_lbl)
    layout.addWidget(caption)
    return frame


def fill_table(table: QTableWidget, headers: list[str], rows: list[list], ids: list[int]) -> None:
    table.clear()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    table.setAlternatingRowColors(True)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    for r, row in enumerate(rows):
        table.setItem(r, 0, QTableWidgetItem(str(ids[r])))
        table.item(r, 0).setData(Qt.UserRole, ids[r])
        for c, value in enumerate(row):
            item = QTableWidgetItem(str(value) if value is not None else "")
            table.setItem(r, c + 1, item)
    table.setColumnHidden(0, True)


def selected_id(table: QTableWidget) -> Optional[int]:
    row = table.currentRow()
    if row < 0:
        return None
    item = table.item(row, 0)
    return None if item is None else int(item.data(Qt.UserRole))


class ChartCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None) -> None:
        self.fig = Figure(figsize=(5, 3.2), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.patch.set_facecolor("#FFFFFF")

    def pie(self, labels: list[str], values: list[int], title: str) -> None:
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_title(title, fontsize=11, color="#0B3D3A", pad=10)
        if not values or sum(values) == 0:
            ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
            ax.axis("off")
        else:
            colors = ["#0F5C56", "#E07A2F", "#2A9D8F", "#E9C46A", "#264653", "#E76F51", "#8AB17D"]
            ax.pie(values, labels=labels, autopct="%1.0f%%", colors=colors[: len(values)], startangle=90)
        self.fig.tight_layout()
        self.draw()

    def bar(self, labels: list[str], values: list[int], title: str, ylabel: str = "") -> None:
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#FFFFFF")
        ax.set_title(title, fontsize=11, color="#0B3D3A", pad=10)
        if not values:
            ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
            ax.axis("off")
        else:
            short = [lbl if len(lbl) < 28 else lbl[:25] + "…" for lbl in labels]
            bars = ax.barh(short[::-1], values[::-1], color="#0F5C56")
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height() / 2, f" {int(width):,}", va="center", fontsize=8)
            ax.set_xlabel(ylabel)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        self.fig.tight_layout()
        self.draw()


class DashboardPage(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        self.kpi_row = QHBoxLayout()
        layout.addLayout(self.kpi_row)

        charts = QHBoxLayout()
        self.status_chart = ChartCanvas()
        self.dept_chart = ChartCanvas()
        charts.addWidget(card("Applications by status", self.status_chart), 1)
        charts.addWidget(card("Applications by department", self.dept_chart), 1)
        layout.addLayout(charts)

        self.deadline_table = QTableWidget()
        layout.addWidget(card("Open applications approaching MahaDBT deadlines", self.deadline_table), 1)
        self.reload()

    def reload(self) -> None:
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        kpis = self.db.dashboard_kpis()
        tiles = [
            ("Active schemes", str(kpis["active_schemes"]), "#0F5C56"),
            ("Total applications", str(kpis["applications"]), "#0B3D3A"),
            ("In process", str(kpis["pending"]), "#E07A2F"),
            ("Due within 15 days", str(kpis["due_soon"]), "#C2410C"),
            ("Overdue", str(kpis["overdue"]), "#B42318"),
            ("Missing documents", str(kpis["missing_docs"]), "#7A2E0E"),
        ]
        for label, value, color in tiles:
            self.kpi_row.addWidget(kpi_card(label, value, color))

        status = self.db.status_counts()
        self.status_chart.pie([s for s, _ in status], [c for _, c in status], "")
        depts = self.db.department_counts()
        self.dept_chart.bar([d.split(",")[0][:40] for d, _ in depts], [c for _, c in depts], "", "Applications")

        rows = []
        ids = []
        for row in self.db.upcoming_deadlines():
            remaining = days_until(row["close_date"])
            if remaining is None:
                label = "—"
            elif remaining < 0:
                label = f"Overdue by {-remaining} days"
            elif remaining == 0:
                label = "Closes today"
            else:
                label = f"{remaining} days left"
            rows.append(
                [
                    row["full_name"],
                    row["scholarship_name"],
                    row["department"],
                    row["status"],
                    row["close_date"],
                    label,
                    row["app_number"] or "—",
                ]
            )
            ids.append(row["id"])
        fill_table(
            self.deadline_table,
            ["ID", "Student", "Scheme", "Department", "Status", "Deadline", "Countdown", "App no."],
            rows,
            ids,
        )
        for r, row in enumerate(self.db.upcoming_deadlines()):
            remaining = days_until(row["close_date"])
            item = self.deadline_table.item(r, 6)
            if item is None or remaining is None:
                continue
            if remaining < 0:
                item.setForeground(QColor("#B42318"))
            elif remaining <= 7:
                item.setForeground(QColor("#C2410C"))
            elif remaining <= 15:
                item.setForeground(QColor("#B45309"))
            else:
                item.setForeground(QColor("#0F5C56"))


class CrudPage(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search…")
        self.search.textChanged.connect(self.reload)
        toolbar.addWidget(self.search, 1)
        self.extra_filter: Optional[QComboBox] = None
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setObjectName("Ghost")
        self.del_btn = QPushButton("Delete")
        self.del_btn.setObjectName("Danger")
        self.add_btn.clicked.connect(self.add_item)
        self.edit_btn.clicked.connect(self.edit_item)
        self.del_btn.clicked.connect(self.delete_item)
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.del_btn)
        layout.addLayout(toolbar)
        self.table = QTableWidget()
        self.table.doubleClicked.connect(self.edit_item)
        layout.addWidget(self.table)
        self.toolbar = toolbar

    def confirm_delete(self, label: str) -> bool:
        return (
            QMessageBox.question(self, "Delete", f"Delete this {label}? This cannot be undone.")
            == QMessageBox.Yes
        )

    def add_item(self) -> None:
        raise NotImplementedError

    def edit_item(self) -> None:
        raise NotImplementedError

    def delete_item(self) -> None:
        raise NotImplementedError

    def reload(self) -> None:
        raise NotImplementedError

    def require_id(self) -> Optional[int]:
        row_id = selected_id(self.table)
        if row_id is None:
            QMessageBox.information(self, "Select a row", "Please select a record first.")
        return row_id


class StudentsPage(CrudPage):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.search.setPlaceholderText("Search by name, college, course, category, or district")
        self.reload()

    def reload(self) -> None:
        rows, ids = [], []
        for s in self.db.list_students(self.search.text()):
            ids.append(s["id"])
            rows.append(
                [
                    s["full_name"],
                    s["category"],
                    s["gender"],
                    s["course"],
                    s["year_of_study"],
                    s["college"],
                    s["district"],
                    inr(s["annual_income"]),
                    s["phone"],
                ]
            )
        fill_table(
            self.table,
            ["ID", "Name", "Category", "Gender", "Course", "Year", "College", "District", "Income", "Phone"],
            rows,
            ids,
        )

    def add_item(self) -> None:
        dlg = StudentDialog(self)
        if dlg.exec():
            self.db.add_student(dlg.data())
            self.reload()

    def edit_item(self) -> None:
        row_id = self.require_id()
        if row_id is None:
            return
        row = self.db.fetchone("SELECT * FROM students WHERE id = ?", (row_id,))
        dlg = StudentDialog(self, row)
        if dlg.exec():
            self.db.update_student(row_id, dlg.data())
            self.reload()

    def delete_item(self) -> None:
        row_id = self.require_id()
        if row_id is None or not self.confirm_delete("student and linked applications"):
            return
        self.db.delete_student(row_id)
        self.reload()


class ScholarshipsPage(CrudPage):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.search.setPlaceholderText("Search schemes by name, department, category, or type")
        self.portal_btn = QPushButton("Open MahaDBT 2.0")
        self.portal_btn.setObjectName("Ghost")
        self.portal_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://mahadbt2.maharashtra.gov.in"))
        )
        self.toolbar.addWidget(self.portal_btn)
        self.reload()

    def reload(self) -> None:
        rows, ids = [], []
        for s in self.db.list_scholarships(self.search.text()):
            remaining = days_until(s["close_date"])
            if remaining is None:
                countdown = "—"
            elif remaining < 0:
                countdown = f"Closed ({-remaining}d ago)"
            else:
                countdown = f"{remaining} days left"
            ids.append(s["id"])
            rows.append(
                [
                    s["name"],
                    s["department"],
                    s["category"],
                    s["scheme_type"],
                    s["academic_year"],
                    s["open_date"],
                    s["close_date"],
                    countdown,
                    inr(s["income_limit"]),
                    inr(s["max_amount"]),
                    "Open" if s["is_active"] else "Inactive",
                ]
            )
        fill_table(
            self.table,
            [
                "ID",
                "Scheme",
                "Department",
                "Category",
                "Type",
                "Year",
                "Opens",
                "Deadline",
                "Countdown",
                "Income limit",
                "Max amount",
                "Status",
            ],
            rows,
            ids,
        )
        for r, s in enumerate(self.db.list_scholarships(self.search.text())):
            remaining = days_until(s["close_date"])
            item = self.table.item(r, 8)
            if item is None or remaining is None:
                continue
            if remaining < 0:
                item.setForeground(QColor("#B42318"))
            elif remaining <= 15:
                item.setForeground(QColor("#C2410C"))

    def add_item(self) -> None:
        dlg = ScholarshipDialog(self)
        if dlg.exec():
            self.db.add_scholarship(dlg.data())
            self.reload()

    def edit_item(self) -> None:
        row_id = self.require_id()
        if row_id is None:
            return
        row = self.db.fetchone("SELECT * FROM scholarships WHERE id = ?", (row_id,))
        dlg = ScholarshipDialog(self, row)
        if dlg.exec():
            self.db.update_scholarship(row_id, dlg.data())
            self.reload()

    def delete_item(self) -> None:
        row_id = self.require_id()
        if row_id is None or not self.confirm_delete("scheme and linked applications"):
            return
        self.db.delete_scholarship(row_id)
        self.reload()


class ApplicationsPage(CrudPage):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.search.setPlaceholderText("Search by student, scheme, application number, or status")
        self.extra_filter = QComboBox()
        self.extra_filter.addItems(["All"] + APP_STATUSES)
        self.extra_filter.currentTextChanged.connect(self.reload)
        self.toolbar.insertWidget(1, self.extra_filter)
        self.reload()

    def reload(self) -> None:
        rows, ids = [], []
        for a in self.db.list_applications(self.search.text(), self.extra_filter.currentText()):
            remaining = days_until(a["close_date"])
            countdown = "—" if remaining is None else (f"{remaining}d" if remaining >= 0 else f"Overdue {-remaining}d")
            ids.append(a["id"])
            rows.append(
                [
                    a["student_name"],
                    a["scholarship_name"],
                    a["app_number"] or "—",
                    a["app_type"],
                    a["status"],
                    a["submitted_on"] or "—",
                    a["close_date"],
                    countdown,
                    inr(a["claimed_amount"]),
                    a["remarks"] or "",
                ]
            )
        fill_table(
            self.table,
            [
                "ID",
                "Student",
                "Scheme",
                "App no.",
                "Type",
                "Status",
                "Submitted",
                "Deadline",
                "Countdown",
                "Amount",
                "Remarks",
            ],
            rows,
            ids,
        )

    def add_item(self) -> None:
        dlg = ApplicationDialog(self.db, self)
        if dlg.exec():
            self.db.add_application(dlg.data())
            self.reload()

    def edit_item(self) -> None:
        row_id = self.require_id()
        if row_id is None:
            return
        row = self.db.fetchone("SELECT * FROM applications WHERE id = ?", (row_id,))
        dlg = ApplicationDialog(self.db, self, row)
        if dlg.exec():
            self.db.update_application(row_id, dlg.data())
            self.reload()

    def delete_item(self) -> None:
        row_id = self.require_id()
        if row_id is None or not self.confirm_delete("application"):
            return
        self.db.delete_application(row_id)
        self.reload()


class DocumentsPage(CrudPage):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.search.setPlaceholderText("Search documents, students, or schemes")
        self.toggle_btn = QPushButton("Mark uploaded / pending")
        self.toggle_btn.setObjectName("Ghost")
        self.toggle_btn.clicked.connect(self.toggle_upload)
        self.toolbar.addWidget(self.toggle_btn)
        self.reload()

    def reload(self) -> None:
        rows, ids = [], []
        for d in self.db.list_documents(search=self.search.text()):
            ids.append(d["id"])
            rows.append(
                [
                    d["student_name"],
                    d["scholarship_name"],
                    d["app_number"] or "—",
                    d["doc_name"],
                    "Uploaded" if d["is_uploaded"] else "Pending",
                    d["uploaded_on"] or "—",
                    d["notes"] or "",
                ]
            )
        fill_table(
            self.table,
            ["ID", "Student", "Scheme", "App no.", "Document", "Status", "Uploaded on", "Notes"],
            rows,
            ids,
        )
        for r, d in enumerate(self.db.list_documents(search=self.search.text())):
            item = self.table.item(r, 5)
            if item is None:
                continue
            item.setForeground(QColor("#0F5C56") if d["is_uploaded"] else QColor("#B42318"))

    def add_item(self) -> None:
        dlg = DocumentDialog(self.db, self)
        if dlg.exec():
            self.db.add_document(dlg.data())
            self.reload()

    def edit_item(self) -> None:
        row_id = self.require_id()
        if row_id is None:
            return
        row = self.db.fetchone("SELECT * FROM documents WHERE id = ?", (row_id,))
        dlg = DocumentDialog(self.db, self, row)
        if dlg.exec():
            self.db.update_document(row_id, dlg.data())
            self.reload()

    def delete_item(self) -> None:
        row_id = self.require_id()
        if row_id is None or not self.confirm_delete("document item"):
            return
        self.db.delete_document(row_id)
        self.reload()

    def toggle_upload(self) -> None:
        row_id = self.require_id()
        if row_id is None:
            return
        row = self.db.fetchone("SELECT * FROM documents WHERE id = ?", (row_id,))
        self.db.toggle_document(row_id, not bool(row["is_uploaded"]))
        self.reload()


class ReportsPage(QWidget):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db
        layout = QVBoxLayout(self)
        actions = QHBoxLayout()
        export_btn = QPushButton("Export applications to CSV")
        export_btn.clicked.connect(self.export_csv)
        actions.addWidget(export_btn)
        actions.addStretch()
        layout.addLayout(actions)
        charts = QGridLayout()
        self.amount_chart = ChartCanvas()
        self.status_chart = ChartCanvas()
        charts.addWidget(card("Claimed amount by scheme", self.amount_chart), 0, 0)
        charts.addWidget(card("Application pipeline", self.status_chart), 0, 1)
        layout.addLayout(charts)
        self.reload()

    def reload(self) -> None:
        amounts = self.db.amount_by_scholarship()
        self.amount_chart.bar(
            [n.split("(")[0].strip() for n, _ in amounts],
            [v for _, v in amounts],
            "",
            "₹ claimed",
        )
        status = self.db.status_counts()
        self.status_chart.bar([s for s, _ in status], [c for _, c in status], "", "Applications")

    def export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export applications", "mahadbt_applications.csv", "CSV files (*.csv)")
        if not path:
            return
        rows = self.db.list_applications()
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "Student",
                    "Category",
                    "Scheme",
                    "Department",
                    "App number",
                    "Type",
                    "Status",
                    "Submitted",
                    "Deadline",
                    "Claimed amount",
                    "Remarks",
                ]
            )
            for row in rows:
                writer.writerow(
                    [
                        row["student_name"],
                        row["student_category"],
                        row["scholarship_name"],
                        row["department"],
                        row["app_number"],
                        row["app_type"],
                        row["status"],
                        row["submitted_on"],
                        row["close_date"],
                        row["claimed_amount"],
                        row["remarks"],
                    ]
                )
        QMessageBox.information(self, "Exported", f"Saved {len(rows)} applications to:\n{path}")
