import os
from data_conversion_util import load_json, list2csv

DATA_DIR = '../data/'
PARTICIPANTS_TSV = 'participants.tsv'
TASK_TSV = ''
NUM_RUNS = 6
NUM_TRIALS_PER_RUN = 24
NUM_ONSET_DIFF = 1.5
FIX_ONSET_DIFF = 2


def faces():
    # onset times
    temp_onsets = [[], []]  # down, up
    with open('face_onsets_down.txt', 'r') as infile:
        temp_onsets[0] = [line.strip().split(' ') for line in infile.readlines()]
    with open('face_onsets_up.txt', 'r') as infile:
        temp_onsets[1] = [line.strip().split(' ') for line in infile.readlines()]
    face_onsets = []
    for i in range(len(temp_onsets[0])):
        run_onsets = [int(onset) for onset in temp_onsets[0][i] + temp_onsets[1][i]]
        face_onsets.append(sorted(run_onsets))

    participants = [['subject_id', 'sex', 'age', 'up_color', 'down_color']]
    event_header = ['run_index', 'trial_index',
                    'face_onset', 'num_onset', 'fix_onset',
                    'anchor', 'direction', 'steps', 'answer_position', 'congruent_with',
                    'response', 'response_position', 'response_time', 'correct']
    for datafile in os.listdir(DATA_DIR):
        if 'scanner.txt' not in datafile:
            continue
        sid = datafile[:3]
        sdata = load_json(DATA_DIR + datafile, multiple_obj=True)
        participants.append([sdata[0]['ID'], sdata[0]['Gender'][0], sdata[0]['Age'],
                             sdata[2]['U'], sdata[2]['D']])

        old_run_nums = [i + 1 for i in range(NUM_RUNS)]
        remainder = int(sid) % NUM_RUNS
        new_run_nums = old_run_nums[remainder:] + old_run_nums[:remainder]
        run_num_dict = {old_run_nums[i]: new_run_nums[i] for i in range(NUM_RUNS)}

        run_data = [event_header]
        trial_num = 0
        for i, trial in enumerate(sdata[3:-1]):
            run_num = trial_num / NUM_TRIALS_PER_RUN + 1
            trial_index = trial_num % NUM_TRIALS_PER_RUN
            info = [run_num, trial_index + 1]

            face_onset = face_onsets[run_num_dict[run_num] - 1][trial_index]
            info += [face_onset, face_onset + NUM_ONSET_DIFF, face_onset + FIX_ONSET_DIFF]

            options = ['top', 'bottom', 'left', 'right']
            answer_pos = options[trial['answer_index']]
            if trial['answer_index'] == 0:
                congruent_with = 'top_down' if trial['direction'] == 'U' else 'bottom_up'
            elif trial['answer_index'] == 1:
                congruent_with = 'bottom_up' if trial['direction'] == 'U' else 'top_down'
            elif trial['answer_index'] == 2:
                congruent_with = 'left_right' if trial['direction'] == 'U' else 'right_left'
            elif trial['answer_index'] == 3:
                congruent_with = 'right_left' if trial['direction'] == 'U' else 'left_right'
            else:
                raise RuntimeError('Invalid answer index')
            info += [trial['anchor'], trial['direction'].lower(), trial['distance'], answer_pos, congruent_with]

            if trial['response'] is None:
                info += ['n/a', 'n/a', 'n/a', False]
            else:
                response_pos = options[trial['options'].index(trial['response'])]
                info += [trial['response'], response_pos, trial['rt'], trial['correct']]

            run_data.append(info)
            trial_num += 1

            if trial_num % NUM_TRIALS_PER_RUN == 0:  # end of run, save to file
                filename = 'sub-%s_task-face_run-0%d_event.tsv' % (sid, run_num_dict[run_num])
                print filename
                list2csv(run_data, filename, delimiter='\t')
                run_data = [event_header]

    list2csv(participants, 'participants.tsv', delimiter='\t')


faces()
