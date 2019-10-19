import json
from os.path import join
from os import chdir
from shutil import copyfile
from glob import glob
import pandas as pd

staging_dir = '/jukebox/hasson/snastase/narratives-staging'
bids_dir = '/jukebox/hasson/snastase/narratives'

desc = {"Acknowledgements": "We thank the administrative staff "
                            "of the Princeton Neuroscience Institute.",
        "Authors": ["Samuel A. Nastase", 
                    "Yun-Fei Liu",
                    "Hanna Hillman",
                    "Asieh Zadbood",
                    "Liat Hasenfratz",
                    "Neggin Keshavarzian", 
                    "Janice Chen",
                    "Christopher J. Honey",
                    "Yaara Yeshurun",
                    "Mor Regev",
                    "Mai Nguyen",
                    "Claire H. C. Chang",
                    "Christopher Baldassano",
                    "Olga Lositsky",
                    "Michael A. Chow",
                    "Yuan Chang Leong",
                    "Paula P. Brooks",
                    "Kenneth A. Norman",
                    "Uri Hasson"],
        "BIDSVersion": "1.2.1",
        "DatasetDOI": "TODO",
        "Funding": ["National Institutes of Health Grant R01-MH094480",
                    "National Institutes of Health Grant DP1-HD091948",
                    "National Institutes of Health Grant R01-MH112566",
                    "National Institutes of Health Grant R01-MH112357",
                    "National Institutes of Health Grant T32-MH065214",
                    "Defense Advanced Research Projects Agency Grant FA8750-18-C-0213"],
        "HowToAcknowledge": "TODO",
        "License": "PDDL (http://opendatacommons.org/licenses/pddl/)",
        "Name": "Narratives",
        "ReferencesAndLinks": ["TODO"]}

with open(join(bids_dir, 'dataset_description.json'), 'w') as f:
    json.dump(desc, f, sort_keys=True, indent=2)


# Copy staged README and CHANGES as well
copyfile(join(staging_dir, 'staging', 'README'), join(bids_dir, 'README'))
copyfile(join(staging_dir, 'staging', 'CHANGES'), join(bids_dir, 'CHANGES'))


# Create *_scans.tsv files
write_files = True

datasets = ['pieman', 'tunnel', 'lucy', 'prettymouth',
            'milkyway', 'slumlordreach', 'notthefall',
            'merlin', 'sherlock', 'schema', 'shapessocial',
            'shapesphysical', '21styear', 'piemanpni',
            'bronx', 'forgot', 'black']

# Load participant metadata
with open(join(staging_dir, 'staging', 'participants_meta.json')) as f:
    metadata = json.load(f)
    
header = ['filename', 'condition', 'comprehension']

for participant in metadata:
    chdir(join(bids_dir, participant))
    
    scans = []
    anat_fns = glob('anat/*.nii.gz')
    for anat_fn in anat_fns:
        scans.append([anat_fn, 'n/a', 'n/a'])
    
    func_fns = glob('func/*.nii.gz')
    for func_fn in func_fns:
        task = func_fn.split('_')[1].split('-')[1]
        task_i = metadata[participant]['task'].index(task)
        cond = metadata[participant]['condition'][task_i]
        comp = metadata[participant]['comprehension'][task_i]
        scans.append([func_fn, cond, comp])
        
    scans = pd.DataFrame(scans, columns=header)
    scans_fn = join(bids_dir, participant,
                    f'{participant}_scans.tsv')
    if write_files:
        scans.to_csv(scans_fn, sep='\t', index=False)

# Optionally create a scans.json
scans_meta = {"filename": {"Description": "filename for the scan"},
              "comprehension": {"Description": "behavioral comprehension "
                                "score ranging from 0 to 1 for the scan "
                                "(if applicable)"},
              "condition": {"Description": "within- or between-subject "
                            "experimental condition for the scan "
                            "(if applicable)"}}

for subject in metadata:
    with open(join(bids_dir, subject, f'{subject}_scans.json'), 'w') as f:
        json.dump(scans_meta, f, sort_keys=True, indent=2)

    
# Fix task names in metadata
datasets = ['pieman', 'tunnel', 'lucy', 'prettymouth',
            'milkyway', 'slumlordreach', 'notthefall',
            'merlin', 'sherlock', 'schema', 'shapessocial',
            'shapesphysical', '21styear', 'piemanpni',
            'bronx', 'forgot', 'black']

for participant in metadata:
    chdir(join(bids_dir, participant))
    
    func_fns = glob('func/*.json')
    for func_fn in func_fns:
        with open(func_fn) as f:
            func_meta = json.load(f)
            
        task = func_fn.split('_')[1].split('-')[1]

        if func_meta['TaskName'] != task:
            print(f"Task mismatch for {func_fn}\n\t "
                  f"got {func_meta['TaskName']}; should be {task}")
        func_meta['TaskName'] = task
        func_meta['TaskDescription'] = ("Passively listened to "
                                        f"audio story '{task}'")
        func_meta['NumberOfVolumesDiscardedByScanner'] = 3
        if 'ParellelReductionType' in func_meta:
            if func_meta['ParellelReductionType'] == 'TODO':
                func_meta.pop('ParellelReductionType')
                func_meta['ParallelReductionType'] = 'GRAPPA'
                print("Filled in GRAPPA ParallelReductionType")
        
        with open(func_fn, 'w') as f:
            json.dump(func_meta, f, sort_keys=True, indent=2)
