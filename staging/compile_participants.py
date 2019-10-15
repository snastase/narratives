from os.path import exists, join
import json
import numpy as np
import pandas as pd

base_dir = '/jukebox/hasson/snastase'
staging_dir = join(base_dir, 'narratives-staging')
final_dir = join(base_dir, 'narratives-raw')

datasets = ['pieman', 'tunnel', 'lucy', 'prettymouth',
            'milkyway', 'slumlordreach', 'notthefall',
            'merlin', 'sherlock', 'schema', 'shapessocial',
            'shapesphysical', '21styear', 'piemanpni',
            'bronx', 'forgot', 'black']


# Populate metadata for all datasets avoiding collisions
metadata = {}
for dataset in datasets:
    
    if dataset in ['shapesphysical', 'shapessocial']:
        data_dir = join(staging_dir, 'shapes')
    else:
        data_dir = join(staging_dir, dataset)

    with open(join(data_dir, 'participants.tsv')) as f:
        tsv = [line.strip().split('\t') for line in f.readlines()]

    header = tsv.pop(0)

    for row in tsv:
        if row[1] != 'n/a':
            row[1] = str(int(float(row[1])))
        
        if row[0] not in metadata:
            metadata[row[0]] = {'age': [], 'sex': [],
                                'task': [], 'condition': [],
                                'comprehension': []}
        if dataset not in metadata[row[0]]['task']:
            metadata[row[0]]['age'].append(row[1])
            metadata[row[0]]['sex'].append(row[2])
            metadata[row[0]]['task'].append(dataset)
            if 'condition' in header:
                col = header.index('condition')
                metadata[row[0]]['condition'].append(row[col])
            else:
                metadata[row[0]]['condition'].append('n/a')
            if 'comprehension' in header:
                col = header.index('comprehension')
                if row[col] != 'n/a':
                    row[col] = str(np.round(float(row[col]), decimals=3))
                metadata[row[0]]['comprehension'].append(row[col])
            else:
                metadata[row[0]]['comprehension'].append('n/a')


# Include an n/a in completely empty cells
for participant in metadata:
    for entry in metadata[participant]:
        if metadata[participant][entry] == []:
            metadata[participant][entry] = ['n/a']


# Save participants metadata
with open(join(staging_dir, 'participants_metadata.json'), 'w') as f:
    json.dump(metadata, f, sort_keys=True, indent=2)

columns = ['participant_id', 'age', 'sex', 'task',
           'condition', 'comprehension']

new_tsv = []
for participant in sorted(metadata):
    meta = metadata[participant]
    row = [participant,
           ','.join(metadata[participant]['age']),
           ','.join(metadata[participant]['sex']),
           ','.join(metadata[participant]['task']),
           ','.join(metadata[participant]['condition']),
           ','.join(metadata[participant]['comprehension'])]
    new_tsv.append(row)
    
df = pd.DataFrame(new_tsv, columns=columns)

df.to_csv(join(final_dir, 'participants.tsv'), sep='\t', index=False)


# Create descriptive participants.json
desc = {"age": {"Description": "age of the participant",
                "Units": "years"},
        "comprehension": {"Description": "behavioral comprehension "
                          "score ranging from 0 to 1 for corresponding "
                          "task (if applicable)"},
        "condition": {"Description": "within- or between-subject "
                      "experimental condition for corresponding task "
                      "(if applicable)"},
        "task": {"Description": "tasks (story stimuli) collected for participant"},
        "sex": {"Description": "sex of the participant",
                "Levels": {"m": "male", "f": "female"}}}

with open(join(final_dir, 'participants.json'), 'w') as f:
    json.dump(desc, f, sort_keys=True, indent=2)
