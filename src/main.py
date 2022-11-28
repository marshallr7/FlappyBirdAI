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

import pygame
import const

img_pipe_bottom = pygame.image.load("../assets/pipe.png")
img_pipe_top = pygame.transform.flip(img_pipe_bottom, False, True)
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

# List of images used to update score
img_dict = {0: img_num_0, 1: img_num_1, 2: img_num_2, 3: img_num_3, 4: img_num_4, 5: img_num_5, 6: img_num_6,
            7: img_num_7, 8: img_num_8, 9: img_num_9}


def dist_to_rect_side(rectangle_1: "Rectangle", rectangle_2: "Rectangle") -> tuple[float, list[float]]:
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


def get_closest_point(rectangle: "Rectangle", game_state: "GameState") -> tuple[float, list[float]]:
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

    def update(self, game_state: "GameState") -> None:
        """
        NAME:           GameEntity.update
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
        PURPOSE:        This method updates the properties of this instance to be rendered on the next frame.
        PRECONDITION:   This instance is a part of the provided game state
        POSTCONDITION:  This instance is updated and ready to be rendered on the next frame.
        """
        # This is the default behavior, which is to not update since not every entity updates each frame
        pass

    def draw(self, game_state: "GameState", surface: pygame.Surface) -> None:
        """
        NAME:           GameEntity.draw
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
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

    def draw(self, game_state: "GameState", surface: pygame.Surface) -> None:
        """
        NAME:           Rectangle.draw
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
        PURPOSE:        This method draws a red rectangle to the surface that will be used for the next frame.
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        # Draw a red rectangle for simple functionality
        pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.x, self.y, self.size_x, self.size_y))


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
    # Distance to the closest threat and location of the closest point
    threat: tuple[float, list[float]]
    # The fitness of this bird within a generation
    fitness: float

    def __init__(self, y: float):
        """
        NAME:           Bird.__init__
        PARAMETERS:     y coordinate of the top left corner of this entity
        PURPOSE:        This method initializes fields for a new Bird instance.
        PRECONDITION:   all parameters are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(const.BIRD_POS_X, y, const.BIRD_X, const.BIRD_Y)
        self.velocity = 0
        self.dead = False
        self.threat = tuple()
        self.fitness = 0

    def jump(self) -> None:
        """
        NAME:           Bird.jump
        PURPOSE:        This method makes the bird jump from its current position regardless of current velocity.
        PRECONDITION:   None
        POSTCONDITION:  This instance's velocity is set to the jumping velocity
        """
        self.velocity = const.JUMP_VELOCITY

    def update(self, game_state: "GameState") -> None:
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
            self.threat = dist

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

    def draw(self, game_state: "GameState", surface: pygame.Surface) -> None:
        """
        NAME:           Bird.draw
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
        PURPOSE:        This method draws a bird to the surface that will be used for the next frame.
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        surface.blit(img_bird, (self.x, self.y))


