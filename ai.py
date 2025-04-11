# ai.py
from typing import List, Tuple, Dict
from cards import Card
from montecarlo import MonteCarloSimulator
from handrecord import HandRecord
from ml.features import extract_features
from ml.trainer import load_model
import random

class PokerAI:
    def __init__(self, memory_size: int = 1000):
        self.simulator = MonteCarloSimulator()
        self.memory_size = memory_size
        self.hand_history: List[HandRecord] = []
        self.strategy: Dict[str, Dict[str, float]] = {
            "preflop": {"fold": 0.3, "call": 0.4, "raise": 0.3},
            "postflop": {"fold": 0.2, "call": 0.4, "raise": 0.4}
        }
        self.policy: Dict[int, str] = {}  # win_prob bucket -> action
        self.learning_rate = 0.1
        try:
            self.ml_model = load_model()
            self.use_ml = True
        except:
            self.use_ml = False
            print("ML model not found, using rule-based strategy")

    def record_hand(self, record: HandRecord) -> None:
        """Record hand history and limit memory size"""
        self.hand_history.append(record)
        if len(self.hand_history) > self.memory_size:
            self.hand_history.pop(0)

    def learn(self) -> None:
        """Update strategy based on hand history"""
        from collections import defaultdict
        stats = defaultdict(lambda: {"raise": 0, "call": 0, "fold": 0, "total": 0})

        for record in self.hand_history:
            bucket = int(record.win_prob * 10)  # Divide win probability into 10 buckets
            stats[bucket][record.action] += record.result
            stats[bucket]["total"] += 1

        for bucket in stats:
            if stats[bucket]["total"] > 0:
                best_action = max(["raise", "call", "fold"], 
                                key=lambda x: stats[bucket][x] / stats[bucket]["total"])
                self.policy[bucket] = best_action

    def calculate_implied_odds(self, pot: int, bet: int, win_prob: float) -> float:
        """Calculate implied odds for decision making"""
        if pot + bet == 0:
            return 0
        return (pot + bet) * win_prob - bet * (1 - win_prob)

    def make_decision(self, game, player, position) -> Tuple[str, int]:
        """Make decision using ML model or rule-based strategy"""
        win_prob = self.simulator.calculate_win_rate(player.hand, game.community_cards)
        ev = self.calculate_implied_odds(game.pot, game.current_bet, win_prob)

        if self.use_ml:
            features = extract_features(player.hand, game.community_cards, 
                                     position, game.pot, game.current_bet)
            action = self.ml_model.predict([features])[0]
        else:
            # Rule-based strategy
            if win_prob > 0.7:
                action = "raise"
            elif win_prob > 0.4:
                action = "call"
            else:
                action = "fold"

        # Determine bet amount
        if action == "raise":
            bet_amount = min(game.current_bet * 2, player.chips)
        elif action == "call":
            bet_amount = game.current_bet
        else:
            bet_amount = 0

        return action, bet_amount

    def generate_hand_summary(self, record: HandRecord) -> str:
        """Generate summary of a hand"""
        return (
            f"Hand: {' '.join(str(c) for c in record.hand)}\n"
            f"Community: {' '.join(str(c) for c in record.community_cards)}\n"
            f"Position: {record.position}\n"
            f"Win Rate: {record.win_prob:.1%}\n"
            f"Action: {record.action}\n"
            f"Bet Amount: ${record.bet_amount}\n"
            f"Pot Size: ${record.pot_size}\n"
            f"Result: {record.result:+.2f}\n"
        )
