from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QLabel


class ConnectionIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status = "disconnected"
        self._update_icon()

    def set_status(self, status: str):
        self._status = status
        self._update_icon()

    def _update_icon(self):
        if self._status in ("connected", "reconnected"):
            color = QColor(0, 200, 0)
        elif self._status in ("connecting",):
            color = QColor(255, 200, 0)
        elif self._status in ("lost", "error"):
            color = QColor(255, 80, 80)
        else:
            color = QColor(180, 0, 0)

        pix = QPixmap(14, 14)
        pix.fill(QColor(0, 0, 0, 0))

        p = QPainter(pix)
        p.setBrush(color)
        p.setPen(color)
        p.drawEllipse(0, 0, 14, 14)
        p.end()

        self.setPixmap(pix)
