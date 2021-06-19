#!/usr/bin/env python

# Run this from the command line from storyteller/scripts/ directory using, e.g.:
#   ./soundcheck_presentation.py stimuli/bronx_clean.wav .5

import sys
import time
from os.path import exists, join
from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']
prefs.general['audioDriver'] = ['coreaudio']
prefs.general['audioDevice'] = ['Built-in Line Output']
from psychopy import core, event, logging, sound, visual
print sound.Sound

# Command line arguments for audio file and initial volume
audio_fn = sys.argv[1]
volume = float(sys.argv[2])

# Reduce verbosity of PsychoPy logging
logging.console.setLevel(logging.DATA)

# Set up function to check keyboard inputs
def proceed_keys(keys, wait):
    if '1' in keys:
        wait = False
    return wait

def quit_keys(keys, stimulus=None, message=None):
    if 'q' in keys or 'escape' in keys:
        wait = False
        if stimulus:
            stimulus.stop()
        logging.flush()
        win.close()
        if message:
            print(message)
        core.quit()

def scanner_keys(keys, wait=False):
    if 'equal' in keys:
        logging.info('Trigger received')
        wait = False
    if '1' in keys:
        logging.data('Response 1')
    if '2' in keys:
        logging.data('Response 2')
    if '3' in keys:
        logging.data('Response 3')
    if '4' in keys:
        logging.data('Response 4')
    return wait

# Load audio story stimulus at mid-volume
stimulus = sound.Sound(audio_fn, stereo=False,
                       volume=volume, name=audio_fn)

# Open window and provide instructions
win = visual.Window([1280, 720], screen=0, fullscr=True, color=0, name='Window')

instructions = visual.TextStim(win, pos=[-.625, .575], wrapWidth=1.3,
                               alignHoriz='left', alignVert='top', name='Instructions',
                               text=("Use the buttons to adjust the volume until "
                                     "you can hear and understand clearly. "
                                     "Button 1 is closest to the cord and button "
                                     "4 is farthest from the cord."))

buttons = visual.TextStim(win, pos=[0, .075], wrapWidth=1.5,
                          alignHoriz='center', alignVert='top', name='Button list',
                          text=("button 1: volume +\n"
                                "button 2: volume -\n"
                                "button 4: finished"))

ready = visual.TextStim(win, pos=[0, -.4], wrapWidth=1,
                        alignHoriz='center', alignVert='top',
                        text="Ready?")
ready_button = visual.TextStim(win, pos=[0, -.55], alignHoriz='center',
                               text="(press button 1 to continue)")

instructions.draw()
buttons.draw()
ready.draw()
ready_button.draw()
win.flip()

subject_wait = True
while subject_wait:
    keys = event.getKeys()
    subject_wait = proceed_keys(keys, wait=subject_wait)
    quit_keys(keys)
    
# Wait for scanner trigger (or keyboard)
waiting = visual.TextStim(win, pos=[0, -.5], text="Waiting for scanner...",
                          name="Waiting")
instructions.draw()
buttons.draw()
waiting.draw()
win.flip()

scanner_wait = True
while scanner_wait:
    keys = event.getKeys()
    scanner_wait = scanner_keys(keys, wait=scanner_wait)
    quit_keys(keys)

volume_scale = visual.RatingScale(win, low=0, high=20, markerStart=volume*20,
                                  precision=1, noMouse=True, leftKeys='2',
                                  rightKeys='1', acceptKeys='4',
                                  scale=None, disappear=True, showValue=False,
                                  acceptText="finished?", acceptPreText="finished?",
                                  name="Volume scale")
stimulus.play()
while volume_scale.noResponse:
    instructions.draw()
    buttons.draw()
    volume_scale.draw()
    win.flip()
    volume = volume_scale.getRating()/20.
    stimulus.volume = volume
stimulus.stop()

soundcheck_finished = visual.TextStim(win, pos=[0, 0], wrapWidth=1,
                                      alignHoriz='center', alignVert='top',
                                      text="Sound check finished!")
soundcheck_finished.draw()
win.flip()

final_volume = """\n
================================
Subject's volume selection: {0:.2f}
================================\n
""".format(volume)

quit_wait = True
while quit_wait:
    keys = event.getKeys()
    quit_keys(keys, message=final_volume)
