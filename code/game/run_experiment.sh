#! /bin/sh 

# Clear file
rm plots/num_episodes.txt

# Run experiment with curriculum learning 
python3 game.py --mini
# Run experiment without curriculum learning
python3 game.py --mini --no_curriculum

# Generate bar plot of number of episodes
python3 plot_num_episodes.py
