from os.path import basename


# Function to check if scan should be excluded
def exclude_scan(bids_fn, scan_exclude):
    """Checks whether filename should be excluded given exclusion dictionary

    Parameters
    ----------
    bids_fn : str
        BIDS-formatted filename to be checked for exclusion
    scan_exclude : dict
        Dictionary of scans to exclude (e.g. loaded from scan_exclude.json)

    Returns
    -------
    bool
        True if scan should be excluded, otherwise False

    Examples
    --------
    >>> with open('scan_exclude.json') as f:
            scan_exclude = json.load(f)
    >>> bold_fn = '/path/to/sub-001_task-pieman_run-1_bold.nii.gz'
    >>> if not exclude_scan(bold_fn, scan_exclude):
            print(f'Including scan {bold_fn}, continue analysis...')
        else:
            print(f'Excluding scan {bold_fn}')
        Excluding scan /path/to/sub-001_task-pieman_run-1_bold.nii.gz

    """
    
    # Flatten input dictionary for simplicity
    exclude_list = []
    for task in scan_exclude:
        if len(scan_exclude[task].keys()) > 0:
            exclude_list.extend([r for s in 
                                 list(scan_exclude[task].values())
                                 for r in s])

    # Check exclusion strings against BIDS input filename
    for exclude_fn in exclude_list:
        if exclude_fn in basename(bids_fn):
            exclude = True
            break
        else:
            exclude = False

    return exclude


