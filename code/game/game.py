# Imported modules 
import pygame
import sys
import time
from chicken import Action
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT
from board import Board
from board import LOOKAHEAD, LOOKBEHIND, LOOKLEFT, LOOKRIGHT, NUMFRAMES
from objects import UpdateStatus
from tile import NUM_TILES
from level_config import NUM_LEVELS
from dqn import QAgent
import torch
from plot import plot_results

ACTION_SPACE = [Action.STAY, Action.LEFT, Action.RIGHT, Action.UP, Action.DOWN]
TIMESTEP_LEN = 0  # for easy viewing of agent's actions

# Rewards 
TIMESTEP_REWARD = 0 # reward earned per timestep 
DEATH_REWARD = -500 # reward earned if chicken dies 
TREE_REWARD = 0     # reward earned if chicken runs into tree
FORWARD_REWARD = 5  # reward earned if chicken moves one step closer to finish line
BACKWARD_REWARD = -6 # reward earned if chicken moves one step farther from finish line 
WIN_REWARD = 1000 # reward earned if chicken beats the level 

NUM_CONSECUTIVE_WINS = 5  # number of times agent is required to beat a level IN A ROW before
                          # moving on to the next level 
NUM_RUNS = 5 # number of trials to average in results

# Deep Q Learning specific functionality 
BATCH_SIZE = 128 
MEM_CAP = 10000
UPDATE_RATE = 0.05
EPSILON_HI = 0.2
EPSILON_LO = 0
GAMMA = 0.95
OPTIMIZE_RATE = 1e-4


# Run one iteration, assuming the user is playing the game 
def run_play(board, level, screen):
    won = False
    died = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        keys = pygame.key.get_pressed()

        # set action based on key pressed, ensuring that only one 
        # press is read at a time 
        direction = None
        if keys[pygame.K_UP]:
            direction = Action.UP
        elif keys[pygame.K_LEFT]:
            direction = Action.LEFT
        elif keys[pygame.K_DOWN]:
            direction = Action.DOWN
        elif keys[pygame.K_RIGHT]:
            direction = Action.RIGHT
        elif keys[pygame.K_SPACE]:
            direction = Action.STAY
        else:
            continue

        # Move chicken 
        board.chicken.move(direction)

        # Update environment 
        statuses = board.update_board()

        # check if you w®n 
        if UpdateStatus.DEATH in statuses:
            died = True
        elif UpdateStatus.WIN in statuses:
            print("Congratulations! You beat level " + str(level) + "!")
            won = True

        # Sets display to painted screen
        board.draw_screen(screen)

    board.draw_screen(screen)

    return won, died


# Run one iteration, assuming agent is playing the game
def run_agent(board, level, screen, agent):
    won = False
    died = False

    features = board.extract_features()
    state_tensor = torch.tensor(features).float().unsqueeze(0)
    time.sleep(TIMESTEP_LEN)

    # pick action 
    action_tensor = agent.select_action(state_tensor)
    direction = action_tensor.item()

    prev_y = board.chicken.y

    # Move chicken 
    board.chicken.move(Action(direction))

    # Update environment 
    statuses = board.update_board()

    # Extract reward and update Q
    reward = TIMESTEP_REWARD
    if UpdateStatus.DEATH in statuses:
        reward = DEATH_REWARD
        died = True
        agent.epsilon = EPSILON_HI # turn on exploration if agent dies at all
    elif UpdateStatus.NO_MOVEMENT in statuses:
        reward = TREE_REWARD 
    elif UpdateStatus.WIN in statuses:
        reward = WIN_REWARD
        won = True
        agent.epsilon = EPSILON_LO # turn off exploration if agent wins 
        print("Congratulations! You beat level " + str(level) + "!")

    # Encourage moving forward 
    if board.chicken.y < prev_y:
        reward += FORWARD_REWARD 
    if board.chicken.y > prev_y:
        reward += BACKWARD_REWARD 

    next_features = board.extract_features()
    
    # Convert to tensors
    reward_tensor = torch.tensor([reward], dtype=torch.float)
    next_state_tensor = torch.from_numpy(next_features).float().unsqueeze(0)

    # Store this transition in memory 
    agent.memory.push(state_tensor, action_tensor, next_state_tensor, reward_tensor)

    # Optimize 
    agent.optimize_model()

    # Update weights of target network 
    agent.update_target_weights()

    # Sets display to painted screen
    board.draw_screen(screen)
    return won, died, reward


