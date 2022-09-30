import math

import pygame
import const


img_pipe_bot = pygame.image.load("../assets/pipe.png")
img_pipe_top = pygame.transform.flip(img_pipe_bot, False, True)


class DrawableEntity:
    # Absolute positions can change based on the object
    # Circle position is center, rectangle is top left, etc
    x: int
    y: int
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def draw(self, surface: pygame.Surface):
        # Error, this should be implemented
        # No abstract classes in plain python?
        assert False


class Bird(DrawableEntity):
    def __init__(self, x, y, image):
        super().__init__(x, y)
        self.image = image

    def jump(self, y):
        self.y = y

    def get_image(self):
        return self.image


class Rectangle(DrawableEntity):
    """
    A solid color rectangle.
    The x/y position is the top left of the rectangle
    """
    size_x: int
    size_y: int

    def __init__(self, x, y, size_x, size_y):
        super().__init__(x, y)
        self.size_x = size_x
        self.size_y = size_y

    def get_center_pos(self):
        """
        Get the center position of this sprite
        This is calculated by adding half of the size to the top left coordinate
        :return: a 2 entry list of the x and y positions respectively
        """
        return [self.x + (self.size_x / 2), self.y + (self.size_y / 2)]

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.x, self.y, self.size_x, self.size_y))


class Pipe(Rectangle):
    """
    A single pipe in the game.
    The x/y position is the top left point of the pipe sprite
    """
    img: pygame.Surface

    def __init__(self, x, y, top):
        super().__init__(x, y, const.PIPE_X, const.PIPE_Y)
        if top:
            self.img = img_pipe_top
        else:
            self.img = img_pipe_bot

    def draw(self, surface: pygame.Surface):
        surface.blit(self.img, [self.x, self.y])


class MouseLine(DrawableEntity):
    # The distance to the closest point
    dist: float
    # The point we are closest to
    point: list[int]

    def __init__(self):
        # The position of this entity updates every frame
        super().__init__(0, 0)
        self.dist = 0
        self.point = [0, 0]

    def dist_to_rect_side(self, rectangle: Rectangle) -> tuple[float, list[int]]:
        """
        Calculates the distance to the closest point of a rectangle
        :param rectangle: the rectangle to check
        :return: a tuple of the distance and closest point
        """
        # 8 states for the 8 areas created by dividing the coordinate space
        # along the sides of the rectangle (as if they were infinite)
        # Excluding inside the rectangle
        #     LEFT    RIGHT
        #     11 # 22 # 33
        #     11 # 22 # 33
        #     ## # ## # ## TOP
        #     44 # XX # 55
        #     44 # XX # 55
        #     ## # ## # ## BOT
        #     66 # 77 # 88
        #     66 # 77 # 88

        # Rectangle sides as 1D planes
        left = rectangle.x
        right = rectangle.x + rectangle.size_x
        top = rectangle.y
        bot = rectangle.y + rectangle.size_y

        # The point to check distance to
        p: list[int]
        # State 1
        if self.x < left and self.y < top:
            p = [rectangle.x, rectangle.y]
        # State 3
        elif self.x > right and self.y < top:
            p = [rectangle.x + rectangle.size_x, rectangle.y]
        # State 6
        elif self.x < left and self.y > bot:
            p = [rectangle.x, rectangle.y + rectangle.size_y]
        # State 8
        elif self.x > right and self.y > bot:
            p = [rectangle.x + rectangle.size_x, rectangle.y + rectangle.size_y]
        # State 2
        elif self.y < top:
            p = [self.x, rectangle.y]
        # State 7
        elif self.y > bot:
            p = [self.x, rectangle.y + rectangle.size_y]
        # State 4
        elif self.x < left:
            p = [rectangle.x, self.y]
        # State 5
        else:
            p = [rectangle.x + rectangle.size_x, self.y]

        return math.dist([self.x, self.y], p), p

    def draw(self, surface: pygame.Surface):
        # Compare distance to the mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.x = mouse_pos[0]
        self.y = mouse_pos[1]

        # Check distances to all rectangles and find the closest
        self.dist = 10000000.0
        for e in entities:
            if isinstance(e, Rectangle):
                dist_tuple = self.dist_to_rect_side(e)
                if dist_tuple[0] < self.dist:
                    self.dist = dist_tuple[0]
                    self.point = dist_tuple[1]

        pygame.draw.line(surface, (255, 0, 255), [self.x, self.y], self.point)


def add_pipe_pair(entity_list, x, y, gap):
    entity_list.append(Pipe(x, y - const.PIPE_Y, True))
    entity_list.append(Pipe(x, y + gap, False))

entities = list()
# Pipes
add_pipe_pair(entities, 100, 50, 200)
add_pipe_pair(entities, 200, 100, 150)
add_pipe_pair(entities, 300, 150, 100)
add_pipe_pair(entities, 400, 200, 50)
entities.append(MouseLine())


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
    game.blit(bird.get_image(), (bird.x, bird.y))

    for entity in entities:
        entity.draw(game)

    if i == -const.WIDTH:
        i = 0
        game.blit(background, (const.WIDTH + i, 0))
    i -= 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump(bird.y + -25)
    pygame.display.update()
