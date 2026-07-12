import pygame
from game import Game

pygame.init()

WIDTH = 1200
HEIGHT = 900

CARD_WIDTH = 90
CARD_HEIGHT = 130
GAP_X = 20
GAP_Y = 35
MARGIN = 30
TABLEAU_Y = 200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1-Suit Spider Solitaire")

font = pygame.font.SysFont("arial", 22)
small_font = pygame.font.SysFont("arial", 16)

rank_map = {
    1: "A",
    11: "J",
    12: "Q",
    13: "K"
}

for i in range(2, 11):
    rank_map[i] = str(i)


def draw_card(card, x, y):
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    if card.face_up:
        pygame.draw.rect(screen, "white", rect, border_radius=10)
        pygame.draw.rect(screen, "black", rect, width=2, border_radius=10)

        rank_text = rank_map[card.rank] + "♠"
        text = font.render(rank_text, True, "black")
        screen.blit(text, (x + 10, y + 10))

        suit = font.render("♠", True, "black")
        screen.blit(suit, (x + 35, y + 55))

    else:
        pygame.draw.rect(screen, "navy", rect, border_radius=10)
        pygame.draw.rect(screen, "white", rect, width=2, border_radius=10)

        text = small_font.render("Back", True, "white")
        screen.blit(text, (x + 25, y + 55))


def draw_game(game, selected_col=None):
    screen.fill("darkgreen")

    title = font.render("1-Suit Spider Solitaire", True, "white")
    screen.blit(title, (MARGIN, 20))

    stock_text = small_font.render(f"Stock cards left: {len(game.stock)}", True, "white")
    screen.blit(stock_text, (MARGIN, 55))

    completed = sum(1 for pile in game.foundations if len(pile) == 13)
    foundation_text = small_font.render(f"Foundations completed: {completed}", True, "white")
    screen.blit(foundation_text, (MARGIN, 80))

    # Draw stock pile
    stock_rect = pygame.Rect(MARGIN + 350, 40, CARD_WIDTH, CARD_HEIGHT)

    stock_label = small_font.render("Stock", True, "white")
    screen.blit(stock_label, (stock_rect.x + 20, stock_rect.y - 22))

    if len(game.stock) > 0:
        pygame.draw.rect(screen, "navy", stock_rect, border_radius=10)
        pygame.draw.rect(screen, "white", stock_rect, width=2, border_radius=10)

        count_text = font.render(str(len(game.stock)), True, "white")
        screen.blit(count_text, (stock_rect.x + 30, stock_rect.y + 45))

        card_text = small_font.render("cards", True, "white")
        screen.blit(card_text, (stock_rect.x + 25, stock_rect.y + 75))
    else:
        pygame.draw.rect(screen, "darkgreen", stock_rect, border_radius=10)
        pygame.draw.rect(screen, "white", stock_rect, width=2, border_radius=10)

        empty_text = small_font.render("Empty", True, "white")
        screen.blit(empty_text, (stock_rect.x + 25, stock_rect.y + 55))

    # Draw tableau columns
    for col_index, column in enumerate(game.tableau):
        x = MARGIN + col_index * (CARD_WIDTH + GAP_X)
        y = TABLEAU_Y

        label = small_font.render(f"Col {col_index + 1}", True, "white")
        screen.blit(label, (x + 20, y - 25))

        if selected_col == col_index:
            highlight_rect = pygame.Rect(x - 5, y - 5, CARD_WIDTH + 10, 650)
            pygame.draw.rect(screen, "yellow", highlight_rect, width=3)

        for card in column:
            draw_card(card, x, y)
            y += GAP_Y

    pygame.display.flip()

    return stock_rect


def get_clicked_column(pos):
    mouse_x, mouse_y = pos

    if mouse_y < TABLEAU_Y:
        return None

    for col_index in range(10):
        x = MARGIN + col_index * (CARD_WIDTH + GAP_X)

        if x <= mouse_x <= x + CARD_WIDTH:
            return col_index

    return None


def find_move(game, from_col, to_col):
    legal_moves = game.get_legal_moves()

    matching_moves = [
        move for move in legal_moves
        if move[0] == from_col and move[1] == to_col
    ]

    if len(matching_moves) == 0:
        return None

    # Pick the move with the most cards
    return max(matching_moves, key=lambda move: move[2])


def run_gui():
    game = Game()
    game.setup_board()

    selected_col = None
    running = True

    while running:
        stock_rect = draw_game(game, selected_col)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Click stock pile to deal
                if stock_rect.collidepoint(mouse_pos):
                    game.deal_from_stock()
                    continue

                clicked_col = get_clicked_column(mouse_pos)

                if clicked_col is None:
                    continue

                if selected_col is None:
                    selected_col = clicked_col
                else:
                    from_col = selected_col
                    to_col = clicked_col

                    move = find_move(game, from_col, to_col)

                    if move is not None:
                        from_col, to_col, num_cards = move
                        game.make_move(from_col, to_col, num_cards)
                    else:
                        print("Illegal move.")

                    selected_col = None

        if game.is_won():
            print("Game Won!")
            running = False

        elif game.is_lost():
            print("Game Lost!")
            running = False

    pygame.quit()


if __name__ == "__main__":
    run_gui()