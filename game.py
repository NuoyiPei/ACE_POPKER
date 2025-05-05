from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from cards import Card, Deck
from ai import PokerAI
from handrecord import HandRecord

@dataclass
class AIAction:
    position: str
    action: str
    amount: int

# @dataclass
class Player:
    name: str
    chips: int
    hand: List[Card]
    is_active: bool = True
    position: str = ""

    def __init__(self, name: str, chips: int = 1000, position: str = ""):
        self.name = name
        self.chips = chips
        self.hand = []
        self.is_active = True
        self.position = position

    def add_card(self, card: Card) -> None:
        self.hand.append(card)

    def clear_hand(self) -> None:
        self.hand = []

    def bet(self, amount: int) -> int:
        if amount > self.chips:
            amount = self.chips
        self.chips -= amount
        return amount

class PokerGame:
    def __init__(self, num_players=9):
        self.num_players = num_players
        self.current_stage = "preflop"
        self.deck = Deck()
        self.players = []
        # self.ai = Player("BB", position="BB")
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.small_blind = 10
        self.big_blind = 20
        self.ai_agent = PokerAI()
        self.history: List[HandRecord] = []
        self.ai_actions: List[AIAction] = []
        self.positions = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
        self.dealer_position = 0

    def start_new_hand(self) -> None:
        self.deck.reset()
        for player in self.players:
            player.clear_hand()
        # self.ai.clear_hand()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.ai_actions = []

        for _ in range(2):
            for player in self.players:
                player.add_card(self.deck.deal())
        print("Dealt hands:", player.hand)
        if len(self.players) >= 2:
            self.pot += self.players[0].bet(self.small_blind)
            self.pot += self.players[1].bet(self.big_blind)
            self.current_bet = self.big_blind

    def deal_community_cards(self, count: int = 3) -> None:
        for _ in range(count):
            self.community_cards.append(self.deck.deal())

    def player_action(self, action: str, amount: Optional[int] = None) -> Tuple[bool, int]:
        bet_amount = 0
        if action == "fold":
            self.player.is_active = False
            return False, 0
        elif action == "call":
            bet_amount = self.current_bet
            self.pot += self.player.bet(bet_amount)
        elif action == "raise" and amount is not None:
            bet_amount = amount
            self.current_bet = amount
            self.pot += self.player.bet(amount)
        elif action == "check":
            bet_amount = 0
        return True, bet_amount
    



    def ai_action(self, player=None) -> Tuple[str, int]:
        player = player or self.ai
        action, amount = self.ai_agent.make_decision(self, player, player.position)
        
        
        if action == "call":
            amount = self.current_bet
        elif action == "raise":
            
            amount = max(amount, self.current_bet * 2)
        
        
        if action == "fold":
            player.is_active = False
        elif action == "call":
            self.pot += player.bet(amount)
        elif action == "raise":
            self.current_bet = amount
            self.pot += player.bet(amount)
        
        return action, amount

    def simulate_other_players_actions(self):
        """
        Simulate pre-flop actions of all AI players except the human and the main AI opponent,
        following standard positional order: UTG → MP → CO → BTN.
        Ensure at least one AI doesn't fold.
        """
        self.ai_actions = []
        ordered_positions = ["UTG", "MP", "CO", "BTN"]
        non_folders = []

        for idx, pos in enumerate(ordered_positions):
            if pos not in [self.player.position, self.ai.position]:
                action, amount = self.ai_agent.make_decision(self, self.ai, pos)

                # ensure that there is an AI in the flop
                if action == "fold" and idx == len(ordered_positions) - 1 and len(non_folders) == 0:
                    action = "call"
                    amount = self.current_bet

                if action == "call":
                    self.pot += amount
                elif action == "raise":
                    self.current_bet = max(self.current_bet, amount)
                    self.pot += amount
                elif action == "check":
                    amount = 0

                if action != "fold":
                    non_folders.append(pos)

                self.ai_actions.append(AIAction(position=pos, action=action, amount=amount))

    def record_hand(self, player: Player, action: str, bet_amount: int, result: float) -> None:
        record = HandRecord(
            hand=player.hand.copy(),
            community_cards=self.community_cards.copy(),
            win_prob=self.ai_agent.simulator.calculate_win_rate(player.hand, self.community_cards),
            action=action,
            result=result,
            position=player.position,
            pot_size=self.pot,
            bet_amount=bet_amount
        )
        self.history.append(record)
        if player == self.ai:
            self.ai_agent.record_hand(record)

    def get_hand_summary(self) -> str:
        if not self.history:
            return "No history available"
        return self.ai_agent.generate_hand_summary(self.history[-1])

    def get_ai_actions(self) -> List[AIAction]:
        return self.ai_actions