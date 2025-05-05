import tkinter as tk
from tkinter import messagebox
import math
from PIL import Image, ImageTk
from game import PokerGame, Player, AIAction
from cards import HandRank
import os
import random

# ==== Poker Constants ====
SUITS = ['spades', 'hearts', 'diamonds', 'clubs']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
PLAYER_POSITIONS = ["SB", "BB", "UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN"]

# ==== Poker Card Class ====
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        rank_mapping = {
            'A': 'ace',
            'K': 'king',
            'Q': 'queen',
            'J': 'jack'
        }
        
        # Use the mapping for face cards, or just use the rank as is
        rank_name = rank_mapping.get(self.rank, self.rank.lower())
        
        return f"{rank_name}_of_{self.suit.lower()}"

# ==== Dummy Game for GUI ====
class DummyPlayer:
    def __init__(self):
        self.hand = [Card('A', 'spades'), Card('Q', 'diamonds')]

class DummyGame:
    def __init__(self):
        self.player = DummyPlayer()

# ==== Ellipse Positioning ====
def get_ellipse_positions(cx, cy, a, b, n):
    positions = []
    for i in range(n):
        theta = 2 * math.pi * i / n
        x = cx + a * math.cos(theta)
        y = cy + b * math.sin(theta)
        positions.append((x, y))
    return positions

