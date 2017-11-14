import operator
from config import *
import random
import pickle
import os

DIR = 'neurodesign/'
DESIGN_IDS = [subdir[6:] for subdir in sorted(os.listdir(DIR)) if subdir.startswith('design')]
NUM_STIMULI = 2
STIMULUS_DURATION = 11.0
PRE_STIM_TIME = 2.0
LAST_ITI = 4


class ExpDesign:
    def __init__(self, stim_order, itis):
        if len(stim_order) != len(itis) or len(stim_order) != NUM_TRIALS_PER_RUN:
            raise ValueError('Wrong length of design parameters')
        self.trials = zip(stim_order, itis)

    def __str__(self):
        return str(self.trials)


def get_order(stimuli_onset_lists):
    # stimuli_onset_lists: a list of lists of stimuli onsets
    order, onsets = [], []
    indexes = [0 for _ in range(len(stimuli_onset_lists))]
    current_onsets = [stimuli_onset_lists[stim_i][0] for stim_i in range(len(stimuli_onset_lists))]
    for onset_list in stimuli_onset_lists:
        onset_list.append(float('inf'))
    while True:
        stim_i, min_onset = min(enumerate(current_onsets), key=operator.itemgetter(1))
        if min_onset == float('inf'):
            return order, onsets
        order.append(stim_i)
        onsets.append(min_onset)
        indexes[stim_i] += 1
        current_onsets[stim_i] = stimuli_onset_lists[stim_i][indexes[stim_i]]


def check_iti(onsets, itis):
    # TODO this is temporary and supposed to be wrong if neurodesign gives correct output...
    assert(len(onsets) == len(itis))
    assert(itis[0] == 0)
    for i in range(len(onsets) - 1):
        assert(onsets[i] + STIMULUS_DURATION + itis[i + 1] == onsets[i + 1])
    # print('ITIs match stimuli onsets.')


def generate_trials(filename):
    """
    Run this function to save a list of runs and another list of practice trials to a pickle file
    """
    assert len(designs) >= NUM_RUNS
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
                trial['answer_index'] = random.randrange(4)
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
    # randomize answer indexes TODO WRONG
    answer_indexes = [[i for i in range(4) for _ in range(NUM_TRIALS_PER_RUN/4)] for _ in range(NUM_RUNS)]
    for run in answer_indexes:
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
                              'distance': param['distance'],
                              'answer_index': answer_indexes[r][t]})
    print trials
    print practices
    # write to pickle
    with open(filename, 'w') as outfile:
        pickle.dump(trials, outfile)
        pickle.dump(practices, outfile)


if __name__ == '__main__':
    designs = []
    nav_onsets = []
    face_onsets = []
    for des in DESIGN_IDS:
        folder = DIR + 'design' + des + '/'
        file_names = ['stimulus_{}.txt'.format(i) for i in range(NUM_STIMULI)] + ['ITIs.txt']
        design = {}
        for i, filename in enumerate(file_names):
            with open(folder + filename, 'r') as iti_file:
                design[file_names[i][:-4]] = [float(time) for time in iti_file.read().split('\n') if len(time) > 1]

        stim_order, all_onsets = get_order([design[k[:-4]] for k in file_names[:-1]])
        check_iti(all_onsets, design['ITIs'])
        # put the zero ITI at the back rather than front, and convert time to integer
        design['ITIs'] = [int(i) for i in design['ITIs'][1:]]
        design['ITIs'].append(LAST_ITI)

        designs.append(ExpDesign(stim_order=stim_order, itis=design['ITIs']))
        print des
        print stim_order

        # real stimulus onsets
        stim_onsets = [[] for _ in range(NUM_STIMULI)]
        face_onsets.append([[] for _ in range(NUM_STIMULI)])
        nav_onsets.append([[] for _ in range(NUM_STIMULI)])
        time = 0.0
        for i in range(len(stim_order)):
            stim_onsets[stim_order[i]].append(str(time + PRE_STIM_TIME))
            # onset time files
            face_onsets[-1][stim_order[i]].append(str(int(time)))
            nav_onsets[-1][stim_order[i]].append(str(int(time + PRE_STIM_TIME)))
            time += STIMULUS_DURATION + float(design['ITIs'][i])

        # txt for AFNI
        # for i in range(NUM_STIMULI):
        #     with open(folder + 'real_stimulus_{}.txt'.format(i), 'w') as outfile:
        #         outfile.write('\n'.join(stim_onsets[i]))

    # more txt for AFNI
    for stim in range(NUM_STIMULI):
        with open(DIR + 'face_onsets_%d.txt' % stim, 'w') as outfile:
            for run in face_onsets:
                outfile.write(' '.join(run[stim]))
                outfile.write('\n')
        with open(DIR + 'nav_onsets_%d.txt' % stim, 'w') as outfile:
            for run in nav_onsets:
                outfile.write(' '.join(run[stim]))
                outfile.write('\n')

    # generate_trials(DESIGN_FILENAME)
