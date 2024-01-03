import matplotlib.pyplot as plt
import sys 
import numpy as np 
import os
from plot_num_episodes import NEPISODES_FILE_PATH 

def get_plot_info(qty):
    # qty = 3D list: run, level, episode 
    if len(qty) < 1 or len(qty[0]) < 1 or len(qty[0][0]) < 1:
        sys.stderr.write('ERROR: Dimensions of `qty` list must all be greater than 0.\n')
        exit(1)

    num_runs = len(qty)
    num_levels = len(qty[0])
    avg_by_level = list()
    stdev_by_level = list()
    for level in range(num_levels):
        avg_by_episode = list()
        stdev_by_episode = list()

        max_episode_len = max([len(qty[run][level]) for run in range(num_runs)])
        for episode_no in range(max_episode_len):
            avg, stdev = get_info_across_runs(qty, level, episode_no)
            avg_by_episode.append(avg)
            stdev_by_episode.append(stdev)
        
        avg_by_level.append(avg_by_episode)
        stdev_by_level.append(stdev_by_episode)
    
    return avg_by_level, stdev_by_level 

def get_info_across_runs(qty, level, episode_no):
    num_runs = len(qty)
    qty_by_run = list()
    for run in range(num_runs):
        try:
            qty_by_run.append(qty[run][level][episode_no])
        except:
            pass # if out of bounds, then did not reach this episode_no in this 
                 # run. Simply ignore those numbers 
    
    return np.average(qty_by_run), np.std(qty_by_run)

def plot_rewards(rewards, start_level, agent_label, file_prefix):
    num_levels = len(rewards[0])
    avg_reward_by_level, stdev_reward_by_level = get_plot_info(rewards)

    for i in range(num_levels):
        level = i + start_level 
    
        avg_reward = np.array(avg_reward_by_level[i])
        stdev_reward = np.array(stdev_reward_by_level[i])
        num_episodes = len(avg_reward)
        episode_nos = range(1, num_episodes + 1)

        plt.title(f"Average Reward Earned per Episode Across Runs \nfor {agent_label} Agent on Level {level}")
        plt.xlabel("Episode Number")
        plt.ylabel("Total Reward During Episode")
        plt.plot(episode_nos, avg_reward, color="black")
        plt.fill_between(episode_nos, avg_reward, avg_reward + stdev_reward, color="lightsteelblue")
        plt.fill_between(episode_nos, avg_reward - stdev_reward, avg_reward, color="lightsteelblue")
        plt.savefig(f"plots/{file_prefix}_reward_level{level}.png")
        plt.clf()

def plot_episode_lens(eplens, start_level, agent_label, file_prefix):
    num_levels = len(eplens[0])
    avg_eplen_by_level, stdev_eplen_by_level = get_plot_info(eplens)

    for i in range(num_levels):
        level = i + start_level 
    
        avg_eplen = np.array(avg_eplen_by_level[i])
        stdev_eplen = np.array(stdev_eplen_by_level[i])
        num_episodes = len(avg_eplen)
        episode_nos = range(1, num_episodes + 1)

        plt.title(f"Average Episode Length Across Runs \nfor {agent_label} Agent on Level {level}")
        plt.xlabel("Episode Number")
        plt.ylabel("Length of Episode")
        plt.plot(episode_nos, avg_eplen, color="black")
        plt.fill_between(episode_nos, avg_eplen, avg_eplen + stdev_eplen, color="lightsteelblue")
        plt.fill_between(episode_nos, avg_eplen - stdev_eplen, avg_eplen, color="lightsteelblue")
        plt.savefig(f"plots/{file_prefix}_eplen_level{level}.png")
        plt.clf()

def save_num_episodes(num_episodes, start_level, agent_label):
    if len(num_episodes) < 1 or len(num_episodes[0]) < 1:
        sys.stderr.write('ERROR: Dimensions of `num_episodes` list must all be greater than 0.\n')
        exit(1)
    
    # Generate header if file doesn't exist yet 
    if not os.path.isfile(NEPISODES_FILE_PATH):
        with open(NEPISODES_FILE_PATH, 'w') as file:
            file.write('Category\tNumber of Episodes\n')

    num_runs = len(num_episodes)
    num_levels = len(num_episodes[0])
    for i in range(num_levels):
        level = start_level + i 
        with open(NEPISODES_FILE_PATH, 'a') as file:
            for run in range(num_runs):
                file.write(f'{agent_label}, Level {level}\t{num_episodes[run][i]}\n')

# generate plots 
# 
def plot_results(rewards, episode_lens, num_episodes, start_level, agent_label, file_prefix):
    # Plot rewards earned and episode lengths 
    plot_rewards(rewards, start_level, agent_label, file_prefix)
    plot_episode_lens(episode_lens, start_level, agent_label, file_prefix)
    save_num_episodes(num_episodes, start_level, agent_label)
