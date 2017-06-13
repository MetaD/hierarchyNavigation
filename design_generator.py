from config import *
import random
import pickle


class ExpDesign:
    def __init__(self, directions, itis):
        if len(directions) != len(itis) or len(directions) != NUM_TRIALS_PER_RUN:
            raise ValueError('Wrong length of design parameters')
        self.trials = zip(directions, itis)

designs = [ExpDesign(directions=[0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
                     itis=[5, 6, 5, 5, 4, 5, 4, 6, 5, 7, 6, 6, 4, 7, 6, 5, 6, 6, 7, 6, 4, 6, 4, 7]),
           ExpDesign(directions=[0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
                     itis=[5, 6, 5, 5, 4, 5, 4, 6, 5, 7, 6, 6, 4, 7, 6, 5, 6, 6, 7, 6, 4, 6, 4, 7]),
           ExpDesign(directions=[0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
                     itis=[5, 6, 5, 5, 4, 5, 4, 6, 5, 7, 6, 6, 4, 7, 6, 5, 6, 6, 7, 6, 4, 6, 4, 7]),
           ExpDesign(directions=[0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
                     itis=[5, 6, 5, 5, 4, 5, 4, 6, 5, 7, 6, 6, 4, 7, 6, 5, 6, 6, 7, 6, 4, 6, 4, 7])]


def generate_trials(filename):
    """
    Run this function to save a list of runs and another list of practice trials to a pickle file
    """
    assert len(designs) == NUM_RUNS
    # generate unique combinations of anchor faces & distances
    up_trials, down_trials = [], []
    practices = []
    for anchor in range(NUM_FACES):
        for dist in range(1, NUM_FACES):
            trial = {'anchor': anchor, 'distance': dist}
            practice = False if (anchor in ANCHOR_INDEXES) and (dist >= MIN_DISTANCE) and (dist <= MAX_DISTANCE) \
                else True
            if practice:
                trial['iti'] = random.randrange(4, 8)
            if anchor - dist >= 0:
                if practice:
                    trial['direction'] = DIRECTIONS[1]  # up
                    practices.append(trial)
                else:
                    up_trials.append(trial)
            if anchor + dist < NUM_FACES:
                if practice:
                    trial['direction'] = DIRECTIONS[0]  # down
                    practices.append(trial)
                else:
                    down_trials.append(trial)
    # copy and shuffle
    up_runs = [list(up_trials) for i in range(NUM_RUNS)]
    down_runs = [list(down_trials) for i in range(NUM_RUNS)]
    for runs in (down_runs, up_runs):
        for run in runs:
            random.shuffle(run)
    # create trials
    trials = []
    for r in range(NUM_RUNS):
        trials.append([])
        for t in range(NUM_TRIALS_PER_RUN):
            direction, iti = designs[r].trials[t]
            param = (down_runs, up_runs)[direction][r].pop()
            trials[r].append({'direction': DIRECTIONS[direction],
                              'iti': iti,
                              'anchor': param['anchor'],
                              'distance': param['distance']})
    print trials
    print practices
    # write to pickle
    with open(filename, 'wb') as outfile:
        pickle.dump(trials, outfile)
        pickle.dump(practices, outfile)

generate_trials(DESIGN_FILENAME)
