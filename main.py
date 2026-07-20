# 1-Suit Spider Solitaire Simulation
import random
import copy
import statistics
from scipy import stats as scipy_stats

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
    def __init__(self, seed=None):
        self.deck = [Card(rank) for rank in RANKS * 8]
        # self.suit = ["spades" for card in self.deck]
        # self.color = ["black" for card in self.deck]

        # set seed for reproducibility
        if seed is not None:
            rng = random.Random(seed)
            rng.shuffle(self.deck)
        else:
            random.shuffle(self.deck) 

        # initialize 10 tableau columns, 1 stock pile, and 8 foundation piles
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
                 # check for completed seq after dealing a card incase a completed seq is formed
                self.check_completed_sequence(col)
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
                        
                    # non-empty column check
                    if other_col:
                        if other_col[-1].face_up:
                            if other_col[-1].rank == moving_card.rank + 1:
                                legal_moves.append((i, k, seq_len))
                    else:
                        idx = len(col) - seq_len - 1
                        if seq_len == len(col) or (idx >= 0 and not col[idx].face_up):
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

        # move completed sequence to foundations
        self.check_completed_sequence(end_col)

        return True
    
    # check last 13 cards in a column for a completed sequence and move to foundations if found
    def check_completed_sequence(self, col):
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

    # check if the game is won (all 8 foundations completed)
    def is_won(self):
        return sum(1 for foundation in self.foundations if len(foundation) == 13) == 8
    
    # print the current state of the board
    def display_board(self):
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
    max_score = -1
    best_moves = []

    for m in legal_moves: 
        start_col, end_col, seq_len = m
        dest_col = state.tableau[end_col] 
        moving_card = state.tableau[start_col][-seq_len]
        
        score = seq_len

        # check if the move continues a run in the destination column
        if dest_col and dest_col[-1].face_up and dest_col[-1].rank == moving_card.rank + 1:
            # count how many cards are in the dest col
            for i in range(1, len(dest_col) + 1):
                card = dest_col[-i]
                if card.face_up:
                    if i > 1 and dest_col[-i].rank != dest_col[-(i-1)].rank + 1:
                        break
                    score += 1 
                else:
                    break

        # prioritize moves that clear columns
        if len(state.tableau[start_col]) == seq_len:
            score += 100

        # prioritize moves that flip hidden cards
        if len(state.tableau[start_col]) > seq_len:
            if not state.tableau[start_col][-seq_len-1].face_up:
                score += 10

        # save the best move if score beats our tracking max
        if score > max_score:
            max_score = score
            best_moves = [m]
        elif score == max_score:
            best_moves.append(m)

    if best_moves:
        best_m = random.choice(best_moves)

    return best_m

# strategy 2: random walks (baseline)
def get_random_move(state, legal_moves):
    if legal_moves:
        return random.choice(legal_moves)
    return None

# strategy 3: look-ahead strategy
def lookahead_strategy(state, legal_moves):
    if not legal_moves:
        return None
    
    best_m = None
    max_seq = -1
    
    legal_moves = sorted(legal_moves, key=lambda x: x[2], reverse=True)[:10]

    for m in legal_moves:
        start_col, end_col, seq_len = m
        idx = len(state.tableau[start_col]) - seq_len
        
        score = seq_len * 10
        
        if idx > 0 and not state.tableau[start_col][idx - 1].face_up:
            score += 100

        if not state.tableau[end_col]:
            score += 50
        
        if len(state.tableau[start_col]) == seq_len:
            score += 200
        
        # Heavy deepcopy happens much less often now
        sim = copy.deepcopy(state)
        sim.move_seq(start_col, end_col, seq_len)
        
        after_moves = sim.get_legal_moves()
        if len(after_moves) > len(legal_moves):
            score += (len(after_moves) - len(legal_moves)) * 20
        
        empty_cols = sum(1 for col in sim.tableau if not col)
        if empty_cols > 0:
            score += empty_cols * 30

        before_fdns = sum(1 for f in state.foundations if len(f) == 13)
        after_fdns = sum(1 for f in sim.foundations if len(f) == 13)
        if after_fdns > before_fdns:
            score += 1000

        if score > max_seq:
            max_seq = score
            best_m = m
        
    return best_m

