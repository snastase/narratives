#!/bin/bash

# Run within BIDS code/ directory:
# sbatch slurm_mriqc.sh

# Set partition
#SBATCH --partition=all

# How long is job (in minutes)?
#SBATCH --time=180

# How much memory to allocate (in MB)?
#SBATCH --cpus-per-task=8 --mem-per-cpu=10000

# Name of jobs?
#SBATCH --job-name=mriqc

# Where to output log files?
#SBATCH --output='../derivatives/logs/mriqc-%A_%a.log'

# Number jobs to run in parallel
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
echo "Running MRIQC on sub-$subj"

./run_mriqc.sh $subj

echo "Finished running MRIQC on sub-$subj"
date
