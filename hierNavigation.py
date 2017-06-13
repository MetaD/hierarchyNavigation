#!/usr/bin/env python

from psychopy_util import *
from config import *
import pickle


def show_one_trial(param):
    infoLogger.info('Starting trial')
    # 0 anchor face
    infoLogger.info('Showing anchor face')
    presenter.draw_stimuli_for_duration(images[param['anchor']], FACE_TIME)
    infoLogger.info('End of anchor face')
    # 1 fixation
    presenter.show_fixation(random.choice(FIXATION_TRIGGERS), wait_trigger=True)
    # 2 number
    num_stim = visual.TextStim(presenter.window, str(param['distance']), height=1, color=DIR_COLORS[param['direction']])
    infoLogger.info('Showing number')
    presenter.draw_stimuli_for_duration(num_stim, NUMBER_TIME)
    infoLogger.info('End of number')
    # 3 fixation (mental navigation)
    presenter.show_fixation(random.choice(BLANK_TRIGGERS), wait_trigger=True)
    # 4.0 options
    correct_option = param['anchor'] + param['distance'] if param['direction'] == DIRECTIONS[0] else \
                     param['anchor'] - param['distance']
    options = [correct_option]
    # 4.1 randomly pick 3 other adjacent images
    abs_dist = 1  # absolute value of distance
    while len(options) < NUM_OPTIONS:
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
    correct_bg = visual.Rect(presenter.window, width=2, height=2, fillColor=GREEN)
    incorrect_feedback = visual.TextStim(presenter.window, FEEDBACK_WRONG, height=0.2, color=BLACK)
    incorrect_bg = visual.Rect(presenter.window, width=2, height=2, fillColor=RED)
    resp_feedback = ([incorrect_bg, incorrect_feedback], [correct_bg, correct_feedback])
    no_resp_feedback = visual.TextStim(presenter.window, FEEDBACK_SLOW)
    # 4&5 show options, get response, show feedback
    response = presenter.select_from_stimuli(option_stims, options, RESPONSE_KEYS, SELECTION_TIME, 0, highlight,
                                             lambda x: x == correct_option, None, resp_feedback, no_resp_feedback,
                                             FEEDBACK_TRIGGER, feedback_wait_trigger=True)
    # 4.2 recover central positions
    for option in option_stims:
        option.pos = presenter.CENTRAL_POS
    # 6 interval between trials
    infoLogger.info('End of trial')
    presenter.show_fixation(random.choice(ITI_TRIGGERS), wait_trigger=True)
    # return
    param['options'] = options
    if response is None:
        param['response'] = None
    else:
        param.update(response)
    return param


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
    # subject ID dialog
    sinfo = {'ID': '', 'Gender': ['Female', 'Male'], 'Age': '', 'Mode': ['Exp', 'Test']}
    show_form_dialog(sinfo, validation, order=['ID', 'Gender', 'Age', 'Mode'])
    sid = int(sinfo['ID'])
    img_prefix = sinfo['Gender'][0]

    # create logging files
    infoLogger = logging.getLogger()
    if not os.path.isdir(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)
    logging.basicConfig(filename=LOG_FOLDER + str(sid) + '.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)8s %(message)s')
    dataLogger = DataHandler(DATA_FOLDER, str(sid) + '.txt')
    # save info from the dialog box
    dataLogger.write_data({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # create window
    serial = SerialUtil(SERIAL_PORT, BAUD_RATE)
    presenter = Presenter(fullscreen=(sinfo['Mode'] == 'Exp'), serial=serial)
    img_positions = get_positions(presenter.window)
    # load images
    example_images = presenter.load_all_images(IMG_FOLDER, '.png', img_prefix='usericon')
    for img, pos in zip(example_images, img_positions):
        img.pos = pos
    images = presenter.load_all_images(IMG_FOLDER, '.jpg', img_prefix)
    highlight = visual.ImageStim(presenter.window, image=IMG_FOLDER + 'highlight.png')
    # get trials from pickle file
    trials = pickle.load(DESIGN_FILENAME)
    practices = pickle.load(DESIGN_FILENAME)
    print trials
    print practices
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
    infoLogger.info('Starting experiment')
    presenter.show_instructions(INSTR_0, next_instr_text=None, wait_trigger=True)
    presenter.show_instructions(color_instr, next_instr_text=None, wait_trigger=True)
    presenter.show_instructions(INSTR_1, next_instr_text=None, wait_trigger=True)
    presenter.show_instructions(INSTR_2, TOP_INSTR_POS, example_images, next_instr_text=None, wait_trigger=True)
    texts = [visual.TextStim(presenter.window, key.upper(), pos=pos, color=BLACK, height=0.5)
             for key, pos in zip(RESPONSE_KEYS, img_positions)]
    presenter.show_instructions(INSTR_3, TOP_INSTR_POS, example_images + texts, next_instr_text=None, wait_trigger=True)
    # practice
    presenter.show_instructions(INSTR_PRACTICE, next_instr_text=None, wait_trigger=True)
    practices = random.sample(practices, NUM_PRACTICE_TRIALS)
    for trial in practices:
        presenter.show_instructions(color_instr, next_instr_text=None, wait_trigger=True)
        data = show_one_trial(trial.copy())
        data['practice'] = True
        dataLogger.write_data(data)
    # show trials
    presenter.show_instructions(INSTR_4, next_instr_text=None, wait_trigger=True)
    trial_counter = 0
    for run in trials:
        # instructions
        presenter.show_instructions('Run #' + str(trials.index(run)+1) + ' of ' + str(len(trials)+1) + '\n\n' +
                                    'Remember: ' + color_instr, next_instr_text=None, wait_trigger=True)

        # start run
        for trial in run:
            trial_counter += 1
            data = show_one_trial(trial.copy())
            dataLogger.write_data(data)
            if trial_counter >= MAX_NUM_TRIALS:
                break
        if trial_counter >= MAX_NUM_TRIALS:
            break
    presenter.show_instructions(INSTR_END, next_instr_text=None, wait_trigger=True)
    infoLogger.info('Experiment ended')
