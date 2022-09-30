import math
import sys

import pygame
import const


img_pipe_bot = pygame.image.load("../assets/pipe.png")
img_pipe_top = pygame.transform.flip(img_pipe_bot, False, True)
img_bird = pygame.image.load("../assets/bird1.png")
img_background = pygame.image.load("../assets/bg.png")
img_background = pygame.transform.scale(img_background, (const.WIDTH, const.HEIGHT))


class DrawableEntity:
    # Absolute positions can change based on the object
    # Circle position is center, rectangle is top left, etc
    x: float
    y: float
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, game_state):
        """
        Update the entity before being drawn, if needed.
        :param game_state: the GameState instance this entity belongs to
        :return: None
        """
        pass
    
    def draw(self, game_state, surface: pygame.Surface):
        # Error, this should be implemented
        # No abstract classes in plain python?
        assert False


class Bird(DrawableEntity):
    """
    A bird which can be controlled by the player or an AI.
    """
    # The y velocity of the bird
    velocity: float

    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocity = 0

    def jump(self):
        self.velocity += const.JUMP_VELOCITY

    def update(self, game_state):
        # Position Check
        # Move the bird to a safe area if needed
        if self.y < const.BIRD_MIN_Y:
            self.y = const.BIRD_MIN_Y
            self.velocity = 0
            return
        elif self.y > const.BIRD_MAX_Y:
            # FUTURE: This will be a death condition
            self.y = const.BIRD_MAX_Y
            self.velocity = 0
            return

        # Gravity update
        self.velocity += const.GRAVITY

        # Bounds check
        if self.velocity > const.MAX_VELOCITY:
            self.velocity = const.MAX_VELOCITY
        elif self.velocity < const.MIN_VELOCITY:
            self.velocity = const.MIN_VELOCITY

        # Update Position
        self.y += self.velocity

        print(self.velocity)

    def draw(self, game_state, surface: pygame.Surface):
        surface.blit(img_bird, (self.x, self.y))


class Rectangle(DrawableEntity):
    """
    A solid color rectangle.
    The x/y position is the top left of the rectangle
    """
    size_x: float
    size_y: float

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

    def draw(self, game_state, surface: pygame.Surface):
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

    def update(self, game_state):
        self.x -= game_state.pipe_speed

    def draw(self, game_state, surface: pygame.Surface):
        surface.blit(self.img, [self.x, self.y])


class MouseLine(DrawableEntity):
    # The distance to the closest point
    dist: float
    # The point we are closest to
    point: list[float]

    def __init__(self):
        # The position of this entity updates every frame
        super().__init__(0, 0)
        self.dist = 0
        self.point = [0, 0]

    def dist_to_rect_side(self, rectangle: Rectangle) -> tuple[float, list[float]]:
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
        p: list[float]
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

    def update(self, game_state):
        # Compare distance to the mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.x = mouse_pos[0]
        self.y = mouse_pos[1]

        # Check distances to all rectangles and find the closest
        self.dist = 10000000.0
        for e in game_state.entities:
            if isinstance(e, Rectangle):
                dist_tuple = self.dist_to_rect_side(e)
                if dist_tuple[0] < self.dist:
                    self.dist = dist_tuple[0]
                    self.point = dist_tuple[1]

    def draw(self, game_state, surface: pygame.Surface):
        pygame.draw.line(surface, (255, 0, 255), [self.x, self.y], self.point)


def add_pipe_pair(entity_list, x, y, gap):
    entity_list.append(Pipe(x, y - const.PIPE_Y, True))
    entity_list.append(Pipe(x, y + gap, False))


class GameState:
    """
    An organized structure of all entities in the game
    """
    game: pygame.Surface

    bird: Bird
    entities: list[DrawableEntity]
    background: pygame.Surface
    bg_i: int

    pipe_speed: int

    def __init__(self, debug: bool):
        self.bird = Bird(50, 500)

        self.entities = list()
        add_pipe_pair(self.entities, 100, 50, 200)
        add_pipe_pair(self.entities, 200, 100, 150)
        add_pipe_pair(self.entities, 300, 150, 100)
        add_pipe_pair(self.entities, 400, 200, 50)

        if debug:
            self.entities.append(MouseLine())

        self.background = img_background
        self.bg_i = 0

        self.pipe_speed = const.INIT_SPEED

    def init_window(self):
        self.game = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
        self.bg_i = 0

        pygame.display.set_caption("Flappy Bird AI")
        clock = pygame.time.Clock()
        clock.tick(30)

    def do_update(self):
        """
        Update entities before drawing them.
        :return: None
        """
        self.pipe_speed += const.GAIN_SPEED

        if self.bg_i == -const.WIDTH:
            self.bg_i = 0
            self.game.blit(self.background, (const.WIDTH + self.bg_i, 0))
        self.bg_i -= 1

        # Bad workaround, we remove pipes one at a time but add them two at a time
        spawn_pipes = False
        for entity in self.entities:
            entity.update(self)
            # Respawn pipes if needed
            # FUTURE: Handle pipes better, just move them to the right
            if isinstance(entity, Pipe):
                if entity.x < const.PIPE_TRASH:
                    # Self modification issues?
                    self.entities.remove(entity)
                    spawn_pipes = True

        if spawn_pipes:
            add_pipe_pair(self.entities, 100, 50, 400)

        self.bird.update(self)

    def do_draw(self):
        """
        Draw entities onto the window surface.
        :return: None
        """
        self.game.blit(self.background, (self.bg_i, 0))
        self.game.blit(self.background, (const.WIDTH + self.bg_i, 0))

        for entity in self.entities:
            entity.draw(self, self.game)

        self.bird.draw(self, self.game)

    def do_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.bird.jump()


if __name__ == "__main__":
    debug = bool(sys.argv[1]) if (len(sys.argv) > 1) else False

    game_state = GameState(debug)
    game_state.init_window()

    while True:
        game_state.do_update()
        game_state.do_draw()
        game_state.do_event()
        pygame.display.update()
