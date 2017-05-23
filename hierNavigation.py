#!/usr/bin/env python

from psychopy_util import *
from config import *
import copy


def show_one_trial(param, question=False):
    """
    # 0 anchor face
    presenter.draw_stimuli_for_duration(images[param['anchor']], FACE_TIME)
    # 1 fixation
    presenter.show_fixation(FIXATION_TIME)
    # 2 number
    num_stim = visual.TextStim(presenter.window, str(param['distance']), height=1, color=DIR_COLORS[param['direction']])
    presenter.draw_stimuli_for_duration(num_stim, NUMBER_TIME)
    # 3 fixation (mental navigation)
    presenter.show_fixation(BLANK_TIME)
    """
    # 3.5 question
    if question:
        anchors = [visual.ImageStim(presenter.window, images[param['anchor']]._imName) for i in range(4)]
        if param['distance'] == 2:
            for i, pos in enumerate(two_step_anchor_pos):
                anchors[i].pos = pos
                anchors[i].size = q_img_size
            stims = two_step_stim + anchors
        else:
            stims = three_step_stim + anchors
        response = presenter.select_from_stimuli(stims, ('down', 'up', 'left', 'right', 'none'), question_keys,
                                                 feedback_time=0)
        param['visualization'] = response
    # 4.0 options
    correct_option = param['anchor'] + param['distance'] if param['direction'] == DIRECTIONS[0] else \
                     param['anchor'] - param['distance']
    options = [correct_option]
    # 4.1 randomly pick 3 other adjacent images
    abs_dist = 1  # absolute value of distance
    while len(optgions) < NUM_OPTIONS:
        dist_candidates = [-abs_dist, abs_dist]
        while len(dist_candidates) > 0:
            dist = random.choice(dist_candidates)
            dist_candidates.remove(dist)
            option = correct_option + dist
            if (option not in options) and (option >= 0) and (option < len(images)) and (option != param['anchor']):
                options.append(option)
            if len(options) == NUM_OPTIONS:
                break
        abs_dist += 1
    random.shuffle(options)
    option_stims = [images[index] for index in options]
    for option, position in zip(option_stims, img_positions):
        option.pos = position
    # 5.0 feedback
    correct_feedback = visual.TextStim(presenter.window, FEEDBACK_RIGHT, height=0.2)
    correct_bg = visual.Rect(presenter.window, width=2.1, height=2.1, fillColor=GREEN)
    incorrect_feedback = visual.TextStim(presenter.window, FEEDBACK_WRONG, height=0.2, color=BLACK)
    incorrect_bg = visual.Rect(presenter.window, width=2.1, height=2.1, fillColor=RED)
    resp_feedback = ([incorrect_bg, incorrect_feedback], [correct_bg, correct_feedback])
    no_resp_feedback = visual.TextStim(presenter.window, FEEDBACK_SLOW)
    # 4&5 show options, get response, show feedback
    selection_time = float('inf') if question else SELECTION_TIME
    response = presenter.select_from_stimuli(option_stims, options, RESPONSE_KEYS, selection_time, 0, highlight,
                                             lambda x: x == correct_option, None, resp_feedback, no_resp_feedback,
                                             FEEDBACK_TIME)
    # 4.2 recover central positions
    for option in option_stims:
        option.pos = presenter.CENTRAL_POS
    # 6 interval between trials
    presenter.show_fixation(random.choice(TRIAL_INTERVALS))
    # return
    param['options'] = options
    if response is None:
        param['response'] = None
    else:
        param.update(response)
    return param


def generate_trials():
    # generate unique combinations
    unique_trials = []
    practices = []
    for anchor in range(NUM_FACES):
        for dist in range(1, NUM_FACES):
            trials = unique_trials \
                if (anchor in ANCHOR_INDEXES) and (dist >= MIN_DISTANCE) and (dist <= MAX_DISTANCE) \
                else practices
            if anchor - dist >= 0:
                trials.append({
                    'anchor': anchor,
                    'direction': DIRECTIONS[1],  # up
                    'distance': dist
                })
            if anchor + dist < NUM_FACES:
                trials.append({
                    'anchor': anchor,
                    'direction': DIRECTIONS[0],  # down
                    'distance': dist
                })
    trials = [list(unique_trials) for i in range(NUM_RUNS)]
    for run in trials:
        random.shuffle(run)
    return trials, practices


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


