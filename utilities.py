#
# Utilities for PsychoPy experiments
# Author: Meng Du
# Nov 16 2016
#

import os
import json
import random
from psychopy import gui, visual, core, event, info


def show_form_dialog(items, validation_func=None, reset_after_error=True, title='', order=(), tip=None):
    """
    Show a form to be filled within a dialog. The user input values will be stored in items.
    See wxgui.DlgFromDict
    :param items: a dictionary with item name strings as keys, e.g. {'Subject ID': ''}
    :param validation_func: a function that takes the items dictionary, checks whether inputs are valid,
                            and returns a tuple valid (a boolean), message (a string)
    :param reset_after_error: a boolean; if true, all filled values will be reset in case of error
    :param title: a string form title
    :param order: a list containing keys in items, indicating the order of the items
    :param tip: a dictionary of tips for the items
    """
    while True:
        original_items = items.copy()
        dialog = gui.DlgFromDict(dictionary=items, title=title, order=order, tip=tip)
        if dialog.OK:
            if validation_func is None:
                break
            # validate
            valid, message = validation_func(items)
            if valid:
                break
            else:
                print 'Error: ' + message
                if reset_after_error:
                    items = original_items
        else:
            print 'User cancelled'
            core.quit()


class Presenter:
    """
    Methods that help to draw stuff in a window
    """
    def __init__(self, fullscreen=True, window=None):
        """
        :param fullscreen: a boolean indicating either full screen or not
        :param window: an optional psychopy.visual.Window
                       a new full screen window will be created if this parameter is not provided
        """
        self.window = window if window is not None else visual.Window(fullscr=fullscreen)
        self.expInfo = info.RunTimeInfo(win=window, refreshTest=None, verbose=False)
        # Positions
        self.CENTRAL_POS = (0.0, 0.0)
        self.LEFT_CENTRAL_POS = (-0.5, 0.0)
        self.RIGHT_CENTRAL_POS = (0.5, 0.0)
        self.LIKERT_SCALE_INSTR_POS = (0, 0.8)
        self.LIKERT_SCALE_OPTION_INTERVAL = 0.2
        self.LIKERT_SCALE_OPTION_POS_Y = -0.2
        self.LIKERT_SCALE_LABEL_POS_Y = -0.35
        self.FEEDBACK_POS_Y_DIFF = -0.4
        # Selection
        self.SELECTED_STIM_OPACITY_CHANGE = 0.3

    def load_all_images(self, img_path, img_extension, img_prefix=None):
        """
        Read all image files in img_path that end with img_extension, and create corresponding ImageStim.
        :param img_path: a string path which should end with '/'
        :param img_extension: a string of image file extension
        :param img_prefix: a string prefix of file names. If specified, files without this prefix wouldn't be loaded
        :return: a list of psychopy.visual.ImageStim
        """
        img_files = [filename for filename in os.listdir(img_path) if filename.endswith(img_extension)]
        if img_prefix is not None:
            img_files = [filename for filename in img_files if filename.startswith(img_prefix)]
        img_files = [img_path + filename for filename in img_files]
        img_stims = [visual.ImageStim(self.window, image=img_file) for img_file in img_files]
        return img_stims

    def draw_stimuli_for_duration(self, stimuli, duration):
        """
        Display the given stimuli for a given duration
        :param stimuli: either a psychopy.visual stimulus or a list of them to draw
        :param duration: a float time duration in seconds
        """
        if isinstance(stimuli, visual.BaseVisualStim):
            stimuli.draw()
        else:
            for stim in stimuli:
                if stim is not None:  # skipping "None"
                    stim.draw()
        self.window.flip()
        if duration is not None:
            core.wait(duration)

    def draw_stimuli_for_response(self, stimuli, response_keys, max_wait=float('inf')):
        """
        :param stimuli: either a psychopy.visual stimulus or a list of them to draw
        :param response_keys: a list containing strings of response keys
        :param max_wait: a numeric value indicating the maximum number of seconds to wait for keys.
                         By default it waits forever
        :return: a tuple (key_pressed, reaction_time_in_seconds)
        """
        self.draw_stimuli_for_duration(stimuli, duration=None)
        response = event.waitKeys(maxWait=max_wait, keyList=response_keys, timeStamped=core.Clock())
        if response is None:  # timed out
            return None
        return response[0]

    def show_instructions(self, instructions, position=(0, 0), other_stim=(), key_to_continue='space',
                          next_instr_text='Press space to continue', next_instr_pos=(0.0, -0.8)):
        """
        Show a list of instructions strings
        :param instructions: an instruction string, or a list containing instruction strings
        :param position: a tuple (x, y) position for the instruction text
        :param other_stim: a list of other psychopy.visual stimuli to be displayed on each page of instructions
        :param key_to_continue: a string of the key to press
        :param next_instr_text: a string to show together with each page of instruction, could be None
        :param next_instr_pos: a tuple of floats, position for the above string
        """
        if type(instructions) is str:
            instructions = [instructions]
        if next_instr_text is not None:
            next_instr_stim = visual.TextStim(self.window, text=next_instr_text, pos=next_instr_pos)
        else:
            next_instr_stim = None
        for instr in instructions:
            instr_stim = visual.TextStim(self.window, text=instr, pos=position)
            self.draw_stimuli_for_response([instr_stim, next_instr_stim] + list(other_stim), [key_to_continue])

    def show_fixation(self, duration):
        """
        Show a '+' for a specified duration
        :param duration: a time duration in seconds
        """
        plus_sign = visual.TextStim(self.window, text='+')
        self.draw_stimuli_for_duration(plus_sign, duration)

    def show_blank_screen(self, duration):
        """
        Show a blank screen for a specified duration
        :param duration: a time duration in seconds
        """
        blank = visual.TextStim(self.window, text='')
        self.draw_stimuli_for_duration(blank, duration)

    def likert_scale(self, instruction, num_options, option_texts=None, option_labels=None, side_labels=None,
                     response_keys=None):
        """
        Show a Likert scale of the given range of numbers and wait for a response
        :param instruction: a string instruction to be displayed
        :param num_options: an integer number of options, should be greater than 1 and less than 11
        :param option_texts: a list of strings to be displayed as the options. If not specified, the default texts are
                             the range from 1 to num_options if num_options < 10, or 0 to 9 if num_options equals 10.
                             Length of this list should be the same as num_options.
        :param option_labels: a list of strings to be displayed alongside the option numbers.
                              Length of this list should be the same as num_options.
        :param side_labels: a tuple of two strings to be shown under the leftmost and rightmost options,
                            e.g. ('Not at all', 'Extremely')
        :param response_keys: an optional list of response keys. If not specified, the default keys are the range from 1
                              to num_options if num_options < 10, or 0 to 9 if num_options equals 10.
        :return: a tuple (response, reaction_time_in_seconds)
        """
        if num_options < 2 or num_options > 10:
            raise ValueError('Number of Likert scale options has to be greater than 1 and less than 11')
        if option_texts is not None and len(option_texts) != num_options:
            raise ValueError('Number of Likert scale option texts does not match the number of options')
        if option_labels is not None and len(option_labels) != num_options:
            raise ValueError('Number of Likert scale option labels does not match the number of options')
        if side_labels is not None and len(side_labels) != 2:
            raise ValueError('Number of Likert scale side labels has to be 2')

        # instruction
        stimuli = [visual.TextStim(self.window, text=instruction, pos=self.LIKERT_SCALE_INSTR_POS)]
        # option texts
        if option_texts is None:
            if num_options == 10:
                option_texts = [str(i) for i in range(num_options)]
            else:
                option_texts = [str(i + 1) for i in range(num_options)]
        # side labels
        if side_labels is not None:
            if len(side_labels) != 2:
                raise ValueError('Length of side labels must be 2')
            option_labels = [side_labels[0]] + [''] * (num_options - 2) + [side_labels[1]]
        # positions of options/labels
        scale_width = (len(option_texts) - 1) * self.LIKERT_SCALE_OPTION_INTERVAL
        if scale_width > 2:
            pos_x = [float(pos) / 100 for pos in range(-100, 100, int(200 / (len(option_texts) - 1)))]
        else:
            pos_x = [float(pos) / 100 for pos in range(-int(scale_width * 50), int(scale_width * 50) + 2,
                                                       int(self.LIKERT_SCALE_OPTION_INTERVAL * 100))]
        # construct stimuli
        for i in range(len(option_texts)):
            stimuli.append(visual.TextStim(self.window, text=option_texts[i],
                                           pos=(pos_x[i], self.LIKERT_SCALE_OPTION_POS_Y)))
        if option_labels is not None:
            for i in range(len(option_texts)):
                stimuli.append(visual.TextStim(self.window, text=option_labels[i],
                                               pos=(pos_x[i], self.LIKERT_SCALE_LABEL_POS_Y)))
        # response
        if response_keys is None:
            response_keys = [str(i + 1) for i in range(num_options)]
            if num_options == 10:
                response_keys[9] = '0'
        response = self.draw_stimuli_for_response(stimuli, response_keys)
        return response

    def select_from_stimuli(self, stimuli, values, response_keys, max_wait=float('inf'), post_selection_time=1,
                            highlight=None, correctness_func=None, positioned_feedback_stims=(), feedback_stims=(),
                            no_response_stim=None, feedback_time=1):
        """
        Draw stimuli on one screen and wait for a selection (key response). The selected stimulus can be highlighted.
        A feedback stimulus can be optionally displayed next to the selected stimulus.
        The value associated with the selected image (specified as parameters) will be returned.
        :param stimuli: a list of psychopy.visual stimulus
        :param values: a list of objects associated with stimuli. When a stimulus is selected, the value object with
                       the same index will be returned
        :param response_keys: a list of string response keys corresponding to the list of stimuli
        :param max_wait: a numeric value indicating the maximum number of seconds to wait for keys.
                         By default it waits forever
        :param post_selection_time: the duration (in seconds) to display the selected stimulus with a highlight (or
                                    reduced opacity if highlight is None)
        :param highlight: a psychopy.visual stimuli to be displayed at same position as the selected stimulus during
                          both post_selection_time and feedback_time. If None, the selected stimulus will be shown with
                          reduced opacity
        :param correctness_func: a function that takes the value associated with the selected stimuli and returns a bool
                                 indicating whether the selection is correct or not
        :param positioned_feedback_stims: a tuple of two psychopy.visual stimuli (incorrect, correct) to be displayed
                               beside the selection as feedback
        :param feedback_stims: a tuple of either two psychopy.visual stimuli (incorrect, correct), or two lists of them
                               ([incorrect], [correct]) to be displayed at the positions they come with
        :param no_response_stim: a psychopy.visual stimulus to be displayed when participants respond too slow
        :param feedback_time: the duration (in seconds) to display the stimuli with highlight and feedback
        :return: a dictionary containing trial and response information.
        """
        # display stimuli and get response
        response = self.draw_stimuli_for_response(stimuli, response_keys, max_wait)
        if response is None:  # response too slow
            if no_response_stim is None:
                return
            # show feedback and return
            self.draw_stimuli_for_duration(no_response_stim, feedback_time)
            return
        else:
            key_pressed = response[0]
            rt = response[1]
            selection = values[response_keys.index(key_pressed)]

            # post selection screen
            selected_stim = stimuli[response_keys.index(key_pressed)]
            if highlight is None:
                selected_stim.opacity -= self.SELECTED_STIM_OPACITY_CHANGE
                self.draw_stimuli_for_duration(stimuli, post_selection_time)
                selected_stim.opacity += self.SELECTED_STIM_OPACITY_CHANGE
            else:
                highlight.pos = selected_stim.pos
                stimuli.append(highlight)
                self.draw_stimuli_for_duration(stimuli, post_selection_time)

            # feedback
            correct = None
            if correctness_func is not None:
                correct = correctness_func(selection)
                if positioned_feedback_stims is not None and len(positioned_feedback_stims) == 2:
                    pos_stim = positioned_feedback_stims[int(correct)]
                    pos_stim.pos = (selected_stim.pos[0], selected_stim.pos[1] + self.FEEDBACK_POS_Y_DIFF)
                    stimuli.append(pos_stim)
                if feedback_stims is not None and len(feedback_stims) == 2:
                    stims = feedback_stims[int(correct)]
                    if isinstance(stims, visual.BaseVisualStim):
                        stims = [stims]
                    stimuli += stims
                self.draw_stimuli_for_duration(stimuli, feedback_time)

            # return
            if correct is None:
                return {'response': selection, 'rt': rt}
            else:
                return {'response': selection, 'rt': rt, 'correct': correct}

    def select_from_two_stimuli(self, left_stim, left_value, right_stim, right_value, other_stim=None, random_side=True,
                                response_keys=('f', 'j'), max_wait=float('inf'), post_selection_time=1, highlight=None,
                                correctness_func=None, positioned_feedback_stims=(), feedback_stims=(),
                                no_response_stim=None, feedback_time=1):
        """
        Draw 2 stimuli on one screen and wait for a selection (key response). The selected stimulus can be highlighted.
        A feedback stimulus can be optionally displayed next to the selected stimulus.
        The value associated with the selected image (specified as parameters) will be returned.
        :param left_stim: A psychopy.visual stimulus
        :param left_value: an object to be returned when the left_stim is selected
        :param right_stim: Another psychopy.visual stimulus
        :param right_value: an object to be returned when the right_stim is selected
        :param other_stim: an optional list of psychopy.visual stimuli to be displayed
        :param random_side: if True, the images will show on random sides
        :param response_keys: a list of two strings corresponds to left and right images
        :param max_wait: a numeric value indicating the maximum number of seconds to wait for keys.
                         By default it waits forever
        :param post_selection_time: the duration (in seconds) to display the selected stimulus with a highlight (or
                                    reduced opacity if highlight is None)
        :param highlight: a psychopy.visual stimuli to be displayed at same position as the selected stimulus during
                          both post_selection_time and feedback_time. If None, the selected stimulus will be shown with
                          reduced opacity
        :param correctness_func: a function that takes the value associated with the selected stimuli and returns a bool
                                 indicating whether the selection is correct or not
        :param positioned_feedback_stims: a tuple of two psychopy.visual stimuli (incorrect, correct) to be displayed
                               beside the selection as feedback
        :param feedback_stims: a tuple of two lists of psychopy.visual stimuli ([incorrect], [correct]) to be displayed
                               at the positions they have
        :param no_response_stim: a psychopy.visual stimulus to be displayed when participants respond too slow
        :param feedback_time: the duration (in seconds) to display the stimuli with highlight and feedback
        :return: a dictionary containing trial and response information.
        """
        # assign left/right side
        if random_side and random.randrange(2) == 0:  # swap positions
            left_stim, right_stim = right_stim, left_stim
            left_value, right_value = right_value, left_value
        old_left_pos, old_right_pos = left_stim.pos, right_stim.pos
        left_stim.pos = self.LEFT_CENTRAL_POS
        right_stim.pos = self.RIGHT_CENTRAL_POS
        # display stuff and get response
        if other_stim is None:
            other_stim = []
        result = self.select_from_stimuli(other_stim + [left_stim, right_stim], [left_value, right_value],
                                          response_keys, max_wait, post_selection_time, highlight, correctness_func,
                                          positioned_feedback_stims, feedback_stims, no_response_stim, feedback_time)
        # recover previous positions
        left_stim.pos, right_stim.pos = old_left_pos, old_right_pos

        result['stimuli'] = (left_value, right_value)
        return result


class DataHandler:
    def __init__(self, filepath, filename):
        """
        Open file
        :param filepath: a string data file path
        :param filename: a string data file name
        """
        if filepath[len(filepath) - 1] != '/':
            filepath += '/'
        if not os.path.isdir(filepath):
            os.mkdir(filepath)
        elif os.path.isfile(filepath + filename):
            raise IOError(filepath + filename + ' already exists')

        self.dataFile = open(filepath + filename, mode='w')

    def __del__(self):
        """
        Close file
        """
        if hasattr(self, 'dataFile'):
            self.dataFile.close()

    def write_data(self, data):
        """
        Serialize data as a JSON object and write it to file with a newline character at the end
        :param data: a JSON serializable object
        """
        json.dump(data, self.dataFile)
        self.dataFile.write('\n')

    def load_data(self):
        """
        Read the datafile
        :return: a list of Python objects
        """
        return [json.loads(line) for line in self.dataFile]
