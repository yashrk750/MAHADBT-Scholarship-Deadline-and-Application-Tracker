APP_QSS = """
/* ============ Base ============ */
QMainWindow, QWidget {
    background: #EEF3F1;
    color: #1B2B28;
    font-family: "Segoe UI", "Nirmala UI", sans-serif;
    font-size: 13px;
}

/* ============ Sidebar ============ */
QWidget#Sidebar {
    background: #0B3D3A;
}
QLabel#BrandTitle {
    
    font-size: 16px;
    font-weight: 700;
}
QLabel#BrandSub {
    
    font-size: 11px;
}
QPushButton#NavBtn {
    background: transparent;
    color: #D7EEEA;
    border: none;
    text-align: left;
    padding: 11px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#NavBtn:hover {
    background: #13524E;
}
QPushButton#NavBtn:checked {
    background: #E07A2F;
    color: #FFFFFF;
}
QPushButton#NavBtn:disabled {
    color: #5C7D77;
    background: transparent;
}
QPushButton#NavBtn:focus {
    outline: none;
    border: 1px solid #C5E4DF;
}

/* ============ Top Bar ============ */
QFrame#TopBar {
    background: #FFFFFF;
    border-bottom: 1px solid #D5E0DC;
}
QLabel#PageTitle {
    font-size: 22px;
    font-weight: 700;
    color: #0B3D3A;
}
QLabel#PageHint {
    color: #5C726C;
    font-size: 12px;
}

/* ============ Cards / KPIs ============ */
QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #DCE7E3;
    border-radius: 12px;
}
QLabel#KpiValue {
    font-size: 26px;
    font-weight: 700;
    color: #0B3D3A;
}
QLabel#KpiLabel {
    color: #5C726C;
    font-size: 12px;
    font-weight: 600;
}

/* ============ Buttons ============ */
QPushButton {
    background: #0F5C56;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: #14756E;
}
QPushButton:pressed {
    background: #0B4A45;
}
QPushButton:disabled {
    background: #A9C2BD;
    color: #EEF3F1;
}
QPushButton:focus {
    outline: none;
    border: 2px solid #7FD1C6;
}
QPushButton#Danger {
    background: #B42318;
}
QPushButton#Danger:hover {
    background: #912018;
}
QPushButton#Danger:pressed {
    background: #711A12;
}
QPushButton#Ghost {
    background: #E7F0ED;
    color: #0B3D3A;
}
QPushButton#Ghost:hover {
    background: #D5E6E1;
}
QPushButton#Ghost:pressed {
    background: #C3DAD3;
}

/* ============ Inputs ============ */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {
    background: #FFFFFF;
    border: 1px solid #C9D8D3;
    border-radius: 8px;
    padding: 6px 8px;
    min-height: 28px;
    selection-background-color: #D5EDEB;
    selection-color: #0B3D3A;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QTextEdit:focus {
    border: 1px solid #0F5C56;
}
QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled, QSpinBox:disabled, QTextEdit:disabled {
    background: #F1F5F3;
    color: #8FA39D;
    border: 1px solid #DCE7E3;
}

/* ComboBox dropdown */
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #C9D8D3;
    border-radius: 6px;
    selection-background-color: #D5EDEB;
    selection-color: #0B3D3A;
    outline: none;
    padding: 4px;
}

/* SpinBox arrows */
QSpinBox::up-button, QSpinBox::down-button {
    background: #E7F0ED;
    border: none;
    width: 16px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #D5E6E1;
}

/* ============ Checkboxes / Radio ============ */
QCheckBox, QRadioButton {
    spacing: 8px;
    color: #1B2B28;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #C9D8D3;
    background: #FFFFFF;
}
QCheckBox::indicator {
    border-radius: 4px;
}
QRadioButton::indicator {
    border-radius: 8px;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: #0F5C56;
    border: 1px solid #0F5C56;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
    background: #F1F5F3;
    border: 1px solid #DCE7E3;
}

/* ============ Tables ============ */
QTableWidget {
    background: #FFFFFF;
    alternate-background-color: #F7FBFA;
    gridline-color: #E3ECE9;
    border: 1px solid #DCE7E3;
    border-radius: 10px;
    selection-background-color: #D5EDEB;
    selection-color: #0B3D3A;
}
QHeaderView::section {
    background: #0F5C56;
    color: white;
    padding: 8px;
    border: none;
    font-weight: 600;
}

/* ============ Lists ============ */
QListWidget {
    background: #FFFFFF;
    border: 1px solid #DCE7E3;
    border-radius: 10px;
    outline: none;
}
QListWidget::item {
    padding: 6px 8px;
}
QListWidget::item:selected {
    background: #D5EDEB;
    color: #0B3D3A;
}

/* ============ Tabs ============ */
QTabWidget::pane {
    border: 1px solid #DCE7E3;
    border-radius: 10px;
    background: #FFFFFF;
}
QTabBar::tab {
    background: #E7F0ED;
    color: #0B3D3A;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #0F5C56;
    color: #FFFFFF;
}
QTabBar::tab:hover:!selected {
    background: #D5E6E1;
}

/* ============ Group Box ============ */
QGroupBox {
    border: 1px solid #DCE7E3;
    border-radius: 10px;
    margin-top: 12px;
    font-weight: 600;
    color: #0B3D3A;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}

/* ============ Progress Bar ============ */
QProgressBar {
    background: #E7F0ED;
    border: none;
    border-radius: 6px;
    text-align: center;
    color: #0B3D3A;
    min-height: 12px;
}
QProgressBar::chunk {
    background: #0F5C56;
    border-radius: 6px;
}

/* ============ Scrollbars ============ */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #B9CFC9;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #8FAEA6;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #B9CFC9;
    border-radius: 5px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover {
    background: #8FAEA6;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ============ Menus / Tooltips ============ */
QMenu {
    background: #FFFFFF;
    border: 1px solid #DCE7E3;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: #D5EDEB;
    color: #0B3D3A;
}
QToolTip {
    background: #0B3D3A;
    color: #FFFFFF;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
}

/* ============ Dialog / Status Bar ============ */
QDialog {
    background: #F4F8F6;
}
QStatusBar {
    background: #0B3D3A;
    color: #E8F4F1;
}
"""