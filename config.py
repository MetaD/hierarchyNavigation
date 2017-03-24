# Experimental parameters
NUM_PRACTICE_TRIALS = 6
MAX_NUM_TRIALS = 5  # -> just to test the program TODO
NUM_RUNS = 4
NUM_FACES = 9
NUM_OPTIONS = 4
DIRECTIONS = ('D', 'U')
ANCHOR_INDEXES = (2, 3, 4, 5, 6)
MIN_DISTANCE = 2
RESPONSE_KEYS = ('q', 'w', 'a', 's')
# Colors
DIR_COLORS = ('#f0ad4e', '#5bc0de')
COLOR_NAMES = {'#f0ad4e': 'Orange', '#5bc0de': 'Blue'}
RED = '#ff0000'
GREEN = '#84ff84'
BLACK = '#000000'
# Paths
IMG_FOLDER = 'img/'
DATA_FOLDER = 'data/'
# Positions
TOP_INSTR_POS = (0, 0.8)
IMG_POSITIONS = ((-0.5, 0.5), (0.5, 0.5), (-0.5, -0.5), (0.5, -0.5))  # order corresponds to RESPONSE_KEYS
# Times
FACE_TIME = 0.5
FIXATION_TIMES = (1.5, 3.5)
NUMBER_TIME = 0.5
BLANK_TIMES = (5.5, 7.5)
SELECTION_TIME = 2  # TODO
FEEDBACK_TIME = 1  # TODO
TRIAL_INTERVALS = (4, 6, 8)
# Strings
FEEDBACK_RIGHT = 'Correct!'
FEEDBACK_WRONG = 'Wrong.'
FEEDBACK_SLOW = 'Too slow. Please respond faster.'
# Instructions
INSTR_0 = ['Welcome!\n\nIn this task, you will be asked about the social hierarchy you\'ve learned.']
INSTR_0.append('Each trial will begin with a \'reference\' face.\n\nA few seconds later, a number will appear.')
INSTR_0.append('Your job is to figure out who is that number of steps MORE or LESS powerful than the \'reference\' face in the social hierarchy.\n\nThe color of the number indicates whether you need to figure out who is that number of steps MORE or LESS powerful than the reference face.')
INSTR_bf_1 = 'You\'ll have a few seconds to figure out your response. \n\nAfter that, 4 faces will be briefly presented as possible response options. They won\'t be on the screen for very long, so it\'s important to try to figure out your response before they appear so that you can respond in time.'
INSTR_1 = 'When the response options are presented, they\'ll look something like this:'
INSTR_2 = 'Press the Q, W, A or S key to select a given face, like this:'
INSTR_PRACTICE = 'We\'ll start by doing some practice trials.\n\nIn these practice trials, you\'ll be reminded of the meaning of the numbers\' colors before each trial (but this won\'t happen in the main task).'
INSTR_3 = 'You\'ve completed all of the practice trials.\n\nNow we\'ll begin the task.'
INSTR_END = 'The experiment is complete!\nThank you for participating!'
