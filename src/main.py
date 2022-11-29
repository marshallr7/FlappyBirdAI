"""
AUTHOR:           Hunter Hageman, Marshall Patterson
FILENAME:         main.py
SPECIFICATION:    Create an Artificial Intelligence capable of playing Flappy Bird.
FOR:              CS 3368 Introduction to Artificial Intelligence Section 001
"""

import math
import random
import sys
import copy
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

# Dictionary of entity types and their surfaces to draw
surface_dict = {
    'rectangle': None,  # Rectangle draws a primitive shape, doesn't have a surface
    'pipe_top': img_pipe_top,
    'pipe_bottom': img_pipe_bottom,
    'bird': img_bird,
    'base': img_base
}

# The current frame being rendered
frame_id: int


# ###################################
# #############[ Start ]#############
# ##### Monte Carlo Search Tree #####
# ###################################
# ###################################


class MCST_Node:
    # The game state that belongs to this node
    game_state: "GameState"

    # If this node has created its child nodes before, used to prevent researching and infinite recursion
    populated: bool

    # This nodes parent node, None if root
    parent: "MCST_Node"
    # The future game state if the bird falls, null when explored/unpopulated
    left_node: "MCST_Node"
    # The future game state if the bird jumps, null when explored/unpopulated
    right_node: "MCST_Node"

    def __init__(self, parent: "MCST_Node", game_state: "GameState"):
        self.game_state = game_state
        self.populated = False
        self.parent = parent
        self.left_node = None
        self.right_node = None

    def _populate_children(self):
        """
        Create child nodes for this node
        :return:
        """
        self.populated = True

        # Clone the states and make the right state jump
        left_state = copy.deepcopy(self.game_state)
        right_state = copy.deepcopy(self.game_state)
        right_state.bird.jump()
        # Update the states
        left_state.do_update()
        right_state.do_update()

        # Set left and right nodes if the bird isn't dead, dead bird will always be a terminal node
        if not left_state.bird.dead:
            self.left_node = MCST_Node(self, left_state)
        else:
            self.left_node = None

        if not right_state.bird.dead:
            self.right_node = MCST_Node(self, right_state)
        else:
            self.right_node = None

    def get_best_child(self) -> "MCST_Node":
        if not self.populated:
            self._populate_children()

        if self.left_node is not None and self.right_node is not None:
            left_better = self.left_node.get_score() > self.right_node.get_score()
            return self.left_node if left_better else self.right_node
        elif self.left_node is None and self.right_node is not None:
            return self.right_node
        elif self.left_node is not None and self.right_node is None:
            return self.left_node

    def get_score(self) -> float:
        """
        :return: the threat distance of the bird
        """
        return self.game_state.bird.threat[0]

    def is_terminal(self):
        """
        :return: true if the node has no children (bird is dead)
        """
        return self.left_node is None and self.right_node is None

    def remove_child(self, child: "MCST_Node"):
        if self.left_node == child:
            self.left_node = None
        elif self.right_node == child:
            self.right_node = None
        else:
            raise Exception("Neither child matched!")

    def disintegrate(self):
        """
        Destroy all references this node has, all references of child nodes,
        and the reference the parent has to this node.
        :return: None
        """
        if self.left_node is not None:
            self.left_node.disintegrate()

        if self.right_node is not None:
            self.right_node.disintegrate()


