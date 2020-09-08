from os.path import basename, join
import json
from glob import glob
import numpy as np
from scipy.stats import zscore
from natsort import natsorted
from brainiak.isc import (isc, _check_timeseries_input,
                          compute_summary_statistic)
from exclude_scans import exclude_scan
import matplotlib.pyplot as plt
import seaborn as sns


space = 'fsaverage6'
roi = 'EAC'
afni_pipe = 'afni-nosmooth'
initial_trim = 6
lags = 30

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


# Function for computing ISCs at varying lags
def lagged_isc(data, lags=20, circular=True,
               subjects=None, summary_statistic=None):
    
    # Check response time series input format
    data, n_TRs, n_voxels, n_subjects = _check_timeseries_input(data)
        
    # If lag is integer, get positive and negative range around zero
    if type(lags) is int:
        lags = np.arange(-lags, lags + 1)

    # Iterate through lags to populate lagged ISCs
    lagged_iscs = []
    for lag in lags:

        lagged_isc = []
        for s in np.arange(n_subjects):
            
            lagged_subject = data[..., s]
            lagged_mean = np.mean(np.delete(data, s, 2), axis=2)
            
            # If circular, loop excess elements to beginning
            if circular:
                if lag != 0:
                    lagged_subject = np.concatenate((lagged_subject[-lag:, :],
                                                     lagged_subject[:-lag, :]))
                    
            # If not circular, trim non-overlapping elements
            # Shifts y with respect to x
            else:
                if lag < 0:
                    lagged_subject = lagged_subject[:lag, :]
                    lagged_mean = lagged_mean[-lag:, :]
                elif lag > 0:
                    lagged_subject = lagged_subject[lag:, :]
                    lagged_mean = lagged_mean[:-lag, :]
                    
            loo_isc = isc(np.dstack((lagged_subject, lagged_mean)))
            lagged_isc.append(loo_isc)
            
        lagged_iscs.append(np.dstack(lagged_isc))
    
    lagged_iscs = np.vstack(lagged_iscs)
    
    # Compute lag for maximum ISC per subject
    peak_lags = []
    for lagged_subject in np.moveaxis(lagged_iscs, 2, 0):
        np.argmax(lagged_subject)
        peak_lags.append(int(lags[np.argmax(lagged_subject)]))
    if subjects:
        peak_lags = {subject: peak_lag for subject, peak_lag
                     in zip(subjects, peak_lags)}
        
    # Optionally summarize across subjects
    if summary_statistic:
        lagged_iscs = compute_summary_statistic(lagged_isc,
                            summary_statistic=summary_statistic,
                            axis=2)
    
    return lagged_iscs, peak_lags


# Helper function for visualizing lagged ISCs
def plot_lagged_correlation(correlations, lags=None, save_fn=None,
                            title=None):

    # Get number of correlations (voxels or subjects)
    n_samples = correlations.shape[-1]
    
    # If no lags provided, infer from input correlations
    if not lags:
        lags = (correlations.shape[0] - 1) // 2
        
    # If lag is integer, get positive and negative range around zero
    if type(lags) is int:
        lags = np.arange(-lags, lags + 1)

    # Make sure lags match the input correlations
    assert len(lags) == correlations.shape[0]

    # Simple plotting
    sns.set_style('white')
    sns.set_style('ticks')
    plt.plot(correlations, alpha=.5)
    plt.xticks(np.arange(len(lags))[::len(lags) // 10],
               lags[::len(lags) // 10])
    plt.ylim(-.4, .8)
    plt.xlabel('lag (TRs)')
    plt.ylabel('auditory ISC')
    plt.title(title, loc='right', y=.95, x=.95)
    sns.despine(trim=True, offset=5)
    plt.tight_layout()
    if save_fn:
        plt.savefig(save_fn, dpi=300)
    plt.show()
        

# Compile ROI lagged ISCs across all subjects
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
            results[subtask][hemi] = {'lagged ISCs': {},
                                      'peak lags': {}}
            
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

                # Compute lagged ISCs
                lagged_iscs, peak_lags = lagged_isc(data, lags=lags)
                lagged_iscs = np.squeeze(lagged_iscs)
                
                # Print group-specific ISC notification
                if group:
                    print(f"Within-group lagged ISC computed for "
                          f"{task} ({hemi}): {group}")

                # Plot lags
                if group:
                    plot_title = f"lagged ISC: {subtask} ({group}; {hemi})"
                else:
                    plot_title = f"lagged ISC: {subtask} ({hemi})"
                plot_lagged_correlation(lagged_iscs, title=plot_title)

                # Convert ISCs into subject-keyed dictionary
                assert (len(subject_list) == len(run_list) ==
                        lagged_iscs.shape[1] == len(peak_lags))

                isc_dict, peak_dict = {}, {}
                for s, fn, r, p in zip(subject_list, run_list,
                                       lagged_iscs.T, peak_lags):
                    if s not in isc_dict:
                        isc_dict[s] = {fn: r.tolist()}
                    else:
                        isc_dict[s][fn] = r.tolist()

                    if s not in peak_dict:
                        peak_dict[s] = {fn: p}
                    else:
                        peak_dict[s][fn] = p
                        
                # Using update method to concatenate groups
                results[subtask][hemi]['lagged ISCs'].update(isc_dict)
                results[subtask][hemi]['peak lags'].update(peak_dict)


# Save results to disk
results_fn = join(afni_dir, f'group_roi-{roi}_desc-exclude_lags.json')
with open(results_fn, 'w') as f:
    json.dump(results, f, indent=2, sort_keys=True)
