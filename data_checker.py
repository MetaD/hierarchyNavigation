import json

f = open('data/savanna.txt', 'r')

prac_counter, real_counter, prac_correct, real_correct = 0, 0, 0, 0
for ln_num, ln in enumerate(f):

    # load in data file
    jdict = json.loads(ln)

    # extract data ouput from training and testing blocks separately
    if "response" in jdict:
        if 'practice' in jdict:
            prac_counter += 1
            if 'correct' in jdict and jdict['correct']:
                prac_correct += 1
        else:
            real_counter += 1
            if 'correct' in jdict and jdict['correct']:
                real_correct += 1

print 'Practice trials:', prac_correct, '/', prac_counter, '(' + str(prac_correct * 100.0 / prac_counter) + '%)'
print 'Actual trials:', real_correct, '/', real_counter, '(' + str(real_correct * 100.0 / real_counter) + '%)'
