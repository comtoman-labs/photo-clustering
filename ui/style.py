"""
Modern Dark & Light Theme Stylesheets for PhotoClustering
Inspired by Fluent / Windows 11 design system.
"""

MODERN_DARK_STYLESHEET = """
QMainWindow, QWidget#centralWidget {
    background-color: #1a1b26;
}

QWidget {
    color: #c0caf5;
    font-family: 'Segoe UI', 'Pretendard', 'Malgun Gothic', sans-serif;
    font-size: 13px;
    selection-background-color: #3d59a1;
    selection-color: #ffffff;
}

/* Base Panels / Cards */
QFrame#CardFrame {
    background-color: #24283b;
    border: 1px solid #32374d;
    border-radius: 10px;
    padding: 12px;
}

QFrame#InnerCardFrame {
    background-color: #1f2335;
    border: 1px solid #2f354f;
    border-radius: 8px;
    padding: 10px;
}

/* Header & Base Labels */
QLabel {
    background-color: transparent;
    color: #a9b1d6;
}

QLabel#TitleLabel {
    background-color: transparent;
    font-size: 20px;
    font-weight: 700;
    color: #7aa2f7;
    margin-bottom: 2px;
}

QLabel#SubtitleLabel {
    background-color: transparent;
    font-size: 12px;
    color: #565f89;
}

QLabel#SectionTitle {
    background-color: transparent;
    font-size: 14px;
    font-weight: 600;
    color: #bb9af7;
    margin-bottom: 6px;
}

/* Line Edits */
QLineEdit {
    background-color: #1a1b26;
    border: 1px solid #3b4261;
    border-radius: 6px;
    padding: 8px 12px;
    color: #c0caf5;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #7aa2f7;
    background-color: #1e2030;
}

/* Buttons */
QPushButton {
    background-color: #2e344e;
    border: 1px solid #3e4768;
    border-radius: 6px;
    padding: 8px 16px;
    color: #c0caf5;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #3b4261;
    border-color: #565f89;
}

QPushButton:pressed {
    background-color: #272c42;
}

QPushButton:disabled {
    background-color: #1a1b26;
    border-color: #24283b;
    color: #565f89;
}

/* Primary Action Buttons */
QPushButton#PrimaryBtn {
    background-color: #7aa2f7;
    border: 1px solid #7aa2f7;
    color: #15161e;
    font-weight: 700;
}

QPushButton#PrimaryBtn:hover {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #6183c7;
}

QPushButton#SuccessBtn {
    background-color: #9ece6a;
    border: 1px solid #9ece6a;
    color: #15161e;
    font-weight: 700;
}

QPushButton#SuccessBtn:hover {
    background-color: #b9f27c;
    border-color: #b9f27c;
}

QPushButton#SuccessBtn:disabled {
    background-color: #24283b;
    border-color: #24283b;
    color: #565f89;
}

QPushButton#SecondarySmallBtn {
    background-color: #24283b;
    border: 1px solid #3e4768;
    border-radius: 5px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 500;
    min-width: 85px;
}

QPushButton#SecondarySmallBtn:hover {
    background-color: #3b4261;
    border-color: #565f89;
}

/* SpinBox */
QSpinBox {
    background-color: #1a1b26;
    border: 1px solid #3b4261;
    border-radius: 6px;
    padding: 6px 10px;
    color: #c0caf5;
    font-size: 13px;
    min-width: 95px;
}

QSpinBox:focus {
    border: 1px solid #7aa2f7;
}

/* Radio Button & CheckBox */
QRadioButton, QCheckBox {
    background-color: transparent;
    color: #c0caf5;
    spacing: 8px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #414868;
    background-color: #1a1b26;
}

QRadioButton::indicator {
    border-radius: 8px;
}

QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    background-color: #7aa2f7;
    border: 1px solid #7aa2f7;
}

/* Tables */
QTableWidget {
    background-color: #1f2335;
    border: 1px solid #2f354f;
    border-radius: 8px;
    gridline-color: #292e42;
    color: #c0caf5;
    alternate-background-color: #24283b;
}

QTableWidget::item {
    padding: 6px 10px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #343b58;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #1a1b26;
    color: #7aa2f7;
    font-weight: 600;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #32374d;
}

/* Progress Bar */
QProgressBar {
    background-color: #1a1b26;
    border: 1px solid #2f354f;
    border-radius: 5px;
    text-align: center;
    color: #c0caf5;
    font-weight: 600;
    font-size: 11px;
    height: 18px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7aa2f7, stop:1 #bb9af7);
    border-radius: 4px;
}

/* Log TextEdit */
QPlainTextEdit#LogView {
    background-color: #16161e;
    border: 1px solid #292e42;
    border-radius: 6px;
    color: #a9b1d6;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #1a1b26;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #3b4261;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #565f89;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

MODERN_LIGHT_STYLESHEET = """
QMainWindow, QWidget#centralWidget {
    background-color: #f3f4f6;
}

