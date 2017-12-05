#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#
# Author: Meng Du
# November 2017
#


"""
This script renames and reorganizes the fMRI data into the Brain Imaging Data Structure (BIDS).

Usage:
        python organize_as_BIDS.py <subject_id_1> <subject_id_2> ...
    OR
        python organize_as_BIDS.py --all

It's not thoroughly tested for all cases -- use it with caution, and run a test before you
use it on your actual files. You can test it by running generate_test_files() and then main()
(see below), and see if there's anything wrong in the generated directories/files.

It also assumes that one task has a latin square design made by subject_id % num_runs (see
line #238). Change it based on your design.
"""

from __future__ import print_function
import os
import sys
import re


SUBJECT_DIR_PATH = '../'
SUBJECT_DIR_PREFIX = 'subj'
PATH_BETWEEN_SUBJECT_AND_TASK_DIR = '/raw'
LATIN_SQUARE_TASK_PREFIX = 'Faces_SMS_'
FUNC_NAME_DICT = {  # {current name: (new name, number of runs)}
    'Faces_SMS_': ('face', 6),
    'Eyes_': ('sacc', 2),
    'Eyes_localizer': ('loca', 1)
}
ANAT_NAME_DICT = {'MPRAGE_4_min_1X1X1mm': 'T1w'}
FMAP_NAME_DICT = {'SpinEchoFieldMap_': 'epi'}
TOTAL_READOUT_TIME = '0.059740927'


def rename(old_item, new_item):
    os.rename(old_item, new_item)
    print('Renamed "%s" to "%s".' % (old_item, new_item))


def rename_func_dirs(path, sid, task_prefix, run_num_dict=None, multi_run=True):
    """
    Rename the folder names in path that start with task_prefix, based on FUNC_NAME_DICT
    Assuming 1) the last number in the folder name indicates the position of this
                run in the scanning sequence
             2) if multi_run is True, the first number in the folder name indicates
                the number of run, starting from 1
    :param path: string path to data directory for one subject
    :param sid: string subject id
    :param task_prefix: string prefix of the task name
    :param run_num_dict: an optional dictionary of strings {old_run_#: new_run_#},
                         if run # needs to be changed
    :param multi_run: whether the task contains multiple runs (run number 'runX' has to
                      be present in the file name)
    :return: a dictionary {new_folder_name: old_folder_name}
    """
    dir_list = [dir_name for dir_name in sorted(os.listdir(path))
                if dir_name.startswith(task_prefix)]

    if multi_run:
        dir_list = [d for d in dir_list if 'run' in d]  # TODO this is just for the hierarchy study

    # error checking
    if run_num_dict is not None and len(dir_list) != len(run_num_dict):
        raise RuntimeError(
            'Number of %s folders (%d) does not equal to number of runs (%d).'
            % (task_prefix, len(dir_list), len(run_num_dict)))

    run_order = [int(re.search(r'\d+', d[::-1]).group()[::-1]) for d in dir_list]  # last number
    for i in range(len(run_order) - 1):
        if run_order[i + 1] <= run_order[i]:
            raise RuntimeError('Folders are not ordered by time.')

    if multi_run:
        run_ids = [re.search(r'\d+', d).group() for d in dir_list]  # first number
        for i, run in enumerate(run_ids):
            if i + 1 != int(run):
                raise RuntimeError('Run numbers in the folder names are not ordered.')

    # rename
    folder_dict = {}
    for i, folder in enumerate(dir_list):
        new_name = 'sub-{}_task-{}'.format(sid, FUNC_NAME_DICT[task_prefix][0])
        if multi_run:
            run_num = run_num_dict[run_ids[i]] if run_num_dict is not None else run_ids[i]
            new_name += '_run-' + run_num.zfill(2)
        new_name += '_bold'
        rename(path + folder, path + new_name)
        folder_dict[new_name] = folder

    return folder_dict


def rename_anat_dirs(path, sid):
    """
    Rename the anatomical scan directory based on ANAT_NAME_DICT.
    See rename_func_dirs() for info on parameters and return value.
    """
    folder_dict = {}
    for prefix in ANAT_NAME_DICT:
        anat_name = None
        for dir_name in os.listdir(path):
            if dir_name.startswith(prefix):
                anat_name = dir_name
                break
        if anat_name is None:
            raise RuntimeError('Anatomical scan not found.')

        # renaming
        new_name = 'sub-{}_'.format(sid) + ANAT_NAME_DICT[prefix]
        rename(path + anat_name, path + new_name)
        folder_dict[new_name] = anat_name
    return folder_dict


def rename_fmap_dirs(path, sid):
    """
    Rename the fieldmap scan directory based on FMAP_NAME_DICT.
    See rename_func_dirs() for info on parameters and return value.
    """
    folder_dict = {}
    for prefix in FMAP_NAME_DICT:
        dir_list = [dir_name for dir_name in os.listdir(path) if dir_name.startswith(prefix)]
        for folder in dir_list:
            direction = folder[len(prefix):-2]  # -2: assuming fmap is done before the 10th scan... TODO
            new_name = 'sub-{}_dir-{}_'.format(sid, direction) + FMAP_NAME_DICT[prefix]
            rename(path + folder, path + new_name)
            folder_dict[new_name] = folder
    return folder_dict


