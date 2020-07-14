#! /bin/bash

# Run manually using something like:
# ./run_fmriprep.sh 001 |& tee ../derivatives/logs/fmriprep_sub-001_log.txt  

export SINGULARITYENV_TEMPLATEFLOW_HOME=/home/fmriprep/.cache/templateflow

bids_dir=/jukebox/hasson/snastase/narratives

singularity run --cleanenv \
    --bind $bids_dir:/data \
    --bind /usr/people \
    --bind /scratch/snastase/narratives/work \
    --bind /jukebox/hasson/templateflow:/home/fmriprep/.cache/templateflow \
    /jukebox/hasson/singularity/fmriprep/fmriprep-v20.0.5.simg \
    --skip_bids_validation \
    --participant-label sub-$1 \
    --nthreads 4 --omp-nthreads 4 \
    --longitudinal --bold2t1w-dof 6 \
    --medial-surface-nan \
    --output-spaces anat func fsaverage fsaverage6 fsaverage5 \
                    MNI152NLin2009cAsym:res-native MNI152NLin6Asym:res-native \
    --fs-license-file /data/code/fs-license.txt --notrack \
    --use-syn-sdc --write-graph --work-dir /scratch/snastase/narratives/work \
    /data /data/derivatives participant
