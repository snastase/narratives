from os.path import basename, join
import json
from glob import glob
import numpy as np
from scipy.stats import pearsonr, zscore
from brainiak.isc import isc
from natsort import natsorted
from exclude_scans import exclude_scan
from gifti_io import read_gifti, write_gifti

space = 'fsaverage6'
afni_pipe = 'afni-smooth'
initial_trim = 6

base_dir = '/jukebox/hasson/snastase/narratives'
deriv_dir = join(base_dir, 'derivatives')
preproc_dir = join(deriv_dir, 'fmriprep')
afni_dir = join(base_dir, 'derivatives', afni_pipe)


# Get metadata for all subjects for a given task
with open(join(base_dir, 'code', 'task_meta.json')) as f:
    task_meta = json.load(f)


# Get event onsets and durations for each task
with open(join(base_dir, 'code', 'event_meta.json')) as f:
    event_meta = json.load(f)

    
# Load scans to exclude
exclude = True
with open(join(base_dir, 'code', 'scan_exclude.json')) as f:
    scan_exclude = json.load(f)
        

# Skip 'notthefall' scramble and 'schema' tasks for simplicity
skip_tasks = ['notthefalllongscram', 'notthefallshortscram',
              'schema']


# Compile whole-brain ISCs across all subjects
for task in task_meta:
    
    # Skip 'schema' task for simplicity
    if task in skip_tasks:
        print(f"Skipping {task} for whole-brain ISC analysis")
        continue
    
    # Split off 'slumlordreach' stories
    if task == 'slumlordreach':
        subtasks = ['slumlord', 'reach']
        
    else:
        subtasks = [task]
        
    # Loop through potential substories (i.e. for 'slumlordreach')
    for subtask in subtasks:

        # Split milkyway and prettymouth by condition/group;
        # note that this means we're implicitly ignoring the
        # naive vs non-naive listening conditions of merlin,
        # sherlock, shapesphysical, shapessocial, notthefall
        if task == 'milkyway':
            groups = ['original', 'vodka', 'synonyms']
        elif task == 'prettymouth':
            groups = ['affair', 'paranoia']
        else:
            groups = [None]

        # Grab event onsets and offsets for trimming
        onset = event_meta[task][subtask]['onset']
        offset = onset + event_meta[task][subtask]['duration']

        # Get a convenience subject list for this task
        subjects = sorted(task_meta[task].keys())

        # Loop through hemispheres
        for hemi in ['L', 'R']:
            
            # Loop through potential group manipulations (milkyway, paranoia)
            for group in groups:
                
                # Create lists for storing subjects and run filenames
                subject_list, run_list = [], []
                data = []
                for subject in subjects:

                    # Skip the subjects not belonging to this group
                    if group and group != task_meta[subtask][
                                              subject]['condition']:
                        continue
                    
                    data_dir = join(afni_dir, subject, 'func')

                    bold_fns = natsorted(glob(join(data_dir,
                                  (f'{subject}_task-{task}_*space-{space}_'
                                   f'hemi-{hemi}_desc-clean.func.gii'))))

                    # Grab all runs in case of multiple runs
                    for bold_fn in bold_fns:

                        if exclude and exclude_scan(bold_fn, scan_exclude):
                            print(f"Excluding {basename(bold_fn)}!")
                            continue

                        else:

                            # Strip comments and load in data as numpy array
                            subj_data = read_gifti(bold_fn)

                            # Trim data based on event onset and duration
                            subj_data = subj_data[onset:offset, :]
                            subj_data = subj_data[initial_trim:, :]

                            # Z-score input time series
                            subj_data = zscore(subj_data, axis=0)

                            subject_list.append(subject)
                            run_list.append(basename(bold_fn))
                            data.append(subj_data)
                            print(f"Loaded {subtask} {subject} "
                                  f"({hemi}) for ISC analysis")

                data = np.dstack(data)
                
                # Print group-specific ISC notification
                if group:
                    print(f"Computing within-group ISCs for {task} "
                          f"({hemi}): {group}")

                # Compute ISCs
                print(f"Started ISC analysis for {subtask} ({hemi})")
                iscs = isc(data)
                print(f"Finished ISC analysis for {subtask} ({hemi})")

                # Split ISCs into subject-/run-specific GIfTI files
                assert len(subject_list) == len(run_list) == len(iscs)
                for s, fn, r in zip(subject_list, run_list, iscs):
                    isc_fn = join(afni_dir, s, 'func',
                                  fn.replace('_desc-clean.func.gii',
                                             '_isc.gii').replace(
                                  f'task-{task}', f'task-{subtask}'))
                    template_fn = join(afni_dir, s, 'func', fn)
                    write_gifti(r, isc_fn, template_fn)
                    print(f"Saved {subtask} {s} ({hemi}) ISC")


