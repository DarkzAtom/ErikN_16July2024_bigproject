db = None

delete_background_color = "#b00b1e"
delete_text_color = "white"
run_background_color = "#015c18"
run_text_color = "white"

dark_mode_stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: white;
    }
    QPushButton {
        background-color: #444;
        color: white;
    }
    QLineEdit, QComboBox, QSpinBox {
        background-color: #555;
        color: white;
    }
    QTabBar::tab {
        background: #2b2b2b;
        color: white;
    }
    QTabBar::tab:selected {
        background: #444;
        color: white;
    }
    QTableWidget {
        background-color: #2b2b2b;
        color: white;
        gridline-color: #444;
    }
    QHeaderView::section {
        background-color: #444;
        color: white;
    }
"""

tt_accounts = {}
proxies = {}