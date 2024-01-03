import pygame
import sys
from enum import Enum
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, TILE_WIDTH, TILE_HEIGHT, BOARD_WIDTH, BOARD_HEIGHT
from paint import paint_tile_screen
from tile import Tile

class ObjectType(Enum):
    DEATHZONE = 0
    TREE = 1
    CAR = 2
    LILYPAD = 3
    LOG = 4
    TRACKWARNING = 5  # TRACKWARNING and TRAIN really are one object, but separating them
    TRAIN = 6  # because the images to render are different in those cases
    WINZONE = 7


# Global map: type of object to image file
# Sources of images used:
# Car: https://www.hqturbo.com/en/
# Lilypad: https://www.dreamstime.com/illustration/lily-pad-icon.html
# Log: https://www.clipartkey.com/view/ToJRii_log-png-clipart-tree-log-clipart-png/
# Red: https://aesthetics.fandom.com/wiki/Category:Red
# Track: https://www.vecteezy.com/free-vector/train-tracks
# Train: https://www.istockphoto.com/illustrations/freight-train
# Tree: https://www.clker.com/clipart-green-tree-21.html
OBJECT_FILE_PATHS = {
    ObjectType.DEATHZONE: 'images/red.jpg',
    ObjectType.TREE: 'images/tree.png',
    ObjectType.CAR: 'images/car.png',
    ObjectType.LILYPAD: 'images/lilypad.jpg',
    ObjectType.LOG: 'images/log.png',
    ObjectType.TRACKWARNING: 'images/track_warning.png',
    ObjectType.TRAIN: 'images/train.jpg'
    # no associated image for WINZONE 
}


CAR_LENGTH = 2
LOG_LENGTH = 3
TRAIN_SAFE_TIME = 5
TRAIN_WARN_TIME = 2
TRAIN_DEATH_TIME = 3

class UpdateStatus(Enum):
    SUCCESS = 0,  # indicates update was successful, nothing weird happened (should probably correspond to -1 reward)
    DEATH = 1,  # indicates chicken died, probably correspond to some large negative reward
    WIN = 2,  # indicates chicken beat the game, end episode
    NO_MOVEMENT = 3  # indicates chicken didn't move


class WinZone:  # when chicken reaches finish line
    def __init__(self, y):  # y should almost always be 0 (top row of grid)
        self.y = y

    def draw(self, screen):
        pass

    def update_env(self, tiles, chicken):
        if chicken.y == self.y:
            return UpdateStatus.WIN
        return UpdateStatus.SUCCESS

    def reset(self):
        pass


# A single death zone object represents the ENTIRE death zone at the
# bottom of the screen, growing by a certain number of coordinates every 
# certain number of time steps 
class DeathZone:
    def __init__(self, growth_rate):
        self.y = BOARD_HEIGHT
        self.growth_rate = growth_rate  # number of time steps before death zone grows by one row
        self.counter = growth_rate  # number of time steps UNTIL the next growth

        self.img = pygame.image.load(OBJECT_FILE_PATHS[ObjectType.DEATHZONE])
        # will be scaled before drawing because size depends on a variety of factors 

    def draw(self, screen):
        img = pygame.transform.scale(self.img, (DISPLAY_WIDTH, (BOARD_HEIGHT - self.y) * TILE_HEIGHT))
        screen.blit(img, (0, self.y * TILE_HEIGHT))

    def update_env(self, tiles, chicken):  # returns an update status
        # Update size of death zone if timestep is multiple of `self.growth_rate`
        self.counter -= 1
        if self.counter == 0:
            self.y -= 1

            self.counter = self.growth_rate

        # Update tiles 
        for i in range(self.y, BOARD_HEIGHT):
            tiles[:, i] = [Tile.DEATH] * BOARD_WIDTH  

        if chicken.y >= self.y:  # if chicken is in death zone
            return UpdateStatus.DEATH

        return UpdateStatus.SUCCESS

    def reset(self):  # reset of chicken dies
        self.y = BOARD_HEIGHT
        self.counter = self.growth_rate