# Name guard for when we want to compile exclusion lists via ISC
if __name__ == '__main__':

    from os.path import join
    import json
    from natsort import natsorted
    from glob import glob
    import numpy as np
    from scipy.stats import pearsonr, zscore
    from brainiak.isc import isc

    base_dir = '/jukebox/hasson/snastase/narratives'
    afni_dir = join(base_dir, 'derivatives', 'afni-nosmooth')

    # Set up some subjects to exclude a priori due to
    # e.g. mismatching TRs, poor behavior, noncompliance
    # Store task, subject, and BIDS filename root (w/ e.g. run)
    scan_exclude = {'pieman': {},
                    'tunnel': {
                        'sub-004': ['sub-004_task-tunnel'],
                        'sub-013': ['sub-013_task-tunnel']},
                    'lucy': {},
                    'prettymouth': {
                        'sub-038': ['sub-038_task-prettymouth'],
                        'sub-105': ['sub-105_task-prettymouth']},
                    'milkyway': {
                        'sub-038': ['sub-038_task-milkyway'],
                        'sub-105': ['sub-105_task-milkyway'],
                        'sub-123': ['sub-123_task-milkyway']},
                    'slumlordreach': {
                        'sub-139': ['sub-139_task-slumlordreach']},
                    'notthefallintact': {},
                    'notthefalllongscram': {},
                    'notthefallshortscram': {},
                    'merlin': {},
                    'sherlock': {},
                    'schema': {},
                    'shapesphysical': {},
                    'shapessocial': {},
                    '21styear': {},
                    'bronx': {},
                    'piemanpni': {},
                    'black': {},
                    'forgot': {}}
    
    # Save a priori exclusion for initial ISC calculation
    with open(join(base_dir, 'code', 'scan_exclude.json'), 'w') as f:
        json.dump(scan_exclude, f, indent=2, sort_keys=True)


    # Create exclusion based on peak lags
    roi = 'EAC'
    hemi = 'L'
    lags = 30
    threshold = 3

    # Load in lagged ISC results
    results_fn = join(afni_dir, f'group_roi-{roi}_lags.json')
    with open(results_fn) as f:
        results = json.load(f)

    lag_exclude = {}
    exclude_count = 0
    for task in results:
        lag_exclude[task] = {}
        for subject in results[task][hemi]['peak lags']:
            for run in results[task][hemi]['peak lags'][subject]:
                peak_lag = results[task][hemi]['peak lags'][subject][run]
                if abs(peak_lag) > threshold:
                    exclude_count += 1
                    if subject not in lag_exclude[task]:
                        lag_exclude[task][subject] = [basename(run).split(
                            '_space')[0]]
                    else:
                        lag_exclude[task][subject].append(basename(run).split(
                            '_space')[0])
                    print(f"Excluding {task} {subject} with "
                          f"peak lag {peak_lag}")

    print(f"Excluding {exclude_count} with peak lags > {threshold} TRs")


    # Specifically check pieman subjects with multiple runs
    task, subtask = 'pieman', 'pieman'
    space = 'fsaverage6'
    roi = 'EAC'
    hemi = 'L'
    initial_trim = 6
    threshold = 0.1

    # Helper function to load in AFNI's 3dTproject 1D outputs
    def load_1D(fn):
        with open(fn) as f:
            lines = [line.strip().split(' ') for line in f.readlines()
                     if '#' not in line]
        assert len(lines) == 1
        return np.array(lines[0]).astype(float)

    with open(join(base_dir, 'code', 'task_meta.json')) as f:
        task_meta = json.load(f)

    with open(join(base_dir, 'code', 'event_meta.json')) as f:
        event_meta = json.load(f)

    one_runs = []
    multi_runs = {}
    for subject in task_meta[task]:

        # Grab event onsets and offsets for trimming
        onset = event_meta[task][subtask]['onset']
        offset = onset + event_meta[task][subtask]['duration']

        data_dir = join(afni_dir, subject, 'func')

        roi_fns = natsorted(glob(join(data_dir,
                      (f'{subject}_task-{task}_*space-{space}_'
                       f'hemi-{hemi}_roi-{roi}_desc-clean_'
                       'timeseries.1D'))))

        # Grab subjects with only one run
        if len(roi_fns) == 1:

            roi_fn = roi_fns[0]

            # Strip comments and load in data as numpy array
            subj_data = load_1D(roi_fn)

            # Trim data based on event onset and duration
            subj_data = subj_data[onset:offset]
            subj_data = subj_data[initial_trim:]

            # Z-score input time series
            subj_data = zscore(subj_data)

            one_runs.append(subj_data)

        # Grab subjects with multiple runs for later
        elif len(roi_fns) > 1:

            multi_runs[subject] = {}
            for roi_fn in roi_fns:

                # Strip comments and load in data as numpy array
                subj_data = load_1D(roi_fn)

                # Trim data based on event onset and duration
                subj_data = subj_data[onset:offset]
                subj_data = subj_data[initial_trim:]

                # Z-score input time series
                subj_data = zscore(subj_data)

                multi_runs[subject][roi_fn] = subj_data        

    # Get a clean average pieman template time series for comparison
    one_runs = np.column_stack(one_runs)
    one_clean = one_runs[:, isc(one_runs).flatten() >= threshold]
    one_avg = np.mean(one_clean, axis=1)

    # Check correlation of each run against average
    pieman_exclude = {task: {}}
    for subject in multi_runs:
        for run in multi_runs[subject]:
            r = pearsonr(one_avg, multi_runs[subject][run])[0]

            if r < threshold:
                if subject not in pieman_exclude:
                    pieman_exclude[task][subject] = [basename(run).split(
                        '_space')[0]]
                else:
                    pieman_exclude[task][subject].append(
                        basename(run).split('_space')[0])

            print(f"{subject} correlation with template = {r}\n"
                  f"  {basename(run)}")


    # Load in existing resuls
    results_fn = join(afni_dir, f'group_roi-{roi}_isc.json')
    with open(results_fn) as f:
        results = json.load(f)

    # Create exclusion based on ROI ISC   
    hemi = 'L'
    threshold = .1

    isc_exclude = {}
    exclude_count = 0
    for task in results:
        isc_exclude[task] = {}
        for subject in results[task][hemi]:
            for run in results[task][hemi][subject]:
                roi_isc = results[task][hemi][subject][run]
                if roi_isc < threshold:
                    exclude_count += 1
                    if subject not in isc_exclude[task]:
                        isc_exclude[task][subject] = [basename(run).split(
                            '_space')[0]]
                    else:
                        isc_exclude[task][subject].append(basename(run).split(
                            '_space')[0])
                    print(f"Excluding {task} {subject} with ISC {roi_isc}")

    print(f"Excluding {exclude_count} with ISC < {threshold}")


    # Combine lag exclusion list into scan_exclude
    for task in lag_exclude:
        if len(lag_exclude[task].keys()) > 0:
            for subject in lag_exclude[task]:
                if subject not in scan_exclude[task]:
                    scan_exclude[task][subject] = []
                    print(f"Adding {subject} to scan_exclude")
                else:
                    print(f"{subject} already in scan_exclude")
                for run in lag_exclude[task][subject]:
                    if run not in scan_exclude[task][subject]:
                        scan_exclude[task][subject].append(run)
                        print(f"Adding {run} to scan_exclude")
                    else:
                        print(f"{run} already in scan_exclude")
                        
    # Combine ISC exclusion list into scan_exclude
    for task in isc_exclude:
        if len(isc_exclude[task].keys()) > 0:
            for subject in isc_exclude[task]:
                if subject not in scan_exclude[task]:
                    scan_exclude[task][subject] = []
                    print(f"Adding {subject} to scan_exclude")
                else:
                    print(f"{subject} already in scan_exclude")
                for run in isc_exclude[task][subject]:
                    if run not in scan_exclude[task][subject]:
                        scan_exclude[task][subject].append(run)
                        print(f"Adding {run} to scan_exclude")
                    else:
                        print(f"{run} already in scan_exclude")

    # Combine pieman-specific ISC exclusion list into scan_exclude
    task = 'pieman'
    for subject in isc_exclude[task]:
        if subject not in scan_exclude[task]:
            scan_exclude[task][subject] = []
            print(f"Adding {subject} to scan_exclude")
        else:
            print(f"{subject} already in scan_exclude")
        for run in isc_exclude[task][subject]:
            if run not in scan_exclude[task][subject]:
                scan_exclude[task][subject].append(run)
                print(f"Adding {run} to scan_exclude")
            else:
                print(f"{run} already in scan_exclude")

    # Count final number of excluded scans
    exclude_list = []
    for task in scan_exclude:
        if len(scan_exclude[task].keys()) > 0:
            exclude_list.extend([r for s in 
                                 list(scan_exclude[task].values())
                                 for r in s])
    n_exclude = len(exclude_list)
    n_scans = 891
    
    print(f"Excluding {n_exclude} scans across all criteria; "
          f"{n_exclude / n_scans:.1%} of {n_scans} total scans")
            
    with open(join(base_dir, 'code', 'scan_exclude.json'), 'w') as f:
        json.dump(scan_exclude, f, indent=2, sort_keys=True)
