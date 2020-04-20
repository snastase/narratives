#! /bin/bash

# Run manually using something like:
# ./run_mriqc.sh |& tee ../derivatives/logs/mriqc-log.txt 

bids_dir=/jukebox/hasson/snastase/narratives

singularity run --cleanenv \
    --bind $bids_dir:/home \
    --bind /usr/people \
    --bind /scratch/snastase/narratives/work \
    /jukebox/hasson/singularity/mriqc/mriqc-v0.15.1.simg \
    --participant-label $1 --correct-slice-timing \
    --nprocs 8 -w /scratch/snastase/narratives/work \
    /home /home/derivatives/mriqc participant