class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.img = pygame.image.load(OBJECT_FILE_PATHS[ObjectType.TREE])
        self.img = pygame.transform.scale(self.img, (TILE_WIDTH, TILE_HEIGHT))

    def draw(self, screen):
        screen.blit(self.img, (self.x * TILE_WIDTH, self.y * TILE_HEIGHT))

    def update_env(self, tiles, chicken):
        # A bit redundant, but probably the cleanest given the current framework 
        tiles[self.x][self.y] = Tile.TREE

        if chicken.x == self.x and chicken.y == self.y:  # if chicken tried to run into a tree
            chicken.undo_move()
            return UpdateStatus.NO_MOVEMENT
        return UpdateStatus.SUCCESS

    def reset(self):
        pass


class Car:
    def __init__(self, start_x, y, vel, mov_rate):
        self.start_x = start_x
        self.x1 = start_x
        self.x2 = self.x1 + CAR_LENGTH 
        self.y = y

        # vel / rate is the number of tiles moved per time step 
        # positive vel = move right, negative vel = move left
        self.vel = vel  # num tiles moved every time the car moves
        self.mov_rate = mov_rate  # number of time steps per movement
        self.mov_counter = mov_rate

        # Examples of above (for clarity) 
        # A car moving 2 tiles per time step to the left would have vel = -2, mov_rate = 1
        # A car moving 1 tile every 2 time steps to the right would have vel = 1, mov_rate = 2

        self.img = pygame.image.load(OBJECT_FILE_PATHS[ObjectType.CAR])
        self.img = pygame.transform.scale(self.img, (TILE_WIDTH * CAR_LENGTH, TILE_HEIGHT))

    def draw(self, screen):
        screen.blit(self.img, (self.x1 * TILE_WIDTH, self.y * TILE_HEIGHT))

    def update_env(self, tiles, chicken):
        # clear car from tiles
        for i in range(self.x1, self.x2):
            if 0 <= i < BOARD_WIDTH: # ensure that i is in range
                tiles[i][self.y] = Tile.ROAD 
        
        # move car
        self.mov_counter -= 1
        if self.mov_counter == 0:
            self.x1 = self.x1 + self.vel
            self.x2 = self.x1 + CAR_LENGTH 

            self.mov_counter = self.mov_rate

        # wrap around if out of bounds 
        self.x2 = self.x2 % (BOARD_WIDTH + CAR_LENGTH) # clamp to range of 0 to BOARD_WIDTH + LOG_LENGTH - 1
        self.x1 = self.x2 - CAR_LENGTH

        # update tiles to reflect car's new position 
        for i in range(self.x1, self.x2):
            if 0 <= i < BOARD_WIDTH:
                tiles[i][self.y] = Tile.CAR

        # kill chicken if chicken impacts car
        if chicken.y == self.y and (self.x1 <= chicken.x < self.x2):
            return UpdateStatus.DEATH

        return UpdateStatus.SUCCESS

    def reset(self):
        self.x1 = self.start_x


class Lilypad:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.img = pygame.image.load(OBJECT_FILE_PATHS[ObjectType.LILYPAD])
        self.img = pygame.transform.scale(self.img, (TILE_WIDTH, TILE_HEIGHT))

    def draw(self, screen):
        screen.blit(self.img, (self.x * TILE_WIDTH, self.y * TILE_HEIGHT))

    def update_env(self, tiles, chicken):
        # again, a little needless recomputation but I think cleanest given current framework 
        tiles[self.x][self.y] = Tile.LILYPAD 

        return UpdateStatus.SUCCESS 

    def reset(self):
        pass


