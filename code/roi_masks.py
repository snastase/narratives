from os.path import join
import json
import numpy as np
from gifti_io import read_gifti, write_gifti


# Set up directories for ROI analysis
base_dir = '/jukebox/hasson/snastase/narratives'
afni_dir = join(base_dir, 'derivatives', 'afni-nosmooth')
tpl_dir = join(afni_dir, 'tpl-fsaverage6')


# Early auditory cortex (EAC) ROI labels
roi = 'EAC'
parcels = {"A1": 24,
           "LBelt": 174,
           "MBelt": 173,
           "PBelt": 124,
           "RI": 104}


# Create ROI masks for both hemispheres
for hemi in ['L', 'R']:

    # Load in MMP on fsaverage6
    mmp_fn = join(tpl_dir, f'tpl-fsaverage6_hemi-{hemi}_desc-MMP_dseg.label.gii')
    mmp = read_gifti(mmp_fn)[0]

    # Set up empty mask and fill with 1s for ROI
    mask = np.zeros(mmp.shape)
    for parcel in parcels:
        mask[mmp == parcels[parcel]] = 1

    # Write out a GIfTI ROI mask
    write_gifti(mask,
                join(tpl_dir,
                     f'tpl-fsaverage6_hemi-{hemi}_desc-{roi}_mask.label.gii'),
                join(tpl_dir,
                     f'tpl-fsaverage6_hemi-{hemi}_desc-MMP_dseg.label.gii'))

    # Let's make a boolean numpy mask as well
    mask = mask.astype(bool)
    n_voxels = np.sum(mask)
    np.save(join(tpl_dir,
                 f'tpl-fsaverage6_hemi-{hemi}_desc-{roi}_mask.npy'), mask)
    print(f"Created {hemi} {roi} mask containing "
          f"{n_voxels} vertices")
