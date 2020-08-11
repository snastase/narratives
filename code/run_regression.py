#!/usr/bin/env python3

from sys import argv
from os.path import basename, exists, join
from os import chdir
import json
from subprocess import run


# Pull in variables (from Slurm submission)
subject = f'sub-{argv[1]}'
space = argv[2]
afni_pipe = argv[3]

# Smoothing kernel width for smoothed data
if afni_pipe == 'afni-smooth':
    smoothness = 'sm6'

# Check that we get a reasonable space
if 'MNI' not in space and 'fsaverage' not in space:
    raise AssertionError("Expected either MNI or fsaverage space")
    
# Assign some directories
base_dir = '/jukebox/hasson/snastase/narratives'
deriv_dir = join(base_dir, 'derivatives')
fmriprep_dir = join(deriv_dir, 'fmriprep', subject, 'func')
afni_dir = join(deriv_dir, afni_pipe, subject, 'func')

# Move into output directory (AFNI seems to want to save in wd)
chdir(afni_dir)


# Load subject metadata to get filenames
with open(join(base_dir, 'code', 'subject_meta.json')) as f:
    subject_meta = json.load(f)


# Grab input BOLD filenames from metadata
if afni_pipe == 'afni-smooth':
    bold_fns = subject_meta[subject]['bold'][space][smoothness]

elif afni_pipe == 'afni-nosmooth':
    bold_fns = subject_meta[subject]['bold'][space]['preproc']


# Loop through BOLD filenames (tasks and runs)
for bold_fn in bold_fns:
    
    # Get corresponding model regressors filename
    model_fn = join(afni_dir, (basename(bold_fn).split('_space')[0] + 
                              '_desc-model_regressors.1D'))
    assert exists(model_fn)
    
    # Get output clean BOLD filename
    if afni_pipe == 'afni-smooth':
        clean_fn = join(afni_dir,
                        basename(bold_fn).replace(f'desc-{smoothness}',
                                                  'desc-clean'))
    elif afni_pipe == 'afni-nosmooth' and 'fsaverage' not in space:
        clean_fn = join(afni_dir,
                        basename(bold_fn).replace(f'desc-preproc',
                                                  'desc-clean'))
    elif afni_pipe == 'afni-nosmooth' and 'fsaverage' in space:
        clean_fn = join(afni_dir,
                        basename(bold_fn).replace(f'.func.gii',
                                                  '_desc-clean.func.gii'))
    
    # Get the volumetric mask resampled for this task if necessary
    if 'fsaverage' not in space:
        task = basename(bold_fn).split('task-')[-1].split('_')[0]
        mask_fn = join(deriv_dir, afni_pipe, f'tpl-{space}',
                       f'tpl-{space}_res-{task}_desc-brain_mask.nii.gz')
        assert exists(mask_fn)
    

    # Perform confound regression via AFNI's 3dTproject
    if 'fsaverage' in space:
        run(f"3dTproject -input {bold_fn} -ort {model_fn} -TR 1.5 "
            f"-prefix {clean_fn} -polort 2 -overwrite", shell=True)
    else:
        run(f"3dTproject -input {bold_fn} -ort {model_fn} -overwrite "
            f"-prefix {clean_fn} -mask {mask_fn} -polort 2", shell=True)

    print(f"Finished model confound regression(s) for {subject}:"
          f"\n  {basename(clean_fn)}")
