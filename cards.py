from enum import Enum
from dataclasses import dataclass
from typing import List
import random

SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    def __str__(self):
        return {
            11: "J", 12: "Q", 13: "K", 14: "A"
        }.get(self.value, str(self.value))

    def __lt__(self, other):  
        if isinstance(other, Rank):
            return self.value < other.value
        return NotImplemented

@dataclass
class Card:
    suit: Suit
    rank: Rank

    def __str__(self) -> str:
        return f"{self.rank}_of_{self.suit.value}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

class Deck:
    def __init__(self):
        self.cards = [Card(suit=suit, rank=rank) for suit in SUITS for rank in RANKS]
        # print("Deck initialized with cards:", self.cards)
        random.shuffle(self.cards)

    def deal(self, n=1):
        return [self.cards.pop() for _ in range(n)]

    def __len__(self) -> int:
        return len(self.cards)
    def reset(self):
        self.__init__()  
#  HandRank 
class HandRank:
    ROYAL_FLUSH = 10
    STRAIGHT_FLUSH = 9
    FOUR_OF_A_KIND = 8
    FULL_HOUSE = 7
    FLUSH = 6
    STRAIGHT = 5
    THREE_OF_A_KIND = 4
    TWO_PAIR = 3
    ONE_PAIR = 2
    HIGH_CARD = 1

    @staticmethod
    def evaluate_hand(cards: List[Card]) -> int:
        if len(cards) < 5:
            return HandRank.HIGH_CARD
        print("evaluate_hand:", cards)
        ranks = [card.rank for card in cards]
        suits = [card.suit for card in cards]
        print("ranks:", ranks)
        print("suits:", suits)
        ranks = []
        for card in cards:
            if hasattr(card, 'rank'):
                ranks.append(card.rank)
        
        suits = []
        for card in cards:
            if hasattr(card, 'suit'):
                suits.append(card.suit)
        
    
        rank_values = []
        for r in ranks:
            if hasattr(r, 'value'):  
                rank_values.append(r.value)
            else:  
                rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                        '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
                rank_values.append(rank_map.get(str(r), 0))
            
        rank_counts = {}
        for v in rank_values:
            rank_counts[v] = rank_counts.get(v, 0) + 1

        is_flush = any(suits.count(suit) >= 5 for suit in set(suits))

        sorted_unique_values = sorted(set(rank_values))

        is_straight = False
        for i in range(len(sorted_unique_values) - 4):
            if sorted_unique_values[i:i+5] == list(range(sorted_unique_values[i], sorted_unique_values[i]+5)):
                is_straight = True
                break

        if not is_straight and 14 in sorted_unique_values:
            # Ace-low straight
            is_straight = all(v in sorted_unique_values for v in [2, 3, 4, 5, 14])

        if is_flush and is_straight:
            if set([10, 11, 12, 13, 14]).issubset(sorted_unique_values):
                return HandRank.ROYAL_FLUSH
            return HandRank.STRAIGHT_FLUSH
        if 4 in rank_counts.values():
            return HandRank.FOUR_OF_A_KIND
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            return HandRank.FULL_HOUSE
        if is_flush:
            return HandRank.FLUSH
        if is_straight:
            return HandRank.STRAIGHT
        if 3 in rank_counts.values():
            return HandRank.THREE_OF_A_KIND
        if list(rank_counts.values()).count(2) >= 2:
            return HandRank.TWO_PAIR
        if 2 in rank_counts.values():
            return HandRank.ONE_PAIR
        return HandRank.HIGH_CARD
