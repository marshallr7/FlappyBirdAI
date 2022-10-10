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
    NAME:           dist_to_rect_side
    PARAMETERS:     rectangle_1, the rectangle to start from
                    rectangle_2, the rectangle to calculate the distance to
    PURPOSE:        This function calculates the distance from the center of rectangle_1
                    to the closest edge of rectangle_2 to measure the distance to a collision.
    PRECONDITION:   Both rectangles should be initialized and not None.
    POSTCONDITION:  The rectangles will not be modified. A tuple will be returned.
                    The first value of the tuple will be the distance to the closest edge as a float.
                    The second value will be a coordinate pair of where the collision is, with
                    the first value being the x position and the second value being the y position.
                    The coordinates are returned as a list of floats.
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

    # Center of rectangle 1
    r1_center = rectangle_1.get_center_pos()
    r1_x = r1_center[0]
    r1_y = r1_center[1]

    # Rectangle sides as 1D planes
    left = rectangle_2.x
    right = rectangle_2.x + rectangle_2.size_x
    top = rectangle_2.y
    bot = rectangle_2.y + rectangle_2.size_y

    # The point to check distance to
    p: list[float]
    # State 1
    if r1_x < left and r1_y < top:
        p = [rectangle_2.x, rectangle_2.y]
    # State 3
    elif r1_x > right and r1_y < top:
        p = [rectangle_2.x + rectangle_2.size_x, rectangle_2.y]
    # State 6
    elif r1_x < left and r1_y > bot:
        p = [rectangle_2.x, rectangle_2.y + rectangle_2.size_y]
    # State 8
    elif r1_x > right and r1_y > bot:
        p = [rectangle_2.x + rectangle_2.size_x, rectangle_2.y + rectangle_2.size_y]
    # State 2
    elif r1_y < top:
        p = [r1_x, rectangle_2.y]
    # State 7
    elif r1_y > bot:
        p = [r1_x, rectangle_2.y + rectangle_2.size_y]
    # State 4
    elif r1_x < left:
        p = [rectangle_2.x, r1_y]
    # State 5
    else:
        p = [rectangle_2.x + rectangle_2.size_x, r1_y]

    return math.dist([r1_x, r1_y], p), p


def get_closest_point(rectangle, game_state) -> tuple[float, list[float]]:
    """
    NAME:           get_closest_point
    PARAMETERS:     rectangle, the rectangle to start from
                    game_state, the state of the game the rectangle is in
    PURPOSE:        This function measures the distance from the provided rectangle
                    to the closest rectangle side in the game state
    PRECONDITION:   Both parameters should be initialized and not None. There must be at least one other
                    rectangle in the game state which is not the same as the rectangle parameter.
    POSTCONDITION:  The parameters will not be modified. A tuple will be returned.
                    The first value of the tuple will be the distance to the closest edge as a float.
                    The second value will be a coordinate pair of where the collision is, with
                    the first value being the x position and the second value being the y position.
                    The coordinates are returned as a list of floats.
    """
    closest = 1000000.0, list[int]
    for e in game_state.entities:
        if isinstance(e, Rectangle):
            dist_tuple = dist_to_rect_side(rectangle, e)
            if dist_tuple[0] < closest[0]:
                closest = dist_tuple

    return closest


