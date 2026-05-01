from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QFileDialog


class ProjectSelector(QWidget):
    def __init__(self, data_root: Path, on_project_loaded, log_callback=None, parent=None):
        super().__init__(parent)
        self.data_root = Path(data_root)
        self.on_project_loaded = on_project_loaded
        self.log_callback = log_callback
        self.on_folder_selected = None
        self.on_open_selected = None
        self._projects = []

        layout = QVBoxLayout(self)

        btn_row = QHBoxLayout()
        self.btn_select_folder = QPushButton("Select Folder")
        self.btn_open_selected = QPushButton("Open Selected")
        btn_row.addWidget(self.btn_select_folder)
        btn_row.addWidget(self.btn_open_selected)
        layout.addLayout(btn_row)

        self.list_projects = QListWidget()
        layout.addWidget(self.list_projects)

        self.btn_select_folder.clicked.connect(self._select_folder)
        self.btn_open_selected.clicked.connect(self._open_selected)

    def set_projects(self, projects):
        self.list_projects.clear()
        for p in projects:
            self.list_projects.addItem(p["name"])
        self._projects = projects

    def _select_folder(self):
        self._log("Select Folder clicked.")
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder", str(self.data_root))
        if folder:
            if self.on_folder_selected:
                self.on_folder_selected(folder)
        else:
            self._log("Folder selection canceled.")

    def _open_selected(self):
        self._log("Open Selected clicked.")
        row = self.list_projects.currentRow()
        if row < 0:
            self._log("No project selected.")
            return
        project = self._projects[row]
        if self.on_open_selected:
            self.on_open_selected(project)

    def _log(self, message: str):
        if self.log_callback:
            self.log_callback(message)
