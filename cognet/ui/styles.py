STYLE_SHEET = """
QWidget {
    background-color: #07090e;
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #07090e;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #1e293b;
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #38bdf8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Input Fields & Text Editor */
QLineEdit, QTextEdit {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 10px 14px;
    color: #f8fafc;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #38bdf8;
}

/* Buttons styling */
QPushButton {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    color: #e2e8f0;
    outline: none;
}
QPushButton:hover {
    background-color: #1e293b;
    border-color: #38bdf8;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #07090e;
    border-color: #0284c7;
}

/* Specific Accent Button styling (Yellow Accent) */
QPushButton#accentButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fef08a, stop:1 #eab308);
    color: #07090e;
    border: none;
    font-weight: bold;
}
QPushButton#accentButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fef9c3, stop:1 #facc15);
}
QPushButton#accentButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #facc15, stop:1 #ca8a04);
}

/* Custom Dropdown styling */
QComboBox {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 6px 12px;
    color: #e2e8f0;
    min-width: 150px;
}
QComboBox:hover {
    border-color: #38bdf8;
}
QComboBox::drop-down {
    border: none;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
}
QComboBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #38bdf8;
    margin-right: 8px;
    margin-top: 2px;
}
QComboBox QAbstractItemView {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
    outline: none;
}

/* QMessageBox styling */
QMessageBox {
    background-color: #07090e;
    border: 1px solid #1e293b;
}
QMessageBox QLabel {
    color: #e2e8f0;
    background: transparent;
}
QMessageBox QPushButton {
    min-width: 80px;
}

/* Custom Titles */
QLabel#titleLabel {
    font-size: 44px;
    font-weight: 800;
    color: #facc15;
    background: transparent;
    letter-spacing: -1px;
}
QLabel#subtitleLabel {
    font-size: 14px;
    color: #64748b;
    background: transparent;
    margin-bottom: 20px;
}
"""