class GameEntity:
    """
    NAME:           GameEntity
    PURPOSE:        A super class for all game entities which need to be updated or drawn to the screen
                    x and y coordinate, and update/draw methods to be called each frame.
    INVARIANTS:     x and y can be any positive or negative float value. x and y are not always the top left coordinate
                    depending on the implementing class. x and y will not be none or uninitialized
    """
    # Absolute positions can change based on the subclass
    # Circle position is center, Rectangle is top left, etc.
    # But for the most part, rectangle is used
    x: float
    y: float
    
    def __init__(self, x, y):
        """
        NAME:           GameEntity.__init__
        PARAMETERS:     x and y coordinates of the location of this entity
        PURPOSE:        This method initializes fields for a new DrawableEntity instance.
        PRECONDITION:   x and y are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        self.x = x
        self.y = y

    def update(self, game_state):
        """
        NAME:           GameEntity.update
        PARAMETERS:     game_state, the game state this entity is a part of
        PURPOSE:        This method updates the properties of this instance to be rendered on the next frame.
        PRECONDITION:   This instance is a part of the provided game state
        POSTCONDITION:  This instance is updated and ready to be rendered on the next frame.
        """
        # This is the default behavior, which is to not update since not every entity updates each frame
        pass
    
    def draw(self, game_state):
        """
        NAME:           GameEntity.draw
        PARAMETERS:     game_state, the game state this entity is a part of
        PURPOSE:        This method draws this entity to the surface that will be used for the next frame.
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        # Error, this should be implemented for drawn entities, or not called if the entity doesn't draw itself
        assert False


class Rectangle(GameEntity):
    """
    NAME:           Rectangle
    PURPOSE:        A game entity with a rectangular shape.
    INVARIANTS:     size_x and size_y must be greater than 0, not None, and initialized.
    """
    size_x: float
    size_y: float

    def __init__(self, x, y, size_x, size_y):
        """
        NAME:           Rectangle.__init__
        PARAMETERS:     x and y coordinates of the location of this entity
                        size_x and size_y are the width and height of this entity
        PURPOSE:        This method initializes fields for a new Rectangle instance.
        PRECONDITION:   all parameters are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(x, y)
        self.size_x = size_x
        self.size_y = size_y

    def get_center_pos(self) -> list[float]:
        """
        NAME:           Rectangle.get_center_pos
        PURPOSE:        This method calculates and returns the center coordinates of this entity
        PRECONDITION:   x, y, size_x, and size_y are not none and initialized
        POSTCONDITION:  This instance is not modified, and the coordinates for this entities center are returned
                        in a list consisting of the x and y position as float values
        """
        return [self.x + (self.size_x / 2), self.y + (self.size_y / 2)]

    def draw(self, game_state):
        """
        NAME:           Rectangle.draw
        PARAMETERS:     game_state, the game state this entity is a part of
        PURPOSE:        This method draws a red rectangle to the surface that will be used for the next frame.
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        # Draw a red rectangle for simple functionality
        pygame.draw.rect(game_state.surface, (255, 0, 0), pygame.Rect(self.x, self.y, self.size_x, self.size_y))


class Bird(Rectangle):
    """
    NAME:           Bird
    PURPOSE:        A game entity representing a moving bird.
    INVARIANTS:     x and y must not be None and initialized
                    y must be within the const.BIRD_MIN_Y and const.BIRD_MAX_Y
    """
    # The y velocity of the bird
    velocity: float
    # If the bird is dead
    dead: bool
    # Distance to the closest threat
    threat: float
    # The fitness of this bird within a generation
    fitness: float

    def __init__(self, x, y):
        """
        NAME:           Bird.__init__
        PARAMETERS:     x and y coordinates of the top left corner of this entity
        PURPOSE:        This method initializes fields for a new Bird instance.
        PRECONDITION:   all parameters are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(x, y, const.BIRD_X, const.BIRD_Y)
        self.velocity = 0
        self.dead = False
        self.threat = 0
        self.fitness = 0

    def jump(self):
        """
        NAME:           Bird.jump
        PURPOSE:        This method makes the bird jump from its current position regardless of current velocity.
        PRECONDITION:   None
        POSTCONDITION:  This instance's velocity is set to the jumping velocity
        """
        self.velocity = const.JUMP_VELOCITY

    def update(self, game_state):
        """
        NAME:           Bird.update
        PURPOSE:        This method performs checks and calculations each frame to detect if the bird has died,
                        and the new velocity/position for the bird.
        PRECONDITION:   The bird is not dead.
        POSTCONDITION:  This instance's fields have been updated
        """
        # Check if we're colliding
        dist = get_closest_point(self, game_state)
        if dist[0] < const.BIRD_DEATH:
            self.dead = True
        else:
            self.threat = dist[0]

        # The bird has died, stop the update
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

        # Bounds check for velocity
        if self.velocity > const.MAX_VELOCITY:
            self.velocity = const.MAX_VELOCITY
        elif self.velocity < const.MIN_VELOCITY:
            self.velocity = const.MIN_VELOCITY

        # Update Position
        self.y += self.velocity * game_state.delta

    def draw(self, game_state):
        """
        NAME:           Bird.draw
        PARAMETERS:     game_state, the game state this entity is a part of
        PURPOSE:        This method draws a bird to the surface that will be used for the next frame.
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        game_state.surface.blit(img_bird, (self.x, self.y))


