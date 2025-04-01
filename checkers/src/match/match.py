from typing import List, Optional
from uuid import uuid4
from .game_instance import GameInstance

class Match:
    def __init__(self, engine1_id: str, engine2_id: str, games_count: int = 3, must_capture: bool = True):
        self.match_id = str(uuid4())
        self.engine1_id = engine1_id
        self.engine2_id = engine2_id
        self.game_instances: List[GameInstance] = []
        self.current_game_index = 0
        self.match_result = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED
        self.games_count = games_count
        self.scores = {engine1_id: 0, engine2_id: 0}
        self.must_capture = must_capture

    def start_match(self) -> bool:
        """Start the match and its first game"""
        if self.match_result != "PENDING":
            return False
            
        self.match_result = "IN_PROGRESS"
        return self._start_next_game()

    def _start_next_game(self) -> bool:
        """Start the next game in the match"""
        if len(self.game_instances) >= self.games_count:
            return False

        game = GameInstance(f"{self.match_id}_game_{len(self.game_instances) + 1}", must_capture=self.must_capture)
        self.game_instances.append(game)
        return game.start_game()

    def record_game_result(self, game_id: str, winner: Optional[str]) -> bool:
        """Record the result of a game and update match status"""
        game = next((g for g in self.game_instances if g.game_id == game_id), None)
        if not game or game.status == "ACTIVE":
            return False

        if winner:
            if winner == self.engine1_id:
                self.scores[self.engine1_id] += 1
            elif winner == self.engine2_id:
                self.scores[self.engine2_id] += 1

        # Check if match is complete
        total_games = len([g for g in self.game_instances if g.status in ["COMPLETED", "DRAWN"]])
        if total_games >= self.games_count:
            self.determine_winner()
        elif game.status in ["COMPLETED", "DRAWN"]:
            self._start_next_game()

        return True

    def determine_winner(self) -> Optional[str]:
        """Determine the match winner based on scores"""
        if self.match_result == "COMPLETED":
            return max(self.scores, key=self.scores.get)

        if sum(self.scores.values()) >= self.games_count:
            self.match_result = "COMPLETED"
            return max(self.scores, key=self.scores.get)

        return None

    def get_current_game(self) -> Optional[GameInstance]:
        """Get the current active game instance"""
        return self.game_instances[self.current_game_index] if self.game_instances else None

    def get_match_state(self):
        """Get the current match state"""
        return {
            "match_id": self.match_id,
            "engine1_id": self.engine1_id,
            "engine2_id": self.engine2_id,
            "scores": self.scores,
            "status": self.match_result,
            "current_game": self.get_current_game().get_state() if self.get_current_game() else None,
            "games_completed": len([g for g in self.game_instances if g.status != "ACTIVE"])
        }
