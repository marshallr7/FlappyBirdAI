import pygame
import const

game = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
pygame.display.set_caption("Flappy Bird AI")
clock = pygame.time.Clock()
clock.tick(30)

background = pygame.image.load("../assets/bg.png")
background = pygame.transform.scale(background, (const.WIDTH, const.HEIGHT))
bird = pygame.image.load("../assets/bird1.png")

i = 0

while True:
    bird_rect = bird.get_rect()
    game.blit(background, (i, 0))
    game.blit(background, (const.WIDTH+i, 0))

    if i == -const.WIDTH:
        i = 0
        game.blit(background, (const.WIDTH + i, 0))
    i -= 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("space")
        pygame.display.update()