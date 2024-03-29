# Global variables

import math 
import sys 

DISPLAY_WIDTH = 500
DISPLAY_HEIGHT = 500

if '--mini' in sys.argv:
    DISPLAY_WIDTH = 250
    DISPLAY_HEIGHT = 250 

TILE_WIDTH = 25
TILE_HEIGHT = 25

BOARD_WIDTH = DISPLAY_WIDTH // TILE_WIDTH
BOARD_HEIGHT = DISPLAY_HEIGHT // TILE_HEIGHT

DEATHZONE_GROWTHRATE = math.ceil(BOARD_WIDTH / 2)

