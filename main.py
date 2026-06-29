# 1-Suit Spider Solitaire Simulation
import random 

RANKS = list(range(1, 14)) # integers 1-13 for ease of comparison

rank_map = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
for i in range(2, 11):
    rank_map[i] = str(i)

class Card:
    def __init__(self, rank):
        self.rank = rank
        self.suit = "spades"
        self.face_up = False

    def __str__(self):
        return f"{rank_map[self.rank]} of {self.suit}"

"""
1-suit Spider Solitaire layout

104 blackcards of 1 suit (8 sets of 13 cards, all spades)

10 tableau columns
1 stock pile
10 foundation piles

stock deals 54 cards are dealt to the tableau
1 card is dealt to each column, card is placed face up from left to right
can move a face up card to another column if the card is one rank lower than the top card of that column
a completed K to A set are auto moved to the foundation
"""
class Game:
    def __init__(self):
        self.deck = [Card(rank) for rank in RANKS * 8]
        # self.suit = ["spades" for card in self.deck]
        # self.color = ["black" for card in self.deck]
        random.shuffle(self.deck) 

        # initialize 10 tableau columns, 1 stock pile, and 10 foundation piles
        self.tableau = [[] for _ in range(10)] 
        self.stock = []
        self.foundations = [[] for _ in range(10)]

    # set up the board with the initial tableau and stock pile
    def setup_board(self):
        # a total of 54 cards are dealt to the tableau
        # column 1-4 has 6 cards, column 5-10 has 5 cards
        for col in range(10):
            num_cards = 6 if col < 4 else 5
            for c in range(num_cards):
                if self.deck:
                    card = self.deck.pop()
                    # Last card of each column is dealt face up
                    if c == num_cards - 1:
                        card.face_up = True
                    self.tableau[col].append(card)
        # remaining 50 cards go to the stock pile
        while self.deck:
            self.stock.append(self.deck.pop())
    
    # deal a card face up from the stock pile to each column
    def deal(self):
        # while there are cards in the stock pile, deal a card to each column face up
        if self.stock:
            for col in range(10):
                card = self.stock.pop()
                card.face_up = True
                self.tableau[col].append(card)
            return True
        return False
    
    # get legal moves (start_col_id, end_col_id, seq_en)
    def get_legal_moves(self):
        legal_moves = []
    
        for i, col in enumerate(self.tableau):
            if col and col[-1].face_up:
                seq_len = 1
                for j in range(2 , len(col)+1) :
                    if col[-j].rank == col[-(j-1)].rank - 1 and col[-j].face_up:
                        seq_len += 1
                    else:
                        break

                first_moveable_card = col[-seq_len]
                for k, other_col in enumerate(self.tableau):
                    if i != k and (not other_col or other_col[-1].rank == first_moveable_card.rank + 1):
                        legal_moves.append((i, k, seq_len))
        return legal_moves

    # finish up the game play...

# player strategies
# strategy 1: prioritze moves that build the longest sequence 
def build_longest_seq(state, legal_moves):
    if not legal_moves: 
        return None
    
    best_m = None 
    max_seq = -1
    for m in legal_moves: 
        start_col_id, end_col_id, seq_len = m
        legal_col = state.tableau[end_col_id] 
        seq = 0

        if legal_col:
            for i in range(len(legal_col)):
                # +1 to get the correct flipped indexing starting from the bottom
                card = legal_col[-(i+1)]

                # check sequence when if the card is face up
                if card.face_up:
                    # first card
                    if i == 0: 
                        seq = 1
                    # check if the card ranks in sequence are consecutive
                    if i > 0: 
                        card_below = legal_col[-i]
                        if card.rank == card_below.rank - 1:
                            seq += 1
                        else: 
                            break # stop counting when the sequence is not consecutive
                else: 
                    break # face down card does not count toward the sequence
        seq += seq_len
        # update the max sequence length and best move
        if seq > max_seq:
            max_seq = seq
            best_m = m
    return best_m

# strategy 2: prioritize moves that result in empty columns (free up columns)
def free_up_cols(state, legal_moves):
    if not legal_moves: 
        return None
    
    for m in legal_moves: 
        start_col_id, end_col_id, seq_len = m
        if len(state.tableau[start_col_id]) == seq_len:
            return m 
    return legal_moves[0]

# strategy 3: random walks
# simple one to include in sim for evaluation based on research...
def get_random_move(state):
    legal_moves = state.get_legal_moves()
    if legal_moves:
        return random.choice(legal_moves)
    return None

# set up sim engine 
class SimEngine:
    def __init__(self, game, strategy):
        self.game = game
        self.strategy = strategy
