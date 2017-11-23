import csv
import os
from data_utilities import load_json

DATA_DIR = '../data/'
PARTICIPANTS_TSV = 'participants.tsv'
TASK_TSV = ''

participants = [['subject_id', 'sex', 'age', 'up_color', 'down_color']]
events = ['face_onset', 'num_onset', 'fix_onset',
          'anchor', 'direction', 'steps', 'answer_index', 'congruent_with'
          'response', 'response_time', 'correct']
for datafile in os.listdir(DATA_DIR):
    if 'scanner.txt' not in datafile:
        continue
    sid = datafile[:3]
    raw_data = load_json(DATA_DIR + datafile, multiple_obj=True)
    participants.append([raw_data[0]['ID'], raw_data[0]['Gender'][0], raw_data[0]['Age'],
                         raw_data[2]['U'], raw_data[2]['D']])

    data = []
    for i, trial in enumerate(raw_data[3:-1]):

