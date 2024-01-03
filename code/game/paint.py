import pygame
import sys


def paint_tiles(screen, scr_width, scr_height, tile_width, tile_height):
    if scr_width % tile_width != 0:
        sys.stderr.write('ERROR: screen width is not divisible by tile width\n')
        exit(1)
    if scr_height % tile_height != 0:
        sys.stderr.write('ERROR: screen height is not divisible by tile height\n')
        exit(1)

    # Paints black border around each tile
    for x in range(0, scr_width, tile_width):
        for y in range(0, scr_height, tile_height):
            paint_tile(screen, x, x + tile_width, y, y + tile_height)

    # Sets display to painted screen
    pygame.display.flip()


def paint_tile_screen(screen, scr_width, scr_height, tile_width, tile_height):
    # Initializes screen to white tiles
    screen.fill('white')

    # Paints the tiles on top of white screen 
    paint_tiles(screen, scr_width, scr_height, tile_width, tile_height)


def paint_tile(screen, x_start, x_end, y_start, y_end):
    # Paint top and bottom edges of tile
    for x in range(x_start, x_end):
        screen.set_at((x, y_start), 'black')
        screen.set_at((x, y_end - 1), 'black')

    # Paint left and right edges of tile
    for y in range(y_start, y_end):
        screen.set_at((x_start, y), 'black')
        screen.set_at((x_end - 1, y), 'black')
