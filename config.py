# Numbers/Experimental parameters
NUM_PRACTICE_TRIALS = 6
MAX_NUM_TRIALS = 5  # -> just to test the program TODO
NUM_RUNS = 4
NUM_FACES = 9
NUM_OPTIONS = 4
DIRECTIONS = ('D', 'U')
ANCHOR_INDEXES = (2, 3, 4, 5, 6)
MIN_DISTANCE = 2
RESPONSE_KEYS = ('q', 'w', 'a', 's')
DIR_COLORS = ('#f0ad4e', '#5bc0de')
COLOR_NAMES = {'#f0ad4e': 'orange', '#5bc0de': 'blue'}
FEEDBACK_COLORS = ('#ff0000', '#84ff84')  # (incorrect, correct)
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
FEEDBACK_RIGHT = 'Yayyy'
FEEDBACK_WRONG = 'Wrong'
FEEDBACK_SLOW = 'Too slow'
# Instructions
INSTR_0 = 'WARNING\nThis experiment may contain content inappropriate for facial phobics and law-abiding citizens'
INSTR_1 = 'You\'ll see 4 potential victims like this:'
INSTR_2 = 'Press keys Q, W, A, S to select the target you want to murder, like this:'
INSTR_PRACTICE = 'Practice'
INSTR_3 = 'You are a real murderer now'
INSTR_END = 'Everybody is dead.\nThank you for participating!'