QWidget {
    color: #1f2937;
    font-family: 'Segoe UI', 'Pretendard', 'Malgun Gothic', sans-serif;
    font-size: 13px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

/* Base Panels / Cards */
QFrame#CardFrame {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 12px;
}

QFrame#InnerCardFrame {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px;
}

/* Header & Base Labels */
QLabel {
    background-color: transparent;
    color: #374151;
}

QLabel#TitleLabel {
    background-color: transparent;
    font-size: 20px;
    font-weight: 700;
    color: #2563eb;
    margin-bottom: 2px;
}

QLabel#SubtitleLabel {
    background-color: transparent;
    font-size: 12px;
    color: #6b7280;
}

QLabel#SectionTitle {
    background-color: transparent;
    font-size: 14px;
    font-weight: 600;
    color: #4f46e5;
    margin-bottom: 6px;
}

/* Line Edits */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 8px 12px;
    color: #111827;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #2563eb;
    background-color: #ffffff;
}

/* Buttons */
QPushButton {
    background-color: #f9fafb;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 8px 16px;
    color: #1f2937;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #f3f4f6;
    border-color: #9ca3af;
}

QPushButton:pressed {
    background-color: #e5e7eb;
}

QPushButton:disabled {
    background-color: #f3f4f6;
    border-color: #e5e7eb;
    color: #9ca3af;
}

/* Primary Action Buttons */
QPushButton#PrimaryBtn {
    background-color: #2563eb;
    border: 1px solid #1d4ed8;
    color: #ffffff;
    font-weight: 700;
}

QPushButton#PrimaryBtn:hover {
    background-color: #1d4ed8;
    border-color: #1e40af;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #1e40af;
}

QPushButton#SuccessBtn {
    background-color: #16a34a;
    border: 1px solid #15803d;
    color: #ffffff;
    font-weight: 700;
}

QPushButton#SuccessBtn:hover {
    background-color: #15803d;
    border-color: #166534;
}

QPushButton#SuccessBtn:disabled {
    background-color: #e5e7eb;
    border-color: #d1d5db;
    color: #9ca3af;
}

QPushButton#SecondarySmallBtn {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 5px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 500;
    min-width: 85px;
    color: #374151;
}

QPushButton#SecondarySmallBtn:hover {
    background-color: #f3f4f6;
    border-color: #9ca3af;
}

/* SpinBox */
QSpinBox {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px 10px;
    color: #111827;
    font-size: 13px;
    min-width: 95px;
}

QSpinBox:focus {
    border: 1px solid #2563eb;
}

/* Radio Button & CheckBox */
QRadioButton, QCheckBox {
    background-color: transparent;
    color: #1f2937;
    spacing: 8px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #9ca3af;
    background-color: #ffffff;
}

QRadioButton::indicator {
    border-radius: 8px;
}

QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    background-color: #2563eb;
    border: 1px solid #2563eb;
}

/* Tables */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    gridline-color: #f3f4f6;
    color: #1f2937;
    alternate-background-color: #f9fafb;
}

QTableWidget::item {
    padding: 6px 10px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #dbeafe;
    color: #1e40af;
}

QHeaderView::section {
    background-color: #f9fafb;
    color: #2563eb;
    font-weight: 600;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #e5e7eb;
}

/* Progress Bar */
QProgressBar {
    background-color: #e5e7eb;
    border: 1px solid #d1d5db;
    border-radius: 5px;
    text-align: center;
    color: #111827;
    font-weight: 600;
    font-size: 11px;
    height: 18px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #4f46e5);
    border-radius: 4px;
}

/* Log TextEdit */
QPlainTextEdit#LogView {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    color: #374151;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #f3f4f6;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


def get_stylesheet(theme: str = "dark") -> str:
    if theme == "light":
        return MODERN_LIGHT_STYLESHEET
    return MODERN_DARK_STYLESHEET
