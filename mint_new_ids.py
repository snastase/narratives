from os.path import join
import json
import pandas as pd

# Base staging directory
base_dir = '/jukebox/hasson/snastase/narratives-staging'

# Session label to BIDS ID mapping--check date!
with open(join(base_dir, 'bids_ids_2019-12-10.json')) as f:
    bids_ids = json.load(f)

# Get current max BIDS ID
max_id = max([int(i) for i in bids_ids.values()])
    
# Lable for story with new participants
# (so we don't look all over the spreadsheet)
new_story = "It's Not the Fall that Gets You"
    
# Read in subjects spreadsheet--check date!
df = pd.read_csv(join(base_dir, 'subjects_spreadsheet_2020-01-28.tsv'), delimiter="\t")
df = df[df['Story'] == new_story]
df = df.reset_index()

# Make a dictionary for new sessions and BIDS IDs
minted_ids = {}
existing_ids = {}

# Loop through session IDs and mint new BIDS IDs
for i, row in df.iterrows():
    session = row['Session']
    duplicates = row['Repetitions']
    if session in bids_ids:
        bids_id = bids_ids[session]
        print(f"Session {session} already assigned old BIDS ID {bids_id}")
        continue
    if session in minted_ids:
        bids_id = minted_ids[session]
        print(f"Session {session} already assigned new BIDS ID {bids_id}")
        continue
    else:
        if pd.isna(duplicates):
            max_id += 1
            minted_ids[session] = str(max_id)
            print(f"Minting new BIDS ID {max_id} for session {session}!")
        else:
            dups = duplicates.replace(' ', '').split(',')
            for dup in dups:
                if dup in bids_ids:
                    bids_id = bids_ids[dup]
                    existing_ids[session] = bids_id
                    print(f"Duplicate {dup} for {session} already assigned old BIDS ID {bids_id}")
                    continue
                if dup in minted_ids:
                    bids_id = minted_ids[dup]
                    minted_ids[session] = bids_id
                    print(f"Duplicate {dup} for {session} already assigned new BIDS ID {bids_id}")
                    raise

# Check that we don't have colliding sessions across BIDS IDs
for eid in existing_ids:
    assert eid not in bids_ids
    assert existing_ids[eid] in bids_ids.values()
    assert eid not in minted_ids
    assert existing_ids[eid] not in minted_ids.values()
    
for mid in minted_ids:
    assert mid not in bids_ids
    assert minted_ids[mid] not in bids_ids.values()
    assert int(minted_ids[mid]) > int(max(bids_ids.values()))
    assert mid not in existing_ids
    assert minted_ids[mid] not in existing_ids.values()
    assert int(minted_ids[mid]) > int(max(existing_ids.values()))

# Merge all IDs
new_bids_ids = {**bids_ids, **existing_ids, **minted_ids}
final_bids_ids = dict(sorted(new_bids_ids.items()))

# Save the new updated BIDS IDs--check date!
with open(join(base_dir, 'bids_ids_2020-01-29.json'), 'w') as f:
    json.dump(final_bids_ids, f, indent=2, sort_keys=True)