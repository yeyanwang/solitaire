import random
from card import Card


RANKS = list(range(1, 14)) # integers 1-13 for ease of comparison
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

        for from_col_index, from_col in enumerate(self.tableau):

            if len(from_col) == 0:
                continue

            # Check every possible face-up starting card in the column
            for start_index in range(len(from_col)):

                moving_stack = from_col[start_index:]

                # First card of moving stack must be face up
                if not moving_stack[0].face_up:
                    continue

                # Moving stack must be in descending order
                valid_stack = True

                for i in range(len(moving_stack) - 1):
                    current_card = moving_stack[i]
                    next_card = moving_stack[i + 1]

                    if not next_card.face_up:
                        valid_stack = False
                        break

                    if current_card.rank != next_card.rank + 1:
                        valid_stack = False
                        break

                if not valid_stack:
                    continue

                top_moving_card = moving_stack[0]
                num_cards = len(moving_stack)

                for to_col_index, to_col in enumerate(self.tableau):

                    if from_col_index == to_col_index:
                        continue

                    # Can move to empty column
                    if len(to_col) == 0:
                        legal_moves.append(
                            (from_col_index, to_col_index, num_cards)
                        )

                    else:
                        destination_card = to_col[-1]

                        # Spider rule: moving card must be one rank lower
                        if destination_card.face_up and top_moving_card.rank == destination_card.rank - 1:
                            legal_moves.append(
                                (from_col_index, to_col_index, num_cards)
                            )

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

    def make_move(self, from_col, to_col, num_cards):
        moving_cards = self.tableau[from_col][-num_cards:]

        # Remove cards from old column
        self.tableau[from_col] = self.tableau[from_col][:-num_cards]

        # Add cards to new column
        self.tableau[to_col].extend(moving_cards)

        # Flip the new top card in the old column
        if len(self.tableau[from_col]) > 0:
            self.tableau[from_col][-1].face_up = True

        # Check if a full K to A sequence was completed
        self.check_completed_foundation()

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
        return len(self.stock) == 0 and all(len(col) == 0 for col in self.tableau)
    
    def display_board(self):
        print("\n=== Spider Solitaire Board ===")

        for i, col in enumerate(self.tableau, start=1):
            cards = []

            for card in col:
                if card.face_up:
                    cards.append(str(card))
                else:
                    cards.append("[Hidden]")

            print(f"Column {i}: " + " | ".join(cards))

        print("Stock cards left:", len(self.stock))
        completed = sum(1 for pile in self.foundations if len(pile) == 13)
        print("Foundations completed:", completed)
    
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
    
    def deal_from_stock(self):
        if len(self.stock) < 10:
            print("Not enough cards in stock to deal.")
            return

        # Spider rule: cannot deal if any tableau column is empty
        if any(len(col) == 0 for col in self.tableau):
            print("Cannot deal because one or more columns are empty.")
            return

        for i in range(10):
            card = self.stock.pop()
            card.face_up = True
            self.tableau[i].append(card)

        print("Dealt one card to each column.")
        self.check_completed_foundation()
    
    def check_completed_foundation(self):
        # A complete Spider Solitaire sequence is:
        # K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2, A
        complete_sequence = list(range(13, 0, -1))

        for col_index, column in enumerate(self.tableau):

            if len(column) < 13:
                continue

            # Check the top 13 cards in this column
            top_13_cards = column[-13:]
            top_13_ranks = [card.rank for card in top_13_cards]

            # All cards must be face up
            all_face_up = all(card.face_up for card in top_13_cards)

            if top_13_ranks == complete_sequence and all_face_up:

                # Remove completed sequence from tableau
                completed_cards = self.tableau[col_index][-13:]
                self.tableau[col_index] = self.tableau[col_index][:-13]

                # Put completed sequence into the first empty foundation pile
                for foundation in self.foundations:
                    if len(foundation) == 0:
                        foundation.extend(completed_cards)
                        break

                print("Completed one foundation pile!")

                # Flip next card if the column still has cards
                if len(self.tableau[col_index]) > 0:
                    self.tableau[col_index][-1].face_up = True   