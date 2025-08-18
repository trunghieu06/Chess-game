import pygame

# Thông số cố định
pygame.init()
pygame.font.init()
pygame.mouse.set_visible(False)
SCALE = 3
WIDTH, HEIGHT = 1280, 720
TILE = 16 * SCALE
BOARD_WIDTH = 142 * SCALE
BOARD_HEIGHT = 142 * SCALE
BOARD_CENTER = (WIDTH // 2, HEIGHT // 2)
WINNER_WIDTH = 80 * SCALE
WINNER_HEIGHT = 100 * SCALE

# Màu sắc
WHITE = (245, 245, 220)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
A_GRAY = (128, 128, 128, 128)
BLACK = (0, 0, 0)
BG = (36, 37, 38)
LIGHT = (200, 200, 200)
DARK = (90, 100, 120)
RED = (255, 0, 0)

image = dict()
image_s = dict()
font = pygame.font.Font('./fonts/Jersey10-Regular.ttf', 30)
font_l = pygame.font.Font('./fonts/Jersey10-Regular.ttf', 35)
font_s = pygame.font.Font('./fonts/Jersey10-Regular.ttf', 20)
board_image = pygame.image.load('./images/boards/board_plain_01.png')
board_image = pygame.transform.scale(board_image, (BOARD_WIDTH, BOARD_HEIGHT))
board_rect = board_image.get_rect(center=BOARD_CENTER)
ui_sheet = pygame.image.load('./images/UI.png')
ui_rect = pygame.Rect(99, 7, 90, 25)
ui_bar_image = ui_sheet.subsurface(ui_rect).copy()
selector_sheet = pygame.image.load('./images/selector.png')
selector_rect = pygame.Rect(0, 0, 24, 24)
attacker_rect = pygame.Rect(24, 0, 24, 24)
selector = selector_sheet.subsurface(selector_rect).copy()
selector = pygame.transform.scale(selector, (TILE, TILE))
attacker = selector_sheet.subsurface(attacker_rect).copy()
attacker = pygame.transform.scale(attacker, (TILE, TILE))
status_bar = pygame.transform.scale(ui_bar_image, (WIDTH // 5, HEIGHT // 10))
STATUS_TOPLEFT = (WIDTH // 2 - status_bar.get_width() // 2, 30)
cursor_sheet = pygame.image.load('./images/cursor.png')
cursor_rect = pygame.Rect(0, 0, 16, 16)
cursor_default = cursor_sheet.subsurface(cursor_rect).copy()
cursor_rect = pygame.Rect(16, 0, 16, 16)
cursor_hover = cursor_sheet.subsurface(cursor_rect).copy()
cursor_rect = pygame.Rect(32, 0, 16, 16)
cursor_click = cursor_sheet.subsurface(cursor_rect).copy()
win_image = pygame.image.load('./images/win.png')
win_image = pygame.transform.scale(win_image, (120 * SCALE, 150 * SCALE))
win_rect = win_image.get_rect(center=BOARD_CENTER)
button_image = pygame.image.load('./images/button.png')
button_image = pygame.transform.scale(button_image, (button_image.get_width() * SCALE, button_image.get_height() * SCALE))
promotion_image = pygame.image.load('./images/promotion.png')
promotion_image = pygame.transform.scale(promotion_image, (16 * SCALE, 16 * 4 * SCALE))
bg_image = pygame.image.load('./images/background.png')
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
history_board = pygame.image.load('./images/history.png')
history_board = pygame.transform.scale(history_board, (history_board.get_width() * SCALE, history_board.get_height() * SCALE))
history_rect = history_board.get_rect(center=(WIDTH - 150, HEIGHT // 2))

def get_cursor_image(state):
    if state == 'default':
        return cursor_default
    elif state == 'hover':
        return cursor_default
    else:
        return cursor_default

W_CHARACTER = ['wp', 'wn', 'wr', 'wb', 'wk', 'wq']
B_CHARACTER = ['bp', 'bn', 'br', 'bb', 'bk', 'bq']

image['wa'] = pygame.image.load('./images/16x32_pieces/wk.png')
image['wa'] = pygame.transform.scale(image['wa'], (image['wa'].get_width() // 2 * SCALE, image['wa'].get_height() // 2 * SCALE))
image['ba'] = pygame.image.load('./images/16x32_pieces/bk.png')
image['ba'] = pygame.transform.scale(image['ba'], (image['ba'].get_width() // 2 * SCALE, image['ba'].get_height() // 2 * SCALE))

w_sheet = pygame.image.load('./images/16x16_pieces/WhitePieces.png')
w_sheet = pygame.transform.scale(w_sheet, (w_sheet.get_width() * SCALE, w_sheet.get_height() * SCALE))
b_sheet = pygame.image.load('./images/16x16_pieces/BlackPieces.png')
b_sheet = pygame.transform.scale(b_sheet, (b_sheet.get_width() * SCALE, b_sheet.get_height() * SCALE))

for i in range(w_sheet.get_width() // TILE):
    rect = pygame.Rect(i * TILE, 0, TILE, TILE)
    sprite = w_sheet.subsurface(rect).copy()
    image[W_CHARACTER[i]] = pygame.transform.scale(sprite, (sprite.get_width(), sprite.get_height()))

for i in range(b_sheet.get_width() // TILE):
    rect = pygame.Rect(i * TILE, 0, TILE, TILE)
    sprite = b_sheet.subsurface(rect).copy()
    image[B_CHARACTER[i]] = pygame.transform.scale(sprite, (sprite.get_width(), sprite.get_height()))

for key, value in image.items():
    image_s[key] = pygame.transform.scale(value, (value.get_width() // 1.5, value.get_height() // 1.5))