# ------------------------------------------------------------
# machine_session.py
# Central runtime controller for UMS Studio.
# ------------------------------------------------------------
from datetime import datetime

class MachineSession:
    """
    Owns:
      - Machine object (real or mock)
      - Execution state
      - Overrides
      - Fault state
      - UI callbacks
    """

    def __init__(self):
        # Machine object (assigned by MainWindow)
        self.machine = None

        # Live machine state
        self.state = {}

        # Execution state
        self.is_running = False
        self.is_paused = False

        # Overrides
        self.feed_override = 1.0
        self.spindle_override = 1.0

        # Fault state
        self.is_faulted = False

        # UI callbacks
        self.state_callback = None
        self.log_callback = None
        self.on_log = None
        self.ui_lock_callback = None  # called with True/False


    # ------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------
    def set_state_callback(self, cb):
        self.state_callback = cb

    def set_log_callback(self, cb):
        self.log_callback = cb
        self.on_log = cb

    # ------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        if self.on_log:
            self.on_log(formatted)
        elif self.log_callback:
            self.log_callback(formatted)

    # ------------------------------------------------------------
    # Machine state updates (from machine)
    # ------------------------------------------------------------
    def on_machine_state(self, state: dict):
        # Merge incoming state into session state
        self.state.update(state)

        if self.state_callback:
            self.state_callback(self.state)

    # ------------------------------------------------------------
    # Jog / Home / Zero
    # ------------------------------------------------------------
    def jog(self, axis, direction, step):
        if not self.machine:
            self.log("[SESSION] No machine connected")
            return
        if self.is_faulted:
            self.log("[SESSION] Jog blocked: fault active")
            return
        self.machine.jog(axis, direction, step)
        signed_step = step * direction
        self.log(f"[JOG] {axis} {signed_step:+.3f} mm")


    def home(self, axis):
        if not self.machine:
            self.log("[SESSION] No machine connected")
            return
        if self.is_faulted:
            self.log("[SESSION] Home blocked: fault active")
            return

        self.log(f"[HOME] {axis if axis else 'ALL'}")
        self.machine.home(axis)


    def zero(self, axis):
        if not self.machine:
            self.log("[SESSION] No machine connected")
            return
        if self.is_faulted:
            self.log("[SESSION] Zero blocked: fault active")
            return

        self.log(f"[ZERO] {axis if axis else 'ALL'}")
        self.machine.zero(axis)


    # ------------------------------------------------------------
    # Overrides
    # ------------------------------------------------------------
    def set_feed_override(self, factor: float):
        self.feed_override = factor
        self.log(f"[SESSION] Feed override set to {factor:.2f}")

    def set_spindle_override(self, factor: float):
        self.spindle_override = factor
        self.log(f"[SESSION] Spindle override set to {factor:.2f}")

    # ------------------------------------------------------------
    # Cycle control
    # ------------------------------------------------------------
    def start_cycle(self):
        if not self.machine:
            self.log("[SESSION] No machine connected")
            return
        if self.is_faulted:
            self.log("[SESSION] Start blocked: fault active")
            return
        if self.is_running:
            self.log("[SESSION] Cycle already running")
            return

        self.log("[SESSION] Cycle Start")
        self.is_running = True
        self.is_paused = False

        self.machine.start_execution()

    def pause_cycle(self):
        if not self.machine:
            self.log("[SESSION] No machine connected")
            return
        if not self.is_running:
            self.log("[SESSION] Cannot pause - no cycle running")
            return

        self.log("[SESSION] Cycle Paused")
        self.is_paused = True

        self.machine.pause_execution()

    def stop_cycle(self):
        if not self.machine:
            self.log("[SESSION] No machine connected")
            return
        if not self.is_running:
            self.log("[SESSION] Cannot stop - no cycle running")
            return

        self.log("[SESSION] Cycle Stopped")
        self.is_running = False
        self.is_paused = False

        self.machine.stop_execution()

    # ------------------------------------------------------------
    # E‑STOP / RESET
    # ------------------------------------------------------------
    def estop(self):
        self.log("[SESSION] *** E-STOP ACTIVATED ***")

        self.is_faulted = True
        self.is_running = False
        self.is_paused = False

        if self.machine:
            self.machine.estop()

        if self.ui_lock_callback:
            self.ui_lock_callback(True)

        # Notify UI via state
        self.on_machine_state({"fault": True})

    def reset_fault(self):
        self.log("[SESSION] Fault reset")

        self.is_faulted = False

        if self.machine:
            self.machine.reset_fault()

        if self.ui_lock_callback:
            self.ui_lock_callback(False)

        self.on_machine_state({"fault": False})

    def reset(self):
        self.log("[SESSION] Reset requested")
        self.reset_fault()

