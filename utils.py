from enum import Enum

class Suit(Enum):
    HEARTS = 'h'
    DIAMONDS = 'd'
    CLUBS = 'c'
    SPADES = 's'

class Rank(Enum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = 'T'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'

# Convert hand to readable string
def hand_to_text(hand):
    
    if not hand:
        return "--"
    return " ".join(f"{card.rank.value}{card.suit.value}" for card in hand)

# Format chip value
def format_chips(chips):
    
    return f"${chips:,.0f}"

# Calculate win probability (mock)
def calculate_win_probability(hand, community_cards, active_players=2, position=""):
    
    if not hand or len(hand) < 2:
        return "Unknown", 0.0
    
    # Dummy logic: give higher win rate for high cards or pairs
    ranks = [card.rank.value for card in hand]
    if ranks[0] == ranks[1]:
        return "Pair", 75.0
    elif 'A' in ranks or 'K' in ranks:
        return "High Card", 60.0
    else:
        return "Low Card", 40.0

# Recommend action based on win rate and situation
def suggest_action(win_prob, current_bet, pot, chips, position_index):
    
    if win_prob > 70:
        return "raise", int(min(pot * 0.5, chips)), "Strong hand, aggressive play"
    elif win_prob > 50:
        return "call", int(current_bet), "Decent hand, can call"
    else:
        return "fold", 0, "Weak hand, better fold"