class MCST:
    # The root node
    root: MCST_Node
    # The ending node
    tail: MCST_Node
    # Ordered list of nodes from the root node to the best ending node
    path: list[MCST_Node]
    # The current frame ID
    frame_id: int
    # The max depth of the search tree (frame lookahead)
    frame_limit: int

    def __init__(self, game_state: "GameState"):
        game_state.delta = const.MCST_DELTA
        self.root = MCST_Node(None, game_state)
        self.tail = self.root
        self.path = list()
        self.path.append(self.root)
        self.frame_id = 0
        self.frame_limit = const.MCST_DEPTH

    def _climb(self):
        """
        Climb up a node from the tail until there is a node with a non-terminal child
        :return:
        """
        if not self.tail.is_terminal():
            raise Exception("Back propagating when tail isn't terminal!")

        parent = self.tail.parent
        self.tail.disintegrate()
        self.path.pop()
        parent.remove_child(self.tail)
        self.tail = parent

        # Keep climbing up until we find an unexplored path
        if parent.is_terminal():
            self._climb()

    def search(self):
        """
        Search for the best path from the current tail
        :return:
        """
        global frame_id

        # Loop until we find a good route that leads to the frame limit
        # This expands and searches as it goes
        while self.frame_id + self.frame_limit > self.frame_id + len(self.path):
            print(len(self.path))
            # Case #1, continuing down the tree
            next_node = self.tail.get_best_child()
            if not self.tail.is_terminal():
                if next_node is not None:
                    # Add the node to the path and continue
                    self.path.append(next_node)
                    self.tail = next_node
                    continue

            # Case #2, node is terminal, climb and let the next loop search
            self._climb()

    def proceed(self):
        """
        advance the root to the next node in the path and disintegrate the old root
        :return: the new root's game state
        """
        new_root = self.path[1]
        self.path.pop(0)
        self.root.remove_child(new_root)
        self.root.disintegrate()
        self.root = new_root
        return self.root.game_state


# ###################################
# ###################################
# ##### Monte Carlo Search Tree #####
# ##############[ End ]##############
# ###################################


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
        POSTCONDITION:  The surface will have this entity drawn onto it
        """
        # Error, this should be implemented for drawn entities, or not called if the entity doesn't draw itself
        assert False


class PositionEntity(GameEntity):
    """
    NAME:           PositionEntity
    PURPOSE:        An abstract class which has no references to objects that cannot be deep-copied.
                    Removing such references is required for deep-copy to work, but also optimizes memory usage.
                    Provides default behavior to render the specified entity_type at the provided location
    INVARIANTS:     x and y must be greater than zero
                    entity_type must match a key value in the surface_dict dictionary
    """
    def __init__(self, entity_type: str, x: float, y: float):
        """
        NAME:           PositionEntity.__init__
        PARAMETERS:     x and y coordinates of the location of this entity
                        entity_type, a value within
        PURPOSE:        This method initializes fields for a new PositionEntity instance.
        PRECONDITION:   entity_type, x, and y are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(x, y)
        self.entity_type = entity_type

        if entity_type not in surface_dict:
            assert f"entity_type '{entity_type}' doesn't exist!"

    def draw(self, game_state: "GameState", surface: pygame.Surface) -> None:
        """
        NAME:           PositionEntity.draw
        PARAMETERS:     game_state, the game state this entity is a part of
                        surface, the window surface to draw to
        PURPOSE:        This method loads the proper pygame.Surface according to the set self.entity_type
                        and draws that entity_type with the x/y position being the top left of the surface.
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface will have this entity drawn onto it
        """
        surface.blit(surface_dict[self.entity_type], (self.x, self.y))