class Pipe(Rectangle):
    """
    NAME:           Pipe
    PURPOSE:        A game entity representing a pipe that will kill the bird on contact.
    INVARIANTS:     x and y must not be None and initialized
                    top must be True or False
    """
    img: pygame.Surface
    top: bool

    def __init__(self, x, y, top):
        """
        NAME:           Pipe.__init__
        PARAMETERS:     x and y coordinates of the top left corner of this entity
                        top is False when this pipe connects with the floor
                        top is True when this pipe should be flipped and go up through the top of the screen
        PURPOSE:        This method initializes fields for a new Pipe instance.
        PRECONDITION:   all parameters are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(x, y, const.PIPE_X, const.PIPE_Y)
        self.top = top
        if top:
            self.img = img_pipe_top
        else:
            self.img = img_pipe_bot

    def draw(self, game_state):
        """
        NAME:           Pipe.draw
        PARAMETERS:     game_state, the game state this entity is a part of
        PURPOSE:        This method draws the respective pipe image to the surface that will be used for the next frame.
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        game_state.surface.blit(self.img, [self.x, self.y])


class PipePair(GameEntity):
    """
    NAME:           PipePair
    PURPOSE:        A game entity linked to two pipes that have the same x position.
    INVARIANTS:     x must not be None and initialized
    """
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
    passed: bool

    def __init__(self, x: int):
        """
        NAME:           PipePair.__init__
        PARAMETERS:     x, the location of the left side of both pipes
        PURPOSE:        This method initializes fields for a new PipePair instance.
        PRECONDITION:   all parameters are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(x, 0)
        self.x = x
        self.top_pipe = Pipe(x, 0, True)
        self.bot_pipe = Pipe(x, 0, False)
        self.change_gap()
        self.passed = False

    def change_gap(self):
        """
        NAME:           PipePair.change_gap
        PARAMETERS:     None
        PURPOSE:        This method updates the y positions of both pipes to create a gap between them
        PRECONDITION:   the pipes have passed the left side of the screen and are no longer visible
        POSTCONDITION:  the pipes have new randomly generated positions which moves
                        them and changes the size of their gap
        """
        # Calculate the gap size
        gap = random.randrange(const.GAP_MIN, const.GAP_MAX)
        # The lowest point the top of the gap can be at to not be too low to show the end of the image
        lowest = const.HEIGHT - const.PIPE_BOT - gap
        # Where the top pipe will reach to
        pipe_loc = random.randrange(const.PIPE_TOP, lowest)

        # Move pipes
        self.top_pipe.y = pipe_loc - const.PIPE_Y
        self.bot_pipe.y = pipe_loc + gap

    def update(self, game_state):
        """
        NAME:           PipePair.update
        PURPOSE:        This method updates the locations of the pipes to move them to the left for their update.
                        If the pipes are off-screen to the left of the bird then they are moved
                        to the right side of the screen and have their gap/position updated.
        PRECONDITION:   The pipes are initialized and not none.
        POSTCONDITION:  The location of the pipes for this instance have been updated.
                        The score counter is incremented if the popes are passed.
                        The pipes are moved to the right side of the screen if they have moved off-screen.
        """
        self.x -= game_state.pipe_speed * game_state.delta

        # # Pipes have passed the bird, increment the pipe counter
        if self.x + const.PIPE_X < game_state.bird.x and not self.passed:
            self.passed = True
            game_state.pipes_passed += 1

        # Pipes moved off-screen, change the gap and move them to the right
        if self.x < const.PIPE_TRASH:
            self.x = const.PIPE_SPAWN
            self.change_gap()
            # We're in front of the bird now
            self.passed = False

        # Set the new x positions of the pipes
        self.top_pipe.x = self.x
        self.bot_pipe.x = self.x


class FloorTile(Rectangle):
    """
    NAME:           FloorTile
    PURPOSE:        A game entity representing a floor section that will kill the bird on contact.
    INVARIANTS:     x must not be None and initialized
    """

    def __init__(self, x: int):
        """
        NAME:           FloorTile.__init__
        PARAMETERS:     x, the location of the left side of this tile
        PURPOSE:        This method initializes fields for a new FloorTile instance.
        PRECONDITION:   all parameters are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(x, const.FLOOR_Y, const.BASE_X, const.BASE_Y)

    def draw(self, game_state):
        """
        NAME:           FloorTile.draw
        PARAMETERS:     game_state, the game state this entity is a part of
        PURPOSE:        This method draws a floor image at the location of this entity to the game surface.
        PRECONDITION:   This instance is a part of the provided game state.
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        game_state.surface.blit(img_base, [self.x, self.y])


class Floor(GameEntity):
    """
    NAME:           Floor
    PURPOSE:        A game entity representing a floor section that will kill the bird on contact.
    INVARIANTS:     x must not be None and initialized
    """
    # A list of all floor tiles used to render the floor
    tiles: list[FloorTile]

    def __init__(self):
        """
        NAME:           Floor.__init__
        PARAMETERS:     None
        PURPOSE:        This method initializes fields for a new Floor instance and creates
                        the needed FloorTile instances.
        PRECONDITION:   the img_base global variable is set
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(0, 0)
        self.tiles = list()

        num_tiles = math.ceil((const.WIDTH + const.BASE_X) / const.BASE_X)
        for i in range(num_tiles):
            self.tiles.append(FloorTile(i * const.BASE_X))

    def update(self, game_state):
        """
        NAME:           Floor.update
        PURPOSE:        This method updates the locations of the FloorTile's to move them to the left for their update.
                        If a tile is off-screen to the left of the bird then it is moved
                        to the right side of the screen.
        PRECONDITION:   None, this can be called at any time. But only one instance should exist.
        POSTCONDITION:  The location of the FloorTiles in this instance have been updated.
                        The tiles are moved to the right side of the screen if they have moved off-screen.
        """
        for tile in self.tiles:
            tile.x -= game_state.pipe_speed * game_state.delta
            # If the tile is off the screen then move it back to the right
            if const.BASE_X + tile.x < 0:
                tile.x += const.BASE_X * len(self.tiles)


