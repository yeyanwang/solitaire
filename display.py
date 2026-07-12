from PIL import Image, ImageDraw, ImageFont
import pygame
import os

CARD_WIDTH = 80
CARD_HEIGHT = 120

rank_file_map = {
    1: "A_spades.png",
    2: "2_spades.png",
    3: "3_spades.png",
    4: "4_spades.png",
    5: "5_spades.png",
    6: "6_spades.png",
    7: "7_spades.png",
    8: "8_spades.png",
    9: "9_spades.png",
    10: "10_spades.png",
    11: "J_spades.png",
    12: "Q_spades.png",
    13: "K_spades.png",
}

def load_card_image(card):
    if not card.face_up:
        image = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), "navy")
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle(
            [0, 0, CARD_WIDTH - 1, CARD_HEIGHT - 1],
            radius=10,
            fill="navy",
            outline="white",
            width=3
        )

        try:
            small_font = ImageFont.truetype("arial.ttf", 16)
        except:
            small_font = ImageFont.load_default()

        draw.text((20, 50), "Back", fill="white", font=small_font)
        return image

    file_name = rank_file_map[card.rank]
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(BASE_DIR,"assets", file_name)

    image = Image.open(image_path).convert("RGBA")
    image = image.resize((CARD_WIDTH, CARD_HEIGHT))
    return image

def display_board_image(game, filename="board.png"):
    card_width = CARD_WIDTH
    card_height = CARD_HEIGHT
    gap_x = 20
    gap_y = 35
    margin = 30

    board_width = margin * 2 + 10 * (card_width + gap_x)
    board_height = 900

    img = Image.new("RGBA", (board_width, board_height), "darkgreen")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 22)
        small_font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text((margin, 10), "1-Suit Spider Solitaire", fill="white", font=font)
    draw.text((margin, 40), f"Stock cards left: {len(game.stock)}", fill="white", font=small_font)

    # Draw stock pile image
    stock_x = margin + 350
    stock_y = 20

    draw.text((stock_x, stock_y - 18), "Stock", fill="white", font=small_font)

    if len(game.stock) > 0:
        draw.rounded_rectangle(
            [stock_x, stock_y, stock_x + card_width, stock_y + card_height],
            radius=10,
            fill="navy",
            outline="white",
            width=2
        )

        draw.text(
            (stock_x + 20, stock_y + 45),
            f"{len(game.stock)}",
            fill="white",
            font=font
        )

        draw.text(
            (stock_x + 15, stock_y + 75),
            "cards",
            fill="white",
            font=small_font
        )

    else:
        draw.rounded_rectangle(
            [stock_x, stock_y, stock_x + card_width, stock_y + card_height],
            radius=10,
            fill="darkgreen",
            outline="white",
            width=2
        )

        draw.text(
            (stock_x + 20, stock_y + 55),
            "Empty",
            fill="white",
            font=small_font
        )
    
    completed = sum(1 for pile in game.foundations if len(pile) == 13)
    draw.text((margin, 60), f"Foundations completed: {completed}", fill="white", font=small_font)

    for col_index, column in enumerate(game.tableau):
        x = margin + col_index * (card_width + gap_x)
        y = 190

        draw.text((x + 15, y - 25), f"Col {col_index + 1}", fill="white", font=small_font)

        for card in column:
            card_image = load_card_image(card)
            img.paste(card_image, (x, y), card_image)
            y += gap_y

    img = img.convert("RGB")
    img.save(filename)
    img.show()