def get_positions(window):
    # calculate 4 image positions so that the distances from them to the screen center are the same
    x0, y0 = window.size
    x = float(IMG_DIST) / x0
    y = float(IMG_DIST) / y0
    return (-x, y), (x, y), (-x, -y), (x, -y)


if __name__ == '__main__':
    """
    # subject ID dialog
    sinfo = {'ID': '', 'Gender': ['Female', 'Male'], 'Age': '', 'Mode': ['Exp', 'Test']}
    show_form_dialog(sinfo, validation, order=['ID', 'Gender', 'Age', 'Mode'])
    sid = int(sinfo['ID'])
    img_prefix = sinfo['Gender'][0]
    """
    sid = 'testtest'
    img_prefix = 'F'
    sinfo = {'Mode': 'Exp'}
    if os.path.exists(DATA_FOLDER + sid + '.txt'):
        os.remove(DATA_FOLDER + sid + '.txt')
    # TODO delete above

    # create data file
    dataLogger = DataHandler(DATA_FOLDER, str(sid) + '.txt')
    # save info from the dialog box
    dataLogger.write_data({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # create window
    presenter = Presenter(fullscreen=(sinfo['Mode'] == 'Exp'))
    img_positions = get_positions(presenter.window)
    dataLogger.write_data(str(info.RunTimeInfo(win=presenter.window, refreshTest=None, verbose=False)))
    # load images
    example_images = presenter.load_all_images(IMG_FOLDER, '.png', img_prefix='usericon')
    for img, pos in zip(example_images, img_positions):
        img.pos = pos
    images = presenter.load_all_images(IMG_FOLDER, '.jpg', img_prefix)
    highlight = visual.ImageStim(presenter.window, image=IMG_FOLDER + 'highlight.png')
    # randomize trials TODO
    trials, practices = generate_trials()
    # randomize images
    random.seed(sid)
    random.shuffle(images)  # status high -> low
    dataLogger.write_data({i: stim._imName for i, stim in enumerate(images)})
    # randomize colors
    DIR_COLORS = {DIRECTIONS[0]: DIR_COLORS[0], DIRECTIONS[1]: DIR_COLORS[1]} if random.randrange(2) == 0 else \
                 {DIRECTIONS[0]: DIR_COLORS[1], DIRECTIONS[1]: DIR_COLORS[0]}
    dataLogger.write_data({direc: COLOR_NAMES[DIR_COLORS[direc]] for direc in DIR_COLORS.keys()})
    color_instr = INSTR_COLOR.format(down_color=COLOR_NAMES[DIR_COLORS[DIRECTIONS[0]]],
                                     up_color=COLOR_NAMES[DIR_COLORS[DIRECTIONS[1]]])

    # show instructions
    """
    presenter.show_instructions(INSTR_0)
    presenter.show_instructions(color_instr)
    presenter.show_instructions(INSTR_1)
    presenter.show_instructions(INSTR_2, TOP_INSTR_POS, example_images, next_instr_pos=(0, -0.9))
    texts = [visual.TextStim(presenter.window, key.upper(), pos=pos, color=BLACK, height=0.5)
             for key, pos in zip(RESPONSE_KEYS, img_positions)]
    presenter.show_instructions(INSTR_3, TOP_INSTR_POS, example_images + texts, next_instr_pos=(0, -0.9))
    # practice
    presenter.show_instructions(INSTR_PRACTICE)
    practices = random.sample(practices, NUM_PRACTICE_TRIALS)
    for trial in practices:
        presenter.show_instructions(color_instr)
        data = show_one_trial(trial.copy())
        data['practice'] = True
        dataLogger.write_data(data)
    # show trials
    presenter.show_instructions(INSTR_4)
    trial_counter = 0
    for run in trials:
        # instructions
        presenter.show_instructions('Run #' + str(trials.index(run) + 1) + '\n\nRemember: ' + color_instr)
        # start run
        for trial in run:
            trial_counter += 1
            data = show_one_trial(trial.copy())
            dataLogger.write_data(data)
            if trial_counter >= MAX_NUM_TRIALS:
                break
        if trial_counter >= MAX_NUM_TRIALS:
            break
    """
    # show questions at the end
    if END_QUESTIONS:
        question_keys = ('d', 'f', 't', 'g', 'v')  # down, left, right, up, none
        q_img_size = (0.12, 0.12 * presenter.window.size[0] / presenter.window.size[1])
        quesion = visual.TextStim(presenter.window, QUESTION, pos=(0, 0.9), height=0.08, wrapWidth=1.95)
        option_c = visual.TextStim(presenter.window, 'None of the above', pos=(0, -0.85))
        # arrange stimuli
        grey = '#727272'
        shapes = [visual.Rect(presenter.window, width=0.2, height=1, pos=(-0.6, 0), lineWidth=0, fillColor=grey),
                  visual.Rect(presenter.window, width=0.2, height=1, pos=(-0.2, 0), lineWidth=0, fillColor=grey),
                  visual.Rect(presenter.window, width=0.59, height=0.3, pos=(0.4, 0.35), lineWidth=0, fillColor=grey),
                  visual.Rect(presenter.window, width=0.59, height=0.3, pos=(0.4, -0.35), lineWidth=0, fillColor=grey),
                  visual.Rect(presenter.window, width=0.6, height=0.15, pos=(0, -0.85), lineWidth=0, fillColor=grey)]
        #  a) 2 steps
        two_step_stim = [copy.copy(shape) for shape in shapes]
        two_step_stim += [quesion, option_c]
        option_pos = [(-0.73, 0.53), (-0.33, 0.53), (0.07, 0.53), (0.07, -0.17), (-0.33, -0.75)]
        two_step_stim += [visual.TextStim(presenter.window, str(k.upper()), pos=pos, color='yellow')
                          for k, pos in zip(question_keys, option_pos)]
        two_step_arrows = []
        for i in range(2):
            two_step_arrows += presenter.load_all_images(IMG_FOLDER, '.png', 'arrow')
        two_arrow_pos = [(-0.6, 0.175),  (0.3, 0.35), (0.3, -0.35), (-0.2, -0.175),  # down, left, right, up
                         (-0.6, -0.175), (0.5, 0.35), (0.5, -0.35), (-0.2, 0.175)]   # down, left, right, up
        for stim, pos in zip(two_step_arrows, two_arrow_pos):
            stim.pos = pos
        two_step_stim += two_step_arrows
        two_step_stim += [visual.ImageStim(presenter.window, image=IMG_FOLDER + 'person.png', size=q_img_size)
                          for i in range(4)]
        two_step_stim += [visual.ImageStim(presenter.window, image=IMG_FOLDER + 'person_in_q.png', size=q_img_size)
                          for i in range(4)]
        person_pos = [(-0.6, 0), (0.395, 0.35), (0.395, -0.35), (-0.2, 0),         # person
                      (-0.6, -0.35), (0.195, 0.35), (0.595, -0.35), (-0.2, 0.35)]  # person in question
        for i, pos in enumerate(person_pos):
            two_step_stim[i - 8].pos = pos
        two_step_anchor_pos = [(-0.6, 0.35), (0.595, 0.35), (0.195, -0.35), (-0.2, -0.35)]  # down, left, right, up
        #  b) 3 steps
        three_step_stim = shapes
        three_step_stim += [quesion, option_c]
        three_step_arrows = []
        for i in range(2):
            three_step_arrows += presenter.load_all_images(IMG_FOLDER, '.png', 'arrow')
        three_arrow_pos = [(-0.5, 0.125), (0.25, 0.4), (-0.45, -0.4), (0.5, -0.475),  # down, left, right, up
                           (-0.5, 0.475), (0.45, 0.4), (-0.25, -0.4), (0.5, -0.125)]  # down, left, right, up
        three_step_stim += [visual.ImageStim(presenter.window, image=IMG_FOLDER + 'person.png', size=q_img_size)
                            for i in range(8)]
        three_step_stim += [visual.ImageStim(presenter.window, image=IMG_FOLDER + 'person_in_q.png', size=q_img_size)
                            for i in range(4)]
        person_pos = [(), (), (), (), (), (), (), (), (), (), (), ()]

        # generate trials
        question_trials = [{
            'anchor': random.randint(NUM_FACES / 2 - 1, NUM_FACES / 2 + 1),
            'direction': DIRECTIONS[0] if i % 2 == 0 else DIRECTIONS[1],
            'distance': 2 if i < 2 else 3
        } for i in range(4)]
        random.shuffle(question_trials)
        # start
        # presenter.show_instructions(INSTR_QUESTION + '\n\nRemember: ' + color_instr)
        for q in question_trials:
            data = show_one_trial(q, True)
            dataLogger.write_data(data)
    # end
    presenter.show_instructions(INSTR_END)
