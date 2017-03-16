# Numbers/Experimental parameters
NUM_TRIALS_PER_CONDITION = 4  # one condition == one face + one direction + one distance
NUM_TRIALS_PER_RUN = 20
NUM_FACES = 9
DIRECTIONS = ('D', 'U')
ANCHOR_INDEXES = (2, 3, 4, 5, 6)
MIN_DISTANCE = 2
DIR_COLORS = ('#5cb85c', '#5bc0de')
RESPONSE_KEYS = ('q', 'w', 'a', 's')
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
BLANK_TIMES = (3.5, 5.5)
SELECTION_TIME = 1  # TODO
FEEDBACK_TIME = 1
TRIAL_INTERVALS = (4, 6, 8)
# Strings
FEEDBACK_RIGHT = 'Yayyy'
FEEDBACK_WRONG = 'Wrong'
FEEDBACK_SLOW = 'Too slow'
# Instructions
INSTR_0 = 'WARNING\nThis experiment may contain content inappropriate for facial phobics and law-abiding citizens'
INSTR_1 = 'You\'ll see 4 potential victims like this:'
INSTR_2 = 'Press keys Q, W, A, S to select the target you want to murder, like this:'
INSTR_END = 'Everybody is dead.\nThank you for participating!'
