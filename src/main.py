"""
AUTHOR:           Hunter Hageman, Marshall Patterson
FILENAME:         main.py
SPECIFICATION:    Create an Artificial Intelligence capable of playing Flappy Bird.
FOR:              CS 3368 Introduction to Artificial Intelligence Section 001
"""

import math
import random
import sys
import time

import neat
import pygame
import const


img_pipe_bot = pygame.image.load("../assets/pipe.png")
img_pipe_top = pygame.transform.flip(img_pipe_bot, False, True)
img_bird = pygame.image.load("../assets/bird1.png")
img_background = pygame.image.load("../assets/bg.png")
img_background = pygame.transform.scale(img_background, (const.WIDTH, const.HEIGHT))
img_base = pygame.image.load("../assets/base.png")

img_num_0 = pygame.image.load("../assets/numbers/0.png")
img_num_1 = pygame.image.load("../assets/numbers/1.png")
img_num_2 = pygame.image.load("../assets/numbers/2.png")
img_num_3 = pygame.image.load("../assets/numbers/3.png")
img_num_4 = pygame.image.load("../assets/numbers/4.png")
img_num_5 = pygame.image.load("../assets/numbers/5.png")
img_num_6 = pygame.image.load("../assets/numbers/6.png")
img_num_7 = pygame.image.load("../assets/numbers/7.png")
img_num_8 = pygame.image.load("../assets/numbers/8.png")
img_num_9 = pygame.image.load("../assets/numbers/9.png")


