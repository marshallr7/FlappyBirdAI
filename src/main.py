import math

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


class DrawableEntity:
    def draw(self, surface: pygame.Surface):
        # Error, this should be implemented
        # No abstract classes in plain python?
        assert False


class Rectangle(DrawableEntity):
    tl_x: int
    tl_y: int
    size_x: int
    size_y: int

    def __init__(self, tl_x, tl_y, size_x, size_y):
        self.tl_x = tl_x
        self.tl_y = tl_y
        self.size_x = size_x
        self.size_y = size_y

    def get_center_pos(self):
        """
        Get the center position of this sprite
        This is calculated by adding half of the size to the top left coordinate
        :return: a 2 entry list of the x and y positions respectively
        """
        return [self.tl_x + (self.size_x / 2), self.tl_y + (self.size_y / 2)]

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.tl_x, self.tl_y, self.size_x, self.size_y))


class MouseLine(DrawableEntity):
    # Center coordinates
    x: int
    y: int
    # The distance to the closest point
    dist: float
    # The point we are closest to
    point: list[int]

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
        left = rectangle.tl_x
        right = rectangle.tl_x + rectangle.size_x
        top = rectangle.tl_y
        bot = rectangle.tl_y + rectangle.size_y

        # The point to check distance to
        p: list[int]
        # State 1
        if self.x < left and self.y < top:
            p = [rectangle.tl_x, rectangle.tl_y]
        # State 3
        elif self.x > right and self.y < top:
            p = [rectangle.tl_x + rectangle.size_x, rectangle.tl_y]
        # State 6
        elif self.x < left and self.y > bot:
            p = [rectangle.tl_x, rectangle.tl_y + rectangle.size_y]
        # State 8
        elif self.x > right and self.y > bot:
            p = [rectangle.tl_x + rectangle.size_x, rectangle.tl_y + rectangle.size_y]
        # State 2
        elif self.y < top:
            p = [self.x, rectangle.tl_y]
        # State 7
        elif self.y > bot:
            p = [self.x, rectangle.tl_y + rectangle.size_y]
        # State 4
        elif self.x < left:
            p = [rectangle.tl_x, self.y]
        # State 5
        else:
            p = [rectangle.tl_x + rectangle.size_x, self.y]

        return math.dist([self.x, self.y], p), p
        # dist_left = abs(left - self.x)
        # dist_right = abs(right - self.x)
        # dist_x = left if dist_left < dist_right else right
        #
        # dist_top = abs(top - self.y)
        # dist_bot = abs(bot - self.y)
        # dist_y = top if dist_top < dist_bot else bot
        #
        # dist_corner_x = dist_x - self.x
        # dist_corner_y = dist_y - self.y
        # dist_corner = math.sqrt((dist_corner_x * dist_corner_x) + (dist_corner_y * dist_corner_y))
        #
        # return min(dist_left, dist_right, dist_top, dist_bot, dist_corner)

    def draw(self, surface: pygame.Surface):
        # Compare distance to the mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.x = mouse_pos[0]
        self.y = mouse_pos[1]

        # Check distances to all rectangles and find the closest
        self.dist = 10000000.0
        for e in entities:
            if isinstance(e, Rectangle):
                # dist = math.dist(mouse_pos, e.get_center_pos())
                dist_tuple = self.dist_to_rect_side(e)
                if dist_tuple[0] < self.dist:
                    self.dist = dist_tuple[0]
                    self.point = dist_tuple[1]

        # Draw
        #pygame.draw.circle(surface, (100, 100, 100), [self.x, self.y], self.dist)
        pygame.draw.line(surface, (255, 0, 255), [self.x, self.y], self.point)


entities = list()
# top rect
entities.append(Rectangle(100, 100, 200, 100))
# middle rect
entities.append(Rectangle(300, 200, 50, 200))
# bottom rect
entities.append(Rectangle(500, 100, 20, 20))
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
    game.blit(bird.get_image(), (bird.x, bird.height))

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
                bird.jump(bird.height + -25)
    pygame.display.update()
