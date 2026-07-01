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

        self.foundations = [[] for _ in range(8)]

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
    def display_board(self):
            """Print the current tableau."""
            for i, column in enumerate(self.tableau):
                cards = []
                for card in column:
                    if card.face_up:
                        cards.append(str(card))
                    else:
                        cards.append("[Hidden]")
                print(f"Column {i}: {cards}")
            print(f"Stock cards remaining: {len(self.stock)}")
            print(f"Completed foundations: {sum(1 for f in self.foundations if f)}")


    def can_move_card(self, source_col, dest_col):
        """
        A card (or an ordered sequence of cards) may be moved if:
        - The destination card is exactly one rank higher than the moving card.
        - The moved cards form a continuous descending sequence.
        """
        if source_col == dest_col:
            return False

        if not self.tableau[source_col]:
            return False

        moving_card = self.tableau[source_col][-1]

        if not moving_card.face_up:
            return False

        # Can move to empty column
        if not self.tableau[dest_col]:
            return True

        dest_card = self.tableau[dest_col][-1]

        if not dest_card.face_up:
            return False

        # The destination card is exactly one rank higher than the moving card
        return moving_card.rank + 1 == dest_card.rank


    def move_card(self, source_col, dest_col):
        """Move one card from source column to destination column."""
        if self.can_move_card(source_col, dest_col):
            card = self.tableau[source_col].pop()
            self.tableau[dest_col].append(card)

            # Flip next card if needed
            if self.tableau[source_col] and not self.tableau[source_col][-1].face_up:
                self.tableau[source_col][-1].face_up = True

            self.check_completed_sequence(dest_col)
            return True

        return False

    def has_valid_moves(self):
        for source in range(10 ):
            for dest in range(10):
                if source != dest:
                    if self.can_move_card(source, dest):
                        return True
        return False





    def check_completed_sequence(self, col):
        """
        Check if the last 13 cards in a column form:
        K, Q, J, 10, ..., 2, A
        """
        column = self.tableau[col]

        if len(column) < 13:
            return False

        last_13 = column[-13:]
        expected_ranks = list(range(13, 0, -1))

        actual_ranks = [card.rank for card in last_13]

        if actual_ranks == expected_ranks and all(card.face_up for card in last_13):
            completed_set = [column.pop() for _ in range(13)]
            completed_set.reverse()

            for foundation in self.foundations:
                if not foundation:
                    foundation.extend(completed_set)
                    break

            # Flip next hidden card
            if column and not column[-1].face_up:
                column[-1].face_up = True

            return True

        return False


    def is_won(self):
        """Game is won when all 8 foundations are complete."""
        return sum(1 for foundation in self.foundations if len(foundation) == 13) == 8

    def is_lost(self):
        return (not self.has_valid_moves()) and (len(self.stock)<10)

    def deal(self):
        """Deal one card face up from stock to each tableau column."""
        if len(self.stock) >= 10:
            for col in range(10):
                card = self.stock.pop()
                card.face_up = True
                self.tableau[col].append(card)
                self.check_completed_sequence(col)
            return True
        return False

    def is_game_over(self):
        return self.is_won() or self.is_lost()

# set up sim engine 
class SimEngine:
    def __init__(self, game, strategy):
        self.game = game
        self.strategy = strategy
        
        
if __name__ == "__main__":
    game = Game()
    game.setup_board()

    print("Spider Solitaire board created!")
    print("Stock cards:", len(game.stock))
    print("Tableau columns:")

    for i, col in enumerate(game.tableau, start=1):
        print(f"Column {i}: {len(col)} cards, top card = {col[-1]}")
        
    while not game.is_game_over():

        # Display card boadr
        game.display_board()
        break

    if game.is_won():
        print("Game Won!")

    elif game.is_lost():
        print("Game Lost!")