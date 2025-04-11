# timers.py

import threading
from typing import Callable

class ActionTimer:
    """
    Explicitly manages timers for player inactivity, triggering default actions after a timeout.
    """

    def __init__(self, timeout_seconds: int, on_timeout: Callable, *args, **kwargs):
        self.timeout_seconds = timeout_seconds
        self.on_timeout = on_timeout
        self.args = args
        self.kwargs = kwargs
        self.timer_thread = None

    def start_timer(self) -> None:
        """
        Explicitly starts the inactivity timer.
        """
        print(f"Explicitly starting timer for {self.timeout_seconds} seconds.")
        self.timer_thread = threading.Timer(self.timeout_seconds, self._handle_timeout)
        self.timer_thread.start()

    def cancel_timer(self) -> None:
        """
        Explicitly cancels the inactivity timer if the player acts in time.
        """
        if self.timer_thread is not None:
            self.timer_thread.cancel()
            print("Explicitly cancelled timer due to player action.")

    def _handle_timeout(self) -> None:
        """
        Explicitly handles the timer expiry, triggering the predefined default action.
        """
        print("Timer explicitly expired. Executing default action.")
        self.on_timeout(*self.args, **self.kwargs)
