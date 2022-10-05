# Target Frames Rendered Per Second
FPS = 60
# Window Properties
WIDTH = 600
HEIGHT = 800
# Size of pipe image
PIPE_X = 52
PIPE_Y = 320
# Size of the bird image
BIRD_X = 32
BIRD_Y = 24
# Pipe Speed/Increase
INIT_SPEED = 100
GAIN_SPEED = 1
# Pipe gap Min/Max distance from screen bounds
PIPE_MIN = 200
PIPE_MAX = 320
# Where pipes are relocated to
PIPE_SPAWN = WIDTH
# Where pipes must be moved from
PIPE_TRASH = -1 * PIPE_X
# Bird Bounds
BIRD_MIN_Y = 50
BIRD_MAX_Y = 705
# Bird Physics
# Remember that y=0 is the top of the screen
GRAVITY = 800
JUMP_VELOCITY = -400
MAX_VELOCITY = GRAVITY * 30
MIN_VELOCITY = GRAVITY * -50
