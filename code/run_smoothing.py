#!/usr/bin/env python3

from sys import argv
from os.path import basename, exists, join
from os import makedirs, remove
import json
from subprocess import run


# Pull in variables (from Slurm submission)
subject = f'sub-{argv[1]}'
space = argv[2]
width = argv[3]


# Check that we get a reasonable space
if 'MNI' not in space and 'fsaverage' not in space:
    raise AssertionError("Expected either MNI or fsaverage space")


# Create output AFNI directory if it doesn't exist
base_dir = '/jukebox/hasson/snastase/narratives'
deriv_dir = join(base_dir, 'derivatives')
fmriprep_dir = join(deriv_dir, 'fmriprep', subject, 'func')
freesurfer_dir = join(deriv_dir, 'freesurfer')


# Assign an AFNI pipeline output directory (either -smooth or -nosmooth)
afni_pipe = 'afni-smooth'
afni_dir = join(deriv_dir, afni_pipe, subject, 'func')
if not exists(afni_dir):
    makedirs(afni_dir)

if 'fsaverage' in space:
    surf_dir = join(deriv_dir, 'freesurfer', space, 'surf')
    surf_fns = {'L': join(surf_dir, 'lh.pial'),
                'R': join(surf_dir, 'rh.pial')}


# Load subject metadata to get filenames
with open(join(base_dir, 'code', 'subject_meta.json')) as f:
    subject_meta = json.load(f)

bold_fns = subject_meta[subject]['bold'][space]['preproc']


# Loop through BOLD images and smooth
for bold_fn in bold_fns:
    task = bold_fn.split('task-')[1].split('_')[0]

    # Volumetric smoothing for MNI space
    if 'MNI' in space:
        mask_fn = join(deriv_dir, afni_pipe, f'tpl-{space}',
                       f'tpl-{space}_res-{task}_desc-brain_mask.nii.gz')
        smooth_fn = join(afni_dir, basename(bold_fn).replace(
            'desc-preproc', f'desc-sm{width}'))
        if not exists(smooth_fn):
            run(f"3dBlurToFWHM -mask {mask_fn} -FWHM {width} "
                f"-input {bold_fn} -prefix {smooth_fn} "
                f"-blurmaster {bold_fn} -detrend -bmall", shell=True)

    # Surface-based smoothing for fsaverage space
    elif 'fsaverage' in space:
        hemi = bold_fn.split('hemi-')[1][0]
        smooth_fn = join(afni_dir, basename(bold_fn).replace(
            '.func.gii', f'_desc-sm{width}.func.gii'))
        mask_fn = join(deriv_dir, afni_pipe, f'tpl-{space}',
                       f'tpl-{space}_hemi-{hemi}_desc-cortex_mask.1D')
        
        if task in ['schema', 'shapesphysical', 'shapessocial']:
            sigma = .6
        elif task in ['black', 'forgot', 'bronx', 'piemanpni']:
            sigma = .55
        else:
            sigma = .48

        run(f"SurfSmooth -input {bold_fn} -target_fwhm {width} "
            f"-i_fs {surf_fns[hemi]} -output {smooth_fn} "
            f"-blurmaster {bold_fn} -detrend_master -b_mask {mask_fn} "
            f"-met HEAT_07 -bmall -sigma {sigma} -overwrite", shell=True)
