DIR = 'design_0_0x/'
FILE_NAMES = ('ITIs.txt', 'stimulus_0.txt', 'stimulus_1.txt')
TRIAL_TIME = 11.0

design = {}
for i, filename in enumerate(FILE_NAMES):
    with open(DIR + filename, 'r') as iti_file:
        design[FILE_NAMES[i][:-4]] = [float(time) for time in iti_file.read().split('\n') if len(time) > 1]


def get_order(s0, s1):
    order = []
    i, j = 0, 0
    while True:
        if i == len(s0):
            for k in range(len(s1) - j):
                order.append(1)
            break
        elif j == len(s1):
            for k in range(len(s0) - i):
                order.append(0)
            break
        if s0[i] < s1[j]:
            order.append(0)
            i += 1
        else:
            order.append(1)
            j += 1
    return order

order = get_order(design['stimulus_0'], design['stimulus_1'])
iti_onset = [[], []]
time = 0.0
for i in range(len(order)):
    iti_onset[order[i]].append(str(time))
    time += float(design['ITIs'][i]) + TRIAL_TIME

with open(DIR + 'iti_stimulus_0.txt', 'w') as outfile0:
    outfile0.write('\n'.join(iti_onset[0]))
with open(DIR + 'iti_stimulus_1.txt', 'w') as outfile1:
    outfile1.write('\n'.join(iti_onset[1]))
