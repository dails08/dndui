BG = "#1b1b1f"
SURFACE = "#242429"
SURFACE_HOVER = "#2c2c33"
SURFACE_PRESSED = "#1f1f24"
BORDER = "#3a3a41"
TEXT = "#e8e8ea"
TEXT_MUTED = "#8a8a92"
ACCENT = "#5b8cff"
ACCENT_HOVER = "#6f9bff"
ACCENT_PRESSED = "#4a76e0"

CHROMA_KEY = "#00ff00"


def load_stylesheet():
    return f"""
    * {{
        font-family: "Segoe UI", sans-serif;
        font-size: 13px;
        color: {TEXT};
    }}

    QWidget {{
        background-color: {BG};
    }}

    QMainWindow, QDialog {{
        background-color: {BG};
    }}

    QLabel {{
        background: transparent;
    }}

    QLabel[role="heading"] {{
        color: {TEXT};
        font-weight: 600;
        font-size: 14px;
    }}

    QLabel[role="muted"] {{
        color: {TEXT_MUTED};
    }}

    QPushButton {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 12px;
    }}
    QPushButton:hover {{
        background-color: {SURFACE_HOVER};
        border-color: {ACCENT};
    }}
    QPushButton:pressed {{
        background-color: {SURFACE_PRESSED};
    }}
    QPushButton:disabled {{
        color: {TEXT_MUTED};
        border-color: {BORDER};
    }}

    QPushButton[role="primary"] {{
        background-color: {ACCENT};
        border: 1px solid {ACCENT};
        color: #0d0d0f;
        font-weight: 600;
    }}
    QPushButton[role="primary"]:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton[role="primary"]:pressed {{
        background-color: {ACCENT_PRESSED};
    }}

    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 5px 8px;
        selection-background-color: {ACCENT};
        selection-color: #0d0d0f;
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {ACCENT};
    }}

    QListWidget, QTreeWidget {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 6px;
        outline: none;
    }}
    QListWidget::item, QTreeWidget::item {{
        padding: 3px 4px;
        border-radius: 4px;
    }}
    QListWidget::item:hover, QTreeWidget::item:hover {{
        background-color: {SURFACE_HOVER};
    }}
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {ACCENT};
        color: #0d0d0f;
    }}
    QHeaderView::section {{
        background-color: {SURFACE};
        color: {TEXT_MUTED};
        border: none;
        border-bottom: 1px solid {BORDER};
        padding: 4px;
    }}

    QTabWidget::pane {{
        border: 1px solid {BORDER};
        border-radius: 6px;
        top: -1px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {TEXT_MUTED};
        padding: 8px 18px;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:selected {{
        color: {TEXT};
        border-bottom: 2px solid {ACCENT};
    }}
    QTabBar::tab:hover {{
        color: {TEXT};
    }}

    QSplitter::handle {{
        background-color: {BORDER};
    }}
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    QSplitter::handle:vertical {{
        height: 2px;
    }}

    QMenuBar {{
        background-color: {BG};
        border-bottom: 1px solid {BORDER};
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 4px 10px;
    }}
    QMenuBar::item:selected {{
        background-color: {SURFACE_HOVER};
        border-radius: 4px;
    }}
    QMenu {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
    }}
    QMenu::item {{
        padding: 6px 20px;
    }}
    QMenu::item:selected {{
        background-color: {ACCENT};
        color: #0d0d0f;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 4px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        border-radius: 4px;
        min-width: 24px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    #bgDisplayFrame {{
        background-color: black;
        border: none;
        border-radius: 0;
    }}
    #bgPreviewFrame {{
        background-color: black;
        border: 1px solid {BORDER};
        border-radius: 6px;
    }}
    #initiativeView {{
        background-color: {CHROMA_KEY};
        border: none;
        border-radius: 0;
    }}
    """
