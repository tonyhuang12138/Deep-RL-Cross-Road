import pygame
from config import DISPLAY_WIDTH, TILE_WIDTH, TILE_HEIGHT, BOARD_WIDTH
from enum import Enum


# Specifies a certain type of terrain (corresponding to a row on the grid)
class TerrainType(Enum):
    GRASS = 0
    TRAIN = 1
    RIVER = 2
    ROAD = 3
    FINISH = 4


# Global map: type of terrain to image file
# Sources of images used:
# Finish Line: https://www.shutterstock.com/image-vector/finish-line-seamless-pattern-clipart-image-1927049099
# Grass: https://www.vecteezy.com/free-photos/pixel-grass
# Road: https://www.etsy.com/il-en/listing/1121488685/road-elements-road-clipart-highway
# Track: https://www.vecteezy.com/free-vector/train-tracks
# Water: https://www.mypoolrx.com/about-us
TERRAIN_FILE_PATHS = {
    TerrainType.GRASS: 'images/grass.jpg',
    TerrainType.TRAIN: 'images/track.jpg',
    TerrainType.RIVER: 'images/water.jpg',
    TerrainType.ROAD: 'images/road.jpg',
    TerrainType.FINISH: 'images/finish.jpg'
}


class Terrain:
    def __init__(self, ttype, y):
        self.ttype = ttype  # terrain type
        self.y = y

        # each image takes up one tile of the grid, EXCEPT for train, which takes 
        # up an entire row 
        self.width = TILE_WIDTH
        if self.__is_full_row():
            self.width = DISPLAY_WIDTH
        self.height = TILE_HEIGHT

        self.img = pygame.image.load(TERRAIN_FILE_PATHS[ttype])
        self.img = pygame.transform.scale(self.img, (self.width, self.height))

    def __is_full_row(self):
        return self.ttype == TerrainType.TRAIN or self.ttype == TerrainType.FINISH

    def draw(self, screen):
        if self.__is_full_row():
            screen.blit(self.img, (0, self.y * TILE_HEIGHT))
        else:
            for x in range(BOARD_WIDTH):
                screen.blit(self.img, (x * TILE_WIDTH, self.y * TILE_HEIGHT))
