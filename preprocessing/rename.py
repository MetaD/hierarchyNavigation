#!/usr/bin/env python

from __future__ import print_function
import os
import re

SUBJECT_DIR_PATH = '../'
SUBJECT_DIR_PREFIX = 'subj'
PATH_BETWEEN_SUBJECT_AND_TASK_DIR = '/raw'
TASK_DIR_NAME_PREFIX = 'Faces_SMS_run'
SUBJECT_ID_RANGE = list(range(132, 135))

NUM_RUNS = 6


def rename_folders(path, run_name_dict):
    """
    Rename the folder names that starts with TASK_DIR_NAME_PREFIX
    Assuming 1) the first number in the folder name indicates
                the number of run, starting from 1
             2) the last number in the folder name indicates
                the position of this run in the scanning sequence
    :param path: string path to the folders
    :param run_name_dict: {old_run_#: new_run_#}
    :return: {new_folder_name: old_run_name}, e.g. {'run1_5': 'run2', 'run2_4': 'run1'}
    """
    dir_list = [dir_name for dir_name in sorted(os.listdir(path))
                if dir_name.startswith(TASK_DIR_NAME_PREFIX)]
    # error checking
    if len(dir_list) != NUM_RUNS:
        raise ValueError(
            'Number of folders (%d) does not equal to number of runs (%d).'
            % (len(dir_list), NUM_RUNS))

    run_order = [int(re.search(r'\d+', d[::-1]).group()[::-1]) for d in dir_list]  # last number
    for i in range(len(run_order) - 1):
        if run_order[i + 1] <= run_order[i]:
            raise ValueError('Folders are not ordered by time.')

    run_ids = [re.search(r'\d+', d).group() for d in dir_list]  # first number
    for i, run in enumerate(run_ids):
        if i + 1 != int(run):
            raise ValueError('Run numbers in the folder names are not ordered.')

    # rename
    new_folder_dict = {}
    for i, folder in enumerate(dir_list):
        old_run_name = TASK_DIR_NAME_PREFIX + run_ids[i]
        new_name = folder.replace(old_run_name, run_name_dict[old_run_name], 1)
        new_folder_dict[new_name] = old_run_name
        os.rename(path + folder, path + new_name)
        print('Renamed "%s" to "%s".' % (path + folder, path + new_name))

    return new_folder_dict


def rename_files(path, folder_name_dict, run_name_dict):
    """
    Rename the file names that start with TASK_DIR_NAME_PREFIX
    according to their folder name
    :param path: string path to the files
    :param folder_name_dict: {new_folder_name: old_run_name}
    :param run_name_dict: {old_run_#: new_run_#}
    """
    folder_name = path[path.index(TASK_DIR_NAME_PREFIX):-1]
    old_run_name = folder_name_dict[folder_name]
    new_run_name = run_name_dict[old_run_name]
    for filename in os.listdir(path):
        if filename.startswith(TASK_DIR_NAME_PREFIX):
            new_name = filename.replace(old_run_name, new_run_name, 1)
            os.rename(path + filename, path + new_name)
            print('Renamed "%s" to "%s".' % (path + filename, path + new_name))


def generate_test_files():
    try:
        for sid in SUBJECT_ID_RANGE:
            subject_dir = SUBJECT_DIR_PATH + '/' + SUBJECT_DIR_PREFIX + str(sid)
            os.makedirs(subject_dir)
            os.makedirs(subject_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR)
            os.makedirs(subject_dir + '/irrelevant_folder')
            for run in range(1, NUM_RUNS + 1):
                run_name = TASK_DIR_NAME_PREFIX + str(run) + '_' + str(run + 5)  # 5 is just arbitrary
                run_dir = subject_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR + '/' + run_name
                os.makedirs(run_dir)
                # create files
                open(run_dir + '/irrelevant_file.txt', 'a').close()
                for file_postfix in ['.nii.gz', '_yo.ica', '_sth_else.pdf']:  # arbitrary
                    open(run_dir + '/' + run_name + file_postfix, 'a').close()
    except OSError as err:
        print(err)
        return


def main():
    for subj_dir in os.listdir(SUBJECT_DIR_PATH):
        if not subj_dir.startswith(SUBJECT_DIR_PREFIX):
            continue
        sid = int(subj_dir[len(SUBJECT_DIR_PREFIX):])
        if sid not in SUBJECT_ID_RANGE:
            continue

        old_run_names = [TASK_DIR_NAME_PREFIX + str(i + 1) for i in range(NUM_RUNS)]
        remainder = sid % NUM_RUNS
        if remainder == 0:  # no need to rename
            continue
        new_run_names = old_run_names[remainder:] + old_run_names[:remainder]
        run_name_dict = {old_run_names[i]: new_run_names[i] for i in range(NUM_RUNS)}
        path = SUBJECT_DIR_PATH + subj_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR + '/'
        try:
            new_folder_dict = rename_folders(path, run_name_dict)
        except ValueError as err:
            print('Error in %s:' % subj_dir, err, 'Skipping %s.' % subj_dir)
        else:  # no error
            for new_folder in new_folder_dict:
                rename_files(path + new_folder + '/', new_folder_dict, run_name_dict)


if __name__ == '__main__':
    # generate_test_files()
    main()