class Pipe(Rectangle):
    """
    NAME:           Pipe
    PURPOSE:        A game entity representing a pipe that will kill the bird on contact.
    INVARIANTS:     x and y must not be None and initialized
                    top must be True or False
    """
    img: pygame.Surface
    top: bool

    def __init__(self, x: float, y: float, top: bool):
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
            self.img = img_pipe_bottom

    def draw(self, game_state: "GameState", surface: pygame.Surface) -> None:
        """
        NAME:           Pipe.draw
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
        PURPOSE:        This method draws the respective pipe image to the surface that will be used for the next frame.
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        surface.blit(self.img, [self.x, self.y])


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
    x: float
    # If the bird has passed this set of pipes
    passed: bool

    def __init__(self, x: float):
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

    def change_gap(self) -> None:
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

    def update(self, game_state: "GameState") -> None:
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

        # Pipes have passed the bird, increment the pipe counter
        if self.x + const.PIPE_X < const.BIRD_POS_X and not self.passed:
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

    def __init__(self, x: float):
        """
        NAME:           FloorTile.__init__
        PARAMETERS:     x, the location of the left side of this tile
        PURPOSE:        This method initializes fields for a new FloorTile instance.
        PRECONDITION:   all parameters are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(x, const.FLOOR_Y, const.BASE_X, const.BASE_Y)

    def draw(self, game_state: "GameState", surface: pygame.Surface) -> None:
        """
        NAME:           FloorTile.draw
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
        PURPOSE:        This method draws a floor image at the location of this entity to the game surface.
        PRECONDITION:   This instance is a part of the provided game state.
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        surface.blit(img_base, [self.x, self.y])


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

    def update(self, game_state: "GameState") -> None:
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

    def update(self, game_state: "GameState") -> None:
        """
        NAME:           DistanceLine.update
        PURPOSE:        This method updates the distance and closest surface location for the line to be drawn.
        PRECONDITION:   self.start must be set,
        POSTCONDITION:  The closest field is updated with the distance to the closest side and the intersecting point
        """
        self.closest = get_closest_point(self.start, game_state)

    def draw(self, game_state: "GameState", surface: pygame.Surface) -> None:
        """
        NAME:           DistanceLine.draw
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
        PURPOSE:        This method draws a line from this instances start and to the closest point.
        PRECONDITION:   This instance is a part of the provided game state.
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        # The line will be pink
        pygame.draw.line(surface, (255, 0, 255), [self.x, self.y], self.closest[1])


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

    def update(self, game_state: "GameState") -> None:
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
    NAME:           PipePassCounter
    PURPOSE:        A game entity which displays the number of pipes passed in the game.
    INVARIANTS:     The number of pipes passed is greater than or equal to zero.
    """

    def __init__(self, x: float, y: float):
        """
        NAME:           PipePassCounter.__init__
        PARAMETERS:     x and y are the coordinates of the top left location of where the numbers should appear
        PURPOSE:        This method initializes fields for a new PipePassCounter instance
        PRECONDITION:   There are no other instances of this class present
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(x, y)
        self.game_score: int = 0

    def draw(self, game_state: "GameState", surface: pygame.Surface) -> None:
        """
        NAME:           PipePassCounter.draw
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
        PURPOSE:        This method draws the numbers representing the value of game_state.pipes_passed
        PRECONDITION:   The number of pipes passed is greater than or equal to zero.
        POSTCONDITION:  The surface of game_state will have multiple numbers drawn onto it
        """
        passed_str = str(game_state.pipes_passed)
        for index in range(len(passed_str)):
            num = int(passed_str[index])
            pos = [self.x + (index * const.NUM_X), self.y]

            surface.blit(img_dict[num], pos)


def add_pipe_pair(entity_list: list[GameEntity], pipe_pair_list: list[PipePair], x: float) -> None:
    """
    NAME:           add_pipe_pair
    PARAMETERS:     entity_list, a list of entities related to a game_state for the pipes to be added to
                    pipe_list, a list of pipe pairs to add a new pipe pair instance to
                    x, the x position to create the new pipes at
    PURPOSE:        This method creates a new pipe pair instance and adds the pipes to the provided entity list,
                    and adds the PipePair to the provided pipe list.
    PRECONDITION:   The parameters are initialized.
    POSTCONDITION:  The lists will have new entities appended to them
    """
    new_pair = PipePair(x)
    entity_list.append(new_pair.top_pipe)
    entity_list.append(new_pair.bot_pipe)
    pipe_pair_list.append(new_pair)


