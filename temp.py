import pygame
import sys

WIDTH, HEIGHT = 800, 800
SCALING = 5

pygame.init()

WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

pawn_image = pygame.image.load('./images/16x32_pieces/bp.png')
pawn_image = pygame.transform.smoothscale(pawn_image, (pawn_image.get_width() * SCALING, pawn_image.get_height() * SCALING))
pawn_rect = pawn_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        screen.fill(WHITE)
        screen.blit(pawn_image, pawn_rect)
        pygame.display.flip()