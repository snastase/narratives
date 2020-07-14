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
fix_anats = ['sub-038', 'sub-049', 'sub-058', 'sub-075',
             'sub-089', 'sub-095', 'sub-109', 'sub-115',
             'sub-127', 'sub-132', 'sub-146', 'sub-147',
             'sub-148', 'sub-149', 'sub-150', 'sub-151',
             'sub-152', 'sub-153', 'sub-154', 'sub-155',
             'sub-156', 'sub-157', 'sub-158', 'sub-159',
             'sub-160', 'sub-161', 'sub-162', 'sub-163',
             'sub-164', 'sub-165', 'sub-166', 'sub-167',
             'sub-168', 'sub-169', 'sub-170', 'sub-171',
             'sub-172', 'sub-173', 'sub-174', 'sub-175',
             'sub-176', 'sub-177', 'sub-178', 'sub-179',
             'sub-180', 'sub-181', 'sub-182', 'sub-183',
             'sub-184', 'sub-185', 'sub-186', 'sub-187',
             'sub-188', 'sub-189', 'sub-190', 'sub-191',
             'sub-192', 'sub-193', 'sub-194', 'sub-195',
             'sub-196', 'sub-197', 'sub-198', 'sub-199',
             'sub-200', 'sub-201', 'sub-202', 'sub-203',
             'sub-204', 'sub-205', 'sub-206', 'sub-207',
             'sub-208', 'sub-209', 'sub-210', 'sub-211',
             'sub-212', 'sub-213', 'sub-214', 'sub-215',
             'sub-216', 'sub-217', 'sub-218', 'sub-219',
             'sub-220', 'sub-221', 'sub-222', 'sub-223',
             'sub-224', 'sub-225', 'sub-226', 'sub-227',
             'sub-228', 'sub-229', 'sub-230', 'sub-231',
             'sub-232', 'sub-233', 'sub-234', 'sub-235',
             'sub-236', 'sub-237', 'sub-238', 'sub-239',
             'sub-240', 'sub-241', 'sub-242', 'sub-243',
             'sub-244', 'sub-245', 'sub-246', 'sub-247',
             'sub-248', 'sub-249', 'sub-250', 'sub-251',
             'sub-252', 'sub-253']


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