class GameState:
    """
    NAME:           GameState
    PURPOSE:        A class which contains all entities and properties of an active game.
                    This can be considered a class which represents the game itself.
                    All driving logic for the game is contained in this class.
    INVARIANTS:     All fields are initialized and not none.
                    Delta and pipes_passed are always positive.
                    Delta cannot be zero.
    """
    # The drawing surface we draw our entities to for each frame
    surface: pygame.Surface
    # Time change since the last frame was rendered
    delta: float

    # The bird being controlled
    bird: Bird
    # The number of pipes the bird has passed
    pipes_passed: int
    # The entities to update and draw on each frame
    entities: list[GameEntity]
    # The pipe pairs in the game
    pipes: list[PipePair]
    # The floor instance
    floor: Floor
    # The background images
    background: pygame.Surface
    # The x location of the background images
    bg_i: int

    # How fast the pipes are moving each frame
    pipe_speed: int

    def __init__(self, debug_entities: bool):
        """
        NAME:           GameState.__init__
        PARAMETERS:     debug, if lines should be drawn from each bird and the mouse to the nearest threat
        PURPOSE:        This method initializes fields for a new PipePassCounter instance
        PRECONDITION:   There are no other instances of this class present
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        self.delta = 0

        self.bird = Bird(const.BIRD_Y)

        self.pipes_passed = 0

        self.entities = list()
        self.pipes = list()

        # Spawn pipes with their set distances, need to include trash distance for consistency.
        # This method means that if the window width changes then the pipe distance does as well.
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

        # Add a DistanceLine for each bird and the mouse if we are debugging
        if debug_entities:
            self.entities.append(MouseLine())
            self.entities.append(DistanceLine(self.bird))

        # Set up the background
        self.background = img_background
        self.bg_i = 0

        self.pipe_speed = const.INIT_SPEED

    def do_update(self) -> None:
        """
        NAME:           GameState.do_update
        PARAMETERS:     None
        PURPOSE:        This method updates all game entities each frame before they are drawn.
        PRECONDITION:   The previous frame has been drawn, and the delta has been updated with the previous frame time.
        POSTCONDITION:  All entities have been updated and are ready to be drawn to the next frame.
        """
        # Update the background
        if self.bg_i == -const.WIDTH:
            self.bg_i = 0
        self.bg_i -= 1

        # Update the floor
        self.floor.update(self)

        # Update all pipe pairs
        for pipe_pair in self.pipes:
            pipe_pair.update(self)

        # Update all entities
        for entity in self.entities:
            entity.update(self)

        # Update the bird
        self.bird.update(self)

    def do_draw(self, surface: pygame.Surface) -> None:
        """
        NAME:           GameState.do_draw
        PARAMETERS:     surface, the surface of the window to draw to
        PURPOSE:        This method draws all game entities to the next frame
        PRECONDITION:   All entities have been updated for the frame we're about to draw.
        POSTCONDITION:  All entities are drawn to the next frame.
        """
        # Draw the background
        surface.blit(self.background, (self.bg_i, 0))
        surface.blit(self.background, (const.WIDTH + self.bg_i, 0))

        # Draw each entity
        for entity in self.entities:
            entity.draw(self, surface)

        # Always draw the bird on top
        self.bird.draw(self, surface)

    @staticmethod
    def do_event() -> None:
        """
        NAME:           GameState.do_event
        PARAMETERS:     None
        PURPOSE:        This method processes all events each frame, events are mostly from the user.
        PRECONDITION:   The frame has not been updated or drawn yet.
        POSTCONDITION:  All relevant logic has been executed for each event.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()


if __name__ == "__main__":
    # Parse arguments for if we want debugging features
    debug = bool(sys.argv[1]) if (len(sys.argv) > 1) else False

    # Set up the window to draw to
    window_surface = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
    pygame.display.set_caption("Flappy Bird AI")

    current_game_state: GameState

    clock = pygame.time.Clock()
    # The last time a frame was rendered, used to calculate frame time
    last_frame = time.time()

    while True:
        # Create a new game state
        current_game_state = GameState(debug)

        # Execute game state logic forever
        while not current_game_state.bird.dead:
            # Limit the frame rate, this needs to be called every frame
            clock.tick(const.FPS)

            # Calculate the time since the last frame
            # pygame.clock.get_fps() averages the last 10 frames
            # pygame.clock.get_time() returns an int in ms, no decimal. 16 instead if 16.6777
            next_frame = time.time()
            current_game_state.delta = next_frame - last_frame
            last_frame = next_frame

            # Update the game state
            current_game_state.do_event()
            current_game_state.do_update()

            # Draw the next frame
            current_game_state.do_draw(window_surface)
            # Display the next frame
            pygame.display.update()
