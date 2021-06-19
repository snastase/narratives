#!/usr/bin/env python

# Run this from the command line from storyteller/scripts/ directory using, e.g.:
#   export PATH=/Users/hasson/Desktop/snastase/miniconda2/bin:$PATH
#   conda activate sam
#   ./story_presentation.py 1 bronx .5

from sys import argv
import time
from os.path import exists, join
from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']
prefs.general['audioDriver'] = ['coreaudio']
prefs.general['audioDevice'] = ['Built-in Line Output']
from psychopy import core, event, logging, sound, visual

subject = int(argv[1])
story = argv[2]
volume = float(argv[3])

# Start PsychoPy's clock (mostly for logging)
run_clock = core.Clock()

# Set up PsychoPy's logging function
if exists(join('logs', 'listener_log_sub-{0:02d}_{1}.txt'.format(
                subject, story))):
    print("Log file already exists for this subject and story!!!")
    #win.close()
    #core.quit()

logging.setDefaultClock(run_clock)
log = logging.LogFile(f=join('logs', 'listener_log_sub-{0:02d}_{1}.txt'.format(
                          subject, story)), level=logging.INFO,
                      filemode='w')
initial_message = ("Starting storyteller experiment with listener "
                   "subject {0}, {1} story, {2}".format(subject,
                       story, time.ctime()))
logging.exp(initial_message)

# Set up function to check keyboard inputs
def proceed_keys(keys, wait):
    if 'space' in keys or 'return' in keys:
        wait = False
    return wait

def quit_keys(keys, stimulus=None):
    if 'q' in keys or 'escape' in keys:
        wait = False
        quitting = ('Quit command ("q" or "escape") was detected! '
                    'Quitting experiment')
        logging.info(quitting)
        print(quitting)
        if stimulus:
            stimulus.stop()
        win.close()
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

# Load audio story stimulus
stimulus = sound.Sound(join('stimuli', '{0}_audio.wav'.format(story)), stereo=False, volume=volume, name=story)
loaded_stimulus = "Successfully loaded {0} audio story stimulus".format(story)
logging.info(loaded_stimulus)

duration = stimulus.duration
stimulus_duration = "Duration for {0} stimulus is {1}".format(story, duration)

# Open window and provide instructions
win = visual.Window([1280, 720], screen=1, fullscr=True, color=0, name='Window')

instructions = visual.TextStim(win, pos=[-.625, .575], wrapWidth=1.3,
                               alignHoriz='left', alignVert='top',
                               name='Instructions', text=("Listen "
                               "closely to the following story. "
                               "Try to keep still until the end "
                               "of the scan."))
instructions.draw()
win.flip()
        
instructions_wait = True
while instructions_wait:
    keys = event.getKeys()
    instructions_wait = proceed_keys(keys, instructions_wait)
    quit_keys(keys)
logging.info("Finished instructions")

# Wait for scanner trigger (or keyboard)
waiting = visual.TextStim(win, pos=[0, 0], text="Waiting for scanner...",
                          name="Waiting")
waiting.draw()
win.flip()

scanner_wait = True
while scanner_wait:
    keys = event.getKeys()
    scanner_wait = scanner_keys(keys, wait=scanner_wait)
    quit_keys(keys)

# Set run start time and reset PsychoPy's core.Clock() on first trigger
first_trigger = "Got first scanner trigger! Resetting clocks"
run_start = time.time()
run_clock.reset()
logging.info(first_trigger)

# Start fixation after scanner trigger
fixation = visual.TextStim(win, pos=(0, 0), text="+", name="Fixation")
fixation.draw()
win.flip()

# Wait 12 seconds (no-slip) then start story
fixation.draw()
win.flip()
while time.time() - run_start < 12.0:
    keys = event.getKeys()
    scanner_keys(keys)
    quit_keys(keys)
    
# Start the auditory story stimulus
stimulus.play()
story_start = time.time()
starting_story = "Starting story stimulus"
logging.info(starting_story)

while time.time() - story_start <= duration:
    keys = event.getKeys()
    scanner_keys(keys)
    quit_keys(keys, stimulus=stimulus)
    
# Wait 12 seconds and then finish
while time.time() - run_start <= 12 + duration + 12:
    keys = event.getKeys()
    scanner_keys(keys)
    quit_keys(keys)
    
finished = "Finished run successfully!"
logging.info(finished)
print(finished)

win.close()
core.quit()
