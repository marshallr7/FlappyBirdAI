# Target Frames Rendered Per Second
FPS = 60
# Window Properties
WIDTH = 600
HEIGHT = 500
FLOOR_Y = HEIGHT - 50
# Size of the numbers
NUM_X = 24
NUM_Y = 36
# Size of floor image
BASE_X = 336
BASE_Y = 112
# Size of pipe image
PIPE_X = 52
PIPE_Y = 320
# Size of the bird image
BIRD_X = 32
BIRD_Y = 24
# The distance from an object in which the bird dies
BIRD_DEATH = BIRD_Y / 2
# Pipe Speed/Increase
INIT_SPEED = 100
GAIN_SPEED = 1
# Pipe gap Min/Max distance from screen bounds
PIPE_TOP = 25
PIPE_BOT = 75
# Size Bounds for pipe gap size
GAP_MIN = 125
GAP_MAX = 250
# Where pipes are relocated to
PIPE_SPAWN = WIDTH
# Where pipes must be moved from
PIPE_TRASH = -1 * PIPE_X
# Bird Bounds
BIRD_MIN_Y = 25
BIRD_MAX_Y = FLOOR_Y
# Bird Physics
# Remember that y=0 is the top of the screen
GRAVITY = 800
JUMP_VELOCITY = -400
MAX_VELOCITY = GRAVITY * 30
MIN_VELOCITY = GRAVITY * -50
