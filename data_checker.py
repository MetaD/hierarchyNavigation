import json
import os
import csv


DATA_FOLDER = 'data/'
CSV_FILE = 'navigation_data.csv'

with open(CSV_FILE, 'w') as outfile:
    writer = csv.writer(outfile, delimiter=',')
    writer.writerow(['id', 'response rate', 'accuracy'])
    for datafile in sorted(os.listdir(DATA_FOLDER)):
        if not datafile.endswith('.txt') or not datafile[0].isdigit():
            continue
        with open(DATA_FOLDER + datafile, 'r') as infile:
            prac_counter, real_counter, prac_correct, real_correct, prac_resp, real_resp = 0, 0, 0, 0, 0, 0
            for ln_num, ln in enumerate(infile):
                # load in data file
                jdict = json.loads(ln)

                # extract data ouput from training and testing blocks separately
                if "response" in jdict:
                    if 'practice' in jdict:
                        prac_counter += 1
                        if jdict['response'] is not None:
                            prac_resp += 1
                            if jdict['correct']:
                                prac_correct += 1
                    else:
                        real_counter += 1
                        if jdict['response'] is not None:
                            real_resp += 1
                            if jdict['correct']:
                                real_correct += 1
            writer.writerow([datafile[:-4],
                             str(real_resp * 100.0 / real_counter)[:5] + '%',
                             str(real_correct * 100.0 / real_resp)[:5] + '%'])
