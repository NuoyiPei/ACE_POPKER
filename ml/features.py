from typing import List
from cards import Card

POSITION_MAP = {
    "UTG": 0,
    "MP": 1,
    "CO": 2,
    "BTN": 3,
    "SB": 4,
    "BB": 5
}

def extract_features(hand: List[Card], community: List[Card], position: str, pot: int, bet: int) -> List[float]:
    
    features = {
        "is_suited": int(hand[0].suit == hand[1].suit),
        "rank_gap": abs(hand[0].rank.value - hand[1].rank.value),
        "high_card": max(hand[0].rank.value, hand[1].rank.value),
        "position_index": POSITION_MAP.get(position, 0),
        "pot": pot,
        "current_bet": bet,
        "num_community_cards": len(community),
        "is_pair": int(hand[0].rank == hand[1].rank),
        "is_connector": int(abs(hand[0].rank.value - hand[1].rank.value) == 1),
        "is_ace": int(hand[0].rank.value == 14 or hand[1].rank.value == 14),
        "pot_odds": bet / (pot + bet) if pot + bet > 0 else 0
    }
    return list(features.values()) 