from os.path import join
from os import chdir
from glob import glob
import json
import pandas as pd

base_dir = '/jukebox/hasson/snastase'
staging_dir = join(base_dir, 'narratives-staging')
bids_dir = join(base_dir, 'narratives-raw')

datasets = ['pieman', 'tunnel', 'lucy', 'prettymouth',
            'milkyway', 'slumlordreach', 'notthefall',
            'merlin', 'sherlock', 'schema', 'shapessocial',
            'shapesphysical', '21styear', 'piemanpni',
            'bronx', 'forgot', 'black']


# Load participant metadata
with open(join(staging_dir, 'staging', 'participants_meta.json')) as f:
    metadata = json.load(f)
    
header = ['onset', 'duration', 'trial_type', 'stim_file']


# Manually collate event onsets
events = {}
events['pieman'] = [['0.0', '13.0', 'music', 'pieman_audio.wav'],
                    ['15.0', '422.0', 'story', 'pieman_audio.wav']]

events['tunnel'] = [['3.0', '1534.0', 'story', 'tunnel_audio.wav']]

events['lucy'] = [['2.0', '542.0', 'story', 'lucy_audio.wav']]

events['prettymouth'] = [['0.0', '18.0', 'music', 'prettymouth_audio.wav'],
                         ['21.0', '676.0', 'story', 'prettymouth_audio.wav']]

events['milkyway'] = {'original': [['0.0', '18.0', 'music',
                                    'milkywayoriginal_audio.wav'],
                                   ['21.0', '404.0', 'story',
                                    'milkywayoriginal_audio.wav']],
                      'vodka': [['0.0', '18.0', 'music',
                                 'milkywayvodka_audio.wav'],
                                ['21.0', '404.0', 'story',
                                 'milkywayvodka_audio.wav']],
                      'synonyms': [['0.0', '18.0', 'music',
                                    'milkywaysynonyms_audio.wav'],
                                   ['21.0', '404.0', 'story',
                                    'milkywaysynonyms_audio.wav']]}

events['slumlordreach'] = [['4.5', '22.0', 'music', 'slumlordreach_audio.wav'],
                           ['29.5', '903.0', 'story', 'slumlordreach_audio.wav'],
                           ['944.5', '22.0', 'music', 'slumlordreach_audio.wav'],
                           ['969.5', '825.0', 'story', 'slumlordreach_audio.wav']]

events['notthefall'] = [['4.5', '22.0', 'music', 'notthefall_audio.wav'],
                        ['29.5', '547.0', 'story', 'notthefall_audio.wav']]

events['merlin'] = [['4.5', '25.0', 'music', 'merlin_audio.wav'],
                    ['33.5', '886.0', 'story', 'merlin_audio.wav']]

events['sherlock'] = [['4.5', '25.0', 'music', 'sherlock_audio.wav'],
                      ['33.5', '1052.0', 'story', 'sherlock_audio.wav']]

events['shapesphysical'] = [['4.5', '37.0', 'music', 'shapesphysical_audio.wav'],
                            ['49.5', '405.0', 'story', 'shapesphysical_audio.wav']]

events['shapessocial'] = [['4.5', '37.0', 'music', 'shapessocial_audio.wav'],
                          ['49.5', '408.0', 'story', 'shapessocial_audio.wav']]

events['21styear'] = [['0.0', '18.0', 'music', '21styear_audio.wav'],
                      ['21.0', '3338.0', 'story', '21styear_audio.wav']]

events['piemanpni'] = [['12.0', '400.0', 'story', 'piemanpni_audio.wav']]

events['bronx'] = [['12.0', '536.0', 'story', 'bronx_audio.wav']]

events['black'] = [['12.0', '800.0', 'story', 'black_audio.wav']]

events['forgot'] = [['12.0', '837.0', 'story', 'forgot_audio.wav']]



# Check for movie or story in schema
schema_stories = ['bigbang', 'friends', 'himym', 'santa',
                  'seinfeld', 'shame', 'upintheair', 'vinny']


# Loop through subjects and create events files
for subject in metadata:
    
    chdir(join(bids_dir, subject))
    func_fns = glob('func/*.nii.gz')
    for func_fn in func_fns:
        task = func_fn.split('_')[1].split('-')[1]
        
        if task == 'milkyway':
            task_i = metadata[subject]['task'].index(task)
            cond = metadata[subject]['condition'][task_i]
            events_tsv = pd.DataFrame(events[task][cond],
                                      columns=header)
            
        elif task == 'schema':
            events_tsv = pd.read_csv(join(staging_dir, 'schema', subject,
                                          '_'.join(
                                func_fn.split('_')[:-1]) + '_events.tsv'),
                                    sep='\t')
            trial_type, stim_file = [], []
            for stim in events_tsv['trial_type']:
                if stim.lower() in schema_stories:
                    trial_type.append('story')
                    stim_file.append(stim.lower() + '_audio.wav')
                else:
                    trial_type.append('movie')
                    stim_file.append('n/a')
                    
            events_tsv['trial_type'] = trial_type
            events_tsv['stim_file'] = stim_file
            
        else:
            events_tsv = pd.DataFrame(events[task], columns=header)
            
        events_tsv.to_csv('_'.join(func_fn.split('_')[:-1]) + '_events.tsv',
                          sep='\t', index=False)
