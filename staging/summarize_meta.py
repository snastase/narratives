from os.path import basename, join
from glob import glob
import json
import numpy as np
import nibabel as nib


base_dir = '/jukebox/hasson/snastase'
staging_dir = join(base_dir, 'narratives-staging')
bids_dir = join(base_dir, 'narratives-openneuro')


# Load participant metadata
with open(join(staging_dir, 'staging', 'participants_meta.json')) as f:
    metadata = json.load(f)


# Number of participating subjects overall
n_subjects = len(metadata.keys())


# Get ages across all 
ages = []
for subject in metadata:
    for age in metadata[subject]['age']:
        if age != 'n/a':
            ages.append(int(age))
mean_age = np.mean(ages)
min_age = np.amin(ages)
max_age = np.amax(ages)
        

# Get genders
sex = []
for subject in metadata:
    for s in metadata[subject]['sex']:
        if s != 'n/a':
            sex.append(s)
            break
np.unique(sex, return_counts=True)


# Get total number of TRs
n_trs = []
for subject in metadata:
    func_fns = glob(join(bids_dir, subject, 'func',
                         '*_bold.nii.gz'))
    for func_fn in func_fns:
        nimg = nib.load(func_fn)
        assert nimg.ndim == 4
        n_trs.append(nimg.shape[-1])
total_trs = np.sum(n_trs)


# Get veridical story durations from *_events.tsv
story_dur = []
for subject in metadata:
    func_fns = glob(join(bids_dir, subject, 'func',
                         '*_events.tsv'))
    for func_fn in func_fns:
        with open(func_fn) as f:
            events = [line.strip().split('\t')
                      for line in f.readlines()][1:]
            for event in events:
                if event[2] == 'story':
                    story_dur.append(float(event[1]))


# Get number of subjects per dataset
datasets = ['pieman', 'tunnel', 'lucy', 'prettymouth',
            'milkyway', 'slumlordreach', 'notthefall',
            'merlin', 'sherlock', 'schema', 'shapessocial',
            'shapesphysical', '21styear', 'piemanpni',
            'bronx', 'forgot', 'black']

datasets_meta = {dataset: {'subjects': [], 'filenames': []}
                 for dataset in datasets}
for subject in metadata:
    
    func_fns = glob(join(bids_dir, subject, 'func',
                         '*_bold.nii.gz'))
    for func_fn in func_fns:
        task = func_fn.split('_')[1].split('-')[1]
        if subject not in datasets_meta[task]['subjects']:
            datasets_meta[task]['subjects'].append(subject)
        datasets_meta[task]['filenames'].append(basename(func_fn))
for dataset in datasets_meta:
    print(f"{dataset}: N = {len(datasets_meta[dataset]['subjects'])}")