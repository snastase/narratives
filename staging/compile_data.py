from os.path import basename, exists, join
from os import makedirs, remove, rename
from shutil import copyfile, move
from glob import glob
import json
import numpy as np
import pandas as pd
import nibabel as nib

base_dir = '/jukebox/hasson/snastase'
staging_dir = join(base_dir, 'narratives-staging')
bids_dir = join(base_dir, 'narratives-openneuro')

datasets = ['pieman', 'tunnel', 'lucy', 'prettymouth',
            'milkyway', 'slumlordreach', 'notthefall',
            'merlin', 'sherlock', 'schema', 'shapessocial',
            'shapesphysical', '21styear', 'piemanpni',
            'bronx', 'forgot', 'black']


# Toggle to dry-run vs copy files
copy_func = True
copy_anat = True


# Load participant metadata
with open(join(staging_dir, 'staging', 'participants_meta.json')) as f:
    metadata = json.load(f)

exclude_ids = []


# List of duplicate anatomicals to exclude
task_dupli = ['notthefall', 'sherlock', 'shapesphysical',
              'bronx', 'forgot', 'black']

anat_dupli = {'sub-001': ['pieman', 'tunnel', 'lucy'],
              'sub-004': ['pieman', 'tunnel', 'lucy'],
              'sub-005': ['pieman', 'tunnel', 'lucy'],
              'sub-013': ['pieman', 'tunnel', 'lucy'],
              'sub-016': ['pieman', 'tunnel', 'lucy'],
              'sub-022': ['pieman', 'tunnel', 'lucy'],
              'sub-023': ['pieman', 'tunnel', 'lucy'],
              'sub-025': ['pieman', 'tunnel', 'lucy'],
              'sub-026': ['pieman', 'tunnel', 'lucy'],
              'sub-041': ['pieman', 'tunnel', 'lucy'],
              'sub-052': ['pieman', 'tunnel', 'lucy', 'milkyway'],
              'sub-053': ['pieman', 'tunnel', 'lucy'],
              'sub-055': ['pieman', 'tunnel', 'lucy'],
              'sub-056': ['pieman', 'tunnel', 'lucy'],
              'sub-057': ['pieman', 'tunnel', 'lucy'],
              'sub-058': ['pieman', 'tunnel', 'lucy'],
              'sub-059': ['pieman', 'tunnel', 'lucy'],
              'sub-060': ['pieman', 'tunnel', 'lucy'],
              'sub-061': ['pieman', 'tunnel', 'lucy'],
              'sub-062': ['pieman', 'tunnel', 'lucy'],
              'sub-063': ['pieman', 'tunnel', 'lucy'],
              'sub-064': ['pieman', 'tunnel', 'lucy'],
              'sub-065': ['pieman', 'tunnel', 'lucy',
                          'prettymouth', 'slumlord'],
              'sub-066': ['pieman', 'tunnel', 'lucy', 'prettymouth'],
              'sub-079': ['prettymouth', 'milkyway'],
              'sub-084': ['prettymouth', 'milkyway',
                          'slumlordreach'],
              'sub-089': ['prettymouth', 'milkyway'],
              'sub-095': ['prettymouth', 'milkyway'],
              'sub-106': ['prettymouth', 'milkyway',
                          'slumlordreach'],
              'sub-109': ['prettymouth', 'milkyway'],
              'sub-111': ['prettymouth', 'milkyway',
                          'slumlordreach'],
              'sub-132': ['slumlordreach']}

anat_multi = {'sub-016': ['pieman', 'slumlordreach'],
              'sub-049': ['pieman', 'schema', 'shapessocial'],
              'sub-050': ['pieman', 'prettymouth'],
              'sub-052': ['pieman', 'prettymouth'],
              'sub-058': ['pieman', 'shapessocial'],
              'sub-065': ['pieman', 'prettymouth', 'slumlord'],
              'sub-066': ['pieman', 'prettymouth'],
              'sub-075': ['pieman', 'merlin', 'schema',
                          '21styear'],
              'sub-079': ['pieman', 'prettymouth'],
              'sub-089': ['prettymouth', 'schema'],
              'sub-095': ['prettymouth', 'shapessocial'],
              'sub-109': ['prettymouth', 'schema'],
              'sub-115': ['milkyway', 'shapessocial'],
              'sub-131': ['milkyway', 'shapessocial'],
              'sub-127': ['milkyway', 'shapessocial', 'piemanpni'],
              'sub-131': ['milkyway', '21styear'],
              'sub-132': ['slumlordreach', 'schema'],
              'sub-171': ['merlin', 'schema'],
              'sub-181': ['schema', 'shapessocial'],
              'sub-186': ['schema', 'shapessocial'],
              'sub-190': ['schema', 'shapessocial', '21styear'],
              'sub-191': ['schema', 'shapessocial'],
              'sub-200': ['schema', 'shapessocial'],
              'sub-201': ['schema', 'shapessocial', '21styear'],
              'sub-235': ['shapessocial', '21styear'],
              'sub-244': ['shapessocial', '21styear'],
              'sub-249': ['shapessocial', '21styear']}


