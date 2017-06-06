import os

DIR = 'neurodesign_0/design_1/'
FILE_NAMES = ('ITIs.txt', 'stimulus_0.txt', 'stimulus_1.txt')

design = {}
for i, filename in enumerate(FILE_NAMES):
    with open(DIR + filename, 'r') as iti_file:
        design[FILE_NAMES[i][:-4]] = [float(time) for time in iti_file.read().split('\n') if len(time) > 1]

with open('iti_stimulus_0.txt', 'w') as outfile0:
    pass
with open('iti_stimulus_1.txt', 'w') as outfile1:
    pass