class Log:
    def __init__(self, start_x, y, vel, mov_rate):
        self.start_x = start_x
        self.x1 = start_x
        self.x2 = start_x + LOG_LENGTH
        self.y = y

        self.vel = vel  # num tiles moved every time the car moves
        self.mov_rate = mov_rate  # number of time steps per movement
        self.mov_counter = mov_rate 

        self.img = pygame.image.load(OBJECT_FILE_PATHS[ObjectType.LOG])
        self.img = pygame.transform.scale(self.img, (TILE_WIDTH * LOG_LENGTH, TILE_HEIGHT))

    def draw(self, screen):
        screen.blit(self.img, (self.x1 * TILE_WIDTH, self.y * TILE_HEIGHT))

    def update_env(self, tiles, chicken):
        # clear log from tiles
        for i in range(self.x1, self.x2):
            if 0 <= i < BOARD_WIDTH: # ensure that i is in range
                tiles[i][self.y] = Tile.WATER 
        
        # move log
        self.mov_counter -= 1
        if self.mov_counter == 0:
            # move chicken if on log 
            # TODO: fix the bug which the chicken is not on the log but it is still bumped
            if chicken.y == self.y and (self.x1 <= chicken.x < self.x2):
                chicken.x += self.vel 

            self.mov_counter = self.mov_rate
            self.x1 += self.vel
            self.x2 = self.x1 + LOG_LENGTH

        
        # wrap around if out of bounds 
        self.x2 = self.x2 % (BOARD_WIDTH + LOG_LENGTH) # clamp to range of 0 to BOARD_WIDTH + LOG_LENGTH - 1
        self.x1 = self.x2 - LOG_LENGTH 

        # update tiles to reflect new log position 
        for i in range(self.x1, self.x2):
            if 0 <= i < BOARD_WIDTH:
                tiles[i][self.y] = Tile.LOG 

        # kill chicken if out of bounds 
        if chicken.x < 0 or BOARD_WIDTH <= chicken.x: 
            return UpdateStatus.DEATH 

        return UpdateStatus.SUCCESS

    def reset(self):
        self.x1 = self.start_x
        self.x2 = self.x1 + LOG_LENGTH


class Train:  # Train will always appear and disappear in the same pattern
    def __init__(self, y, start_counter):
        self.y = y 

        self.img = pygame.image.load(OBJECT_FILE_PATHS[ObjectType.TRAIN])
        self.img = pygame.transform.scale(self.img, (DISPLAY_WIDTH, TILE_HEIGHT))
        self.warn_img = pygame.image.load(OBJECT_FILE_PATHS[ObjectType.TRACKWARNING])
        self.warn_img = pygame.transform.scale(self.warn_img, (DISPLAY_WIDTH, TILE_HEIGHT))

        self.cycle_len = TRAIN_SAFE_TIME + TRAIN_WARN_TIME + TRAIN_DEATH_TIME 
        self.start_counter = start_counter % self.cycle_len 
        self.counter = self.start_counter

    def __is_safe(self):
        return self.counter % self.cycle_len < TRAIN_SAFE_TIME 
    
    def __is_warn(self):
        return 0 <= (self.counter - TRAIN_SAFE_TIME) % self.cycle_len < TRAIN_WARN_TIME 
    
    def __is_death(self):
        return 0 <= (self.counter - TRAIN_SAFE_TIME - TRAIN_WARN_TIME) % self.cycle_len < TRAIN_DEATH_TIME 

    def draw(self, screen):
        if self.__is_safe():
            pass # don't draw anything if track is empty 
        elif self.__is_warn():
            screen.blit(self.warn_img, (0, self.y * TILE_HEIGHT))
        elif self.__is_death():
            screen.blit(self.img, (0, self.y * TILE_HEIGHT))
        else:
            sys.stderr.write("IMPOSSIBLE ERROR: Train is in neither the 'safe', 'warning', nor 'death' state.\n")
            exit(1)

    def update_env(self, tiles, chicken):
        self.counter += 1

        tile = None 
        if self.__is_safe():
            tile = Tile.TRACK 
        elif self.__is_warn():
            tile = Tile.TRACK_WARNING 
        elif self.__is_death():
            tile = Tile.TRAIN 
        
        for i in range(BOARD_WIDTH):
            tiles[i][self.y] = tile 
        
        # kill chicken if is death 
        if self.__is_death() and self.y == chicken.y:
            return UpdateStatus.DEATH 
        
        return UpdateStatus.SUCCESS 

    def reset(self):
        self.counter = self.start_counter
