import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

NEPISODES_FILE_PATH = 'plots/num_episodes.txt'

def main():
    df = pd.read_csv(NEPISODES_FILE_PATH, delimiter='\t')
    
    data_dict = dict()
    for i in range(len(df)):
        row = df.iloc[i]
        category = row['Category']
        value = row['Number of Episodes']

        if category not in data_dict:
            data_dict[category] = list()
        data_dict[category].append(value)
    
    bars = list(data_dict.keys())

    avgs = [np.average(data_dict[bar]) for bar in bars]
    stdevs = [np.std(data_dict[bar]) for bar in bars]
    bar_xs = range(0, len(bars))

    # Print out average episode length for each category 
    for i in range(len(bars)):
        print(f'Average Number of Episodes for {bars[i]}: {avgs[i]}')
    
    # This code was written with the help of Matplotlib's tutorial on bar 
    # plots: https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_label_demo.html
    _, ax = plt.subplots()
    ax.bar(bars, avgs)
    ax.set(ylabel='Average Number of Episodes', \
           title='Average Number of Episodes Across Runs by Agent and Level')
    ax.errorbar(bar_xs, avgs, yerr=stdevs, color='r', capsize=5, linestyle='None')
    ax.get_xaxis().set_visible(False)
    ax.set(xlabel='Agent-Level Combination (see caption)')
    plt.savefig('plots/num_episodes.png')
    plt.clf()

if __name__ == '__main__':
    main()
