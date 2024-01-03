import pygame
import sys
from config import TILE_WIDTH, TILE_HEIGHT, BOARD_WIDTH, BOARD_HEIGHT
from enum import Enum

# Source of image:
# Chicken: https://sketchfab.com/3d-models/chicken-crossy-road-71ff83cf547048cf8b3b4775f9df45fb
IMG_PATH = 'images/cr_chicken.jpeg'


class Action(Enum):
    STAY = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4 


class Chicken:
    def __init__(self, start_x, start_y):
        self.last_move = None
        self.x = start_x
        self.y = start_y

        self.orig_x = start_x 
        self.orig_y = start_y 

        self.img = pygame.image.load(IMG_PATH)
    
    def move(self, direction):
        if direction == Action.LEFT:
            if self.x > 0:  # move left
                self.x -= 1
        elif direction == Action.RIGHT:
            if self.x < BOARD_WIDTH - 1:
                self.x += 1
        elif direction == Action.UP:
            if self.y > 0:
                self.y -= 1
        elif direction == Action.DOWN:
            if self.y < BOARD_HEIGHT - 1:
                self.y += 1

        self.last_move = direction 
    
    # CANNOT be called two consecutive times without a move in-between 
    def undo_move(self):
        # Error checking 
        if self.last_move == None:
            sys.stderr.write("ERROR: Chicken cannot undo two consecutive times.\n")
            exit(1)
        
        direction = None 
        if self.last_move == Action.LEFT:
            direction = Action.RIGHT 
        elif self.last_move == Action.RIGHT:
            direction = Action.LEFT 
        elif self.last_move == Action.UP:
            direction = Action.DOWN 
        elif self.last_move == Action.DOWN:
            direction = Action.UP 
        
        self.move(direction)

    def reset(self): # call after chicken dies to reset position 
        self.last_move = None 
        self.x = self.orig_x 
        self.y = self.orig_y 

    def draw(self, screen):
        self.img = pygame.transform.scale(self.img, (TILE_WIDTH, TILE_HEIGHT))

        # Place chicken in designated location on screen
        screen.blit(self.img, (self.x * TILE_WIDTH, self.y * TILE_HEIGHT))
