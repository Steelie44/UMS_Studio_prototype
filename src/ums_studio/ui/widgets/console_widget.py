from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QPlainTextEdit

class ConsoleWidget(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def append_line(self, line: str):
        self.appendPlainText(line)
