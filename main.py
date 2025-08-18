from board import *
from engine import *

def winner(screen, turn, reason, bg):
    winner = 'b' if turn == 'w' else 'w'
    win_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    clock = pygame.time.Clock()
    title1 = None
    if reason == 'CHECKMATE':
        title1 = f"{'BLACK' if winner == 'b' else 'WHITE'} WON"
    else:
        title1 = 'DRAW'
    title2 = f"BY {reason}"
    title1_surface = font_l.render(title1, True, WHITE)
    title1_rect = title1_surface.get_rect(center=BOARD_CENTER)
    title2_surface = font_l.render(title2, True, WHITE)
    title2_rect = title2_surface.get_rect(center=(BOARD_CENTER[0], BOARD_CENTER[1] + title1_rect.height))
    new_button_rect = button_image.get_rect(center=(BOARD_CENTER[0], BOARD_CENTER[1] + 80))
    quit_button_rect = button_image.get_rect(center=(BOARD_CENTER[0], BOARD_CENTER[1] + button_image.get_height() + 90))
    new_text = font.render('NEW GAME', True, WHITE)
    quit_text = font.render('QUIT GAME', True, WHITE)
    new_rect = new_text.get_rect(center=new_button_rect.center)
    quit_rect = quit_text.get_rect(center=quit_button_rect.center)
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
                if new_button_rect.collidepoint(mouse_pos):
                    return
                if quit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
        screen.blit(bg, (0, 0))
        win_surface.fill((0, 0, 0, 150))
        win_surface.blit(win_image, win_rect)
        win_surface.blit(title1_surface, title1_rect)
        win_surface.blit(title2_surface, title2_rect)
        win_surface.blit(button_image, new_button_rect)
        win_surface.blit(button_image, quit_button_rect)
        win_surface.blit(new_text, new_rect)
        win_surface.blit(quit_text, quit_rect)
        screen.blit(win_surface, (0, 0))
        cursor_img = get_cursor_image(cursor_state)
        cursor_rect = cursor_img.get_rect(topleft=mouse_pos)
        screen.blit(cursor_img, cursor_rect)
        pygame.display.flip()
        clock.tick(60)
        
def clamp_scroll(y, board):
    max_height = font_s.get_linesize() * ((len(board.history) + 1) // 2) + font_s.get_linesize()
    max_scroll = max(0, max_height - history_rect.height + 25)
    return max(0, min(y, max_scroll))

def game(screen):
    board = Board()
    clock = pygame.time.Clock()
    pressing = None
    valid_moves = []
    turn = 'w'
    cursor_state = 'default'
    check = False
    offset_y = 0.0
    future_ai = None
    while True:
        cursor_state = 'default'
        mouse_pos = pygame.mouse.get_pos()
        checkmate = False
        stalemate = False
        rs = None
        if turn == 'b' and future_ai is None:
            future_ai = executor.submit(get_best_move_rest, board.fen, 8, 1)
        if future_ai and future_ai.done():
            rs = future_ai.result()
            pressing = pos_to_coor(rs['move'][:2])
            to = pos_to_coor(rs['move'][2:])
            pr = None
            if len(rs['move']) == 5:
                pr = rs['move'][-1]
            turn, checkmate, stalemate = board.apply_move(pressing, to, screen, pr)
            future_ai = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif history_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEWHEEL:
                offset_y = clamp_scroll(offset_y - event.y * 40, board)
            elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONUP:
                for i in range(8):
                    for j in range(8):
                        if board.buttons[i][j].collidepoint(mouse_pos):
                            cursor_state = 'hover'
            for i in range(8):
                for j in range(8):
                    if event.type == pygame.MOUSEBUTTONDOWN and board.buttons[i][j].collidepoint(mouse_pos):
                        cursor_state = 'click'
                        if pressing != (i, j):
                            if pressing is None or (i, j) not in valid_moves:
                                if board.table[i][j] is not None and board.table[i][j][0] == turn:
                                    pressing = (i, j)
                            else:
                                turn, checkmate, stalemate = board.apply_move(pressing, (i, j), screen, None)
                        else:
                            pressing = None
        screen.blit(bg_image, (0, 0))
        screen.blit(board_image, board_rect)
        screen.blit(status_bar, STATUS_TOPLEFT)
        board.draw_board(screen)
        board.draw_avatar(screen, turn)
        board.draw_announce(screen, turn, check)
        board.draw_lost(screen)
        valid_moves = board.valid_moves(pressing, board.get_move(pressing))
        if turn == 'w':
            board.draw_move(screen, valid_moves)
        board.draw_history(screen, offset_y)
        halfmove = parse_fen(board.fen)[4]
        if checkmate:
            winner(screen, turn, 'CHECKMATE', screen.copy())
            return
        elif stalemate:
            winner(screen, turn, 'STALEMATE', screen.copy())
            return
        elif halfmove >= 100:
            winner(screen, turn, 'THE FIFTY-MOVE RULE', screen.copy())
        cursor_img = get_cursor_image(cursor_state)
        cursor_rect = cursor_img.get_rect(topleft=mouse_pos)
        screen.blit(cursor_img, cursor_rect)
        pygame.display.flip()
        clock.tick(60)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    while True:
        game(screen)

if __name__ == "__main__":
    main()