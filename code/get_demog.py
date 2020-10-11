from os.path import join
import json
import numpy as np
import pandas as pd


base_dir = '/jukebox/hasson/snastase/narratives'


participants_fn = join(base_dir, 'participants.tsv')
participants = pd.read_csv(participants_fn, sep='\t')

# Extract the age column of participant demographic information
def extract_age(participants, task=None):
    
    if task and task != 'pieman':
        participants = participants[participants['task'].str.contains(task)]
    
    elif task == 'pieman':
        participants = participants[
            (participants['task'].str.contains(task)) &
            ~(participants['task'].str.contains('piemanpni'))]
    
    n = len(participants)
    ages = [int(p) for l in
            [p.split(',') if type(p) == str else p
             for p in participants['age'].dropna()]
            for p in l if p != 'n/a']
    
    return ages, n


# Extra the sex column of participant demographic information
def extract_sex(participants, task=None):
    
    if task and task != 'pieman':
        participants = participants[participants['task'].str.contains(task)]
        
    elif task == 'pieman':
        participants = participants[
            (participants['task'].str.contains(task)) &
            ~(participants['task'].str.contains('piemanpni'))]
    
    n = len(participants)
    sexes = [p.split(',')[0] for p in participants['sex'].dropna()]
    
    return sexes, n


# Get descriptive demographic stats for across all tasks
ages, n = extract_age(participants)
sexes, n = extract_sex(participants)
print(f"all tasks: {n} participants ({sexes.count('F')} female; "
      f"mean age: {np.mean(ages):.1f}, SD: {np.std(ages):.1f} "
      f"range: {np.amin(ages)}-{np.amax(ages)})")


# Get descriptive demographic stats for each task
with open(join(base_dir, 'code', 'task_meta.json')) as f:
    task_meta = json.load(f)

for task in task_meta:
    # Get descriptive demographic stats for across all tasks
    ages, n = extract_age(participants, task=task)
    sexes, n = extract_sex(participants, task=task)
    print(f"{task}: {n} participants ({sexes.count('F')} female; "
          f"mean age: {np.mean(ages):.1f}, SD: {np.std(ages):.1f} "
          f"range: {np.amin(ages)}-{np.amax(ages)})")