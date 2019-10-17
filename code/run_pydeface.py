#!/usr/bin/env python

from os.path import join
from os import chdir
from glob import glob
import json
from subprocess import call

# Running pydeface locally on mounted volumes
base_dir = '/Volumes/hasson/snastase'
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