# Run level
def run_level(level, screen, agent, mini):
    board = Board(level=level, mini=mini)
    board.draw_screen(screen)

    won = False
    died = False
    board.update_board()  # need to update board once before we can successfully get the features

    total_reward = 0
    num_timesteps = 0
    while not won:
        # move chicken
        if agent is None:
            won, _died = run_play(board, level, screen)
        else:
            won, _died, reward = run_agent(board, level, screen, agent)
            total_reward += reward 
        num_timesteps += 1

        died = died or _died

    mean_reward = total_reward / num_timesteps
    # return whether agent died at all this episode 
    return died, mean_reward, num_timesteps 

# run a range of levels 
def run_levels(levels, play, mini):
    pygame.init()

    screen = pygame.display.set_mode([DISPLAY_WIDTH, DISPLAY_HEIGHT])
    pygame.display.set_caption('Crossy Road')

    # initialize agent 
    state_size = NUMFRAMES * (LOOKAHEAD + LOOKBEHIND + 1) * (LOOKLEFT + LOOKRIGHT + 1) * NUM_TILES 
    action_size = len(ACTION_SPACE)
    agent = None 
    if not play:
        agent = QAgent(state_size, action_size, ACTION_SPACE, mem_cap=MEM_CAP, batch_size=BATCH_SIZE, \
                       op_lr=OPTIMIZE_RATE, epsilon=EPSILON_HI, gamma=GAMMA, weight_update_rate=UPDATE_RATE)

    rewards_by_level = list()
    episode_lens_by_level = list()
    num_episodes_by_level = list()
    for level in levels:
        rewards = list()
        episode_lens = list()
        num_episodes = 0
        # Only allowed to proceed to the next level after winning 
        # NUM_CONSECUTIVE_WINS games without dying at all 
        num_consecutive_wins = 0
        while num_consecutive_wins < NUM_CONSECUTIVE_WINS - 1:
            died, reward, episode_len = run_level(level, screen, agent, mini)
            if died:
                num_consecutive_wins = 0
            else:
                num_consecutive_wins += 1
            rewards.append(reward)
            episode_lens.append(episode_len)
            num_episodes += 1

        rewards_by_level.append(rewards)
        episode_lens_by_level.append(episode_lens)
        num_episodes_by_level.append(num_episodes)
    
    pygame.quit()

    return rewards_by_level, episode_lens_by_level, num_episodes_by_level


# Main Script
# Usage if you want agent to play: python3 game.py 
# Usage if you want to play: python3 game.py --play
# Usage if you want to play an easier version: python3 game.py --mini
# Usage if you want to stop at level 4: python3 game.py --num_levels 4
# Usage if you do NOT want curriculum learning: python3 game.py --no_curriculum
def main():
    mini = False 
    play = False
    curriculum = True
    # command line option for having user play the game instead of agent
    if '--play' in sys.argv:
        play = True 
    # command line option for a "mini" version of the game 
    if '--mini' in sys.argv:
        mini = True 
    # command line option for stopping at a certain level before 7 
    num_levels = NUM_LEVELS 
    if '--num_levels' in sys.argv:
        flag_idx = sys.argv.index('--num_levels')
        if flag_idx == len(sys.argv) - 1 or not sys.argv[flag_idx + 1].isnumeric():
            sys.stderr.write('--num_levels needs to be followed by a number\n')
            exit(1)
        num_levels = int(sys.argv[flag_idx + 1])
        if num_levels < 1 or num_levels > NUM_LEVELS:
            sys.stderr.write('num_levels needs to be between 1 and ' + NUM_LEVELS + '\n')
            exit(1)
    # command line option for ditching curriculum learning (begin at last level)
    if '--no_curriculum' in sys.argv:
        curriculum = False

    rewards_by_run = list()
    episode_lens_by_run = list()
    num_episodes_by_run = list()
    start_level = 1 if curriculum else num_levels
    num_runs = 1 if play else NUM_RUNS 
    for i in range(num_runs):
        print(f"Beginning Run {i + 1}")
        rewards, episode_lens, num_episodes = \
            run_levels(range(start_level, num_levels + 1), play, mini)
        rewards_by_run.append(rewards)
        episode_lens_by_run.append(episode_lens)
        num_episodes_by_run.append(num_episodes)

    if not play:
        if curriculum:
            plot_results(rewards_by_run, episode_lens_by_run, num_episodes_by_run, start_level, \
                         'Curriculum Learning Agent', 'curric')
        else:
            plot_results(rewards_by_run, episode_lens_by_run, num_episodes_by_run, start_level, \
                         'Non-Curriculum Learning Agent', 'noncurric')


if __name__ == '__main__':
    main()