def rename_files(path, folder_name_dict):
    """
    Rename all files according to their parent folder name,
    based on folder_name_dict
    :param path: string path to the folders where files need renaming
    :param folder_name_dict: {current_folder_name: old_name}
    """
    for folder_name in folder_name_dict:
        old_name = folder_name_dict[folder_name]
        for filename in os.listdir(path + folder_name):
            if filename.startswith(old_name):
                new_name = filename.replace(old_name, folder_name, 1)
                rename(path + folder_name + '/' + filename, path + folder_name + '/' + new_name)


def reorganize_files(subj_dir, sid, dir_list, file_extensions=('.json', '.nii.gz')):
    """
    Reorganize files into BIDS (Brain Imaging Data Structure), i.e. move data from functional
    scans, anatomical scans and fieldmaps to sub-<id>/func, sub-<id>/anat, sub-<id>/fmap,
    respectively. Only files that match <parent_folder_name>.<extension> (where <extension>
    has to be one of the strings specified in file_extensions parameter) are moved. The other
    files stay at where they are.
    :param subj_dir: string path to the directory of a subject that needs to be reorganized
    :param sid: string subject id
    :param dir_list: a list of directory names where the files are (i.e. directories in
                     subj_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR)
    :param file_extensions: a list of file extensions that need to be moved
    """
    dir_lists = {'/func': [], '/anat': [], '/fmap': []}
    for folder in dir_list:
        if 'bold' in folder:
            dir_lists['/func'].append(folder)
        elif any(postfix in folder for postfix in ANAT_NAME_DICT.values()):
            dir_lists['/anat'].append(folder)
        elif any(postfix in folder for postfix in FMAP_NAME_DICT.values()):
            dir_lists['/fmap'].append(folder)

    data_path = subj_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR + '/'
    for dir_type in dir_lists:
        os.makedirs(subj_dir + dir_type)
        for folder in dir_lists[dir_type]:
            for f in os.listdir(data_path + folder):
                if any(f == folder + ext for ext in file_extensions):
                    rename(data_path + folder + '/' + f, subj_dir + dir_type + '/' + f)

    rename(subj_dir, SUBJECT_DIR_PATH + 'sub-' + sid)


def append_to_json(filename, contents):
    """
    Append contents to a json file, i.e. insert the content string(s) to the second last line
    (before the "}") of the file.
    :parameter filename: string path and file name of the json
    :parameter contents: (string, or a list of strings) content to insert
    """
    # read
    with open(filename, 'r') as json_file:
        json_content = json_file.readlines()
    # change
    if len(json_content[-2]) > 2 and json_content[-2][-1] != ',':
        json_content[-2] = json_content[-2][:-1] + ',\n'
    if type(contents) is str:
        contents = [contents]
    for line in contents:
        json_content.insert(-1, line)
    # write
    with open(filename, 'w') as json_file:
        json_file.write(''.join(json_content))


def fix_fmap_json(sid, total_readout_time=None):
    """
    Add the "IntendedFor" and optionally "TotalReadoutTime" parameters to the json files for
    fieldmap data so the fieldmaps are intended for all functional scans.
    Assuming the files are already organized as BIDS.
    :parameter sid: string subject id
    :parameter total_readout_time: string or float number, or None if unnecessary
    """
    # get functional scan names
    subject_path = SUBJECT_DIR_PATH + 'sub-%s/' % sid
    func_names = ['func/' + f for f in os.listdir(subject_path + 'func/') if f.endswith('bold.nii.gz')]
    intended_for = '\t"IntendedFor": ["' + '",\n\t\t"'.join(func_names) + '"\n\t],\n'

    # change json
    json_filenames = [f for f in os.listdir(subject_path + 'fmap/') if f.endswith('json')]
    for json_name in json_filenames:
        json_name = subject_path + 'fmap/' + json_name
        contents = intended_for if total_readout_time is None \
                   else [intended_for, '\t"TotalReadoutTime": %s\n' % str(total_readout_time)]
        append_to_json(json_name, contents)


def fix_func_json(sid):
    """
    Add the "TaskName" parameter to json files for functional scans.
    Assuming the files are already organized as BIDS.
    :parameter sid: string subject id
    """
    subject_path = SUBJECT_DIR_PATH + 'sub-%s/' % sid
    json_filenames = [f for f in os.listdir(subject_path + 'func/') if f.endswith('json')]
    for json_name in json_filenames:
        task_name = re.search(r'task-\w+_', json_name).group()[5:-1]
        append_to_json(subject_path + 'func/' + json_name, '\t"TaskName": "%s"\n' % task_name)


