from game import PokerGame
from montecarlo import MonteCarloSimulator
import sys
import random
import os

# Clear terminal screen at start
os.system('cls' if os.name == 'nt' else 'clear')

print("\n>>> Starting ACE Poker script")
print("Welcome to ACE POKER")

def print_game_state(game: PokerGame, simulator: MonteCarloSimulator):
    print("\n" + "="*45 + f" GAME STATE / {game.round_name} " + "="*45)
    print(f"Your Position: {game.player.position}")
    print(f"Your Chips: ${game.player.chips}")
    print(f"Your Hand: {' '.join(str(card) for card in game.player.hand)}")
    print(f"Pot: ${game.pot}")

    if game.community_cards:
        print(f"Community Cards: {' '.join(str(card) for card in game.community_cards)}")

    print("\nPlayer Actions:")
    for action in game.ai_actions:
        action_desc = f"${action.amount}" if action.amount > 0 else ""
        print(f"{action.position:<6} -> {action.action.capitalize()} {action_desc}")

    if game.player.hand:
        win_rate = simulator.calculate_win_rate(game.player.hand, game.community_cards)
        pot_odds = simulator.calculate_pot_odds(game.pot, game.current_bet)
        ev = simulator.calculate_expected_value(win_rate, game.pot, game.current_bet)

        print(f"\nWin Rate (Monte Carlo): {win_rate:.1%}")
        print(f"Implied Odds: {pot_odds:.2f} : 1")
        print(f"Expected Value (EV): ${ev:+.1f}")
        print(f"GTO Recommendation: {'Call' if win_rate > 0.5 else 'Fold'}")
        print(f"Suggested Action: {'Raise to $' + str(int(game.pot * 0.75)) if win_rate > 0.65 else 'Check or Call'}")

    print("\n" + "="*100)

def print_hand_summary(game: PokerGame):
    print("\n" + "="*50 + " Hand Review " + "="*50)
    print(f"Player: {game.player.name} (Position: {game.player.position})")
    print(f"Starting Hand: {' '.join(str(card) for card in game.player.hand)}")

    if game.community_cards:
        print(f"Community Cards: {' '.join(str(card) for card in game.community_cards)}")

    win_rate = game.ai_agent.simulator.calculate_win_rate(game.player.hand, game.community_cards)
    pot_odds = game.ai_agent.simulator.calculate_pot_odds(game.pot, game.current_bet)
    ev = game.ai_agent.simulator.calculate_expected_value(win_rate, game.pot, game.current_bet)

    print(f"Final Win Rate: {win_rate:.1%}")
    print(f"Final EV: ${ev:+.1f}")

    if game.history:
        last_action = game.history[-1]
        print(f"Final Action: {last_action.action} {'$' + str(last_action.bet_amount) if last_action.bet_amount > 0 else ''}")
        print(f"Suggested Action: {'Call' if win_rate > 0.5 else 'Fold'}")

    print("\nAI Player Actions:")
    for action in game.get_ai_actions():
        action_desc = f"${action.amount}" if action.amount > 0 else ""
        print(f"{action.position:<6} -> {action.action.capitalize()} {action_desc}")

    print(f"\nOutcome: {'Win' if game.history and game.history[-1].result > 0 else 'Loss'} (Pot: ${game.pot})")

    if ev > 0 and game.history and game.history[-1].action == "raise":
        print("Summary: Aggressive play secured high EV. Well played!")
    elif ev < 0 and game.history and game.history[-1].action == "call":
        print("Summary: Overly optimistic play. Consider controlling bet size.")
    else:
        print("Summary: Reasonable play. Keep it up!")

    print("\n" + "="*100)

def handle_betting_round(game: PokerGame, simulator: MonteCarloSimulator, round_name: str) -> bool:
    print(f"\n {round_name} :")

    game.round_name = round_name  # ✅ 新增：设置当前阶段

    game.simulate_other_players_actions()
    print_game_state(game, simulator)

    action, amount = get_player_action()
    success, bet_amount = game.player_action(action, amount)

    if not success:
        print("You folded!")
        result = 0
        game.record_hand(game.player, action, 0, result)
        print_hand_summary(game)
        return False

    ai_action, ai_amount = game.ai_action()
    print(f"\n{game.ai.position} chooses: {ai_action} {'$' + str(ai_amount) if ai_amount > 0 else ''}")

    ai_actives = sum(1 for a in game.get_ai_actions() if a.action != "fold")
    active_count = int(game.player.is_active) + int(game.ai.is_active) + ai_actives
    return active_count >= 2

def get_player_action():
    while True:
        action = input("\nYour action (fold / call / raise): ").lower().strip()
        if action in ['fold', 'call', 'raise']:
            if action == 'raise':
                try:
                    amount = int(input("Raise amount: $"))
                    return action, amount
                except ValueError:
                    print("Please enter a valid amount")
            else:
                return action, None
        print("Invalid action. Please choose fold, call, or raise")

def main():
    player_name = input("Please enter your name: ").strip()
    print(f"\nHello, {player_name}! Let's begin ...")

    game = PokerGame(player_name)
    game.round_name = ""  # ✅ 初始化默认 round_name
    simulator = MonteCarloSimulator()
    hands_played = 0

    while True:
        game.start_new_hand()

        if not handle_betting_round(game, simulator, "Pre-flop"):
            if input("\nPlay again? (y/n): ").lower() != 'y':
                print("Thank you for playing!")
                break
            continue

        game.deal_community_cards(3)
        if not handle_betting_round(game, simulator, "Flop"):
            if input("\nPlay again? (y/n): ").lower() != 'y':
                print("Thank you for playing!")
                break
            continue

        game.deal_community_cards(1)
        if not handle_betting_round(game, simulator, "Turn"):
            if input("\nPlay again? (y/n): ").lower() != 'y':
                print("Thank you for playing!")
                break
            continue

        game.deal_community_cards(1)
        if not handle_betting_round(game, simulator, "River"):
            if input("\nPlay again? (y/n): ").lower() != 'y':
                print("Thank you for playing!")
                break
            continue

        print("\nShowdown ")
        if game.player.is_active and game.ai.is_active:
            print(f"{game.ai.position}'s hand: {' '.join(str(card) for card in game.ai.hand)}")

        player_strength = simulator.calculate_win_rate(game.player.hand, game.community_cards)
        ai_strength = simulator.calculate_win_rate(game.ai.hand, game.community_cards)
        result = 1 if player_strength > ai_strength else 0

        game.record_hand(game.player, "showdown", 0, result)
        print_hand_summary(game)

        game.ai_agent.learn()
        hands_played += 1

        if input("\nPlay again? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main()
