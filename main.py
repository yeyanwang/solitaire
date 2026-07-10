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
        if len(self.stock) >= 10:
            for col in range(10):
                card = self.stock.pop()
                card.face_up = True
                self.tableau[col].append(card)
                self.check_completed_sequence(col) # check for completed seq after dealing a card incase a completed seq is formed
            return True
        return False
    
    # get legal moves (start_col, end_col, seq_len)
    def get_legal_moves(self):
        legal_moves = []

        for i, col in enumerate(self.tableau):
            if not col:
                continue

            # find all movable face-up sequences
            for seq_len in range(1, len(col) + 1):
                moving_cards = col[-seq_len:]
                if not all(card.face_up for card in moving_cards):
                    break

                # check descending sequence
                valid_seq = True
                for j in range(seq_len - 1):
                    if moving_cards[j].rank != moving_cards[j + 1].rank + 1:
                        valid_seq = False
                        break

                if not valid_seq:
                    break

                moving_card = moving_cards[0]
                for k, other_col in enumerate(self.tableau):

                    if i == k:
                        continue
                    # empty column
                    if not other_col:
                        legal_moves.append((i, k, seq_len))
                    # non-empty column
                    elif other_col[-1].face_up:
                        if other_col[-1].rank == moving_card.rank + 1:
                            legal_moves.append((i, k, seq_len))
        return legal_moves
    
    # replaced move_card to allow moving cards in sequence
    def move_seq(self, start_col, end_col, seq_len):
        if start_col == end_col:
            return False
        # check if source col has enough cards to move
        if len(self.tableau[start_col]) < seq_len:
            return False

        moving_cards = self.tableau[start_col][-seq_len:]

        # only allow moving face up cards
        if not all(card.face_up for card in moving_cards):
            return False

        # check if the sequence is in descending order
        for i in range(seq_len - 1):
            if moving_cards[i].rank != moving_cards[i + 1].rank + 1:
                return False

        # only allow cards when the col is empty or the dest card is one rank higher
        if self.tableau[end_col]:
            dest_card = self.tableau[end_col][-1]

            if not dest_card.face_up:
                return False

            if moving_cards[0].rank + 1 != dest_card.rank:
                return False

        del self.tableau[start_col][-seq_len:]
        self.tableau[end_col].extend(moving_cards)

        # if the bottom card is face down flip it face up
        if self.tableau[start_col] and not self.tableau[start_col][-1].face_up:
            self.tableau[start_col][-1].face_up = True

        # Remove completed sequence if formed
        self.check_completed_sequence(end_col)

        return True
    
    def check_completed_sequence(self, col):
        """
        Check if the last 13 cards in a column form:
        K, Q, J, 10, ..., 2, A
        """
        c = self.tableau[col]
        completed = False

        while len(c) >= 13:
            last_13 = c[-13:]
            expected_ranks = list(range(13, 0, -1))
            actual_ranks = [card.rank for card in last_13]

            if actual_ranks == expected_ranks and all(card.face_up for card in last_13):
                completed_set = [c.pop() for _ in range(13)]
                completed_set.reverse()

                for foundation in self.foundations:
                    if not foundation:
                        foundation.extend(completed_set)
                        break

                if c and not c[-1].face_up:
                    c[-1].face_up = True

                completed = True
                continue # check for another completed sequence in the same column

            else:
                break

        return completed

    def is_won(self):
        """Game is won when all 8 foundations are complete."""
        return sum(1 for foundation in self.foundations if len(foundation) == 13) == 8
    
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
        print(f"Completed foundations: {sum(1 for f in self.foundations if len(f) == 13)}")

# player strategies
# strategy 1: greedy strategy to build the longest sequence and prioritize moves that free up columns
def greedy_strategy(state, legal_moves):
    if not legal_moves: 
        return None
    
    best_m = None 
    max_seq = -1

    for m in legal_moves: 
        start_col, end_col, seq_len = m
        dest_col = state.tableau[end_col] 
        seq = 0

        if dest_col:
            for i in range(len(dest_col)):
                # flip index to check from the bottom
                card = dest_col[-(i+1)]

                # check sequence when if the card is face up
                if card.face_up:
                    # first card
                    if i == 0: 
                        seq = 1
                    # check if the card ranks in sequence are consecutive
                    if i > 0: 
                        card_below = dest_col[-i]
                        if card.rank == card_below.rank + 1:
                            seq += 1
                        else: 
                            break # stop counting when the sequence is not consecutive
                else: 
                    break # face down card does not count toward the sequence

        seq += seq_len

        # prioritize moves that result in empty columns
        if len(state.tableau[start_col]) == seq_len:
            seq += 100

        # prioritize moves that flip hidden cards
        if len(state.tableau[start_col]) > seq_len:
            if not state.tableau[start_col][-seq_len-1].face_up:
                seq += 10

        # update the max sequence length and best move
        if seq > max_seq:
            max_seq = seq
            best_m = m

    return best_m

# strategy 2: random walks (baseline)
def get_random_move(state, legal_moves):
    if legal_moves:
        return random.choice(legal_moves)
    return None

# set up sim engine
class SimEngine:
    def __init__(self, game, strategy):
        self.game = game
        self.strategy = strategy
        seen_states = set()

    def run(self, max_moves=5000):
        moves = 0
        deals = 0

        while moves < max_moves:
            legal_moves = self.game.get_legal_moves()

            # make a move if there are legal moves available
            if legal_moves:
                move = self.strategy(self.game, legal_moves)

                # break if no valid move is returned by the strategy
                if move is None:
                    break

                start_col, end_col, seq_len = move

                if self.game.move_seq(start_col, end_col, seq_len):
                    moves += 1

                    if self.game.is_won():
                        break
                else:
                    break

            # deal from the stock if there are no legal moves available
            elif self.game.deal():
                deals += 1

                if self.game.is_won():
                    break

            # game is lost if there are no legal moves and the stock is empty
            else:
                break

        foundations_completed = sum(
            1 for foundation in self.game.foundations
            if len(foundation) == 13
        )

        return {
            "won": self.game.is_won(),
            "lost": not self.game.is_won(),
            "moves": moves,
            "deals": deals,
            "foundations_completed": foundations_completed,
            "timeout": moves >= max_moves
        }

def run_sims(num_games, strategy, max_moves = 5000):
    wins = 0
    losses = 0
    timeouts = 0

    total_moves = 0
    total_deals = 0
    total_foundations = 0

    for i in range(num_games):

        game = Game()
        game.setup_board()

        sim = SimEngine(game, strategy)
        result = sim.run(max_moves)

        if result["won"]:
            wins += 1
        else:
            losses += 1

        if result["timeout"]:
            timeouts += 1

        total_moves += result["moves"]
        total_deals += result["deals"]
        total_foundations += result["foundations_completed"]

    return {
        "stategy": strategy.__name__,
        "games": num_games,
        "wins": wins,
        "losses": losses,
        "win_rate": wins / num_games,
        "average_moves": total_moves / num_games,
        "average_deals": total_deals / num_games,
        "average_foundations_completed": total_foundations / num_games,
        "timeouts": timeouts
    }


if __name__ == "__main__":
    results_greedy = run_sims(500, greedy_strategy)
    results_random = run_sims(500, get_random_move)
    print(results_greedy)
    print(results_random)