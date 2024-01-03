from enum import Enum

class Tile(Enum):
    # grass tiles
    GRASS = 0
    TREE = 1
    # road tiles
    ROAD = 2
    CAR = 3
    # river
    WATER = 4
    LILYPAD = 5
    LOG = 6
    # train
    TRACK = 7
    TRACK_WARNING = 8
    TRAIN = 9
    # finish line 
    FINISH = 10
    # death zone 
    DEATH = 11
    # out of bounds 
    OOB = 12

NUM_TILES = 13
