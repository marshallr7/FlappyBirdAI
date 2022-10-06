import math
import random
import sys
import time

import pygame
import const


img_pipe_bot = pygame.image.load("../assets/pipe.png")
img_pipe_top = pygame.transform.flip(img_pipe_bot, False, True)
img_bird = pygame.image.load("../assets/bird1.png")
img_background = pygame.image.load("../assets/bg.png")
img_background = pygame.transform.scale(img_background, (const.WIDTH, const.HEIGHT))
img_base = pygame.image.load("../assets/base.png")


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
        self.velocity = const.JUMP_VELOCITY

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
        self.velocity += const.GRAVITY * game_state.delta

        # Bounds check
        if self.velocity > const.MAX_VELOCITY:
            self.velocity = const.MAX_VELOCITY
        elif self.velocity < const.MIN_VELOCITY:
            self.velocity = const.MIN_VELOCITY

        # Update Position
        self.y += self.velocity * game_state.delta

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
    top: bool

    def __init__(self, x, y, top):
        super().__init__(x, y, const.PIPE_X, const.PIPE_Y)
        self.top = top
        if top:
            self.img = img_pipe_top
        else:
            self.img = img_pipe_bot

    def draw(self, game_state, surface: pygame.Surface):
        surface.blit(self.img, [self.x, self.y])


class PipePair(DrawableEntity):
    """
    A Pair of Pipes in the game.
    Both need to be tracked so that it is known when the bird passes one pair of pipes.
    Also removes a check to move a pipe, since only this object needs to be updated.
    We can get more control over the size and location by knowing where the pipes are.
    """
    # Top and Bottom pipe
    top_pipe: Pipe
    bot_pipe: Pipe
    # The X position of the pipes, their position is set to this
    x: int

    def __init__(self, x: int):
        """
        Initialize a pipe pair at the provided x coordinate
        :param x: the x coordinate to place the pipes at
        """
        super().__init__(x, 0)
        self.x = x
        self.top_pipe = Pipe(x, 0, True)
        self.bot_pipe = Pipe(x, 0, False)
        self.change_gap()

    def change_gap(self):
        """
        Change the y positions of the pipes to move where the gap is.
        Called on init and when the pipes move past the bird off-screen
        :return: None
        """
        # Calculate the gap size
        gap = random.randrange(const.GAP_MIN, const.GAP_MAX)
        # The lowest point the top of the gap can be at to not be too low
        lowest = const.HEIGHT - const.PIPE_BOT - gap
        # Where the top pipe will reach to
        pipe_loc = random.randrange(const.PIPE_TOP, lowest)

        # Move pipes
        self.top_pipe.y = pipe_loc - const.PIPE_Y
        self.bot_pipe.y = pipe_loc + gap

    def update(self, game_state):
        """
        Update the positions of the pipes for them.
        We don't want to handle varying state of if this or the pipes update before/after each other.

        :param game_state: the current state of the game we update from
        :return: None
        """
        self.x -= game_state.pipe_speed * game_state.delta

        # Pipes moved off-screen, change the gap and move them to the right
        if self.x < const.PIPE_TRASH:
            self.x = const.PIPE_SPAWN
            self.change_gap()

        self.top_pipe.x = self.x
        self.bot_pipe.x = self.x


class FloorTile(Rectangle):
    """
    A single floor tile which is repeated across the bottom of the screen.
    This is updated by the Floor class.
    """

    def __init__(self, x: int):
        super().__init__(x, const.FLOOR_Y, const.BASE_X, const.BASE_Y)

    def draw(self, game_state, surface: pygame.Surface):
        surface.blit(img_base, [self.x, self.y])


class Floor(DrawableEntity):
    """
    A collection of floor sprites which scroll by.
    Like the pipe pair class, this will only update the x positions of the sprites
    """
    tiles: list[FloorTile]

    def __init__(self):
        super().__init__(0, 0)
        self.tiles = list()

        num_tiles = math.ceil((const.WIDTH + const.BASE_X) / const.BASE_X)
        for i in range(num_tiles):
            self.tiles.append(FloorTile(i * const.BASE_X))

    def update(self, game_state):
        for tile in self.tiles:
            tile.x -= game_state.pipe_speed * game_state.delta
            # If the tile is off the screen then move it back to the right
            if const.BASE_X + tile.x < 0:
                tile.x += const.BASE_X * len(self.tiles)


class DistanceLine(DrawableEntity):
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

    def set_closest_point(self, game_state):
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


class MouseLine(DistanceLine):
    def update(self, game_state):
        # Compare distance to the mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.x = mouse_pos[0]
        self.y = mouse_pos[1]

        self.set_closest_point(game_state)


class BirdLine(DistanceLine):
    def update(self, game_state):
        bird_pos = [game_state.bird.x + const.BIRD_X / 2, game_state.bird.y + const.BIRD_Y / 2]
        self.x = bird_pos[0]
        self.y = bird_pos[1]

        self.set_closest_point(game_state)


def add_pipe_pair(entity_list, pipe_list, x):
    new_pair = PipePair(x)
    entity_list.append(new_pair.top_pipe)
    entity_list.append(new_pair.bot_pipe)
    pipe_list.append(new_pair)


class GameState:
    """
    An organized structure of all entities in the game
    """
    game: pygame.Surface
    # Time change since the last frame was rendered
    delta: float
    # The frame of this game state
    state_frame: int

    bird: Bird
    entities: list[DrawableEntity]
    pipes: list[PipePair]
    floor: Floor
    background: pygame.Surface
    bg_i: int

    pipe_speed: int

    def __init__(self, debug: bool):
        self.delta = 0
        self.state_frame = 0

        self.bird = Bird(50, const.HEIGHT / 2)

        self.entities = list()
        self.pipes = list()
        # Spawn pipes with their set distances, need to include trash distance for consistency
        add_pipe_pair(self.entities, self.pipes, (const.PIPE_TRASH + const.WIDTH))
        add_pipe_pair(self.entities, self.pipes, (const.PIPE_TRASH + const.WIDTH) * 1.4)
        add_pipe_pair(self.entities, self.pipes, (const.PIPE_TRASH + const.WIDTH) * 1.8)
        # Add the Floor
        self.floor = Floor()
        for tile in self.floor.tiles:
            self.entities.append(tile)

        if debug:
            self.entities.append(MouseLine())
            self.entities.append(BirdLine())

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
        self.state_frame = self.state_frame + 1
        self.pipe_speed += const.GAIN_SPEED * game_state.delta

        if self.bg_i == -const.WIDTH:
            self.bg_i = 0
            self.game.blit(self.background, (const.WIDTH + self.bg_i, 0))
        self.bg_i -= 1

        self.floor.update(self)

        for pipe_pair in self.pipes:
            pipe_pair.update(self)

        for entity in self.entities:
            entity.update(self)

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

    clock = pygame.time.Clock()
    # The current rendered frame, tracked separately from game state
    real_frame = 0
    # The last time a frame was rendered, used to calculate frame time
    last_frame = time.time()

    while True:
        # Prevent de-sync
        if game_state.state_frame != real_frame:
            assert False

        real_frame = real_frame + 1
        # Limit the frame rate
        clock.tick(const.FPS)

        # Calculate the time since the last frame
        # pygame.clock.get_fps() averages the last 10 frames
        # pygame.clock.get_time() returns an int in ms, no decimal. 16 instead if 16.6777
        next_frame = time.time()
        game_state.delta = next_frame - last_frame
        last_frame = next_frame

        # Perform per-frame game operations
        game_state.do_update()
        game_state.do_draw()
        game_state.do_event()
        pygame.display.update()