# set up sim engine
class SimEngine:
    def __init__(self, game, strategy):
        self.game = game
        self.strategy = strategy
        self.seen_states = set()

    def get_state_key(self):
        return tuple(
            tuple((card.rank, card.face_up) for card in col)
            for col in self.game.tableau
        )

    def run(self, max_moves=5000):
        moves = 0
        deals = 0

        turned_over = 0

        while moves < max_moves:
            legal_moves = self.game.get_legal_moves()

            # make a move if there are legal moves available
            if legal_moves:
                move = self.strategy(self.game, legal_moves)

                # break if no valid move is returned by the strategy
                if move is None:
                    break

                start_col, end_col, seq_len = move

                # determine whether this move reveals a hidden card
                reveals_hidden = (
                    len(self.game.tableau[start_col]) > seq_len and
                    not self.game.tableau[start_col][-seq_len-1].face_up
                )

                if self.game.move_seq(start_col, end_col, seq_len):
                    # count new hidden cards
                    if reveals_hidden:
                        turned_over += 1
                    moves += 1

                    if self.game.is_won():
                        break
                    
                    # check for repeated states to avoid infinite loops
                    state_key = self.get_state_key()
                    if state_key in self.seen_states:
                        break
                    self.seen_states.add(state_key)
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
            "moves": moves,
            "deals": deals,
            "foundations_completed": foundations_completed,
            # return number of hidden cards turned over
            "turned_over": turned_over
        }

def run_sims(num_games, strategy, max_moves = 5000):
    # wins = 0 # no wins... 
    total_moves = 0
    total_deals = 0
    total_foundations = 0
    total_turned_over = 0

    for i in range(num_games):
        game = Game()
        game.setup_board()
        sim = SimEngine(game, strategy)
        result = sim.run(max_moves)

        # if result["won"]:
        #     wins += 1

        total_moves += result["moves"]
        total_deals += result["deals"]
        total_foundations += result["foundations_completed"]
        # add this for alternative evaluation: total hidden cards turned over
        total_turned_over += result["turned_over"]

    return {
        "strategy": strategy.__name__,
        "games": num_games,
        # "wins": wins,
        "total_moves": total_moves,
        "deals": total_deals,
        "foundations_completed": total_foundations,
        # add this for alternative evaluation: total hidden cards turned over
        "total_cards_turned_over": total_turned_over,
        "avg_cards_turned_over": total_turned_over / num_games
        }

# crn comparison
def run_sims_crn(num_games, strategies, max_moves=5000):
    results = {name: [] for name in strategies}

    for i in range(num_games):
        # same seed for all strategies
        seed = i
        for name, strategy in strategies.items():
            game = Game(seed=seed)
            game.setup_board()
            sim = SimEngine(game, strategy)
            r = sim.run(max_moves)
            results[name].append(r)
    return results

# paired-t ci comaparison
def paired_t_ci(sample_a, sample_b, confidence=0.95):
    diffs = [a - b for a, b in zip(sample_a, sample_b)]
    n = len(diffs)
    mean_diff = statistics.mean(diffs)
    std_diff = statistics.stdev(diffs)
    se_diff = std_diff / (n ** 0.5)

    alpha = 1 - confidence
    t_crit = scipy_stats.t.ppf(1 - alpha / 2, df=n - 1)
    margin = t_crit * se_diff

    return {
        "mean_diff": mean_diff,
        "ci_low": mean_diff - margin,
        "ci_high": mean_diff + margin,
        "games": n
    }

if __name__ == "__main__":
    crn_results = run_sims_crn(5000,
        { "greedy": greedy_strategy,
            "random": get_random_move,
            "lookahead": lookahead_strategy
        }
    )

    turned_over_by_strategy = {}
    for name, game_results in crn_results.items():
        # wins = sum(1 for r in game_results if r["won"])
        total_moves = sum(r["moves"] for r in game_results)
        total_deals = sum(r["deals"] for r in game_results)
        total_foundations = sum(r["foundations_completed"] for r in game_results)
        turned_over = [r["turned_over"] for r in game_results]
        total_turned_over = sum(turned_over)
        turned_over_by_strategy[name] = turned_over

        print({
            "strategy": name,
            "games": len(game_results),
            # "wins": wins,
            "total_moves": total_moves,
            "deals": total_deals,
            "foundations_completed": total_foundations,
            "total_cards_turned_over": total_turned_over,
            "avg_cards_turned_over": total_turned_over / len(game_results)
        })

    # print("greedy vs random:", paired_t_ci(turned_over_by_strategy["greedy"], turned_over_by_strategy["random"]))
    # print("lookahead vs random:", paired_t_ci(turned_over_by_strategy["lookahead"], turned_over_by_strategy["random"]))
    print("greedy vs lookahead:", paired_t_ci(turned_over_by_strategy["greedy"], turned_over_by_strategy["lookahead"]))