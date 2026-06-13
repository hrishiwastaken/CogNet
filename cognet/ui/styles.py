STYLE_SHEET = """
QWidget {
    background-color: #0d0e12;
    color: #e2e2e6;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0d0e12;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #2a2a32;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #b388ff;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Input Fields & Text Editor */
QLineEdit, QTextEdit {
    background-color: #16161a;
    border: 1px solid #2a2a32;
    border-radius: 8px;
    padding: 12px;
    color: #e2e2e6;
    selection-background-color: #b388ff;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #b388ff;
}

/* Buttons styling */
QPushButton {
    background-color: #16161a;
    border: 1px solid #2a2a32;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    color: #e2e2e6;
}
QPushButton:hover {
    background-color: #222228;
    border-color: #b388ff;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #0d0e12;
}

/* Specific Accent Button styling */
QPushButton#accentButton {
    background-color: #b388ff;
    color: #0d0e12;
    border: none;
}
QPushButton#accentButton:hover {
    background-color: #c5a3ff;
}
QPushButton#accentButton:pressed {
    background-color: #9e70ec;
}

/* Custom Titles */
QLabel#titleLabel {
    font-size: 42px;
    font-weight: bold;
    color: #00e5ff;
    background: transparent;
}
QLabel#subtitleLabel {
    font-size: 14px;
    color: #8f8f9d;
    background: transparent;
    margin-bottom: 20px;
}
"""