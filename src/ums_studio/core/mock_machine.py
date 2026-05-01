# ------------------------------------------------------------
# mock_machine.py
# Deterministic mock CNC machine for UMS Studio.
# ------------------------------------------------------------

from PyQt6.QtCore import QTimer


class MockMachine:
    """
    Simulated CNC machine:
      - X/Y/Z positions
      - Jog / home / zero
      - Feed + spindle override
      - Cycle Start / Pause / Stop
      - E‑STOP / RESET
      - Execution + DRO loops
    """

    def __init__(self, session):
        self.session = session

        # Coordinates
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        # Spindle / feed
        self.spindle_rpm = 0
        self.feed_rate = 0

        # Fault
        self.is_faulted = False

        # Timers (not started here)
        self.exec_timer = QTimer()
        self.exec_timer.setInterval(200)  # 5 Hz
        self.exec_timer.timeout.connect(self._exec_step)

        self.dro_timer = QTimer()
        self.dro_timer.setInterval(100)  # 10 Hz
        self.dro_timer.timeout.connect(self._update_dro)

    # ------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------
    def start(self):
        # Start DRO updates once UI is ready
        self.dro_timer.start()

    # ------------------------------------------------------------
    # Jog / Home / Zero
    # ------------------------------------------------------------
    def jog(self, axis, direction, step):
        # Continuous jog mode
        if step is None:
            step = 0.5   # default continuous jog increment

        if axis == "X":
            self.x += step * direction
        elif axis == "Y":
            self.y += step * direction
        elif axis == "Z":
            self.z += step * direction

        self._send_state()

    def home(self, axis):
        if self.is_faulted:
            return

        if axis == "X":
            self.x = 0.0
        elif axis == "Y":
            self.y = 0.0
        elif axis == "Z":
            self.z = 0.0

        self._send_state()

    def zero(self, axis):
        if self.is_faulted:
            return

        if axis == "X":
            self.x = 0.0
        elif axis == "Y":
            self.y = 0.0
        elif axis == "Z":
            self.z = 0.0

        self._send_state()

    # ------------------------------------------------------------
    # Cycle control
    # ------------------------------------------------------------
    def start_execution(self):
        if self.is_faulted:
            return
        print("[MOCK] Execution started")
        self.exec_timer.start()

    def pause_execution(self):
        print("[MOCK] Execution paused")
        self.exec_timer.stop()

    def stop_execution(self):
        print("[MOCK] Execution stopped")
        self.exec_timer.stop()

    # ------------------------------------------------------------
    # E‑STOP / RESET
    # ------------------------------------------------------------
    def estop(self):
        print("[MOCK] E-STOP triggered")
        self.is_faulted = True
        self.exec_timer.stop()
        self.dro_timer.stop()

    def reset_fault(self):
        print("[MOCK] Fault reset")
        self.is_faulted = False
        self.dro_timer.start()

    # ------------------------------------------------------------
    # Execution loop
    # ------------------------------------------------------------
    def _exec_step(self):
        if self.is_faulted:
            return

        base_feed = 50.0
        base_rpm = 6000

        feed_override = getattr(self.session, "feed_override", 1.0)
        spindle_override = getattr(self.session, "spindle_override", 1.0)

        effective_feed = base_feed * feed_override
        effective_spindle = base_rpm * spindle_override

        self.x += effective_feed * 0.01
        self.spindle_rpm = int(effective_spindle)

        print(f"[MOCK] Exec step: X={self.x:.3f}, RPM={self.spindle_rpm}")
        self._send_state()

    # ------------------------------------------------------------
    # DRO loop
    # ------------------------------------------------------------
    def _update_dro(self):
        self._send_state()

    # ------------------------------------------------------------
    # State packet
    # ------------------------------------------------------------
    def _send_state(self):
        state = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "spindle_rpm": self.spindle_rpm,
            "feed_rate": self.feed_rate,
            "feed_override": getattr(self.session, "feed_override", 1.0),
            "spindle_override": getattr(self.session, "spindle_override", 1.0),
            "is_running": getattr(self.session, "is_running", False),
            "is_paused": getattr(self.session, "is_paused", False),
            "fault": self.is_faulted,
        }

        if hasattr(self.session, "on_machine_state"):
            self.session.on_machine_state(state)
