import json
from os.path import basename, exists, join
from os import makedirs
from shutil import copyfile
from glob import glob
import pandas as pd

staging_dir = '/jukebox/hasson/snastase/narratives-staging'
open_dir = '/jukebox/hasson/snastase/narratives-openneuro'
bids_dir = '/jukebox/hasson/snastase/narratives'

copy_files = True

# Load participant metadata
with open(join(staging_dir, 'staging', 'participants_meta.json')) as f:
    metadata = json.load(f)

# Copy non-defaced anatomicals to sourcedata/
for subject in metadata:
    anat_fns = glob(join(bids_dir, subject, 'anat', f'{subject}*_T*w.*'))
    for anat_fn in anat_fns:
        face_dir = join(bids_dir, 'sourcedata', subject, 'anat')
        if not exists(face_dir):
            makedirs(face_dir)
            print(f"Created {subject} in sourcedata")
        
        out_fn = join(face_dir, basename(anat_fn))
        print(f"Copying {anat_fn} to {out_fn}")
        if copy_files:
            copyfile(anat_fn, out_fn)

# Replace anatomicals with defaced versions
for subject in metadata:
    anat_fns = glob(join(open_dir, subject, 'anat', f'{subject}*_T*w.nii.gz'))
    for anat_fn in anat_fns:
        deface_dir = join(bids_dir, subject, 'anat')
        assert exists(join(deface_dir, basename(anat_fn)))
        
        out_fn = join(deface_dir, basename(anat_fn))
        print(f"Copying {anat_fn} to {out_fn}")
        if copy_files:
            copyfile(anat_fn, out_fn)

# Replaced some anats with strange cropping
fix_anats = ['sub-038', 'sub-075', 'sub-146', 'sub-147',
             'sub-148', 'sub-149', 'sub-150', 'sub-151',
             'sub-152', 'sub-153', 'sub-154', 'sub-155',
             'sub-156', 'sub-157', 'sub-158', 'sub-159',
             'sub-160', 'sub-161', 'sub-162', 'sub-163',
             'sub-164', 'sub-165', 'sub-166', 'sub-167',
             'sub-168', 'sub-169', 'sub-170', 'sub-171',
             'sub-172', 'sub-173', 'sub-174', 'sub-175',
             'sub-176', 'sub-177', 'sub-178', 'sub-179',
             'sub-180']

# Re-do poorly cropped anas
for subject in fix_anats:
    anat_fns = glob(join(open_dir, subject, 'anat', f'{subject}*_T*w.nii.gz'))
    for anat_fn in anat_fns:
        deface_dir = join(bids_dir, subject, 'anat')
        
        out_fn = join(deface_dir, basename(anat_fn))
        print(f"Copying {anat_fn} to {out_fn}")
        if copy_files:
            copyfile(anat_fn, out_fn)

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
