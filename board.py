import sys
from constants import *

def coor_to_pos(pos):
    row = 'abcdefgh'
    col = '87654321'
    return row[pos[1]] + col[pos[0]]

def pos_to_coor(square: str):
    row = 'abcdefgh'
    col = '87654321'
    return (col.index(square[1]), row.index(square[0]))

def parse_fen(fen):
    parts = fen.split()
    board_str, turn, castling, ep, halfmove, fullmove = parts
    board = []
    for rank in board_str.split('/'):
        row = []
        for char in rank:
            if char.isdigit():
                row.extend(['.'] * int(char))
            else:
                row.append(char)
        board.append(row)
    return board, turn, castling, ep, int(halfmove), int(fullmove)

fen_name = {
    'bk' : 'k',
    'bq' : 'q',
    'bb' : 'b',
    'bn' : 'n',
    'br' : 'r',
    'bp' : 'p',
    'wk' : 'K',
    'wq' : 'Q',
    'wb' : 'B',
    'wn' : 'N',
    'wr' : 'R',
    'wp' : 'P'
}

class Board:
    def __init__(self):
        self.table = [['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
                      ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
                      ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']]
        self.castling_right = {
            'w_kingside' : True,
            'w_queenside' : True,
            'b_kingside' : True,
            'b_queenside' : True
        }
        self.history = []
        self.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        self.bk = (0, 4)
        self.wk = (7, 4)
        self.w_lost = dict()
        self.b_lost = dict()
        for row in self.table:
            for i in row:
                if i is not None:
                    if i[0] == 'w':
                        self.w_lost[i] = 0
                    else:
                        self.b_lost[i] = 0
        def create_board_buttons():
            buttons = []
            for row in range(8):
                row_buttons = []
                for col in range(8):
                    rect = pygame.Rect(
                        BOARD_CENTER[0] - BOARD_WIDTH // 2 + 7 * SCALE + col * TILE,
                        BOARD_CENTER[1] - BOARD_HEIGHT // 2 + 7 * SCALE + row * TILE,
                        TILE,
                        TILE
                    )
                    row_buttons.append(rect)
                buttons.append(row_buttons)
            return buttons
        self.buttons = create_board_buttons()
        self.center = []
        for i in self.buttons:
            a = []
            for j in i:
                a.append(image['wr'].get_rect(center=j.center))
            self.center.append(a)
    def draw_board(self, screen):
        for i in range(8):
            for j in range(8):
                if self.table[i][j] is not None:
                    screen.blit(image[self.table[i][j]], self.center[i][j])
    def draw_avatar(self, screen, turn):
        turn = turn + 'a'
        image_rect = image[turn].get_rect(center=(STATUS_TOPLEFT[0] + image[turn].get_width() // 2 + 20, STATUS_TOPLEFT[1] - 5 + HEIGHT // 20))
        screen.blit(image[turn], image_rect)
    def draw_announce(self, screen, turn, check):
        text_surface = None
        if check:
            text_surface = font.render('CHECK!!!', True, WHITE)
        else:
            text_surface = font.render('Turn of ' + ('WHITE' if turn == 'wa' else 'BLACK'), True, WHITE)
        text_rect = text_surface.get_rect(center=(STATUS_TOPLEFT[0] + status_bar.get_width() // 2, STATUS_TOPLEFT[1] + HEIGHT // 20))
        screen.blit(text_surface, text_rect)
    def draw_selector(self, screen, i, j, attack):
        circle_surface = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        if attack:
            screen.blit(attacker, self.buttons[i][j])
        else:
            screen.blit(selector, self.buttons[i][j])
        screen.blit(circle_surface, self.center[i][j])
    def draw_move(self, screen, moves):
        for (i, j) in moves:
            if self.table[i][j] is None:
                self.draw_selector(screen, i, j, 0)
            else:
                self.draw_selector(screen, i, j, 1)
    def draw_lost(self, screen):
        x = BOARD_CENTER[0] - BOARD_WIDTH // 2
        y = BOARD_CENTER[1] - BOARD_HEIGHT // 2 - 5
        for k, v in self.w_lost.items():
            if v >= 1:
                rect = image_s[k].get_rect(bottomleft=(x, y))
                screen.blit(image_s[k], rect)
                text = 'x' + str(v)
                text_surface = font_s.render(text, True, WHITE)
                text_rect = text_surface.get_rect(topleft=(x + image_s[k].get_width() + 2, y - image_s[k].get_height()))
                screen.blit(text_surface, text_rect)
                x += image_s[k].get_width() * 1.5
        x = BOARD_CENTER[0] - BOARD_WIDTH // 2
        y = BOARD_CENTER[1] + BOARD_HEIGHT // 2 + 5
        for k, v in self.b_lost.items():
            if v >= 1:
                rect = image_s[k].get_rect(topleft=(x, y))
                screen.blit(image_s[k], rect)
                text = 'x' + str(v)
                text_surface = font_s.render(text, True, WHITE)
                text_rect = text_surface.get_rect(topleft=(x + image_s[k].get_width() + 2, y))
                screen.blit(text_surface, text_rect)
                x += image_s[k].get_width() * 1.5
    def check_castling(self, turn):
        rs = []
        op_turn = 'b' if turn == 'w' else 'w'
        skip_king = False
        if op_turn == 'b' and 'b_queenside' in self.castling_right:
            skip_king = True
        elif op_turn == 'w' and 'w_queenside' in self.castling_right:
            skip_king = True
        attacked_square = self.gen_move('w' if turn == 'b' else 'b', False, skip_king)
        queenside, kingside = True, True
        if turn == 'w':
            if 'w_queenside' in self.castling_right and self.castling_right['w_queenside'] == True:
                for i in range(1, 4):
                    if self.table[7][i] is not None:
                        queenside = False
                for i in range(2, 5):
                    if (7, i) in attacked_square:
                        queenside = False
                if queenside == True:
                    rs.append((7, 2))
            if 'w_kingside' in self.castling_right and self.castling_right['w_kingside'] == True:
                for i in range(5, 7):
                    if self.table[7][i] is not None:
                        kingside = False
                    if (7, i) in attacked_square:
                        kingside = False
                if kingside == True:
                    rs.append((7, 6))
        else:
            if 'b_queenside' in self.castling_right and self.castling_right['b_queenside'] == True:
                for i in range(1, 4):
                    if self.table[0][i] is not None:
                        queenside = False
                for i in range(2, 5):
                    if (0, i) in attacked_square:
                        queenside = False
                if queenside == True:
                    rs.append((0, 2))
            if 'b_kingside' in self.castling_right and self.castling_right['b_kingside'] == True:
                for i in range(5, 7):
                    if self.table[0][i] is not None:
                        kingside = False
                    if (0, i) in attacked_square:
                        kingside = False
                if kingside == True:
                    rs.append((0, 6))
        return rs
    def get_move(self, pressing):
        if pressing is None:
            return []
        [i, j] = pressing
        cur = self.table[i][j]
        if cur is None:
            return []
        moves = []
        if cur[1] == 'r':
            for k in range(i + 1, 8):
                if self.table[k][j] is None:
                    moves.append((k, j))
                else:
                    if self.table[k][j][0] != cur[0]:
                        moves.append((k, j))
                    break
            for k in range(i - 1, -1, -1):
                if self.table[k][j] is None:
                    moves.append((k, j))
                else:
                    if self.table[k][j][0] != cur[0]:
                        moves.append((k, j))
                    break
            for k in range(j + 1, 8):
                if self.table[i][k] is None:
                    moves.append((i, k))
                else:
                    if self.table[i][k][0] != cur[0]:
                        moves.append((i, k))
                    break
            for k in range(j - 1, -1, -1):
                if self.table[i][k] is None:
                    moves.append((i, k))
                else:
                    if self.table[i][k][0] != cur[0]:
                        moves.append((i, k))
                    break
        elif cur[1] == 'n':
            dx = [-1, -2, -2, -1, 1, 2, 2, 1]
            dy = [-2, -1, 1, 2, 2, 1, -1, -2]
            for k in range(8):
                ni, nj = i + dx[k], j + dy[k]
                if ni < 0 or 8 <= ni or nj < 0 or 8 <= nj:
                    continue
                t = self.table[ni][nj]
                if t is None:
                    moves.append((ni, nj))
                elif t[0] != cur[0]:
                    moves.append((ni, nj))
        elif cur[1] == 'b':
            for k in range(1, 8):
                if i + k >= 8 or j + k >= 8:
                    break
                if self.table[i + k][j + k] is None:
                    moves.append((i + k, j + k))
                else:
                    if self.table[i + k][j + k][0] != cur[0]:
                        moves.append((i + k, j + k))
                    break
            for k in range(1, 8):
                if i + k >= 8 or j - k < 0:
                    break
                if self.table[i + k][j - k] is None:
                    moves.append((i + k, j - k))
                else:
                    if self.table[i + k][j - k][0] != cur[0]:
                        moves.append((i + k, j - k))
                    break
            for k in range(1, 8):
                if i - k < 0 or j - k < 0:
                    break
                if self.table[i - k][j - k] is None:
                    moves.append((i - k, j - k))
                else:
                    if self.table[i - k][j - k][0] != cur[0]:
                        moves.append((i - k, j - k))
                    break
            for k in range(1, 8):
                if i - k < 0 or j + k >= 8:
                    break
                if self.table[i - k][j + k] is None:
                    moves.append((i - k, j + k))
                else:
                    if self.table[i - k][j + k][0] != cur[0]:
                        moves.append((i - k, j + k))
                    break
        elif cur[1] == 'q':
            for k in range(i + 1, 8):
                if self.table[k][j] is None:
                    moves.append((k, j))
                else:
                    if self.table[k][j][0] != cur[0]:
                        moves.append((k, j))
                    break
            for k in range(i - 1, -1, -1):
                if self.table[k][j] is None:
                    moves.append((k, j))
                else:
                    if self.table[k][j][0] != cur[0]:
                        moves.append((k, j))
                    break
            for k in range(j + 1, 8):
                if self.table[i][k] is None:
                    moves.append((i, k))
                else:
                    if self.table[i][k][0] != cur[0]:
                        moves.append((i, k))
                    break
            for k in range(j - 1, -1, -1):
                if self.table[i][k] is None:
                    moves.append((i, k))
                else:
                    if self.table[i][k][0] != cur[0]:
                        moves.append((i, k))
                    break
            for k in range(1, 8):
                if i + k >= 8 or j + k >= 8:
                    break
                if self.table[i + k][j + k] is None:
                    moves.append((i + k, j + k))
                else:
                    if self.table[i + k][j + k][0] != cur[0]:
                        moves.append((i + k, j + k))
                    break
            for k in range(1, 8):
                if i + k >= 8 or j - k < 0:
                    break
                if self.table[i + k][j - k] is None:
                    moves.append((i + k, j - k))
                else:
                    if self.table[i + k][j - k][0] != cur[0]:
                        moves.append((i + k, j - k))
                    break
            for k in range(1, 8):
                if i - k < 0 or j - k < 0:
                    break
                if self.table[i - k][j - k] is None:
                    moves.append((i - k, j - k))
                else:
                    if self.table[i - k][j - k][0] != cur[0]:
                        moves.append((i - k, j - k))
                    break
            for k in range(1, 8):
                if i - k < 0 or j + k >= 8:
                    break
                if self.table[i - k][j + k] is None:
                    moves.append((i - k, j + k))
                else:
                    if self.table[i - k][j + k][0] != cur[0]:
                        moves.append((i - k, j + k))
                    break
        elif cur[1] == 'k':
            dx = [-1, -1, -1, 0, 1, 1, 1, 0]
            dy = [-1, 0, 1, 1, 1, 0, -1, -1]
            for k in range(8):
                ni, nj = i + dx[k], j + dy[k]
                if ni < 0 or 8 <= ni or nj < 0 or 8 <= nj:
                    continue
                t = self.table[ni][nj]
                if t is None:
                    moves.append((ni, nj))
                elif t[0] != cur[0]:
                    moves.append((ni, nj))
            if cur[0] == 'w' and ('w_queenside' in self.castling_right or 'w_kingside' in self.castling_right):
                moves.extend(self.check_castling('w'))
            elif cur[0] == 'b' and ('b_queenside' in self.castling_right or 'b_kingside' in self.castling_right):
                moves.extend(self.check_castling('b'))
        elif cur == 'bp':
            if i + 1 < 8 and self.table[i + 1][j] is None:
                moves.append((i + 1, j))
                if i == 1 and self.table[i + 2][j] is None:
                    moves.append((i + 2, j))
            if i + 1 < 8:
                if j - 1 >= 0 and self.table[i + 1][j - 1] is not None and self.table[i + 1][j - 1][0] != cur[0]:
                    moves.append((i + 1, j - 1))
                if j + 1 < 8 and self.table[i + 1][j + 1] is not None and self.table[i + 1][j + 1][0] != cur[0]:
                    moves.append((i + 1, j + 1))
            if len(self.history) > 0:
                last_move = self.history[-1]
                if last_move['piece'] == 'wp' and last_move['from_pos'][0] - last_move['to_pos'][0] == 2:
                    en_passant_pos = (last_move['to_pos'][0] + 1, last_move['to_pos'][1])
                    if en_passant_pos == (i + 1, j - 1) or en_passant_pos == (i + 1, j + 1):
                        moves.append(en_passant_pos)
        else:
            if i - 1 >= 0 and self.table[i - 1][j] is None:
                moves.append((i - 1, j))
                if i == 8 - 2 and self.table[i - 2][j] is None:
                    moves.append((i - 2, j))
            if i - 1 >= 0:
                if j - 1 >= 0 and self.table[i - 1][j - 1] is not None and self.table[i - 1][j - 1][0] != cur[0]:
                    moves.append((i - 1, j - 1))
                if j + 1 < 8 and self.table[i - 1][j + 1] is not None and self.table[i - 1][j + 1][0] != cur[0]:
                    moves.append((i - 1, j + 1))
            if len(self.history) > 0:
                last_move = self.history[-1]
                if last_move['piece'] == 'bp' and last_move['to_pos'][0] - last_move['from_pos'][0] == 2:
                    en_passant_pos = (last_move['to_pos'][0] - 1, last_move['to_pos'][1])
                    if en_passant_pos == (i - 1, j - 1) or en_passant_pos == (i - 1, j + 1):
                        moves.append(en_passant_pos)
        return moves
    def valid_moves(self, pressing, moves):
        if pressing is None or len(moves) == 0:
            return []
        i, j = pressing
        rs = []
        for (ii, jj) in moves:
            valid = True
            temp = Board()
            temp.bk, temp.wk = self.bk, self.wk
            temp.table = [row[:] for row in self.table]
            temp.table[ii][jj] = temp.table[i][j]
            temp.table[i][j] = None
            if temp.table[ii][jj] == 'bk':
                temp.bk = (ii, jj)
            elif temp.table[ii][jj] == 'wk':
                temp.wk = (ii, jj)
            turn = 'w' if self.table[i][j][0] == 'b' else 'b'
            king_pos = temp.bk if turn == 'w' else temp.wk
            for x in range(8):
                for y in range(8):
                    if temp.table[x][y] is not None and temp.table[x][y][0] == turn:
                        temp_moves = temp.get_move((x, y))
                        if king_pos in temp_moves:
                            valid = False
            if valid:
                rs.append((ii, jj))
        return rs
    def gen_move(self, turn, validation, skip_king):
        rs = []
        for i in range(8):
            for j in range(8):
                cur = self.table[i][j]
                if cur is not None and cur[0] == turn:
                    if cur[1] == 'k' and skip_king == True:
                        continue
                    if validation == True:
                        rs.extend(self.valid_moves((i, j), self.get_move((i, j))))
                    else:
                        rs.extend(self.get_move((i, j)))
        return rs
    def promotion(self, screen, pos, bg):
        i, j = pos
        turn = self.table[i][j][0]
        clock = pygame.time.Clock()
        pro_rect = None
        if turn == 'w':
            pro_rect = promotion_image.get_rect(topleft=self.buttons[i][j].topleft)
        else:
            pro_rect = promotion_image.get_rect(topleft=self.buttons[i - 3][j].topleft)
        options = []
        buttons = []
        if turn == 'w':
            options.extend(['wq', 'wr', 'wb', 'wn'])
            x, y = pro_rect.topleft
            for k in range(4):
                rect = image[options[k]].get_rect(topleft=(x, y))
                buttons.append(rect)
                y += rect.height
        else:
            options.extend(['bq', 'br', 'bb', 'bn'])
            x, y = pro_rect.topleft
            y += 3 * image['wq'].get_height()
            for k in range(4):
                rect = image[options[k]].get_rect(topleft=(x, y))
                buttons.append(rect)
                y -= rect.height
        while True:
            cursor_state = 'default'
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for k in range(4):
                        if buttons[k].collidepoint(mouse_pos):
                            self.table[i][j] = options[k]
                            return
            screen.blit(bg, (0, 0))
            screen.blit(promotion_image, pro_rect)
            for k in range(4):
                screen.blit(image[options[k]], buttons[k])
            cursor_img = get_cursor_image(cursor_state)
            cursor_rect = cursor_img.get_rect(topleft=mouse_pos)
            screen.blit(cursor_img, cursor_rect)
            pygame.display.flip()
            clock.tick(60)
    def record_move(self, cur, from_pos, to_pos, capture, promotion, castling, en_passant, check, checkmate):
        move = {
            'piece' : cur,
            'from_pos' : from_pos,
            'to_pos' : to_pos,
            'capture' : capture,
            'promotion' : promotion,
            'castling' : castling,
            'en_passant' : en_passant,
            'check' : check,
            'checkmate' : checkmate
        }
        self.history.append(move)
    def draw_history(self, screen, offset_y):
        screen.blit(history_board, history_rect)
        history_text = font_l.render('MOVE HISTORY', True, WHITE)
        x = history_rect.center[0]
        y = history_rect.center[1] - history_rect.height // 2 - history_text.get_height() // 2
        history_text_rect = history_text.get_rect(center=(x, y))
        screen.blit(history_text, history_text_rect)
        history_surface = pygame.Surface((history_rect.width, font_s.get_linesize() * ((len(self.history) + 1) // 2) + font_s.get_linesize()), pygame.SRCALPHA)
        x, y = 50, 25
        move_index = 1
        move_index_text = font_s.render(str(move_index), True, WHITE)
        move_index_text_rect = move_index_text.get_rect(topleft=(15, y))
        history_surface.blit(move_index_text, move_index_text_rect)
        def move_to_notation(move):
            piece = move['piece']
            start = coor_to_pos(move['from_pos'])
            end = coor_to_pos(move['to_pos'])
            capture = move['capture']
            promotion = move['promotion']
            castling = move['castling']
            en_passant = move['en_passant']
            check = move['check']
            checkmate = move['checkmate']
            # --- Handle special moves ---
            if castling == 'kingside':
                return 'O-O'
            elif castling == 'queenside':
                return 'O-O-O'
            # --- Normal moves ---
            notation = ''
            # Pawns don’t show letter unless capturing
            if piece[1] != 'p':
                notation += piece[1]
            # Captures
            if capture is not None:
                if piece[1] == 'p':
                    notation += start[0]  # pawn file (like 'exd5')
                notation += 'x'
            notation += end
            # Promotion
            if promotion is not None:
                notation += '=' + promotion
            # Checks
            if checkmate:
                notation += '#'
            elif check:
                notation += '+'
            return notation
        for move in self.history:
            notation = font_s.render(move_to_notation(move), True, WHITE)
            notation_rect = notation.get_rect(topleft=(x, y))
            history_surface.blit(notation, notation_rect)
            if x == 50:
                x += 100
            else:
                y += notation.get_height()
                x = 50
                move_index += 1
                move_index_text = font_s.render(str(move_index), True, WHITE)
                move_index_text_rect = move_index_text.get_rect(topleft=(15, y))
                history_surface.blit(move_index_text, move_index_text_rect)
        area = pygame.Rect(0, int(offset_y) + 25, history_rect.width, history_rect.height - 50)
        screen.blit(history_surface, (history_rect.topleft[0], history_rect.topleft[1] + 25), area=area)
    def fen_update(self):
        board, turn, castling, ep, halfmove, fullmove = parse_fen(self.fen)
        def board_to_fen(table, turn, castling, ep, halfmove, fullmove):
            rs = ''
            for i in range(8):
                if i > 0:
                    rs = rs + '/'
                cur = ''
                cnt = 0
                for j in range(8):
                    if table[i][j] is None:
                        cnt += 1
                    else:
                        if cnt > 0:
                            cur = cur + (str)(cnt)
                        cur = cur + fen_name[table[i][j]]
                        cnt = 0
                if cnt > 0:
                    cur = cur + (str)(cnt)
                rs = rs + cur
            return rs + f" {turn} {castling} {ep} {halfmove} {fullmove}"
        castling = ''
        if 'w_kingside' in self.castling_right:
            castling += 'K'
        if 'w_queenside' in self.castling_right:
            castling += 'Q'
        if 'b_kingside' in self.castling_right:
            castling += 'k'
        if 'b_queenside' in self.castling_right:
            castling += 'q'
        if castling == '':
            castling = '-'
        last_move = self.history[-1]
        tx, ty = last_move['to_pos']
        if last_move['piece'][1] == 'p' and abs(tx - last_move['from_pos'][0]) == 2:
            if (ty - 1 >= 0 and self.table[tx][ty - 1] is not None and self.table[tx][ty - 1][0] != last_move['piece'][0] and self.table[tx][ty - 1][1] == 'p'):
                ep = coor_to_pos((tx + (1 if turn == 'w' else -1), ty))
            elif (ty + 1 <= 7 and self.table[tx][ty + 1] is not None and self.table[tx][ty + 1][0] != last_move['piece'][0] and self.table[tx][ty + 1][1] == 'p'):
                ep = coor_to_pos((tx + (1 if turn == 'w' else -1), ty))
            else:
                ep = '-'
        else:
            ep = '-'
        if last_move['piece'][1] == 'p' or last_move['capture'] is not None:
            halfmove = 0
        else:
            halfmove += 1
        turn = 'w' if turn == 'b' else 'b'
        if turn == 'w':
            fullmove += 1
        self.fen = board_to_fen(self.table, turn, castling, ep, halfmove, fullmove)
    def apply_move(self, fr, to, screen, pr):
        promotion = None
        castling = None
        en_passant = None
        cur = None
        checkmate = False
        stalemate = False
        turn = self.table[fr[0]][fr[1]][0]
        i, j = to
        lost = self.table[i][j]
        if lost is not None:
            if lost[0] == 'w':
                self.w_lost[lost] += 1
            else:
                self.b_lost[lost] += 1
            if lost == 'wr':
                if j == 0:
                    self.castling_right.pop('w_queenside', None)
                elif j == 7:
                    self.castling_right.pop('w_kingside', None)
            elif lost == 'br':
                if j == 0:
                    self.castling_right.pop('b_kingside', None)
                elif j == 7:
                    self.castling_right.pop('b_queenside', None)
        self.table[i][j] = self.table[fr[0]][fr[1]]
        self.table[fr[0]][fr[1]] = None
        cur = self.table[i][j]
        if cur == 'bk':
            self.bk = (i, j)
            if fr[1] - j == 2:
                self.table[0][0] = None
                self.table[0][3] = 'br'
                castling = 'kingside'
            elif fr[1] - j == -2:
                self.table[0][7] = None
                self.table[0][5] = 'br'
                castling = 'queenside'
            self.castling_right.pop('b_kingside', None)
            self.castling_right.pop('b_queenside', None)
        elif cur == 'wk':
            self.wk = (i, j)
            if fr[1] - j == 2:
                self.table[7][0] = None
                self.table[7][3] = 'wr'
                castling = 'queenside'
            elif fr[1] - j == -2:
                self.table[7][7] = None
                self.table[7][5] = 'wr'
                castling = 'kingside'
            self.castling_right.pop('w_kingside', None)
            self.castling_right.pop('w_queenside', None)
        elif cur == 'br':
            if j == 0:
                self.castling_right.pop('b_kingside', None)
            elif j == 7:
                self.castling_right.pop('b_queenside', None)
        elif cur == 'wr':
            if j == 0:
                self.castling_right.pop('w_queenside', None)
            elif j == 7:
                self.castling_right.pop('w_kingside', None)
        elif cur == 'bp':
            if i == 7:
                promotion = (i, j)
            elif fr[1] != j and lost is None:
                en_passant = True
                lost = 'wp'
                self.w_lost[lost] += 1
                self.table[i - 1][j] = None
        elif cur == 'wp':
            if i == 0:
                promotion = (i, j)
            elif fr[1] != j and lost is None:
                en_passant = True
                lost = 'bp'
                self.b_lost[lost] += 1
                self.table[i + 1][j] = None
        if promotion is not None:
            if pr is not None:
                self.table[i][j] = self.table[i][j][0] + pr
            else:
                self.promotion(screen, promotion, screen.copy())
            promotion = self.table[i][j]
        turn = 'b' if turn == 'w' else 'w'
        king_pos = self.bk if turn == 'b' else self.wk
        if king_pos in self.get_move((i, j)):
            check = True
        else:
            check = False
        all_move = self.gen_move(turn, True, False)
        if len(all_move) == 0:
            if check:
                checkmate = True
            else:
                stalemate = True
        self.record_move(cur, 
                            fr, 
                            (i, j), 
                            lost, 
                            promotion, 
                            castling, 
                            en_passant,
                            check,
                            checkmate)
        self.fen_update()
        return turn, checkmate, stalemate
if __name__ == '__main__':
    pass