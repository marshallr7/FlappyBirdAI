# Target Frames Rendered Per Second
FPS = 60
# Window Properties
WIDTH = 600
HEIGHT = 500
FLOOR_Y = HEIGHT - 50
# Monte Carlo Search Tree
MCST_DEPTH = 40
MCST_DELTA = 0.06  # Wait time for each frame/level in seconds
MCST_PREVIEW = 4  # How often to render the bird previews per second
MCST_STEP = int((1 / MCST_DELTA) / MCST_PREVIEW)  # Used to determine when to render bird previews
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
BIRD_DEATH = BIRD_X / 1.9
# The X position of the bird
BIRD_POS_X = 50
# Pipe Speed/Increase
INIT_SPEED = 100
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
GRAVITY = 1600
JUMP_VELOCITY = -300
MAX_VELOCITY = GRAVITY * 30
MIN_VELOCITY = GRAVITY * -50