# Custom mean estimator with Fisher z transformation for correlations
def fisher_mean(correlation, axis=None):
    return np.tanh(np.nanmean(np.arctanh(correlation), axis=axis))


# Compute mean ISC maps per task
for hemi in ['L', 'R']:

    global_isc = []
    for task in task_meta:

        # Skip 'schema' task for simplicity
        if task in skip_tasks:
            print(f"Skipping {task} for whole-brain ISC analysis")
            continue

        # Split off 'slumlordreach' stories
        if task == 'slumlordreach':
            subtasks = ['slumlord', 'reach']

        else:
            subtasks = [task]

        # Loop through potential substories (i.e. for 'slumlordreach')
        for subtask in subtasks:

            # Get a convenience subject list for this task
            subjects = sorted(task_meta[task].keys())
            
            # Stack data across subjects per task
            task_isc = []
            for subject in subjects:

                data_dir = join(afni_dir, subject, 'func')

                isc_fns = natsorted(glob(join(data_dir,
                              (f'{subject}_task-{subtask}_*space-{space}_'
                               f'hemi-{hemi}_isc.gii'))))

                # Grab all runs in case of multiple runs
                for isc_fn in isc_fns:

                    if exclude and exclude_scan(isc_fn, scan_exclude):
                        print(f"Excluding {basename(isc_fn)}!")
                        continue

                    else:
                        subj_isc = read_gifti(isc_fn)
                        task_isc.append(subj_isc)
                        global_isc.append(subj_isc)
                        print(f"Loaded ISC map for {task} {subject}")

            # Fisher Z-transformed mean across subjects
            task_mean = fisher_mean(task_isc, axis=0)[0, :]
            
            # Save mean ISC map
            task_fn = join(afni_dir, f'group_task-{subtask}_space-{space}_'
                                     f'hemi-{hemi}_desc-mean_isc.gii')
            write_gifti(task_mean, task_fn, isc_fns[0])
            print(f"Computed mean ISC for {subtask} ({hemi})")
            
    # Get the global mean across all subjects and tasks
    print(f"Computing global mean ISC across {len(global_isc)} subjects")
    global_mean = fisher_mean(global_isc, axis=0)[0, :]
    
    # Save mean ISC map
    global_fn = join(afni_dir, f'group_space-{space}_'
                               f'hemi-{hemi}_desc-mean_isc.gii')
    write_gifti(global_mean, global_fn, isc_fns[0])
    print(f"Computed global mean ISC ({hemi})")


# Combine 'slumlord' and 'reach' means
for hemi in ['L', 'R']:    
    slumlord_fn = join(afni_dir, f'group_task-slumlord_space-{space}_'
                                 f'hemi-{hemi}_desc-mean_isc.gii')
    reach_fn = join(afni_dir, f'group_task-reach_space-{space}_'
                              f'hemi-{hemi}_desc-mean_isc.gii')
    
    # Compute mean of 'slumlord' and 'reach' means
    comb_isc = fisher_mean((read_gifti(slumlord_fn),
                            read_gifti(reach_fn)), axis=0)[0, :]
    
    # Save combined map
    comb_fn = join(afni_dir, f'group_task-slumlordreach_space-{space}_'
                             f'hemi-{hemi}_desc-mean_isc.gii')
    write_gifti(comb_isc, comb_fn, slumlord_fn)
    print("Computed combined mean 'slumlordreach' ISC map")
