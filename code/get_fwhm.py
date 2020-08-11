#!/usr/bin/env python3

from sys import argv
from os.path import basename, exists, join
from os import getcwd, remove
import json
from subprocess import run, PIPE


# Get subject from command-line input via Slurm
subject = f'sub-{argv[1]}'

# Assign some directories
base_dir = '/jukebox/hasson/snastase/narratives'
prep_dir = join(base_dir, 'derivatives', 'fmriprep')
afni_dir = join(base_dir, 'derivatives', 'afni-nosmooth')


# Load subject metadata to get filenames
with open(join(base_dir, 'code', 'subject_meta.json')) as f:
    subject_meta = json.load(f)


# Get the BOLD-space BOLD filenames from the MNI filenames
space = 'MNI152NLin2009cAsym'
mni_fns = subject_meta[subject]['bold'][space]['preproc']

for mni_fn in mni_fns:
    bold_fn = mni_fn.replace(f'_space-{space}_res-native_', '_')
    mask_fn = bold_fn.replace('desc-preproc_bold',
                              'desc-brain_mask')

    # Estimate FWHM from the original data
    orig_fwhm = run(f"3dFWHMx -mask {mask_fn} -input {bold_fn} "
                    "-detrend -acf NULL -ShowMeClassicFWHM",
                    shell=True, stdout=PIPE)

    # Parse the smoothing output (X, Y, Z, combined)
    fwhm_str = orig_fwhm.stdout.decode('utf-8').partition('\n')[0]
    fwhm = [s for s in fwhm_str.split(' ') if s not in [' ', '']]

    # Save the output as a TSV file in the AFNI derivatives
    fwhm_fn = join(afni_dir, subject, 'func',
                   basename(bold_fn).replace(
                       'desc-preproc_bold.nii.gz',
                       'desc-fwhm_smoothness.tsv'))

    with open(fwhm_fn, 'w') as f:
        f.write('\n'.join(['\t'.join(['x', 'y', 'z', 'combined']),
                           '\t'.join(fwhm)]))

    # Clean up AFNI's 3dFWHMx.1D file
    rm_fn = join(getcwd(), '3dFWHMx.1D')
    if exists(rm_fn):
        remove(rm_fn)

print(f"Finished computing smoothness estimates for {subject}")
