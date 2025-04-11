# timers.py

import threading
from typing import Callable
from game_logic.actions.stay import StayAction
from game_logic.data.state_manager import StateManager
from game_logic.log_manager import log_event

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

def apply_default_action_after_timeout(session_id: str, player_id: str, turn_number: int) -> None:
    """
    Explicitly applies the default 'Stay' action due to player inactivity.

    Args:
        session_id (str): Explicitly identifies the current game session.
        player_id (str): Explicit identifier for the inactive player.
        turn_number (int): Explicitly tracks the turn when inactivity occurred.
    """
    # Explicitly create and execute the default 'Stay' action
    stay_action = StayAction(session_id=session_id, player_id=player_id)
    action_result = stay_action.execute()

    # Explicitly update the game state
    state_manager = StateManager(session_id=session_id)
    state_manager.update_state(action_result)

    # Explicitly log the inactivity-triggered action
    log_event(
        session_id=session_id,
        turn_number=turn_number,
        actor_type="player",
        actor_id=player_id,
        action_phase="resolution",
        action_type="Stay",
        description=f"Player {player_id} explicitly performed default 'Stay' action due to inactivity.",
        additional_data={"reason": "timeout", "action_result": action_result}
    )

    print(f"Explicitly applied default 'Stay' action for player {player_id} on turn {turn_number} due to inactivity.")