def generate_test_files(subject_ids):
    """
    Generate a bunch of directories and files to test main().
    """
    try:
        for sid in subject_ids:
            subject_dir = SUBJECT_DIR_PATH + SUBJECT_DIR_PREFIX + str(sid)
            os.makedirs(subject_dir)
            os.makedirs(subject_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR)
            os.makedirs(subject_dir + '/irrelevant_folder')
            # a latin square task
            for run in range(1, FUNC_NAME_DICT[LATIN_SQUARE_TASK_PREFIX][1] + 1):
                run_name = LATIN_SQUARE_TASK_PREFIX + 'run' + str(run) + '_' + str(run + 5)  # 5 is just arbitrary
                run_dir = subject_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR + '/' + run_name
                os.makedirs(run_dir)
                # create files
                open(run_dir + '/irrelevant_file.txt', 'a').close()
                for file_postfix in ['.nii.gz', '.json', '_yo.ica', '_sth_else.pdf']:  # arbitrary stuff
                    open(run_dir + '/' + run_name + file_postfix, 'a').close()
                with open(run_dir + '/' + run_name + '.json', 'w') as f:
                    f.write('{\n\t"ABC": 123\n}\n')
            # a one-run task
            run_name = FUNC_NAME_DICT.keys()[2] + '_20'
            run_dir = subject_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR + '/' + run_name
            os.makedirs(run_dir)
            for file_postfix in ['.nii.gz', '.json', '_yo.ica', '_sth_else.pdf']:  # arbitrary stuff
                open(run_dir + '/' + run_name + file_postfix, 'a').close()
            with open(run_dir + '/' + run_name + '.json', 'w') as f:
                f.write('{\n\t"ABC": 123\n}\n')
            # anatomical
            anat_name = ANAT_NAME_DICT.keys()[0] + '_17'
            anat_dir = subject_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR + '/' + anat_name
            os.makedirs(anat_dir)
            for file_postfix in ['.nii.gz', '.json', '_yo.nii.gz', '_sth_else.pdf']:  # arbitrary stuff
                open(anat_dir + '/' + anat_name + file_postfix, 'a').close()
            with open(anat_dir + '/' + anat_name + '.json', 'w') as f:
                f.write('{\n\t"ABC": 123\n}\n')
            # fieldmaps
            for d in ('PA', 'AP'):
                fmap_name = FMAP_NAME_DICT.keys()[0] + d + '_5'
                fmap_dir = subject_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR + '/' + fmap_name
                os.makedirs(fmap_dir)
                for file_postfix in ['.nii.gz', '.json', '_yo.nii.gz', '_sth_else.pdf']:  # arbitrary stuff
                    open(fmap_dir + '/' + fmap_name + file_postfix, 'a').close()
                with open(fmap_dir + '/' + fmap_name + '.json', 'w') as f:
                    f.write('{\n\t"ABC": 123\n}\n')

    except OSError as err:
        print('Error when generating test files: {}'.format(err))
        return


def main():
    try:
        if len(sys.argv) < 2:
            raise RuntimeError()
        subject_ids = sys.argv[1:]
        if len(subject_ids) == 1 and subject_ids[0] == '--all':
            subject_ids = None
    except RuntimeError:
        print('Usage:\n\t\tpython organize_as_BIDS.py <subject_id_1> <subject_id_2> ...'
              '\n\tOR\n\t\tpython organize_as_BIDS.py --all')
        quit()

    for subj_dir in os.listdir(SUBJECT_DIR_PATH):
        # TODO iterate through subject_ids instead (and print errors)
        if not subj_dir.startswith(SUBJECT_DIR_PREFIX):
            continue
        sid = subj_dir[len(SUBJECT_DIR_PREFIX):]
        if subject_ids is not None and sid not in subject_ids:
            continue

        num_latin_sq_runs = FUNC_NAME_DICT[LATIN_SQUARE_TASK_PREFIX][1]
        old_run_nums = [str(i + 1) for i in range(num_latin_sq_runs)]
        remainder = int(sid) % num_latin_sq_runs
        new_run_nums = old_run_nums[remainder:] + old_run_nums[:remainder]
        run_num_dict = {old_run_nums[i]: new_run_nums[i] for i in range(num_latin_sq_runs)}

        path = SUBJECT_DIR_PATH + subj_dir + PATH_BETWEEN_SUBJECT_AND_TASK_DIR + '/'
        sid = str(sid)

        folder_dict = {}
        try:
            folder_dict = rename_anat_dirs(path, sid)
            folder_dict.update(rename_fmap_dirs(path, sid))
            for task_prefix in FUNC_NAME_DICT:
                num_runs = FUNC_NAME_DICT[task_prefix][1]
                run_dict = run_num_dict if task_prefix == LATIN_SQUARE_TASK_PREFIX else None
                folder_dict.update(rename_func_dirs(path, sid, task_prefix, run_dict, multi_run=(num_runs > 1)))
        except RuntimeError as err:
            print('Error in %s:' % subj_dir, err, 'Skipping %s.' % subj_dir)
            # reverse renamed folders
            for item in folder_dict:
                rename(path + item, path + folder_dict[item])
        else:  # no error
            rename_files(path, folder_dict)
            reorganize_files(SUBJECT_DIR_PATH + subj_dir + '/', sid, folder_dict.keys())
            fix_fmap_json(sid, total_readout_time=TOTAL_READOUT_TIME)
            fix_func_json(sid)


if __name__ == '__main__':
    generate_test_files(list(range(101, 103)))
    main()
