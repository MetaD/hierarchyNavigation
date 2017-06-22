import json
import os
import csv


DATA_FOLDER = 'data/'
CSV_FILE = 'navigation_data.csv'

with open(CSV_FILE, 'w') as outfile:
    writer = csv.writer(outfile, delimiter=',')
    writer.writerow(['id', 'response rate', 'accuracy', 'free response'] +
                    [f(i) for i in range(1, 5) for f in (lambda x: '#' + str(x) + ' visualization',
                                                         lambda x: '#' + str(x) + ' direction',
                                                         lambda x: '#' + str(x) + ' correct')])
    for datafile in sorted(os.listdir(DATA_FOLDER)):
        if not datafile.endswith('.txt') or not datafile[0].isdigit():
            continue
        with open(DATA_FOLDER + datafile, 'r') as infile:
            prac_counter, real_counter, prac_correct, real_correct, prac_resp, real_resp = 0, 0, 0, 0, 0, 0
            free_resp, visualizations = None, []
            for ln_num, ln in enumerate(infile):
                # load in data file
                jdict = json.loads(ln)

                # extract data output from training and testing blocks separately
                if 'response' in jdict:
                    if len(jdict) == 2:  # free response question
                        free_resp = jdict['response']
                    elif 'visualization' in jdict:
                        direction = 'UP' if jdict['direction'] == 'U' else 'DOWN'
                        visualizations += [jdict['visualization']['response'], direction, jdict['correct']]
                    elif 'practice' in jdict:
                        prac_counter += 1
                        if jdict['response'] is not None:
                            prac_resp += 1
                            if 'correct' in jdict and jdict['correct']:
                                prac_correct += 1
                    else:
                        real_counter += 1
                        if jdict['response'] is not None:
                            real_resp += 1
                            if 'correct' in jdict and jdict['correct']:
                                real_correct += 1
            sdata = [datafile[:-4],
                     str(real_resp * 100.0 / real_counter)[:5] + '%',
                     str(real_correct * 100.0 / real_resp)[:5] + '%']
            if free_resp is not None:
                sdata.append(free_resp)
                sdata += visualizations
            writer.writerow(sdata)
