import pygame
import numpy as np
import random
import sys
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, TILE_WIDTH, TILE_HEIGHT, BOARD_WIDTH, BOARD_HEIGHT
from config import DEATHZONE_GROWTHRATE
from paint import paint_tiles
from chicken import Chicken
from terrain import Terrain, TerrainType
from objects import DeathZone, Tree, Car, Lilypad, Log, Train, WinZone
from objects import UpdateStatus
from objects import CAR_LENGTH, LOG_LENGTH 
from tile import Tile, NUM_TILES
from level_config import get_level_config
from copy import deepcopy 

TERRAIN_DEFAULTTILE_MAP = {
    TerrainType.GRASS: Tile.GRASS,
    TerrainType.TRAIN: Tile.TRACK,
    TerrainType.RIVER: Tile.WATER,
    TerrainType.ROAD: Tile.ROAD,
    TerrainType.FINISH: Tile.FINISH
}

LOOKAHEAD = 4
LOOKBEHIND= 2
LOOKLEFT = BOARD_WIDTH // 2
LOOKRIGHT = BOARD_WIDTH // 2
NUMFRAMES = 4

class Board:
    def __init__(self, level, mini=False):
        self.chicken = Chicken(BOARD_WIDTH // 2, BOARD_HEIGHT - 1)
        self.config = get_level_config(level, mini)
        self.terrain, self.river_indices, self.road_indices, self.train_indices = self.__init_terrain()  # description of each row
        self.objects = self.__init_objects()  # description of each "thing" on the grid

        # Error checking 
        if len(self.terrain) != BOARD_HEIGHT:
            sys.stderr.write("ERROR: terrain list inputted to Board is incompatible with board height\n")
            exit(1)
        if self.objects and not isinstance(self.objects[-1], DeathZone):
            sys.stderr.write("ERROR: Object list inputted to Board must have a DeathZone as its last element\n")
            exit(1)
        if not any([isinstance(_object, WinZone) for _object in self.objects]):
            sys.stderr.write("ERROR: Object list inputted to Board must contain a WinZone\n")
            exit(1)

        # list keyed by number of frames ago to look 
        self.tiles = [self.__init_tiles() for _ in range(NUMFRAMES)]

    def __init_terrain(self):
        # Initialize terrains (just an example for now)
        terrain = [Terrain(TerrainType.GRASS, y) for y in range(BOARD_HEIGHT)]
        # invariant: top row MUST be FINISH terrain type (to indicate finish line)
        terrain[0] = Terrain(TerrainType.FINISH, 0)

        num_rivers = random.choice(self.config["num_rivers"])
        num_roads = random.choice(self.config["num_roads"])
        num_trains = random.choice(self.config["num_trains"])
        terrain_ys = random.sample(range(1, BOARD_HEIGHT - 2), num_rivers + num_roads + num_trains)
        river_indices = terrain_ys[:num_rivers]
        road_indices = terrain_ys[num_rivers:num_rivers + num_roads]
        train_indices = terrain_ys[num_rivers + num_roads:]

        # Disallow two consecutive river indices 
        river_indices.sort()
        for i in range(1, len(river_indices)):
            if river_indices[i] - river_indices[i - 1] == 1: # upon discovery of two consecutive rivers, remove
                                                             # the second one
                river_indices[i] = -2 # sentinel value for "invalid", in preparation for removal 
        river_indices = list(filter(lambda x : x >= 0, river_indices))

        # Assign to the terrain array
        for i in road_indices:
            terrain[i] = Terrain(TerrainType.ROAD, i)

        for i in river_indices:
            terrain[i] = Terrain(TerrainType.RIVER, i)

        for i in train_indices:
            terrain[i] = Terrain(TerrainType.TRAIN, i)

        return terrain, river_indices, road_indices, train_indices

    def __init_objects(self):
        # Initialize objects (again, just an example for now)
        objects = [WinZone(0)]

        # Initialize objects based on terrain
        prev_row_tree_columns = set()
        prev_row_lily_columns = set()

        for y in range(1, BOARD_HEIGHT - 2):  # Avoiding the first row and last two rows
            terrain_type = self.terrain[y].ttype
            current_row_tree_columns = set()
            current_row_lily_columns = set()

            if terrain_type == TerrainType.GRASS:
                if random.choice([True, False]):  # Randomly decide to put trees or not
                    num_trees = random.choice(self.config["num_trees_per_row"])

                    for _ in range(num_trees):
                        # Avoid columns with lily pads in adjacent rows and already placed trees in the same row
                        available_columns = [x for x in range(BOARD_WIDTH) if
                                             x not in prev_row_lily_columns and x not in current_row_tree_columns]
                        if available_columns:
                            tree_x = random.choice(available_columns)
                            objects.append(Tree(tree_x, y))
                            current_row_tree_columns.add(tree_x)

            elif terrain_type == TerrainType.RIVER:
                if random.choice(self.config["river_is_lilypad"]):  # Randomly decide between lilypad and log
                    num_lilypads = random.choice(self.config["num_lilys_per_row"])

                    for _ in range(num_lilypads):
                        # Avoid columns with trees in adjacent rows and already placed lilypads in the same row
                        available_columns = [x for x in range(BOARD_WIDTH) if
                                             x not in prev_row_tree_columns and x not in current_row_lily_columns]
                        if available_columns:
                            lily_x = random.choice(available_columns)
                            objects.append(Lilypad(lily_x, y))
                            current_row_lily_columns.add(lily_x)
                else:
                    num_logs_per_row = random.choice(self.config["num_logs_per_row"])
                    log_vel = random.choice(self.config["log_vels"])
                    log_mov_rate = random.choice(self.config["log_mov_rates"])
                    unavailable_log_xs = [] # logic to ensure no two logs are "on top of each other"
                    for _ in range(num_logs_per_row):
                        log_x = random.randint(0, BOARD_WIDTH - 1) 
                        while log_x in unavailable_log_xs:
                            log_x = random.randint(0, BOARD_WIDTH - 1)
                        unavailable_log_xs.extend(range(log_x - LOG_LENGTH, log_x + LOG_LENGTH))
                        objects.append(Log(log_x, y, log_vel, log_mov_rate))  # Define velocity and move rate

            elif terrain_type == TerrainType.ROAD:
                num_cars_per_row = random.choice(self.config["num_cars_per_row"])
                car_vel = random.choice(self.config["car_vels"])
                car_mov_rate = random.choice(self.config["car_mov_rates"])
                unavailable_car_xs = [] # logic to ensure no two cars are "on top of each other"
                for _ in range(num_cars_per_row):
                    x = random.randint(0, BOARD_WIDTH - 1)
                    while x in unavailable_car_xs:
                        x = random.randint(0, BOARD_WIDTH - 1)
                    unavailable_car_xs.extend(range(x - CAR_LENGTH, x + CAR_LENGTH))
                    objects.append(Car(x, y, car_vel, car_mov_rate))

            elif terrain_type == TerrainType.TRAIN:
                # Initialize train objects
                objects.append(Train(y, random.randint(0, 100)))

            prev_row_tree_columns = current_row_tree_columns
            prev_row_lily_columns = current_row_lily_columns

        objects.append(DeathZone(DEATHZONE_GROWTHRATE))

        return objects

    def __init_tiles(self):  # initialize tiles based on terrain ONLY (does not initialize objects)
        tiles = np.full((BOARD_WIDTH, BOARD_HEIGHT), None)

        for i in range(BOARD_HEIGHT):
            tiles[:, i] = [TERRAIN_DEFAULTTILE_MAP[self.terrain[i].ttype]] * BOARD_WIDTH
        # tiles updates tiles based on object locations in update_board(), when object.update_env() is called

        return tiles

    def extract_features(self):
        tile_vector_shape = (NUMFRAMES, LOOKLEFT + LOOKRIGHT + 1, LOOKBEHIND + LOOKAHEAD + 1)
        bit_vector_shape = (NUMFRAMES, LOOKLEFT + LOOKRIGHT + 1, LOOKBEHIND + LOOKAHEAD + 1, NUM_TILES)

        tile_vector = np.empty(tile_vector_shape, dtype=Tile)
        for frame in range(NUMFRAMES): # 0 = current frame, 1 = one frame ago, 2 = two frames ago, etc. 
            for i, x in enumerate(range(self.chicken.x - LOOKLEFT, self.chicken.x + LOOKRIGHT + 1)):
                for j, y in enumerate(range(self.chicken.y - LOOKBEHIND, self.chicken.y + LOOKAHEAD + 1)):
                    if x < 0 or x >= BOARD_WIDTH or y < 0:
                        tile_vector[frame][i][j] = Tile.OOB 
                    elif y >= BOARD_HEIGHT:
                        tile_vector[frame][i][j] = Tile.DEATH 
                    else:
                        tile_vector[frame][i][j] = self.tiles[frame][x][y]
        
        # Convert array of enums to array of bit arrays 
        bit_vector = np.empty(bit_vector_shape, dtype=int)
        for frame in range(NUMFRAMES):
            for i in range(len(tile_vector[frame])):
                for j in range(len(tile_vector[frame][i])):
                    bit_vector[frame][i][j] = self.__tile_to_bit_arr(tile_vector[frame][i][j])

        return np.ravel(bit_vector)

    def __tile_to_bit_arr(self, tile):
        arr = [0] * NUM_TILES 
        arr[tile.value] = 1
        return arr 

    def update_board(self):
        statuses = []  # hold update statuses, can later be used to compute reward in actual learning process
        died = False

        for i in range(NUMFRAMES - 1, 1, -1):
            self.tiles[i] = self.tiles[i - 1] 
        if NUMFRAMES > 1:
            self.tiles[1] = deepcopy(self.tiles[0])

        for _object in self.objects:
            status = _object.update_env(self.tiles[0], self.chicken)
            statuses.append(status)

            if status == UpdateStatus.DEATH:
                died = True

        # river kill (check tiles)
        if died != True and self.tiles[0][self.chicken.x][self.chicken.y] == Tile.WATER:
            died = True
            statuses.append(UpdateStatus.DEATH)
        else:
            statuses.append(UpdateStatus.SUCCESS)

        # Reset all objects if chicken died
        if died:
            for _object in self.objects:
                _object.reset()
            self.chicken.reset()

        return statuses

    def draw_screen(self, screen):
        # Draw each terrain first 
        for terrain in self.terrain:
            terrain.draw(screen)

        for _object in self.objects:
            _object.draw(screen)

        # Draw the tiles
        paint_tiles(screen, DISPLAY_WIDTH, DISPLAY_HEIGHT, TILE_WIDTH, TILE_HEIGHT)

        # Draw chicken
        self.chicken.draw(screen)

        # Update the display
        pygame.display.flip()
