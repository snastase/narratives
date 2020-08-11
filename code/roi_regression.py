from os.path import basename, exists, join
from os import chdir
import json
from glob import glob
from subprocess import run


space = 'fsaverage6'
roi = 'EAC'

    
# Assign some directories
afni_pipe = 'afni-nosmooth'
base_dir = '/jukebox/hasson/snastase/narratives'
deriv_dir = join(base_dir, 'derivatives')


# Load subject metadata to get filenames
with open(join(base_dir, 'code', 'subject_meta.json')) as f:
    subject_meta = json.load(f)


# Loop through all subjects
for subject in subject_meta:
    
    # Move into output directory (AFNI seems to want to save in wd)
    afni_dir = join(deriv_dir, afni_pipe, subject, 'func')
    chdir(afni_dir)
    
    # Grab BOLD filenames directly from directory
    bold_fns = glob(join(afni_dir,
                         (f'{subject}_task-*_space-{space}_hemi-*_'
                          f'roi-{roi}_desc-mean_timeseries.1D')))
    
    # Loop through BOLD ROI time series (tasks and runs)
    for bold_fn in bold_fns:
        
        # Get corresponding model regressors filename
        model_fn = join(afni_dir,
                        (basename(bold_fn).split('_space')[0] + 
                        '_desc-model_regressors.1D'))
        assert exists(model_fn)
        
        clean_fn = join(afni_dir,
                        basename(bold_fn).replace('desc-mean',
                                                  'desc-clean'))

        run(f"3dTproject -input {bold_fn} -ort {model_fn} -TR 1.5 "
            f"-prefix {clean_fn} -polort 2 -overwrite", shell=True)

        print(f"Finished model confound regression(s) for {subject}:"
              f"\n  {basename(clean_fn)}")
