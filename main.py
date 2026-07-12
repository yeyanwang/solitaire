# 1-Suit Spider Solitaire Simulation
import random 
from game import Game
from display import display_board_image


"""
1-suit Spider Solitaire layout

104 blackcards of 1 suit (8 sets of 13 cards, all spades)

10 tableau columns
1 stock pile
8 foundation piles

stock deals 54 cards are dealt to the tableau
1 card is dealt to each column, card is placed face up from left to right
can move a face up card to another column if the card is one rank lower than the top card of that column
a completed K to A set are auto moved to the foundation
"""


# set up sim engine 
class SimEngine:
    def __init__(self, game, strategy):
        self.game = game
        self.strategy = strategy

def print_board(game):
    print("\n=== Spider Solitaire Board ===\n")

    for i, column in enumerate(game.tableau, start=1):
        cards_display = []

        for card in column:
            if card.face_up:
                cards_display.append(str(card))
            else:
                cards_display.append("[Hidden]")

        print(f"Column {i}: " + " | ".join(cards_display))

    print("\nStock cards left:", len(game.stock))
    print("Foundations completed:", len(game.foundations))
    
def start_game():
    game = Game()
    game.setup_board()
    
    print("Game Started!")
    return game        




if __name__ == "__main__":

    game = start_game()

    while not game.is_game_over():

        game.display_board()
        display_board_image(game)

        print("\nLegal moves:")
        legal_moves = game.get_legal_moves()

        if len(legal_moves) == 0:
            print("No legal moves available.")
        else:
            for i, move in enumerate(legal_moves, start=1):
                from_col, to_col, num_cards = move
                print(
                    f"{i}. Move {num_cards} card(s) "
                    f"from Column {from_col + 1} to Column {to_col + 1}"
                )

        choice = input("\nChoose a move number, type d to deal, or type q to quit: ")

        if choice.lower() == "q":
            print("Game exited.")
            break

        if choice.lower() == "d":
            game.deal_from_stock()
            continue

        if not choice.isdigit():
            print("Invalid input. Please enter a move number, d, or q.")
            continue

        choice = int(choice)

        if choice < 1 or choice > len(legal_moves):
            print("Invalid move number.")
            continue

        from_col, to_col, num_cards = legal_moves[choice - 1]
        game.make_move(from_col, to_col, num_cards)

    if game.is_won():
        print("Game Won!")

    elif game.is_lost():
        print("Game Lost!")