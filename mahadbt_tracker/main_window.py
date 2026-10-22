"""Primary window with sidebar navigation."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .database import Database
from .pages import ApplicationsPage, DashboardPage, DocumentsPage, ReportsPage, ScholarshipsPage, StudentsPage
from .styles import APP_QSS


NAV_ITEMS = [
    ("Dashboard", "Overview, KPIs, and deadline countdown"),
    ("Students", "Beneficiary profiles used on MahaDBT applications"),
    ("Schemes & deadlines", "MahaDBT 2.0 schemes, open/close dates, and eligibility"),
    ("Applications", "Track Fresh/Renewal status from Draft to Disbursed"),
    ("Documents", "Portal upload checklist linked to each application"),
    ("Reports", "Matplotlib analytics and CSV export"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.setWindowTitle("MahaDBT Scholarship Deadline and Application Tracker")
        self.resize(1280, 780)
        self.setStyleSheet(APP_QSS)

        root = QWidget()
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(236)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 22, 16, 16)
        brand = QLabel("MahaDBT Tracker")
        brand.setObjectName("BrandTitle")
        sub = QLabel("महाराष्ट्र शिष्यवृत्ती · AY 2026-27")
        sub.setObjectName("BrandSub")
        sub.setWordWrap(True)
        side_layout.addWidget(brand)
        side_layout.addWidget(sub)
        side_layout.addSpacing(18)

        self.buttons = QButtonGroup(self)
        self.buttons.setExclusive(True)
        self.nav_buttons: list[QPushButton] = []
        for index, (title, _) in enumerate(NAV_ITEMS):
            btn = QPushButton(title)
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            self.buttons.addButton(btn, index)
            side_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        side_layout.addStretch()
        portal = QLabel("Portal: mahadbt2.maharashtra.gov.in\nTypical window: 1 Jun – 30 Sep 2026")
        portal.setObjectName("BrandSub")
        portal.setWordWrap(True)
        side_layout.addWidget(portal)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(20, 16, 20, 16)

        top = QFrame()
        top.setObjectName("TopBar")
        top_layout = QVBoxLayout(top)
        self.page_title = QLabel(NAV_ITEMS[0][0])
        self.page_title.setObjectName("PageTitle")
        self.page_hint = QLabel(NAV_ITEMS[0][1])
        self.page_hint.setObjectName("PageHint")
        top_layout.addWidget(self.page_title)
        top_layout.addWidget(self.page_hint)

        self.stack = QStackedWidget()
        self.dashboard = DashboardPage(self.db)
        self.students = StudentsPage(self.db)
        self.scholarships = ScholarshipsPage(self.db)
        self.applications = ApplicationsPage(self.db)
        self.documents = DocumentsPage(self.db)
        self.reports = ReportsPage(self.db)
        for page in (
            self.dashboard,
            self.students,
            self.scholarships,
            self.applications,
            self.documents,
            self.reports,
        ):
            self.stack.addWidget(page)

        main_layout.addWidget(top)
        main_layout.addWidget(self.stack, 1)
        shell.addWidget(sidebar)
        shell.addWidget(main, 1)

        self.buttons.idClicked.connect(self._show_page)
        self.nav_buttons[0].setChecked(True)
        self.statusBar().showMessage("Ready · SQLite data stored in the data/ folder · Sample AY 2026-27 records loaded")
        QTimer.singleShot(400, self._show_deadline_alerts)

    def _show_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.page_title.setText(NAV_ITEMS[index][0])
        self.page_hint.setText(NAV_ITEMS[index][1])
        page = self.stack.widget(index)
        if hasattr(page, "reload"):
            page.reload()

    def _show_deadline_alerts(self) -> None:
        alerts = self.db.urgent_alerts(15)
        if not alerts:
            return
        lines = []
        for item in alerts[:8]:
            if item["days"] < 0:
                when = f"OVERDUE by {-item['days']} days"
            elif item["days"] == 0:
                when = "CLOSES TODAY"
            else:
                when = f"{item['days']} days left"
            lines.append(f"• {item['student']} — {item['scheme'][:48]} ({when})")
        extra = "" if len(alerts) <= 8 else f"\n…and {len(alerts) - 8} more."
        QMessageBox.warning(
            self,
            "MahaDBT deadline alert",
            "These open applications need attention before the portal deadline:\n\n"
            + "\n".join(lines)
            + extra,
        )

    def closeEvent(self, event) -> None:
        self.db.close()
        super().closeEvent(event)
