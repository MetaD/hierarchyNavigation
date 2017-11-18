from config import *
import random
import pickle
import os

NUM_STIMULI = 2
STIMULUS_DURATION = 11.0
PRE_STIM_TIME = 2.0
LAST_ITI = 4

with open(DESIGN_FILENAME, 'r') as infile:
    trials = pickle.load(infile)
    practices = pickle.load(infile)

answer_indexes = [[[i for i in range(4) for _ in range(NUM_TRIALS_PER_RUN/4/NUM_STIMULI)]
                    for _ in range(NUM_STIMULI)]
                   for _ in range(NUM_RUNS)]  # 3D list, 6 x 2 x 12

for run in answer_indexes:
    for stim in run:
        random.shuffle(stim)

for i, run in enumerate(trials):
    counters = [0 for _ in range(NUM_STIMULI)]
    for trial in run:
        direction = DIRECTIONS.index(trial['direction'])
        trial['answer_index'] = answer_indexes[i][direction][counters[direction]]
        counters[direction] += 1

with open('fixed_' + DESIGN_FILENAME, 'w') as outfile:
    pickle.dump(trials, outfile)
    pickle.dump(practices, outfile)