class DistanceLine(GameEntity):
    """
    NAME:           DistanceLine
    PURPOSE:        A game entity which draws a line from a referenced entity to the closest rectangle side.
    INVARIANTS:     x must not be None and initialized
    """
    # the entity to start at
    start: Rectangle
    # The distance and location of the closest side
    closest: tuple[float, list[float]]

    def __init__(self, start: Rectangle):
        """
        NAME:           DistanceLine.__init__
        PARAMETERS:     start, the entity which the line will start from and distance is measured from
        PURPOSE:        This method initializes fields for a new DistanceLine instance and creates
                        the needed FloorTile instances.
        PRECONDITION:   the img_base global variable is set
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        # The position of this entity updates every frame
        super().__init__(0, 0)
        self.start = start
        # Initialize to an empty tuple, this will always be updated before a draw
        self.closest = tuple()

    def update(self, game_state):
        """
        NAME:           DistanceLine.update
        PURPOSE:        This method updates the distance and closest surface location for the line to be drawn.
        PRECONDITION:   self.start must be set,
        POSTCONDITION:  The closest field is updated with the distance to the closest side and the intersecting point
        """
        self.closest = get_closest_point(self.start, game_state)

    def draw(self, game_state):
        """
        NAME:           DistanceLine.draw
        PARAMETERS:     game_state, the game state this entity is a part of
        PURPOSE:        This method draws a line from this instances start and to the closest point.
        PRECONDITION:   This instance is a part of the provided game state.
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        # The line will be pink
        pygame.draw.line(game_state.surface, (255, 0, 255), [self.x, self.y], self.closest[1])


