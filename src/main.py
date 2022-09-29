import pygame
import const


class Bird:
    def __init__(self, x, y, image):
        self.x = x
        self.height = y
        self.image = image

    def jump(self, y):
        self.height = y

    def get_image(self):
        return self.image


game = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
pygame.display.set_caption("Flappy Bird AI")
clock = pygame.time.Clock()
clock.tick(30)

background = pygame.image.load("../assets/bg.png")
background = pygame.transform.scale(background, (const.WIDTH, const.HEIGHT))
bird = Bird(50, 500, pygame.image.load("../assets/bird1.png"))

i = 0

while True:
    game.blit(background, (i, 0))
    game.blit(background, (const.WIDTH + i, 0))
    game.blit(bird.get_image(), (bird.x, bird.height))

    if i == -const.WIDTH:
        i = 0
        game.blit(background, (const.WIDTH + i, 0))
    i -= 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump(bird.height + -25)
        pygame.display.update()
