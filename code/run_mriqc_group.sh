#! /bin/bash

# Run manually using something like:
# ./run_mriqc_group.sh |& tee ../derivatives/logs/mriqc_group_log.txt 

bids_dir=/jukebox/hasson/snastase/narratives

singularity run --cleanenv \
    --bind $bids_dir:/home \
    --bind /usr/people \
    --bind /scratch/snastase/narratives/work \
    /jukebox/hasson/singularity/mriqc/mriqc-v0.15.1.simg \
    --correct-slice-timing \
    --nprocs 8 -w /scratch/snastase/narratives/work \
    /home /home/derivatives/mriqc group
