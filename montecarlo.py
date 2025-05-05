from typing import List, Dict
from cards import Card, Deck, Suit, Rank, HandRank
import random
import json
import os

class MonteCarloSimulator:
    def __init__(self, num_simulations: int = 1000):
        self.num_simulations = num_simulations
        self.gto_data = self._load_gto_data()

    def _load_gto_data(self) -> Dict:
        try:
            with open('gto_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("GTO data file not found, using default values")
            return self._create_default_gto_data()

    def _create_default_gto_data(self) -> Dict:
        return {
            "preflop": {
                "positions": ["UTG", "MP", "CO", "BTN", "SB", "BB"],
                "hand_strengths": {
                    "AA": 0.85, "KK": 0.82, "QQ": 0.80, "JJ": 0.78,
                    "TT": 0.75, "99": 0.72, "88": 0.70, "77": 0.68,
                    "66": 0.65, "55": 0.63, "44": 0.60, "33": 0.58, "22": 0.55,
                    "AKs": 0.67, "AQs": 0.66, "AJs": 0.65, "ATs": 0.64,
                    "KQs": 0.63, "KJs": 0.62, "KTs": 0.61,
                    "QJs": 0.60, "QTs": 0.59,
                    "JTs": 0.58,
                    "AKo": 0.65, "AQo": 0.64, "AJo": 0.63, "ATo": 0.62,
                    "KQo": 0.61, "KJo": 0.60, "KTo": 0.59,
                    "QJo": 0.58, "QTo": 0.57,
                    "JTo": 0.56
                }
            },
            "postflop": {
                "board_textures": {
                    "paired": 0.1,
                    "monotone": 0.15,
                    "connected": 0.12,
                    "rainbow": 0.05
                }
            }
        }

    def calculate_win_rate(self, hand: List[Card], community_cards: List[Card], position: str = "SB") -> float:
        print("calculate_win_rate hand: ", hand)
        flat_hand = []
        for item in hand:
            if isinstance(item, list) and item:
                flat_hand.append(item[0])
            else:
                flat_hand.append(item)
        
        flat_community = []
        if community_cards:
            for item in community_cards:
                if isinstance(item, list) and item:
                    flat_community.append(item[0])
                else:
                    flat_community.append(item)
        if len(flat_hand) != 2:
            return 0.0

        hand_key = self._get_hand_key(flat_hand)
        base_win_rate = self.gto_data["preflop"]["hand_strengths"].get(hand_key, 0.5)

        position_index = self.gto_data["preflop"]["positions"].index(position)
        position_factor = 1.0 - (position_index * 0.05)

        board_factor = self._get_board_factor(flat_community) if community_cards else 1.0

        wins = 0
        print(f"Simulating {self.num_simulations} hands for {flat_hand} against {flat_community} community cards.")
        for _ in range(self.num_simulations):
            if self._simulate_hand(flat_hand, flat_community):
                wins += 1
        print(f"Simulated wins: {wins} out of {self.num_simulations}")
        simulated_win_rate = wins / self.num_simulations
        # final_win_rate = (base_win_rate * 0.4 + simulated_win_rate * 0.3 + board_factor * 0.3) * position_factor
        final_win_rate = (base_win_rate * 0.6 + simulated_win_rate * 0.4) * position_factor

        print(f"final_win_rate: {final_win_rate}, base_win_rate: {base_win_rate}, simulated_win_rate: {simulated_win_rate}, position_factor: {position_factor}, board_factor: {board_factor}")
        return max(0.0, min(1.0, final_win_rate))

    def _get_hand_key(self, hand: List[Card]) -> str:
        ranks = sorted([card.rank for card in hand], reverse=True)
        print(f"Hand ranks: {ranks}")
        is_suited = hand[0].suit == hand[1].suit

        if ranks[0] == ranks[1]:
            return f"{ranks[0]}{ranks[1]}"
        else:
            suit = "s" if is_suited else "o"
            return f"{ranks[0]}{ranks[1]}{suit}"

    def _get_board_factor(self, community_cards: List[Card]) -> float:
        print(f"Community cards: {community_cards}")
        
        
        rank_values = []
        for card in community_cards:
            rank = card.rank
            
            rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                    '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
            rank_values.append(rank_map.get(str(rank), 0))
        
        print(f"Board rank values: {rank_values}")
        
        
        if len(set(rank_values)) < len(rank_values):
            return self.gto_data["postflop"]["board_textures"]["paired"]

        
        suits = [card.suit for card in community_cards]
        if len(set(suits)) == 1:
            return self.gto_data["postflop"]["board_textures"]["monotone"]

        
        rank_values.sort()
        is_connected = all(rank_values[i+1] - rank_values[i] <= 2 for i in range(len(rank_values)-1))
        if is_connected:
            return self.gto_data["postflop"]["board_textures"]["connected"]

        
        return self.gto_data["postflop"]["board_textures"]["rainbow"]

    def _simulate_hand(self, hand: List[Card], community_cards: List[Card]) -> bool:
        # print(f"Simulating hand: {hand} with community cards: {community_cards}")

        flat_community = []
        for item in community_cards:
            if isinstance(item, list) and item:
                flat_community.append(item[0])
            else:
                flat_community.append(item)
        # print(f"flat_community: {flat_community}")
        deck = Deck()

        for card in hand + flat_community:
            try:
                deck.cards.remove(card)
            except ValueError:
                pass

        remaining_community = 5 - len(flat_community)
        dealt_community = []
        for _ in range(remaining_community):
            card = deck.deal()[0]  
            dealt_community.append(card)
        all_community = flat_community + dealt_community

        opponent_hand = []
        for _ in range(2):
            card = deck.deal()
            if isinstance(card, list) and card:
                opponent_hand.append(card[0])  
            else:
                opponent_hand.append(card)
        # print(f"hand+all_community: {hand + all_community}")
        player_rank = HandRank.evaluate_hand(hand + all_community)
        opponent_rank = HandRank.evaluate_hand(opponent_hand + all_community)

        return player_rank > opponent_rank

    def calculate_pot_odds(self, pot_size: int, bet_amount: int) -> float:
        if bet_amount == 0:
            return float('inf')
        return pot_size / bet_amount

    def calculate_expected_value(self, win_rate: float, pot_size: int, bet_amount: int) -> float:
        return (win_rate * pot_size) - ((1 - win_rate) * bet_amount)