# ==== GUI ====
class PokerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ACE Poker GUI")
        self.geometry("1024x768")
        # self.resizable(False, False)
        self.configure(bg="#222")
        
        self.canvas = tk.Canvas(self, width=800, height=650, bg="#222", highlightthickness=0)
        self.canvas.pack()
        
        # Initialize game stages
        self.game_stages = {
            "preflop": "Pre-Flop",
            "flop": "Flop",
            "turn": "Turn",
            "river": "River",
            "showdown": "Showdown"
        }
        self.current_stage = "preflop"

        

        # Game logic - initialize PokerGame with a player name
        self.game = PokerGame(num_players=9)
        if not hasattr(self.game, 'dealer_position'):
            self.game.dealer_position = 0  
        # self.game.dealer_position = 0
        
        # Get references to human player and AI
        positions = ["SB", "BB", "UTG", "UTG+1", "MP", "LJ", "HJ", "CO","BTN"]
        self.human_player = Player("You", chips=1000, position="SB")
        self.game.players.append(self.human_player)
        self.game.player = self.human_player

        # self.ai_player = self.game.ai  # Reference to main AI opponent
        # self.ai_player.position = "BB"
        # if self.ai_player not in self.game.players:
        #     self.game.players.append(self.ai_player) 
        remaining_positions = [pos for pos in positions if pos not in ["SB"]]
        for i, pos in enumerate(remaining_positions):
            ai_player = Player(pos, chips=400, position=pos)  
            self.game.players.append(ai_player)

        print("Players in game:", [p.name for p in self.game.players])


        
        
        

        # Draw table
        self.canvas.create_oval(80, 40, 720, 460, fill="#206030", outline="#0a2a12", width=8)
        
        # Draw seats
        self.seat_labels = []
        self.seat_objects = []

        SEAT_COORDS = get_ellipse_positions(400, 250, 300, 180, 9)
        self.seat_status_text = {}
        self.ai_card_images = {}
        position_adjustments = {
            "BTN": (70, -80),    
            "SB": (70, -80),      
            "BB": (70, 0),       
            "UTG": (0, 25),      
            "UTG+1": (-70, 0),   
            "MP": (-70, 0),      
            "LJ": (-70, -80),      
            "HJ": (70, -60),    
            "CO": (70, -60)      
        }
        
        for i, (x, y) in enumerate(SEAT_COORDS):
            seat_position = PLAYER_POSITIONS[i]  
            
            
            x_adjust, y_adjust = position_adjustments.get(seat_position, (0, 0))
            
            
            status_text = self.canvas.create_text(
                x + x_adjust, y + 80 + y_adjust,  
                text="",
                fill="#fff",
                font=("Arial", 10, "bold"),
                tags="status_text"  
            )
            self.seat_status_text[i] = status_text  
            
            
            seat = self.canvas.create_oval(x-40, y-30, x+40, y+30, fill="#111", outline="#444", width=2)
            label = self.canvas.create_text(x, y-20, text=seat_position, fill="#fff", font=("Arial", 12, "bold"))
            chips = self.canvas.create_text(x, y+10, text="400", fill="#0f0", font=("Arial", 12))
            cards = self.canvas.create_rectangle(x-20, y+20, x+20, y+40, fill="#b00", outline="#fff")
            self.seat_labels.append((label, chips, cards))
            self.seat_objects.append(seat)
            
            
            if i != 0:  
                
                self.ai_card_images[i] = [  
                    self.canvas.create_image(x-20, y+55, image=None),  
                    self.canvas.create_image(x+20, y+55, image=None)   
                ]
                    
        # Pot display
        self.pot_text = self.canvas.create_text(400, 240, text=f"pot: {self.game.pot}", fill="#fff", font=("Arial", 16, "bold"))
        
        # Load card images
        self.card_images = self.load_card_images("./cards")
        print("Loaded card images:", list(self.card_images.keys()))

        self.show_ai_hands = tk.BooleanVar(value=True)  
        self.show_hands_btn = tk.Button(
            self, 
            text="Hide AI Hands", 
            command=self.toggle_ai_hands,
            bg="#333",
            fg="#222",
            font=("Arial", 10),
            relief=tk.FLAT  
        )
        self.show_hands_btn.place(x=900, y=20)  


         
        for position in self.ai_card_images:
            for i in range(2):
                self.canvas.itemconfig(self.ai_card_images[position][i], image=self.card_images["back"])
        
        # User hand
        self.user_card_images = [
            self.canvas.create_image(380, 580, image=self.card_images["back"]),
            self.canvas.create_image(430, 580, image=self.card_images["back"])
        ]
        # self.canvas.create_text(400, 550, text="High Card", fill="#fff", font=("Arial", 12))

        self.community_card_images = []
        for i in range(5): 
            x_pos = 280 + i * 60  
            card_img = self.canvas.create_image(x_pos, 300, image=self.card_images["back"])
            self.canvas.itemconfig(card_img, state='hidden')  # hidden at start
            self.community_card_images.append(card_img)
        
        # Action buttons
        self.action_frame = tk.Frame(self, bg="#222")
        self.action_frame.pack(pady=20)
        self.fold_btn = tk.Button(self.action_frame, text="Fold", width=10, command=self.fold_action)
        self.call_btn = tk.Button(self.action_frame, text="Call", width=10, command=self.call_action)
        self.raise_btn = tk.Button(self.action_frame, text="Raise(2x)", width=10, command=self.raise_action)
        # self.check_btn = tk.Button(self.action_frame, text="Check", width=10, command=self.check_action)

        self.fold_btn.grid(row=0, column=0, padx=10)
        self.call_btn.grid(row=0, column=1, padx=10)
        self.raise_btn.grid(row=0, column=2, padx=10)
        # self.check_btn.grid(row=0, column=3, padx=10)
        
        # Info bar
        self.info_bar = tk.Label(self, text=f"Total: ${self.human_player.chips} | Current hand: $0", bg="#222", fg="#fff", font=("Arial", 12))
        self.info_bar.pack(fill="x", side="bottom")

        
        self.stage_text = self.canvas.create_text(400, 210, text="Pre-Flop", fill="#fff", font=("Arial", 16, "bold"))
        # Action prompt
        self.prompt = tk.Label(self, text="Waiting for action...", bg="#222", fg="#fff", font=("Arial", 14))
        self.prompt.pack(pady=5)
        
        # Start a new hand
        self.game.start_new_hand()
        self.update_player_hand()
        # Update display with initial game state
        self.update_display()
        self.highlight_active_player("SB")
    def toggle_ai_hands(self):
        """切换显示/隐藏AI手牌"""
        self.show_ai_hands.set(not self.show_ai_hands.get())
        
        
        if self.show_ai_hands.get():
            self.show_hands_btn.config(text="Hide AI Hands")
        else:
            self.show_hands_btn.config(text="Show AI Hands")
        
        
        self.update_ai_hands()

    def load_card_images(self, folder):
        card_images = {}
        for filename in os.listdir(folder):
            if filename.endswith(".png"):
                key = filename[:-4]  # "2_of_clubs"
                img = Image.open(os.path.join(folder, filename)).resize((40, 60))
                # Create a white background image
                background = Image.new("RGBA", img.size, (255, 255, 255, 255))
            
                # Paste the card image on the white background
                # The alpha_composite method handles transparency properly
                combined = Image.alpha_composite(background.convert("RGBA"), img.convert("RGBA"))
                
                # Convert to RGB (removing alpha channel)
                combined = combined.convert("RGB")
                
                # Resize if needed
                combined = combined.resize((40, 60))
                
                # Convert to PhotoImage
                card_images[key] = ImageTk.PhotoImage(combined)
        
        if "back" not in card_images:
            back_img = Image.new("RGB", (40, 60), color="#b00")
            card_images["back"] = ImageTk.PhotoImage(back_img)
        return card_images
    def highlight_active_player(self, position=None):
        
        for i in range(len(self.seat_objects)):
            self.canvas.itemconfig(self.seat_objects[i], fill="#111", outline="#444", width=2)
        
        
        if position:
            for i, player in enumerate(self.game.players):
                if player.position == position:
                    
                    self.canvas.itemconfig(self.seat_objects[i], fill="#3a3a3a", outline="#ff8800", width=3)
                    break


    def update_community_cards(self):
        
        for img in self.community_card_images:
            self.canvas.itemconfig(img, state='hidden')
        
        
        for i, card in enumerate(self.game.community_cards):
            if i < len(self.community_card_images):
                
                self.canvas.itemconfig(self.community_card_images[i], state='normal')
                
                
                try:
                    
                    card_obj = card[0] if isinstance(card, list) and card else card
                    
                    
                    suit = card_obj.suit.lower()
                    rank = card_obj.rank.lower()
                    
                    
                    if rank in ['hearts', 'diamonds', 'clubs', 'spades']:
                        suit, rank = rank, suit
                    
                    
                    if rank in ['j', 'q', 'k', 'a']:
                        rank_mapping = {'j': 'jack', 'q': 'queen', 'k': 'king', 'a': 'ace'}
                        rank = rank_mapping[rank]
                    
                    card_key = f"{rank}_of_{suit}"
                    
                    if card_key in self.card_images:
                        self.canvas.itemconfig(self.community_card_images[i], 
                                            image=self.card_images[card_key])
                    else:
                        
                        print(f"Community card image not found: {card_key}")
                        self.canvas.itemconfig(self.community_card_images[i], 
                                            image=self.card_images["back"])
                except Exception as e:
                    print(f"Error updating community card {i}: {e}")
                    self.canvas.itemconfig(self.community_card_images[i], 
                                        image=self.card_images["back"])


    def update_ai_hands(self):
        is_showdown = self.current_stage == "showdown"
        
        for i, player in enumerate(self.game.players):
            if player != self.human_player and i in self.ai_card_images:  
                
                if not player.is_active and (not self.show_ai_hands.get() or is_showdown):
                    for card_idx in range(2):
                        self.canvas.itemconfig(self.ai_card_images[i][card_idx], state='hidden')
                    continue
                
                
                for card_idx in range(2):
                    self.canvas.itemconfig(self.ai_card_images[i][card_idx], state='normal')
                
                
                show_cards = (is_showdown and player.is_active) or self.show_ai_hands.get()
                
                if player.hand and len(player.hand) >= 2:
                    
                    for card_idx, card_or_list in enumerate(player.hand[:2]):
                        
                        card = card_or_list[0] if isinstance(card_or_list, list) and card_or_list else card_or_list
                        
                        try:
                            
                            suit = card.suit.lower()
                            rank = card.rank.lower()
                            
                            
                            if rank in ['j', 'q', 'k', 'a']:
                                rank_mapping = {'j': 'jack', 'q': 'queen', 'k': 'king', 'a': 'ace'}
                                rank = rank_mapping[rank]
                            
                            card_key = f"{rank}_of_{suit}"
                            
                            
                            if show_cards:
                                
                                if card_key in self.card_images:
                                    self.canvas.itemconfig(self.ai_card_images[i][card_idx], 
                                                        image=self.card_images[card_key])
                                else:
                                    print(f"AI player card image not found: {card_key} for {player.position}")
                                    self.canvas.itemconfig(self.ai_card_images[i][card_idx], 
                                                        image=self.card_images["back"])
                            else:
                                
                                self.canvas.itemconfig(self.ai_card_images[i][card_idx], 
                                                    image=self.card_images["back"])
                        except Exception as e:
                            print(f"Error updating AI player {player.position} card {card_idx}: {e}")
                            self.canvas.itemconfig(self.ai_card_images[i][card_idx], 
                                                image=self.card_images["back"])
    def update_player_status(self):
        for seat_idx in self.seat_status_text:
            self.canvas.itemconfig(self.seat_status_text[seat_idx], text="")
        
        if hasattr(self.game, 'ai_actions') and self.game.ai_actions:
            for i, player in enumerate(self.game.players):
                if i in self.seat_status_text:
                    status_text = ""
                    
                    if not player.is_active:
                        status_text = "Folded"
                    else:
                        for action_record in self.game.ai_actions:
                            if action_record.position == player.position:
                                if action_record.action == "call":
                                    amount = self.game.current_bet
                                else:
                                    amount = action_record.amount
                                    
                                if amount > 0:
                                    status_text = f"{action_record.action.capitalize()} ${amount}"
                                else:
                                    status_text = f"{action_record.action.capitalize()}"
                                break
                    self.canvas.itemconfig(self.seat_status_text[i], text=status_text)


    def update_display(self):
        
        self.canvas.itemconfig(self.pot_text, text=f"pot: {self.game.pot}")
        self.update_player_hand()
        self.update_ai_hands()
        self.update_community_cards()
        self.update_player_status()
        
        
        for i, player in enumerate(self.game.players):
            self.canvas.itemconfig(self.seat_labels[i][0], text=f"{player.position}")
            
            self.canvas.itemconfig(self.seat_labels[i][1], text=str(player.chips))
            
            if player == self.human_player:
                self.canvas.itemconfig(self.seat_labels[i][0], text=f"{player.position} (You)")
        
        
        self.info_bar.config(text=f"Total: ${self.human_player.chips} | Position: {self.human_player.position} | Current bet: ${self.game.current_bet}")


    def update_stage_display(self):

        stage_name = self.game_stages.get(self.current_stage, "Unknown")
        self.canvas.itemconfig(self.stage_text, text=stage_name)
    # def ai_turn(self):
    
    #     action, amount = self.game.ai_action()
    #     action, amount = self.game.ai_action()
        

    #     amount_text = f"${amount}" if amount else ""
    #     self.prompt.config(text=f"AI {action}ed {amount_text}")
        

    #     self.update_display()
    #     self.after(1000, self.check_game_stage)
    
    
    # self.after(1000, self.check_game_stage)
    # def fold_action(self):
    #     self.prompt.config(text="You folded")
    #     success, amount = self.game.player_action("fold")
    #     self.update_display()  
    #     self.after(1000, self.play_ai_turns)

    # def call_action(self):
    #     success, amount = self.game.player_action("call")
    #     self.update_display()
    #     # After player action, maybe trigger AI action
    #     self.after(1000, self.ai_turn)

    # def raise_action(self):
    #     amount = 100  # Default raise amount
    #     success, bet_amount = self.game.player_action("raise", amount)
    #     self.update_display()
    #     # After player action, maybe trigger AI action
    #     self.after(1000, self.ai_turn)
    # def check_action(self):
    #     success, amount = self.game.player_action("check")
    #     self.update_display()
    #     # After player action, trigger AI action
    #     self.after(1000, self.ai_turn)


    def fold_action(self):
        self.prompt.config(text="You folded")
        success, amount = self.game.player_action("fold")
        
        
        if not hasattr(self.game, 'ai_actions'):
            self.game.ai_actions = []
        self.game.ai_actions.append(AIAction(position=self.human_player.position, action="fold", amount=0))
        
        self.update_display()  
        self.after(1000, self.play_ai_turns)

    def call_action(self):
        call_amount = self.game.current_bet
        self.prompt.config(text=f"You called ${call_amount}")
        success, amount = self.game.player_action("call")
        
        
        if not hasattr(self.game, 'ai_actions'):
            self.game.ai_actions = []
        self.game.ai_actions.append(AIAction(position=self.human_player.position, action="call", amount=call_amount))
        
        self.update_display()
        
        self.after(1000, self.play_ai_turns)

    def raise_action(self):
        
        raise_amount = self.game.current_bet * 2
        if raise_amount < 20:  
            raise_amount = 20
        
        self.prompt.config(text=f"You raised to ${raise_amount}")
        success, bet_amount = self.game.player_action("raise", raise_amount)
        
        
        if not hasattr(self.game, 'ai_actions'):
            self.game.ai_actions = []
        self.game.ai_actions.append(AIAction(position=self.human_player.position, action="raise", amount=raise_amount))
        
        
        self.game.current_bet = raise_amount
        
        self.update_display()
        
        self.after(1000, self.handle_raise)

    def check_action(self):
        self.prompt.config(text="You checked")
        success, amount = self.game.player_action("check")
        
        
        if not hasattr(self.game, 'ai_actions'):
            self.game.ai_actions = []
        self.game.ai_actions.append(AIAction(position=self.human_player.position, action="check", amount=0))
        
        self.update_display()
        
        
        self.human_checked_this_round = True
        self.after(1000, self.play_ai_turns)
    def update_player_hand(self):
        if hasattr(self, 'human_player') and self.human_player.hand:
            # print("Hand content:", self.human_player.hand)
            
            # Process each card in hand (up to 2 cards)
            for i, card_or_list in enumerate(self.human_player.hand[:2]):
                # If it's a list, take the first element
                card = card_or_list[0] if isinstance(card_or_list, list) else card_or_list
                
                # Try to directly build the key in image filename format
                try:
                    suit = card.suit.lower()  # Convert to lowercase
                    rank = card.rank.lower()  # Convert to lowercase
                    
                    # Swap positions (in case they're reversed)
                    if rank in ['hearts', 'diamonds', 'clubs', 'spades']:
                        suit, rank = rank, suit
                    
                    # Handle face cards
                    if rank in ['j', 'q', 'k', 'a']:
                        rank_mapping = {'j': 'jack', 'q': 'queen', 'k': 'king', 'a': 'ace'}
                        rank = rank_mapping[rank]
                    
                    card_key = f"{rank}_of_{suit}"
                    print(f"Trying to build card key: {card_key}")
                    
                    if card_key in self.card_images:
                        self.canvas.itemconfig(self.user_card_images[i], image=self.card_images[card_key])
                    else:
                        print(f"Card image not found: {card_key}")
                        self.canvas.itemconfig(self.user_card_images[i], image=self.card_images["back"])
                except Exception as e:
                    print(f"Error processing card: {e}")
                    self.canvas.itemconfig(self.user_card_images[i], image=self.card_images["back"])
    
    def play_ai_turns(self):
        ai_players = [p for p in self.game.players if p != self.human_player and p.is_active]
        print("AI players in the game:", ai_players)
        self.game.ai_actions = []
        self.update_display()
        
        ai_bet = False
        
        
        for ai_player in ai_players:
            self.highlight_active_player(ai_player.position)
            
            action, amount = self.game.ai_action(player=ai_player)

            self.game.ai_actions.append(AIAction(position=ai_player.position, action=action, amount=amount))
            
            
            if (action == "call" or action == "raise") and amount > 0:
                ai_bet = True
                self.game.current_bet = amount
            
            
            amount_text = f"${amount}" if amount else ""
            self.prompt.config(text=f"{ai_player.position} {action}ed {amount_text}")
            
            
            self.update_display()
            
            
            self.update()
            self.after(1000 if self.human_player.is_active else 300)
        
        
        if hasattr(self, 'human_checked_this_round') and self.human_checked_this_round and ai_bet:
            self.human_checked_this_round = False  
            self.prompt_human_after_ai_bet()
            return
        
        
        active_players = [p for p in self.game.players if p.is_active]
        if len(active_players) <= 1:
            winner = active_players[0] if active_players else None
            if winner:
                self.prompt.config(text=f"{winner.name} wins ${self.game.pot}!")
                winner.chips += self.game.pot
                self.game.pot = 0
            self.after(2000, self.start_new_hand)
            return True  
        
        self.after(1000, self.check_game_stage)
        return False  

    def check_game_stage(self):
        
        active_players = [p for p in self.game.players if p.is_active]
        if len(active_players) <= 1:
            
            winner = active_players[0] if active_players else None
            if winner:
                self.prompt.config(text=f"{winner.name} wins ${self.game.pot}!")
            else:
                self.prompt.config(text="All players folded!")
            self.after(2000, self.start_new_hand)
            return
        
        
        if self.current_stage == "preflop":
            self.current_stage = "flop"
            self.game.deal_community_cards(3)
            self.prompt.config(text="Flop cards dealt")
        elif self.current_stage == "flop":
            self.current_stage = "turn"
            self.game.deal_community_cards(1)
            self.prompt.config(text="Turn card dealt")
        elif self.current_stage == "turn":
            self.current_stage = "river" 
            self.game.deal_community_cards(1)
            self.prompt.config(text="River card dealt")
        elif self.current_stage == "river":
            self.current_stage = "showdown"
            self.update_ai_hands()
            self.handle_showdown()
            return
        
        self.update_display()
        self.update_stage_display()  
        

        if not self.human_player.is_active:
            # self.prompt.config(text="You folded. AI wins.")
            # self.after(2000, self.start_new_hand)
            self.play_ai_turns()
            return
        
        # self.check_btn.config(state=tk.NORMAL)
        self.call_btn.config(text="Call")
        
        # self.update_display()
        
        self.prompt.config(text="Your turn")
        self.highlight_active_player("SB") 

    # def handle_showdown(self):
    #     """Handle showdown phase"""
    #     self.prompt.config(text="Showdown!")
    
    #     if random.random() > 0.5:
    #         self.prompt.config(text="You win!")
    #         self.human_player.chips += self.game.pot
    #     else:
    #         self.prompt.config(text="AI wins!")
    #         self.ai_player.chips += self.game.pot
    #     self.game.pot = 0
    #     self.update_display()
    #     self.after(2000, self.start_new_hand)

    def handle_showdown(self):
        self.prompt.config(text="Showdown!")
        
        
        active_players = [p for p in self.game.players if p.is_active]
        
        
        player_scores = {}
        for player in active_players:
            
            flat_hand = []
            for item in player.hand:
                if isinstance(item, list) and item:
                    flat_hand.append(item[0])
                else:
                    flat_hand.append(item)
            
            flat_community = []
            for item in self.game.community_cards:
                if isinstance(item, list) and item:
                    flat_community.append(item[0])
                else:
                    flat_community.append(item)
            
            
            score = HandRank.evaluate_hand(flat_hand + flat_community)
            player_scores[player] = score
        
        
        max_score = max(player_scores.values())
        winners = [p for p in player_scores if player_scores[p] == max_score]
        
        
        pot_per_winner = self.game.pot // len(winners)
        
        
        if len(winners) == 1:
            winner = winners[0]
            if winner == self.human_player:
                self.prompt.config(text=f"You win ${self.game.pot}!")
            else:
                self.prompt.config(text=f"{winner.position} wins ${self.game.pot}!")
            winner.chips += self.game.pot
        else:
            
            winner_names = []
            for winner in winners:
                if winner == self.human_player:
                    winner_names.append("You")
                else:
                    winner_names.append(winner.position)
                winner.chips += pot_per_winner
            
            self.prompt.config(text=f"Pot split between: {', '.join(winner_names)}! Each gets ${pot_per_winner}")
        
        self.game.pot = 0
        self.update_display()
        self.after(2000, self.start_new_hand)

    def handle_raise(self):
        active_ai_players = [p for p in self.game.players if p != self.human_player and p.is_active]
        
        
        if not active_ai_players:
            self.after(1000, self.check_game_stage)
            return
        
        
        if not hasattr(self, 'responded_to_raise'):
            self.responded_to_raise = set()
        
        
        next_to_respond = None
        for player in active_ai_players:
            if player not in self.responded_to_raise:
                next_to_respond = player
                break
        
        if next_to_respond:
            self.highlight_active_player(next_to_respond.position)
            self.prompt.config(text=f"{next_to_respond.position} is thinking...")
            
            self.game.current_bet = max(self.game.current_bet, 40)  
            
            
            action, amount = self.game.ai_action(player=next_to_respond)
            
            
            if action == "call":
                amount = self.game.current_bet  
            
            
            if not hasattr(self.game, 'ai_actions'):
                self.game.ai_actions = []
            self.game.ai_actions.append(AIAction(position=next_to_respond.position, action=action, amount=amount))
            
            
            self.responded_to_raise.add(next_to_respond)
            
            
            amount_text = f"${amount}" if amount else ""
            self.prompt.config(text=f"{next_to_respond.position} {action}ed {amount_text}")
            
            self.update_display()
            
            
            if action == "raise":
                self.game.current_bet = amount
                self.responded_to_raise = set([next_to_respond])
                
                if self.human_player.is_active:
                    self.after(1000, lambda: self.prompt_human_response_to_raise(amount))
                else:
                    self.after(800, self.handle_raise)
            else:
                
                self.after(800, self.handle_raise)
        else:
            
            self.responded_to_raise = set()
            
            self.after(1000, self.check_game_stage)
    
    def prompt_human_response_to_raise(self, raise_amount):

        self.prompt.config(text=f"AI raised to ${raise_amount}. Your turn.")
        self.highlight_active_player(self.human_player.position)
        
        
        self.check_btn.config(state=tk.DISABLED)
        
        self.call_btn.config(text=f"Call ${raise_amount}")
    
    def prompt_human_after_ai_bet(self):

        self.highlight_active_player(self.human_player.position)
        
        
        self.check_btn.config(state=tk.DISABLED)  
        self.call_btn.config(text=f"Call ${self.game.current_bet}")
        
        
        self.prompt.config(text=f"AI bet ${self.game.current_bet}. Your turn.")

    def start_new_hand(self):
        self.current_stage = "preflop"

        if hasattr(self, 'responded_to_raise'):
            self.responded_to_raise = set()
        
        self.game.dealer_position = (self.game.dealer_position + 1) % len(self.game.players)
        
        
        for player in self.game.players:
            player.is_active = True
        
        
        positions = ["SB", "BB", "UTG", "UTG+1", "MP", "LJ", "HJ", "CO", "BTN"]
        
        
        for i, player in enumerate(self.game.players):
            rel_pos = (i - self.game.dealer_position) % len(self.game.players)
            player.position = positions[rel_pos]
        
        
        self.game.start_new_hand()
        self.update_display()
        self.update_stage_display()
        
        
        self.prompt.config(text=f"New hand started. You're in {self.human_player.position} position")
        
        
        sb_player = None
        for player in self.game.players:
            if player.position == "SB":
                sb_player = player
                break
        
        
        self.highlight_active_player("SB")
        
        
        if sb_player and sb_player != self.human_player:
            self.after(1000, lambda: self.ai_turn(sb_player))
        

    def ai_turn(self, ai_player=None):
        if ai_player is None:
            
            for player in self.game.players:
                if player != self.human_player and player.is_active:
                    ai_player = player
                    break
        
        if ai_player and ai_player.is_active:
            self.highlight_active_player(ai_player.position)
            action, amount = self.game.ai_action(player=ai_player)
            
            
            if not hasattr(self.game, 'ai_actions'):
                self.game.ai_actions = []
            self.game.ai_actions.append(AIAction(position=ai_player.position, action=action, amount=amount))
            
            
            amount_text = f"${amount}" if amount else ""
            self.prompt.config(text=f"{ai_player.position} {action}ed {amount_text}")
            
            
            self.update_display()
            
            
            next_player = self.find_next_player(ai_player)
            
            if next_player == self.human_player:
                
                self.prompt.config(text="Your turn")
                self.highlight_active_player(self.human_player.position)
            else:
                
                self.after(800, lambda: self.ai_turn(next_player))
        else:
            
            self.after(1000, self.check_game_stage)

    def find_next_player(self, current_player):
        current_index = self.game.players.index(current_player)
        for i in range(1, len(self.game.players)):
            next_index = (current_index + i) % len(self.game.players)
            next_player = self.game.players[next_index]
            if next_player.is_active:
                return next_player
        return None

if __name__ == "__main__":
    app = PokerGUI()
    app.mainloop()
