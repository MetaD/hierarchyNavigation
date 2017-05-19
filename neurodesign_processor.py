import os

DIR = 'neurodesign/'
FILE_NAMES = ('/ITIs.txt', '/stimulus_0.txt', '/stimulus_1.txt')

designs = []
for subdir in os.listdir(DIR):
    if os.path.isdir(DIR + subdir):
        design = ['iti', 'stim0', 'stim1']  # strings are just placeholders
        for i, filename in enumerate(FILE_NAMES):
            with open(DIR + subdir + filename, 'r') as iti_file:
                design[i] = [float(time) for time in iti_file.read().split('\n') if len(time) > 1]
        designs.append(design)

print designs
