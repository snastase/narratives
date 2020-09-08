from os.path import join
from glob import glob
import json
from natsort import natsorted
import pandas as pd
import numpy as np


base_dir = '/jukebox/hasson/snastase/narratives'
preproc_dir = join(base_dir, 'derivatives', 'fmriprep')
afni_dir = join(base_dir, 'derivatives', 'afni-smooth')


# Get our subject list from the BIDS directory
n_subjects = 345
subjects = natsorted([p.split('/')[-2] for p in
                      glob(join(preproc_dir, 'sub-*/'))])


# Check that we're not missing subjects
for n, subject in zip(range(1, n_subjects + 1), subjects):
    if subject != f"sub-{n:03}":
        raise AssertionError("Found a mismatching subject: "
                             f"{subject} (expected sub-{n:03})")


# Create a dictionary containing filenames keyed to subjects
spaces = ['MNI152NLin2009cAsym', 'fsaverage6']
width = 'sm6'
subject_meta = {}
for subject in subjects:
    subject_meta[subject] = {'bold': {},
                             'confounds': []}

    # Grab confounds TSV file
    confound_fns = glob(join(preproc_dir, subject, 'func',
                             f'{subject}*desc-confounds'
                             '_regressors.tsv'))
    subject_meta[subject]['confounds'] = confound_fns

    # Grab either volumetric or surface-based BOLD filenames
    for space in spaces:
        if space[:2] == 'fs':
            preproc_fns = glob(join(preproc_dir, subject, 'func',
                                    f'{subject}*space-{space}*func.gii'))
            assert len(preproc_fns) == 2 * len(confound_fns)
            
            smooth_fns = glob(join(afni_dir, subject, 'func',
                                   (f'{subject}*space-{space}*'
                                    f'desc-{width}*func.gii')))
            
        else:
            preproc_fns = glob(join(preproc_dir, subject, 'func',
                                    f'{subject}*space-{space}*desc-'
                                 'preproc_bold.nii.gz'))
            assert len(preproc_fns) == len(confound_fns)

            smooth_fns = glob(join(afni_dir, subject, 'func',
                                   (f'{subject}*space-{space}*'
                                    f'desc-{width}*_bold.nii.gz')))

        subject_meta[subject]['bold'][space] = {'preproc': preproc_fns,
                                                width: smooth_fns}

# Save the subject metadata dictionary
with open(join(base_dir, 'code', 'subject_meta.json'), 'w') as f:
    json.dump(subject_meta, f, indent=2, sort_keys=True)


# Compile task list from BIDS data
tasks = []
for subject in subject_meta:
    for confound_fn in subject_meta[subject]['confounds']:
        task = confound_fn.split('task-')[-1].split('_')[0]
        if task not in tasks:
            tasks.append(task)

tasks = natsorted(tasks)

# Create a dictionary of filenames keyed to tasks for convenience
task_meta = {}
descs = ['preproc', 'sm6']
for task in tasks:
    task_meta[task] = {}
    for subject in subject_meta:

        # Check that subject received task and setup dictionary
        has_task = False
        for confound_fn in subject_meta[subject]['confounds']:
            if f"task-{task}_" in confound_fn:
                task_meta[task][subject] = {'bold': {},
                                            'confounds': []}
                has_task = True

        # Ugly redundant loop but c'est la vie!
        if has_task:
            for confound_fn in subject_meta[subject]['confounds']:
                if f"task-{task}_" in confound_fn:
                    task_meta[task][subject]['confounds'].append(
                        confound_fn)
            for space in subject_meta[subject]['bold']:
                task_meta[task][subject]['bold'][space] = {}
                for desc in descs:
                    task_meta[task][subject]['bold'][space][desc] = []
                    for bold_fn in subject_meta[subject]['bold'][space][desc]:
                        if f"task-{task}_" in bold_fn:
                            task_meta[task][subject]['bold'][space][
                                desc].append(bold_fn)
                            
            # Load in group/condition variables; important for
            # splitting ISC analysis for e.g. milkyway, prettymouth
            scans_fn = join(base_dir, subject, f'{subject}_scans.tsv')
            scans_tsv = pd.read_csv(scans_fn, sep='\t',
                                    keep_default_na=False)
            conditions = scans_tsv[scans_tsv['filename'].str.contains(
                            f'{subject}_task-{task}_')]['condition'].values
            assert np.all(conditions == conditions[0])
            condition = conditions[0]
            task_meta[task][subject]['condition'] = condition

# Save the task metadata dictionary
with open(join(base_dir, 'code', 'task_meta.json'), 'w') as f:
    json.dump(task_meta, f, indent=2, sort_keys=True)


# Get onsets and durations from events.tsv for trimming
tr = 1.5

event_meta = {}
for task in task_meta:

    # Skip 'schema' task for simplicity
    if task == 'schema':
        continue

    for subject in task_meta[task]:
        events_fns = glob(join(base_dir, subject, 'func',
                               f'{subject}_task-{task}_*events.tsv'))
        for events_fn in events_fns:
            events = pd.read_csv(events_fn, sep='\t')
            story = events[events['trial_type'] == 'story']

            # Populate with first subject's events values
            if task not in event_meta:
                event_meta[task] = {}

                if task == 'schema':
                    pass

                elif task == 'slumlordreach':
                    event_meta[task]['slumlord'] = {
                        'onset': int(np.rint(story.iloc[0]['onset'] / tr)),
                        'duration': int(np.rint(story.iloc[0]['duration'] / tr))}
                    event_meta[task]['reach'] = {
                        'onset': int(np.rint(story.iloc[1]['onset'] / tr)),
                        'duration': int(np.rint(story.iloc[1]['duration'] / tr))}

                else:
                    event_meta[task][task] = {
                        'onset': int(np.rint(story.iloc[0]['onset'] / tr)),
                        'duration': int(np.rint(story.iloc[0]['duration'] / tr))}

            # Check subsequent subjects for oddities
            else:
                if task != 'slumlordreach':
                    new_onset = int(np.rint(story.iloc[0]['onset'] / tr))
                    if event_meta[task][task]['onset'] != new_onset:
                        print(f"{subject} has unexpected events: {story}"
                              f"  expected {event_meta[task][task]}")

    print(f"Finished compiling event onsets for {task}")

with open(join(base_dir, 'code', 'event_meta.json'), 'w') as f:
    json.dump(event_meta, f, indent=2, sort_keys=True)


# Get some summary number of runs
n_scans = sum([len(subject_meta[s]['confounds'])
               for s in subject_meta])

# Check that task metadata matches up
n_scans_task = []
for task in task_meta:
    for subject in task_meta[task]:
        n_scans_task.append(
            len(task_meta[task][subject]['confounds']))
n_scans_task = sum(n_scans_task)

assert n_scans == n_scans_task
print(f"Total number of scans: {n_scans}")
