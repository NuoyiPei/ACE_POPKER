from dataclasses import dataclass
from typing import List
from cards import Card

@dataclass
class HandRecord:
    hand: List[Card]
    community_cards: List[Card]
    win_prob: float
    action: str
    result: float
    position: str
    pot_size: int
    bet_amount: int
