# 1-Suit Spider Solitaire
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
        self.suit = ["spades" for card in self.deck]
        self.color = ["black" for card in self.deck]
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
                    # Last card of each column is dealt face-up
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