#!/bin/bash

# Run within BIDS code/ directory:
# sbatch slurm_fmriprep.sh

# Set partition
#SBATCH --partition=all

# How long is job (in minutes)?
#SBATCH --time=960

# How much memory to allocate (in MB)?
#SBATCH --cpus-per-task=4 --mem-per-cpu=12000

# Name of jobs?
#SBATCH --job-name=fmriprep

# Where to output log files?
#SBATCH --output='../derivatives/logs/fmriprep-res-native-v20.0.5-%A_%a.log'

# Number jobs to run in parallel, pass index as subject ID
#SBATCH --array=1-345

# Remove modules because Singularity shouldn't need them
echo "Purging modules"
module purge

# Print job submission info
echo "Slurm job ID: " $SLURM_JOB_ID
echo "Slurm array task ID: " $SLURM_ARRAY_TASK_ID
date

# Set subject ID based on array index
printf -v subj "%03d" $SLURM_ARRAY_TASK_ID

# Run fMRIPrep script with participant argument
echo "Running fMRIPrep on sub-$subj"

./run_fmriprep.sh $subj

echo "Finished running fMRIPrep on sub-$subj"
date
