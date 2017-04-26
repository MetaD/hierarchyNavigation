import json

f = open('data/savanna.txt', 'r')

prac_counter, real_counter, prac_correct, real_correct, prac_resp, real_resp = 0, 0, 0, 0, 0, 0
for ln_num, ln in enumerate(f):

    # load in data file
    jdict = json.loads(ln)

    # extract data ouput from training and testing blocks separately
    if "response" in jdict:
        if 'practice' in jdict:
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


def printer(string, numerator, denominator):
    print string, numerator, '/', denominator, '(' + str(numerator * 100.0 / denominator)[:5] + '%)'

printer('Practice response rate:', prac_resp, prac_counter)
printer('Practice accuracy:', prac_correct, prac_resp)
printer('Actual response rate:', real_resp, real_counter)
printer('Actual accuracy:', real_correct, real_resp)
