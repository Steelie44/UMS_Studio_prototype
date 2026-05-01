import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from ums_studio.ui.windows.main_window import MainWindow


def main():
    data_root = Path.cwd() / "data"
    data_root.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    win = MainWindow(data_root)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
