#!/usr/bin/env python

from utilities import *
from config import *


def show_one_trial(param):
    # 0) face
    presenter.draw_stimuli_for_duration(images[param['anchor']], FACE_TIME)
    # 1) fixation
    presenter.show_fixation(random.choice(FIXATION_TIME))
    # 2) number
    num_stim = visual.TextStim(presenter.window, str(param['distance']), height=1, color=DIR_COLORS[param['direction']])
    presenter.draw_stimuli_for_duration(num_stim, NUMBER_TIME)
    # 3) blank (mental navigation)
    presenter.draw_stimuli_for_duration(visual.TextStim(presenter.window, ''), BLANK_TIME)
    # 4) options
    return {}


def show_one_run():
    pass


def generate_trials():
    # generate unique combinations
    trial_list = []
    for anchor in ANCHOR_INDEXES:
        for dist in range(MIN_DISTANCE, NUM_FACES - MIN_DISTANCE):
            if anchor - dist >= 0:
                trial_list.append({
                    'anchor': anchor,
                    'direction': DIRECTIONS[0],
                    'distance': dist
                })
            if anchor + dist < NUM_FACES:
                trial_list.append({
                    'anchor': anchor,
                    'direction': DIRECTIONS[1],
                    'distance': dist
                })
    trial_list *= NUM_TRIALS_PER_CONDITION
    random.shuffle(trial_list)
    # numbers
    num_runs = len(trial_list) / NUM_TRIALS_PER_RUN
    num_trials_per_anc_per_run = NUM_TRIALS_PER_RUN / len(ANCHOR_INDEXES)
    num_trials_per_dir_per_run = NUM_TRIALS_PER_RUN / len(DIRECTIONS)
    anchor_counter = [{anchor: 0 for anchor in ANCHOR_INDEXES} for i in range(num_runs)]
    direc_counter = [{direc: 0 for direc in DIRECTIONS} for i in range(num_runs)]
    trials = [[] for i in range(num_runs)]  # a list of runs
    # append trials to runs
    j = len(trial_list) - 1  # iterate from back to front
    while j >= 0:
        trial = trial_list[j]
        for i in range(num_runs):
            if anchor_counter[i][trial['anchor']] < num_trials_per_anc_per_run and \
                            direc_counter[i][trial['direction']] < num_trials_per_dir_per_run:  # and \
                            # trial not in trials[i]:  # TODO repetition!!!!!!!!
                trials[i].append(trial_list.pop(j))
                anchor_counter[i][trial['anchor']] += 1
                direc_counter[i][trial['direction']] += 1
                break
        j -= 1
    print trials
    return trials


def validation(items):
    # check empty field
    for key in items.keys():
        if items[key] is None or len(items[key]) == 0:
            return False, str(key) + ' cannot be empty.'
    # check age
    try:
        if int(items['Age']) <= 0:
            raise ValueError
    except ValueError:
        return False, 'Age must be a positive integer'
    # everything is okay
    return True, ''


if __name__ == '__main__':
    # subject ID dialog
    sinfo = {'ID': '', 'Gender': ['Female', 'Male'], 'Age': '', 'Mode': ['Test', 'Exp']}
    show_form_dialog(sinfo, validation, order=['ID', 'Gender', 'Age', 'Mode'])
    sid = int(sinfo['ID'])
    img_prefix = sinfo['Gender'][0]

    # create data file
    dataLogger = DataHandler(DATA_FOLDER, str(sid) + '.dat')
    # save info from the dialog box
    dataLogger.write_data({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # create window
    presenter = Presenter(fullscreen=(sinfo['Mode'] == 'Exp'))
    dataLogger.write_data(presenter.expInfo)
    # load images
    images = presenter.load_all_images(IMG_FOLDER, '.jpg', img_prefix)
    highlight = visual.ImageStim(presenter.window, image=IMG_FOLDER + 'highlight.png')
    # randomize colors
    DIR_COLORS = {DIRECTIONS[0]: DIR_COLORS[0], DIRECTIONS[1]: DIR_COLORS[1]} if random.randrange(2) == 0 else \
                 {DIRECTIONS[0]: DIR_COLORS[1], DIRECTIONS[1]: DIR_COLORS[0]}
    # randomize trials TODO
    trials = generate_trials()
    # randomize images
    random.seed(sid)
    random.shuffle(images)  # status high -> low
    dataLogger.write_data({i: stim._imName for i, stim in enumerate(images)})

    # show trials
    presenter.show_instructions(INSTR_0)
    for run in trials:
        # switch colors
        DIR_COLORS = {DIRECTIONS[0]: DIR_COLORS[DIRECTIONS[1]], DIRECTIONS[1]: DIR_COLORS[DIRECTIONS[0]]}
        # instructions
        presenter.show_instructions('run #' + str(run) + '\n' + str(DIR_COLORS))
        # start run
        for trial in run:
            data = show_one_trial(trial)
            trial['response'] = data
            dataLogger.write_data(trial)
    presenter.show_instructions(INSTR_END)
