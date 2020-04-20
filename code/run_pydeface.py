#!/usr/bin/env python

from os.path import join
from os import chdir
from glob import glob
import json
from subprocess import call

# Running pydeface locally on mounted volumes
#base_dir = '/Volumes/hasson/snastase'
base_dir = '/Users/snastase/Work/mount'
staging_dir = join(base_dir, 'narratives-staging')
bids_dir = join(base_dir, 'narratives-openneuro')

# Load participant metadata
with open(join(staging_dir, 'staging', 'participants_meta.json')) as f:
    metadata = json.load(f)


# Loop through subjects and deface anats
for subject in metadata:
    
    chdir(join(bids_dir, subject, 'anat'))
    anat_fns = glob('*T*w.nii.gz')
    for anat_fn in anat_fns:
        
        call(f'pydeface --outfile {anat_fn} --force {anat_fn}',
             shell=True)
        print(f"Finished defacing {anat_fn}!")
        

# Grab new notthefall subjects and check against existing conditions
new_tasks = ['notthefallintact',
             'notthefalllongscram',
             'notthefallshortscram']

new_subjects, new_funcs, new_anats = [], [], []
for subject in metadata:
    tasks = metadata[subject]['task']
    if 'notthefallintact' in tasks:
        new_subjects.append(subject)
        new_funcs.append(subject)
        old_tasks = list(set(tasks) - set(new_tasks))
        if len(old_tasks) == 0:
            new_anats.append(subject)