# Loop through BIDS IDs and grab data
for participant in metadata:
    
    if participant not in exclude_ids:
        
        anat_n = 0    
        for task in metadata[participant]['task']:
            
            if task in ['shapesphysical', 'shapessocial']:
                input_dir = join(staging_dir, 'shapes')
            else:
                input_dir = join(staging_dir, task)
            
            func_dir_in = join(input_dir, participant, 'func')
            anat_dir_in = join(input_dir, participant, 'anat')

            func_dir_out = join(bids_dir, participant, 'func')
            anat_dir_out = join(bids_dir, participant, 'anat')
            if not exists(func_dir_out):
                makedirs(func_dir_out)
            if not exists(anat_dir_out):
                makedirs(anat_dir_out)

            fn_wild = join(func_dir_in,
                           f'{participant}_task-{task}*_bold.nii.gz')
            func_fns = [basename(path) for path in glob(fn_wild)]
            
            
            if len(func_fns) == 0:
                print(f"WARNING! No input {fn_wild}--skipping!")
            elif task == 'schema':
                assert len(func_fns) == 4, f"Couldn't find input {fn_wild}"
            else:
                assert len(func_fns) >= 1, f"Couldn't find input {fn_wild}"

            for fn in func_fns:
                if not exists(join(func_dir_out, fn)):
                    print(f"Copying {fn} to narratives directory")
                    if copy_func:
                        copyfile(join(func_dir_in, fn),
                                 join(func_dir_out, fn))
                        copyfile(join(func_dir_in, fn[:-6] + 'json'),
                                 join(func_dir_out, fn[:-6] + 'json'))
                else:
                    raise Exception(f"COLLISION! {fn} already exists!")

            anat_fns = [basename(path) for path in
                        glob(join(anat_dir_in,
                                  f'{participant}_T*w.nii.gz'))]

            for fn in anat_fns:
                if task in task_dupli:
                    pass
                elif len(glob(join(anat_dir_out, fn.replace('_T', '*_T')))) == 0:
                    print(f"Copying {fn} to narratives directory")
                    if copy_anat:
                        copyfile(join(anat_dir_in, fn),
                                 join(anat_dir_out, fn))
                        copyfile(join(anat_dir_in, fn[:-6] + 'json'),
                                 join(anat_dir_out, fn[:-6] + 'json'))
                    if anat_n == 0:
                        anat_n += 1
                elif participant in anat_dupli and task in anat_dupli[participant]:
                    print(f"Duplicate! Skipping {join(anat_dir_in, fn)}!")
                    pass
                elif participant in anat_multi and task in anat_multi[participant]:
                    if anat_n == 1:
                        move(join(anat_dir_out, fn),
                             join(anat_dir_out,
                                  fn.replace('_T', f'_run-{anat_n}_T')))
                        move(join(anat_dir_out, fn[:-6] + 'json'),
                             join(anat_dir_out,
                                  (fn[:-6] + 'json').replace(
                                      '_T', f'_run-{anat_n}_T')))
                    anat_n += 1
                    copyfile(join(anat_dir_in, fn),
                             join(anat_dir_out,
                                  fn.replace('_T', f'_run-{anat_n}_T')))
                    j_fn = fn[:-6] + 'json'
                    copyfile(join(anat_dir_in, j_fn),
                             join(anat_dir_out,
                                  j_fn.replace('_T', f'_run-{anat_n}_T')))
                    print(f'Multiple! Additional image {join(anat_dir_in, fn)}!')
                else:
                    for exist_fn in glob(join(anat_dir_out, fn.replace('_T', '*_T'))):
                    
                        existing_img = nib.load(join(exist_fn))
                        incoming_img = nib.load(join(anat_dir_in, fn))

                        if existing_img.shape != incoming_img.shape:
                            print(f"CROPPED?! Different-shaped image already "
                                  f"exists for {join(anat_dir_in, fn)}!")
                        else:
                            existing_data = existing_img.get_fdata()
                            incoming_data = incoming_img.get_fdata()
                            if np.allclose(existing_data, incoming_data):
                                print("Warning! Found identical "
                                      "anatomicals--skipping!")
                            else:
                                print(f"COLLISION! Non-identical image already "
                                      f"exists for {join(anat_dir_in, fn)}!")
                                if anat_n == 1:
                                    move(join(anat_dir_out, fn),
                                         join(anat_dir_out,
                                              fn.replace('_T', f'_run-{anat_n}_T')))
                                    move(join(anat_dir_out, fn[:-6] + 'json'),
                                         join(anat_dir_out,
                                              (fn[:-6] + 'json').replace(
                                                  '_T', f'_run-{anat_n}_T')))
                                anat_n += 1
                                copyfile(join(anat_dir_in, fn),
                                         join(anat_dir_out,
                                              fn.replace('_T', f'_run-{anat_n}_T')))
                                j_fn = fn[:-6] + 'json'
                                copyfile(join(anat_dir_in, j_fn),
                                         join(anat_dir_out,
                                              j_fn.replace('_T', f'_run-{anat_n}_T')))
                            
