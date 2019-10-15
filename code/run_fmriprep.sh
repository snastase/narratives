#! /bin/bash

# Run manually using something like:
# ./run_fmriprep.sh |& tee ../derivatives/logs/fmriprep-log.txt 

export SINGULARITYENV_TEMPLATEFLOW_HOME=/home/fmriprep/.cache/templateflow

bids_dir=/jukebox/hasson/snastase/narratives

singularity run --cleanenv \
    --bind $bids_dir:/data \
    --bind /usr/people \
    --bind /jukebox/hasson/templateflow:/home/fmriprep/.cache/templateflow \
    /jukebox/hasson/singularity/fmriprep/fmriprep-v1.5.0.simg \
    --participant-label sub-$1 \
    --nthreads 8 --omp-nthreads 8 \
    --longitudinal --bold2t1w-dof 6 \
    --output-spaces anat func fsaverage:den-41k \
                    MNI152NLin2009cAsym MNI152NLin6Asym \
    --fs-license-file /data/code/fs-license.txt --notrack \
    --use-syn-sdc --write-graph --work-dir /data/derivatives/work \
    /data /data/derivatives participant