class Rectangle(PositionEntity):
    """
    NAME:           Rectangle
    PURPOSE:        A game entity with a rectangular shape.
    INVARIANTS:     size_x and size_y must be greater than 0, not None, and initialized.
    """
    size_x: float
    size_y: float

    def __init__(self, entity_type, x, y, size_x, size_y):
        """
        NAME:           Rectangle.__init__
        PARAMETERS:     entity_type is the type of entity this is, used by subclasses.
                            Should be 'rectangle' when instantiated directly.
                        x and y coordinates of the location of this entity
                        size_x and size_y are the width and height of this entity
        PURPOSE:        This method initializes fields for a new Rectangle instance.
        PRECONDITION:   all parameters are not none and are initialized.
        POSTCONDITION:  This instance's fields are initialized to the provided parameters.
        """
        super().__init__(entity_type, x, y)
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
        PURPOSE:        If a rectangle type:
                            This method draws a red rectangle to the surface that will be used for the next frame.
                        If any other type:
                            Ths method calls the superclass logic to draw the respective entity
        PRECONDITION:   This instance is a part of the provided game state,
        POSTCONDITION:  The surface of game_state will have this entity drawn onto it
        """
        if self.entity_type == 'rectangle':
            # Draw a red rectangle for simple functionality
            pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.x, self.y, self.size_x, self.size_y))
        else:
            super().draw(game_state, surface)


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
        super().__init__('bird', const.BIRD_POS_X, y, const.BIRD_X, const.BIRD_Y)
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


class Pipe(Rectangle):
    """
    NAME:           Pipe
    PURPOSE:        A game entity representing a pipe that will kill the bird on contact.
    INVARIANTS:     x and y must not be None and initialized
                    top must be True or False
    """
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
        super().__init__('pipe_top' if top else 'pipe_bottom', x, y, const.PIPE_X, const.PIPE_Y)
        self.top = top


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
        super().__init__('base', x, const.FLOOR_Y, const.BASE_X, const.BASE_Y)


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
        pygame.draw.line(surface, (255, 0, 255), self.start.get_center_pos(), self.closest[1])


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
        self.mouse_rect = Rectangle('rectangle', 0, 0, 1, 1)
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
                    All dlineriving logic for the game is contained in this class.
    INVARIANTS:     All fields are initialized and not none.
                    Delta and pipes_passed are always positive.
                    Delta cannot be zero.
    """
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
            # Outstanding bug where pygame is not updating the mouse position
            # self.entities.append(MouseLine())
            self.entities.append(DistanceLine(self.bird))

        # Set up the background
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
        surface.blit(img_background, (self.bg_i, 0))
        surface.blit(img_background, (const.WIDTH + self.bg_i, 0))

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
    frame_id = 0
    window_surface = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
    pygame.display.set_caption("Flappy Bird AI")

    # ########## Test Code for deep copy
    #
    # # Store in a linear list to test memory usage
    # gameStates = list[GameState]()
    #
    # # Create initial game state
    # gameStates.append(GameState(False))  # 1
    # # Establish frame times, this doesn't account
    # gameStates[0].delta = 0.008
    #
    # # Eat memory as a test, proceed linearly
    # for i in range(0, 1000000):
    #     # Deep copy a new state based on the last state and update
    #     new_state = copy.deepcopy(gameStates[i])
    #     new_state.do_update()
    #     # Wait to draw the next frame
    #     time.sleep(0.008)
    #     # Draw the current state
    #     new_state.do_draw(window_surface)
    #     pygame.display.update()
    #     # Put the new state at the end of the list for the next loop
    #     gameStates.append(new_state)
    #
    # # Force early exit as we're just testing deep copy
    # sys.exit(0)
    #
    # ########## Resume normal game run logic

    ########## Test code for MCST

    # Allow deeper recursions, fix would be to limit the depth in each search call on each frame
    sys.setrecursionlimit(1000000)

    mcst = MCST(GameState(debug))

    # path will always start with a length of 1
    while len(mcst.path) > 0:
        frame_id += 1
        mcst.search()
        next_game_state = mcst.proceed()
        next_game_state.do_update()
        next_game_state.do_draw(window_surface)

        if debug:
            # Extremely hacky here, override the bird x pos to be "in the future", draw it, and set it back
            indexes = list(range(const.MCST_STEP, len(mcst.path), const.MCST_STEP))
            indexes.append(len(mcst.path) - 1)  # Manually append the last part of the path
            for i in indexes:
                mcst.path[i].game_state.bird.x += next_game_state.pipe_speed * next_game_state.delta * i
                # The bird draw method in specific doesn't need the game state
                mcst.path[i].game_state.bird.draw(None, window_surface)
                mcst.path[i].game_state.bird.x = const.BIRD_POS_X

        pygame.display.update()
        time.sleep(const.MCST_DELTA)

    exit(0)

    ########## Resume normal game run logic

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
            # this returns seconds with a decimal, such as 0.016 being 16ms
            next_frame = time.time()
            current_game_state.delta = next_frame - last_frame
            print(current_game_state.delta)
            last_frame = next_frame

            # Update the game state
            current_game_state.do_event()
            current_game_state.do_update()

            # Draw the next frame
            current_game_state.do_draw(window_surface)
            # Display the next frame
            pygame.display.update()