def dist_to_rect_side(rectangle_1, rectangle_2) -> tuple[float, list[float]]:
    """
    Calculates the distance to the closest point of a rectangle
    :param rectangle_2: the rectangle to check
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
    left = rectangle_2.x
    right = rectangle_2.x + rectangle_2.size_x
    top = rectangle_2.y
    bot = rectangle_2.y + rectangle_2.size_y

    # The point to check distance to
    p: list[float]
    # State 1
    if rectangle_1.x < left and rectangle_1.y < top:
        p = [rectangle_2.x, rectangle_2.y]
    # State 3
    elif rectangle_1.x > right and rectangle_1.y < top:
        p = [rectangle_2.x + rectangle_2.size_x, rectangle_2.y]
    # State 6
    elif rectangle_1.x < left and rectangle_1.y > bot:
        p = [rectangle_2.x, rectangle_2.y + rectangle_2.size_y]
    # State 8
    elif rectangle_1.x > right and rectangle_1.y > bot:
        p = [rectangle_2.x + rectangle_2.size_x, rectangle_2.y + rectangle_2.size_y]
    # State 2
    elif rectangle_1.y < top:
        p = [rectangle_1.x, rectangle_2.y]
    # State 7
    elif rectangle_1.y > bot:
        p = [rectangle_1.x, rectangle_2.y + rectangle_2.size_y]
    # State 4
    elif rectangle_1.x < left:
        p = [rectangle_2.x, rectangle_1.y]
    # State 5
    else:
        p = [rectangle_2.x + rectangle_2.size_x, rectangle_1.y]

    return math.dist([rectangle_1.x, rectangle_1.y], p), p


def get_closest_point(rectangle, game_state):
    # Check distances to all rectangles and find the closest
    dist = 10000000.0
    point = list[int]
    for e in game_state.entities:
        if isinstance(e, Rectangle):
            dist_tuple = dist_to_rect_side(rectangle, e)
            if dist_tuple[0] < dist:
                dist = dist_tuple[0]
                point = dist_tuple[1]

    return dist, point


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


class Bird(Rectangle):
    """
    A bird which can be controlled by the player or an AI.
    """
    # The y velocity of the bird
    velocity: float
    # True when the bird has died
    dead: bool
    # Distance to closest threat
    threat: float
    # The fitness of this bird within a generation
    fitness: float

    def __init__(self, x, y):
        super().__init__(x, y, const.BIRD_X, const.BIRD_Y)
        self.velocity = 0
        self.dead = False
        self.threat = 0
        self.fitness = 0

    def jump(self):
        self.velocity = const.JUMP_VELOCITY

    def update(self, game_state):
        # Check if we're colliding
        dist = get_closest_point(self, game_state)
        if dist[0] < const.BIRD_DEATH:
            self.dead = True

        # Dead :(
        if self.dead:
            pass

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
    # If the bird has passed this set of pipes

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
        self.passed = False

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

        # # Pipes have passed the bird, increment the pipe counter
        # if self.x + const.PIPE_X < game_state.bird.x and not self.passed:
        #     self.passed = True
        #     game_state.pipes_passed += 1

        # Pipes moved off-screen, change the gap and move them to the right
        if self.x < const.PIPE_TRASH:
            self.x = const.PIPE_SPAWN
            self.change_gap()
            # We're in front of the bird now
            self.passed = False

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

    def set_closest_point(self, game_state):
        # Check distances to all rectangles and find the closest
        self.dist = 10000000.0
        for e in game_state.entities:
            if isinstance(e, Rectangle):
                dist_tuple = dist_to_rect_side(self, e)
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


class BirdDistanceCheck(DistanceLine):
    """
    Entity which sets the distance of the bird from the closest object.
    Also handles bird death.
    """
    def update(self, game_state):
        bird_pos = [game_state.bird.x + const.BIRD_X / 2, game_state.bird.y + const.BIRD_Y / 2]
        self.x = bird_pos[0]
        self.y = bird_pos[1]

        self.set_closest_point(game_state)

        if self.dist < const.BIRD_DEATH:
            game_state.bird.dead = True
        else:
            game_state.bird.threat = self.dist


class PipePassCounter(DrawableEntity):
    """
    Show the number of pipes passed on the screen
    """
    def __init__(self, x, y):
        super().__init__(x, y)

    def draw(self, game_state, surface: pygame.Surface):
        """
        Draw the pipes passed to the screen

        :param game_state: the current game state to update from
        :param surface: the surface to draw to
        :return: None
        """
        passed_str = str(game_state.pipes_passed)
        for index in range(len(passed_str)):
            num = int(passed_str[index])
            pos = [self.x + (index * const.NUM_X), self.y]

            if num == 0:
                surface.blit(img_num_0, pos)
            elif num == 1:
                surface.blit(img_num_1, pos)
            elif num == 2:
                surface.blit(img_num_2, pos)
            elif num == 3:
                surface.blit(img_num_3, pos)
            elif num == 4:
                surface.blit(img_num_4, pos)
            elif num == 5:
                surface.blit(img_num_5, pos)
            elif num == 6:
                surface.blit(img_num_6, pos)
            elif num == 7:
                surface.blit(img_num_7, pos)
            elif num == 8:
                surface.blit(img_num_8, pos)
            elif num == 9:
                surface.blit(img_num_9, pos)


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

    birds: list[Bird]
    pipes_passed: int
    entities: list[DrawableEntity]
    pipes: list[PipePair]
    floor: Floor
    background: pygame.Surface
    bg_i: int

    pipe_speed: int

    def __init__(self, debug: bool):
        self.delta = 0
        self.state_frame = 0

        self.birds = list()
        self.pipes_passed = 0

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

        # Add the bird distance updater
        # self.entities.append(BirdDistanceCheck())
        # add the pipe counter
        self.entities.append(PipePassCounter(50, 50))

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
        self.pipe_speed += const.GAIN_SPEED * self.delta

        if self.bg_i == -const.WIDTH:
            self.bg_i = 0
            self.game.blit(self.background, (const.WIDTH + self.bg_i, 0))
        self.bg_i -= 1

        self.floor.update(self)

        for pipe_pair in self.pipes:
            pipe_pair.update(self)

        for entity in self.entities:
            entity.update(self)

        for bird in self.birds:
            bird.update(self)

    def do_draw(self):
        """
        Draw entities onto the window surface.
        :return: None
        """
        self.game.blit(self.background, (self.bg_i, 0))
        self.game.blit(self.background, (const.WIDTH + self.bg_i, 0))

        for entity in self.entities:
            entity.draw(self, self.game)

        for bird in self.birds:
            bird.draw(self, self.game)

    def do_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()


generation = 0


def eval_genomes(genomes, config):
    # This is the next generation
    global generation
    generation += 1

    nn_networks = []
    nn_birds = []
    nn_genomes = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        network = neat.nn.FeedForwardNetwork.create(genome, config)
        nn_networks.append(network)
        nn_birds.append(Bird(50, const.HEIGHT / 2))
        nn_genomes.append(genome)

    # Setup Game State
    game_state = GameState(debug)
    game_state.init_window()
    game_state.birds = nn_birds

    clock = pygame.time.Clock()
    # The current rendered frame, tracked separately from game state
    real_frame = 0
    # The last time a frame was rendered, used to calculate frame time
    last_frame = time.time()

    running = True
    while running and len(nn_birds) > 0:
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
        # Evaluate if the birds want to jump
        for bird in game_state.birds:
            bird.fitness += 0.1
            dist = get_closest_point(bird, game_state)
            output = nn_networks[nn_birds.index(bird)].activate((bird.y, dist[0], dist[1][1]))
            
            if output[0] > 0.2:
                bird.jump()

        # Update the game state
        game_state.do_event()
        game_state.do_update()
        
        # Check for dead birds
        for bird in game_state.birds:
            if bird.dead:
                index = nn_birds.index(bird)
                bird.fitness -= 1
                nn_networks.pop(index)
                nn_genomes.pop(index)
                nn_birds.pop(index)
        
        game_state.do_draw()
        pygame.display.update()


if __name__ == "__main__":
    debug = bool(sys.argv[1]) if (len(sys.argv) > 1) else False

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "config.txt"
    )

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(eval_genomes, 50)