class MouseLine(DistanceLine):
    """
    NAME:           MouseLine
    PURPOSE:        A game entity which draws a line from the mouse location to the closest rectangle side.
    INVARIANTS:     A mouse must exist within pygame, this may not work with touch screen devices.
    """
    # A single pixel sized rectangle that is moved to the mouse position each frame
    # This rectangle is not exposed to the game state and is not drawn
    mouse_rect: Rectangle

    def __init__(self):
        """
        NAME:           MouseLine.__init__
        PARAMETERS:     None
        PURPOSE:        This method initializes fields for a new MouseLine instance and creates
                        a new rectangle instance.
        PRECONDITION:   a mouse exists in pygame
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        self.mouse_rect = Rectangle(0, 0, 1, 1)
        super().__init__(self.mouse_rect)

    def update(self, game_state):
        """
        NAME:           MouseLine.update
        PURPOSE:        This method updates the distance and closest surface location for the line to be drawn.
        PRECONDITION:   a mouse must be available in pygame
        POSTCONDITION:  mouse_rect is updated to be at the same location as the mouse and the line is drawn
        """
        # Update the rectangle to the mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_rect.x = mouse_pos[0]
        self.mouse_rect.y = mouse_pos[1]

        # Update the closest point with super class logic
        super().update(game_state)


class PipePassCounter(GameEntity):
    """
    Show the number of pipes passed on the screen
    """
    def __init__(self, x, y):
        super().__init__(x, y)

    def draw(self, game_state):
        """
        Draw the pipes passed to the screen

        :param game_state: the current game state to update from
        :return: None
        """
        passed_str = str(game_state.pipes_passed)
        for index in range(len(passed_str)):
            num = int(passed_str[index])
            pos = [self.x + (index * const.NUM_X), self.y]

            if num == 0:
                game_state.surface.blit(img_num_0, pos)
            elif num == 1:
                game_state.surface.blit(img_num_1, pos)
            elif num == 2:
                game_state.surface.blit(img_num_2, pos)
            elif num == 3:
                game_state.surface.blit(img_num_3, pos)
            elif num == 4:
                game_state.surface.blit(img_num_4, pos)
            elif num == 5:
                game_state.surface.blit(img_num_5, pos)
            elif num == 6:
                game_state.surface.blit(img_num_6, pos)
            elif num == 7:
                game_state.surface.blit(img_num_7, pos)
            elif num == 8:
                game_state.surface.blit(img_num_8, pos)
            elif num == 9:
                game_state.surface.blit(img_num_9, pos)


def add_pipe_pair(entity_list, pipe_list, x):
    new_pair = PipePair(x)
    entity_list.append(new_pair.top_pipe)
    entity_list.append(new_pair.bot_pipe)
    pipe_list.append(new_pair)


class GameState:
    """
    An organized structure of all entities in the game
    """
    surface: pygame.Surface
    # Time change since the last frame was rendered
    delta: float
    # The frame of this game state
    state_frame: int

    birds: list[Bird]
    pipes_passed: int
    entities: list[GameEntity]
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
            self.entities.append(DistanceLine(self.bird))

        self.background = img_background
        self.bg_i = 0

        self.pipe_speed = const.INIT_SPEED

    def init_window(self):
        self.surface = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
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
            self.surface.blit(self.background, (const.WIDTH + self.bg_i, 0))
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
        self.surface.blit(self.background, (self.bg_i, 0))
        self.surface.blit(self.background, (const.WIDTH + self.bg_i, 0))

        for entity in self.entities:
            entity.draw(self)

        for bird in self.birds:
            bird.draw(self)

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


