import json
import os
import csv
import numpy as np

# This file is so shitty

DATA_FOLDER = 'data/'
MIN_ID = 77
CSV_FILE = 'navigation_data_' + str(MIN_ID) + '+.csv'

all_data = {}
for datafile in sorted(os.listdir(DATA_FOLDER)):
    if not datafile.endswith('.txt') or not datafile[0].isdigit():
        continue
    sid = int(datafile[:2]) if 'questions' in datafile else int(datafile[:-4])
    if sid < MIN_ID:
        continue
    with open(DATA_FOLDER + datafile, 'r') as infile:
        prac_counter, real_counter, prac_correct, real_correct, prac_resp, real_resp = 0, 0, 0, 0, 0, 0
        free_resp, make_easier, visualizations = None, None, []
        # 0: top + more powerful, 1: top + less powerful, 2: bottom + more powerful, 3: bottom + less powerful,
        # 4: left + more powerful, 5: left + less powerful, 6: right + more powerful, 7: right + less powerful
        # top/bottom/left/right means the location of the correct option
        direction_counters = [0 for _ in range(8)]
        direction_rt = [[] for _ in range(8)]
        for ln_num, ln in enumerate(infile):
            # load in data file
            jdict = json.loads(ln)

            # extract data output from training and testing blocks separately
            if 'response' in jdict:
                if len(jdict) == 2:
                    if free_resp is None:  # first free response question
                        free_resp = jdict['response']
                    else:
                        make_easier = jdict['response']
                elif 'visualization' in jdict:
                    direction = 'UP' if jdict['direction'] == 'U' else 'DOWN'
                    visualizations += [jdict['visualization']['response'], direction, jdict['correct']]
                elif 'practice' in jdict:
                    prac_counter += 1
                    if jdict['response'] is not None:
                        prac_resp += 1
                        if 'correct' in jdict and jdict['correct']:
                            prac_correct += 1
                else:  # a normal trial
                    real_counter += 1
                    correct_option = jdict['anchor'] + (-1 if jdict['direction'] == 'U' else 1) * jdict['distance']
                    type_index = 2 * jdict['options'].index(correct_option)
                    type_index += int(jdict['direction'] == 'D')
                    direction_counters[type_index] += 1
                    if jdict['response'] is not None:
                        real_resp += 1
                        if 'correct' in jdict and jdict['correct']:
                            real_correct += 1
                            direction_rt[type_index].append(np.float64(jdict['rt']) * 1000)  # rt in ms

        if 'questions' in datafile:  # toy navigation task
            sdata = [free_resp] + visualizations + [make_easier]
            if sid in all_data:
                all_data[sid] += sdata
            else:
                all_data[sid] = [sid,
                                 str(prac_resp) + '/' + str(prac_counter),
                                 str(prac_correct) + '/' + str(prac_resp)] + sdata
        else:                        # normal navigation task
            # response rate & accuracy
            sdata = [sid,
                     str(real_resp * 100.0 / real_counter)[:5] + '%',
                     str(real_correct * 100.0 / real_resp)[:5] + '%']
            # direction rt stuff
            for i in range(8):
                rt_mean = np.mean(direction_rt[i])
                rt_std = np.std(direction_rt[i])
                sdata.append('%.0f ' % rt_mean + '%.0f' % rt_std)
                sdata.append(str(len(direction_rt[i])) + '/' + str(direction_counters[i]))
            for indexes in [(0, 3), (1, 2), (4, 7), (5, 6)]:
                group = np.concatenate((direction_rt[indexes[0]], direction_rt[indexes[1]]))
                rt_mean = np.mean(group)
                rt_std = np.std(group)
                sdata.append('%.0f ' % rt_mean + '%.0f' % rt_std)
                sdata.append(str(len(group)) + '/' + str(direction_counters[indexes[0]] + direction_counters[indexes[1]]))
            # other things
            if free_resp is not None:
                sdata.append(free_resp)
                sdata += visualizations
            if sid in all_data:
                all_data[sid] = sdata + all_data[sid][3:]
            else:
                all_data[sid] = sdata


with open(CSV_FILE, 'w') as outfile:
    writer = csv.writer(outfile, delimiter=',')
    writer.writerow(['id', 'response rate', 'accuracy'] +
                    ['top, more powerful', '', 'top, less powerful', '', 'bottom, more powerful', '',
                     'bottom, less powerful', '', 'left, more powerful', '', 'left, less powerful', '',
                     'right, more powerful', '', 'right, less powerful', ''] +
                    ['top-down', '', 'bottom-up', '', 'left-right', '', 'right-left', ''] +
                    ['free response'] +
                    [f(i) for i in range(1, 5) for f in (lambda x: '#' + str(x) + ' visualization',
                                                         lambda x: '#' + str(x) + ' direction',
                                                         lambda x: '#' + str(x) + ' correct')] +
                    ['how to make it easier'])
    for sid in sorted(all_data.keys()):
        writer.writerow(all_data[sid])
