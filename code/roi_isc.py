from os.path import basename, join
import json
from glob import glob
import numpy as np
from scipy.stats import pearsonr, zscore
from brainiak.isc import isc
from natsort import natsorted
from exclude_scans import exclude_scan

space = 'fsaverage6'
roi = 'EAC'
afni_pipe = 'afni-nosmooth'
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


# Helper function to load in AFNI's 3dTproject 1D outputs
def load_1D(fn):
    with open(fn) as f:
        lines = [line.strip().split(' ') for line in f.readlines()
                 if '#' not in line]
    assert len(lines) == 1
    return np.array(lines[0]).astype(float)
        

# Compile ROI ISCs across all subjects
results = {}
for task in task_meta:
    
    # Skip 'schema' task for simplicity
    if task == 'schema':
        continue
    
    # Split off 'slumlordreach' stories
    if task == 'slumlordreach':
        subtasks = ['slumlord', 'reach']
        
    else:
        subtasks = [task]
        
    # Loop through potential substories (i.e. for 'slumlordreach')
    for subtask in subtasks:
        results[subtask] = {}
        
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
            results[subtask][hemi] = {}
        
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

                    roi_fns = natsorted(glob(join(data_dir,
                                  (f'{subject}_task-{task}_*space-{space}_'
                                   f'hemi-{hemi}_roi-{roi}_desc-clean_'
                                   'timeseries.1D'))))

                    # Grab all runs in case of multiple runs
                    for roi_fn in roi_fns:
                        
                        if exclude and exclude_scan(roi_fn, scan_exclude):
                            print(f"Excluding {basename(roi_fn)}!")
                            continue

                        else:

                            # Strip comments and load in data as numpy array
                            subj_data = load_1D(roi_fn)

                            # Trim data based on event onset and duration
                            subj_data = subj_data[onset:offset]
                            subj_data = subj_data[initial_trim:]

                            # Z-score input time series
                            subj_data = zscore(subj_data)

                            subject_list.append(subject)
                            run_list.append(basename(roi_fn))
                            data.append(subj_data)

                data = np.column_stack(data)

                # Compute ISCs
                iscs = isc(data).flatten()
                
                # Print group-specific ISC notification
                if group:
                    print(f"Within-group ISC computed for {task} "
                          f"({hemi}): {group}")

                # Print mean and SD
                print(f"Mean {hemi} {roi} ISC for {subtask} = "
                      f"{np.mean(iscs):.3f} (SD = {np.std(iscs):.3f})")

                # Convert ISCs into subject-keyed dictionary
                assert len(subject_list) == len(run_list) == len(iscs)
                isc_dict = {}
                for s, fn, r in zip(subject_list, run_list, iscs):
                    if s not in isc_dict:
                        isc_dict[s] = {fn: r}
                    else:
                        isc_dict[s][fn] = r

                # Using update method to concatenate groups
                results[subtask][hemi].update(isc_dict)


# Save results to disk
results_fn = join(afni_dir, f'group_roi-{roi}_desc-exclude_isc.json')
with open(results_fn, 'w') as f:
    json.dump(results, f, indent=2, sort_keys=True)
