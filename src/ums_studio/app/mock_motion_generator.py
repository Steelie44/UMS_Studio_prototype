from PyQt6.QtCore import QTimer
import math
import time


class MockMotionGenerator:
    """
    Generates smooth fake machine motion for testing the DRO and dashboard.
    Emits state packets through session.on_state_change.
    """

    def __init__(self, session):
        self.session = session
        self.t0 = time.time()

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(50)   # 20 Hz update rate

    def _tick(self):
        t = time.time() - self.t0

        # Smooth oscillating motion
        x = 50 * math.sin(t * 0.5)
        y = 25 * math.sin(t * 0.8)
        z = 10 * math.sin(t * 1.2)

        # Feed rate oscillates between 500–1500
        feed = 1000 + 500 * math.sin(t * 0.3)

        # Spindle ramps between 3000–9000 RPM
        spindle = 6000 + 3000 * math.sin(t * 0.2)

        # Machine state toggles based on motion
        machine_state = "running" if abs(math.sin(t * 0.5)) > 0.1 else "idle"

        state = {
            "position": {"X": x, "Y": y, "Z": z},
            "effective_feed": feed * self.session.feed_override,
            "effective_rpm": spindle * self.session.spindle_override,
            "machine_state": machine_state,
        }

        if self.session.on_state_change:
            self.session.on_state_change(state)
