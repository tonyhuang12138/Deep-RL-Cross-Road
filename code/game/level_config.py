import sys
import copy

DEFAULT_CONFIG = {
    "num_rivers" : [2, 3, 4],
    "num_roads" : [4, 5, 6],
    "num_trains" : [2, 3, 4],
    "num_trees_per_row" : [1, 2, 3, 4, 5],
    "num_lilys_per_row" : [4, 5, 6],
    "num_logs_per_row" : [3, 4],
    "num_cars_per_row" : [2],
    "car_vels" : [-2, -1, 1, 2],
    "car_mov_rates" : [1],
    "log_vels" : [-1, 1],
    "log_mov_rates" : [1],
    "river_is_lilypad" : [False, True] # whether river holds logs or lilypads 
}

MINI_CONFIG = {
    "num_rivers" : [1, 2],
    "num_roads" : [1, 2],
    "num_trains" : [1, 2],
    "num_trees_per_row" : [2, 3],
    "num_lilys_per_row" : [3, 4, 5],
    "num_logs_per_row" : [2],
    "num_cars_per_row" : [1, 2],
    "car_vels" : [-2, -1, 1, 2],
    "car_mov_rates" : [1],
    "log_vels" : [-1, 1],
    "log_mov_rates" : [1],
    "river_is_lilypad" : [False, True] # whether river holds logs or lilypads 
}

# 1 = no obstacles
# 2 = trees only 
# 3 = slow cars only 
# 4 = slow + fast cars only 
# 5 = trees + cars 
# 6 = lilys only (larger amount of them) 
# 7 = lilys only
# 8 = lilys + trees 
# 9 = lilys + trees + cars
# 10 = logs only 
# 11 = logs + lilys 
# 12 = logs + lilys + trees 
# 13 = logs + lilys + trees + cars
# 14 = trains only 
# 15 = trains + trees 
# 16 = trains + trees + cars 
# 17 = trains + trees + cars + logs + lilys 
NUM_LEVELS = 17

def get_level_config(level, mini=False):
    if level < 1 or level > NUM_LEVELS:
        sys.stderr.write("IMPOSSIBLE ERROR: Requested level out of range\n")
        exit(1)
    
    config = copy.deepcopy(DEFAULT_CONFIG)  
    if mini:
        config = copy.deepcopy(MINI_CONFIG)
    
    if level < 2 or level in [3, 4, 6, 7, 10, 11, 14]:
        config["num_trees_per_row"] = [0]
    if level < 3 or level in [6, 7, 8, 10, 11, 12, 14, 15]:
        config["num_roads"] = [0]
    if level < 4:
        config["car_vels"] = [-1, 1]
    if level < 6 or level in [14, 15, 16]:
        config["num_rivers"] = [0]
    if level == 6 and not mini:
        config["num_lilys_per_row"] = [10, 11, 12]
    if level < 10:
        config["river_is_lilypad"] = [True]
    if level == 10:
        config["river_is_lilypad"] = [False]
    if level < 14:
        config["num_trains"] = [0]
    return config
