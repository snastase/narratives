from os.path import basename, join
import json
import numpy as np
from glob import glob
from gifti_io import read_gifti

space = 'fsaverage6'
roi = 'EAC'

# Assign some directories
base_dir = '/jukebox/hasson/snastase/narratives'
afni_dir = join(base_dir, 'derivatives', 'afni-nosmooth')
tpl_dir = join(afni_dir, f'tpl-{space}')


# Load subject metadata to get filenames
with open(join(base_dir, 'code', 'subject_meta.json')) as f:
    subject_meta = json.load(f)


# Loop through hemispheres and subjects to extract ROI average time series
for hemi in ['L', 'R']:

    # Get the ROI mask
    roi_fn = join(tpl_dir, f'tpl-{space}_hemi-{hemi}_desc-{roi}_mask.npy')
    roi_mask = np.load(roi_fn)  


# Loop through subjects and extract ROI average time series
for hemi in ['L', 'R']:

    # Get the ROI mask
    roi_fn = join(tpl_dir, f'tpl-{space}_hemi-{hemi}_desc-{roi}_mask.npy')
    roi_mask = np.load(roi_fn)

    # Loop through subjects
    for subject in subject_meta:   
        subject_dir = join(afni_dir, subject, 'func')

        # Grab BOLD filenames (and filter for hemisphere)
        bold_fns = subject_meta[subject]['bold'][space]['preproc']
        bold_fns = [bold_fn for bold_fn in bold_fns
                    if f'hemi-{hemi}' in bold_fn]

        # Loop through BOLD images and extract ROI
        for bold_fn in bold_fns:
            bold_map = read_gifti(bold_fn)
            roi_avg = np.nanmean(bold_map[:, roi_mask == 1], axis=1)
            assert bold_map.shape[0] == roi_avg.shape[0]

            roi_1D = join(subject_dir,
                          basename(bold_fn).replace(
                              '.func.gii',
                              f'_roi-{roi}_desc-mean_timeseries.1D'))
            np.savetxt(roi_1D, roi_avg[None, :], delimiter=' ', fmt='%f')

            print(f"Extracted average {roi} time series for {subject}"
                   f"\n  {basename(roi_1D)}")