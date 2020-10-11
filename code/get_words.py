from os.path import exists, join
import json
import numpy as np
import pandas as pd


base_dir = '/jukebox/hasson/snastase/narratives/'
gentle_dir = join(base_dir, 'stimuli', 'gentle')


tasks = ['pieman', 'tunnel', 'lucy', 'prettymouth',
         'milkywayoriginal', 'milkywayvodka', 'milkywaysynonyms',
         'slumlordreach', 'notthefallintact', 'merlin', 'sherlock',
         'shapesphysical', 'shapessocial', '21styear',
         'piemanpni', 'bronx', 'black', 'forgot']

# Get number of words for each story stimulus
total_words, total_miss, total_unk = 0, 0, 0
for task in tasks:
    
    gentle_fn = join(gentle_dir, task, 'align.json')
    if not exists(gentle_fn):
        print(f"Still waiting on {task}...")
    else:
        with open(gentle_fn) as f:
            gentle_json = json.load(f)

        n_words = len(gentle_json['words'])
        n_miss, n_unk = 0, 0
        for word in gentle_json['words']:
            if word['case'] == 'not-found-in-audio':
                n_miss += 1
            elif word['case'] == 'success':
                if word['alignedWord'] == '<unk>':
                    n_unk += 1
                    
        total_words += n_words
        total_miss += n_miss
        total_unk += n_unk

        print(f"{task} has {n_words} words total, "
              f"{n_miss} missed ({n_miss/n_words:.1%}), "
              f"and {n_unk} unknown ({n_unk/n_words:.1%})")

print(f"{total_words} words total across stories, "
      f"{total_miss} missed ({total_miss/total_words:.1%}), "
      f"and {total_unk} unknown ({total_unk/total_words:.1%})")


# Split apart slumlordreach
gentle_fn = join(gentle_dir, 'slumlordreach', 'align.json')

with open(gentle_fn) as f:
    gentle_json = json.load(f)
    
for i, word in enumerate(gentle_json['words']):
    if 'start' in word and word['start'] > 950:
        break

for task in ['slumlord', 'reach']:
    if task == 'slumlord':
        words = gentle_json['words'][:i]
    elif task == 'reach':
        words = gentle_json['words'][i:]

    n_words = len(words)
    n_miss, n_unk = 0, 0
    for word in words:
        if word['case'] == 'not-found-in-audio':
            n_miss += 1
        elif word['case'] == 'success':
            if word['alignedWord'] == '<unk>':
                n_unk += 1

    print(f"{task} has {n_words} words total, "
          f"{n_miss} missed ({n_miss/n_words:.1%}), "
          f"and {n_unk} unknown ({n_unk/n_words:.1%})")
    

# Sum up the schema stories
tasks = ['bigbang', 'friends', 'himym', 'santa',
         'seinfeld', 'shame', 'upintheair', 'vinny']

schema_words, schema_miss, schema_unk = 0, 0, 0
for task in tasks:
    
    gentle_fn = join(gentle_dir, task, 'align.json')

    with open(gentle_fn) as f:
        gentle_json = json.load(f)
    
    n_words = len(gentle_json['words'])
    n_miss, n_unk = 0, 0
    for word in gentle_json['words']:
        if word['case'] == 'not-found-in-audio':
            n_miss += 1
        elif word['case'] == 'success':
            if word['alignedWord'] == '<unk>':
                n_unk += 1
                
    schema_words += n_words
    schema_miss += n_miss
    schema_unk += n_unk

    print(f"{task} has {n_words} words total, "
          f"{n_miss} missed ({n_miss/n_words:.1%}), "
          f"and {n_unk} unknown ({n_unk/n_words:.1%})")
    
print(f"{schema_words} words total across schema stories, "
      f"{schema_miss} missed ({schema_miss/schema_words:.1%}), "
      f"and {schema_unk} unknown ({schema_unk/schema_words:.1%})")


# Add schema words to total
total_words += schema_words
total_miss += schema_miss
total_unk += schema_unk

# Note that this includes multiple conditions (e.g. milkyway)
print(f"{total_words} words total across stories, "
      f"{total_miss} missed ({total_miss/total_words:.1%}), "
      f"and {total_unk} unknown ({total_unk/total_words:.1%})")
