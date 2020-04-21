from os.path import exists, join
from os import makedirs
import json
from subprocess import run
import nibabel as nib

# fMRIPrep's default volumetric MNI template
space = 'MNI152NLin2009cAsym'

# MNI template downloaded from MNI
# http://nist.mni.mcgill.ca/?p=904
mni_name = 'mni_icbm152_nlin_asym_09c'
mni_dir = join('/jukebox/hasson/snastase/templates', mni_name)

# Get the MNI whole-brain mask
brain_fn = join(mni_dir, 'mni_icbm152_t1_tal_nlin_asym_09c_mask.nii')

# Create derivatives directory for MNI masks
deriv_dir = '/jukebox/hasson/snastase/narratives/derivatives'
mask_dir = join(deriv_dir, 'afni', f'tpl-{space}')
if not exists(mask_dir):
    makedirs(mask_dir)

# Load task metadata for matching grids
with open('task_meta.json') as f:
    task_meta = json.load(f)

# Resample masks for each task for convenience (redundant but oh well)
for task in task_meta:
    master_fn = task_meta[task][
        next(iter(task_meta[task]))]['bold'][space][0]

    mask_fn = join(mask_dir,
                   f'tpl-{space}_res-{task}_desc-brain_mask.nii.gz')

    # Resample the mask to match task BOLD grid
    if not exists(mask_fn):
        run(f"3dresample -master {master_fn} -prefix {mask_fn} "
            f"-input {brain_fn} -rmode NN", shell=True)

    # Check that grids match
    assert nib.load(mask_fn).shape == nib.load(master_fn).shape[:3]