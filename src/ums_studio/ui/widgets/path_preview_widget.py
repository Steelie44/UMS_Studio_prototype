from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class PathPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments = []
        self.tool_position = None
        self.setMinimumHeight(220)

    def set_segments(self, segments):
        self.segments = list(segments)
        self.tool_position = self._first_point()
        self.update()

    def clear(self):
        self.segments = []
        self.tool_position = None
        self.update()

    def set_tool_position(self, point):
        self.tool_position = point
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#111827"))

        bounds = self._bounds()
        if bounds is None:
            painter.setPen(QColor("#9ca3af"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No preview")
            return

        self._draw_grid(painter)
        for segment in self.segments:
            self._draw_segment(painter, segment, bounds)
        self._draw_tool(painter, bounds)

    def _draw_grid(self, painter):
        painter.setPen(QPen(QColor("#1f2937"), 1))
        step_x = max(1, self.width() // 8)
        step_y = max(1, self.height() // 6)
        for x in range(0, self.width(), step_x):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step_y):
            painter.drawLine(0, y, self.width(), y)

    def _draw_segment(self, painter, segment, bounds):
        colors = {
            "rapid": QColor("#9ca3af"),
            "feed": QColor("#38bdf8"),
            "arc": QColor("#22c55e"),
        }
        pen = QPen(colors.get(segment.kind, QColor("#ffffff")), 2)
        if segment.kind == "rapid":
            pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        points = [self._map_point(x, y, bounds) for x, y in segment.points]
        for index in range(len(points) - 1):
            painter.drawLine(points[index], points[index + 1])

    def _bounds(self):
        points = [point for segment in self.segments for point in segment.points]
        if self.tool_position is not None:
            points.append(self.tool_position)
        if not points:
            return None
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        if min_x == max_x:
            min_x -= 1
            max_x += 1
        if min_y == max_y:
            min_y -= 1
            max_y += 1
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def _map_point(self, x, y, bounds):
        margin = 16
        scale_x = (self.width() - margin * 2) / bounds.width()
        scale_y = (self.height() - margin * 2) / bounds.height()
        scale = min(scale_x, scale_y)

        draw_width = bounds.width() * scale
        draw_height = bounds.height() * scale
        offset_x = (self.width() - draw_width) / 2
        offset_y = (self.height() - draw_height) / 2

        px = offset_x + (x - bounds.left()) * scale
        py = self.height() - (offset_y + (y - bounds.top()) * scale)
        return QPointF(px, py)

    def _draw_tool(self, painter, bounds):
        if self.tool_position is None:
            return
        point = self._map_point(self.tool_position[0], self.tool_position[1], bounds)
        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.setBrush(QColor("#ef4444"))
        painter.drawEllipse(point, 5, 5)

    def _first_point(self):
        for segment in self.segments:
            if segment.points:
                return segment.points[0]
        return None
