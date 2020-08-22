from os.path import basename, join
from os import chdir
from glob import glob
import json
import numpy as np
from gifti_io import read_gifti, write_gifti
from subprocess import run


# Compute tSNR in surface space for visualization
space = 'fsaverage6'


# Assign some directories
base_dir = '/jukebox/hasson/snastase/narratives'
prep_dir = join(base_dir, 'derivatives', 'fmriprep')
afni_dir = join(base_dir, 'derivatives', 'afni-nosmooth')


# Load subject metadata to get filenames
with open(join(base_dir, 'code', 'subject_meta.json')) as f:
    subject_meta = json.load(f)


# Loop through subjects and compute tSNR
for subject in subject_meta:

    # Change directory for AFNI
    chdir(join(afni_dir, subject, 'func'))

    bold_fns = subject_meta[subject]['bold'][space]['preproc']

    # Loop through BOLD files
    for bold_fn in bold_fns:

        tsnr_fn = join(afni_dir, subject, 'func',
                       (basename(bold_fn).split('.')[0] +
                        '_desc-tsnr.func.gii'))

        # Use AFNI's 3dTstat to compute tSNR (no detrending)
        run(("3dTstat -tsnr -overwrite -prefix "
             f"{tsnr_fn} {bold_fn}"), shell=True)

    print(f"Finished computing tSNR map(s) for {subject}")


# Compute mean across all input images
chdir(afni_dir)
for hemi in ['L', 'R']:
    input_fns = join(afni_dir, 'sub-*', 'func',
                     f'sub-*_task-*_space-{space}_'
                     f'hemi-{hemi}_desc-tsnr.func.gii')
    mean_fn = join(afni_dir, f'group_space-{space}_hemi-{hemi}_'
                             'desc-mean_tsnr.gii')
    run(f'3dMean -verbose -prefix {mean_fn} {input_fns}', shell=True)
    print(f"Finished computing mean tSNR for {hemi} hemisphere")
    
    
# Compute median across all input images
for hemi in ['L', 'R']:
    input_fns = glob(join(afni_dir, 'sub-*', 'func',
                          f'sub-*_task-*_space-{space}_'
                          f'hemi-{hemi}_desc-tsnr.func.gii'))
    tsnr_stack = []
    for input_fn in input_fns:
        tsnr_stack.append(read_gifti(input_fn))
    tsnr_stack = np.vstack(tsnr_stack)
    print(f"Loaded all {tsnr_stack.shape[0]} tSNR maps")
    
    tsnr_median = np.median(tsnr_stack, axis=0)
    median_fn = join(afni_dir, f'group_space-{space}_hemi-{hemi}_'
                               'desc-median_tsnr.gii')

    write_gifti(tsnr_median, median_fn, input_fns[0])
    print(f"Finished computing median tSNR for {hemi} hemisphere")