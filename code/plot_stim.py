from os.path import join
import json
from scipy.io.wavfile import read
import numpy as np
from scipy.stats import zscore
import matplotlib.pyplot as plt
import seaborn as sns

task = 'pieman'
base_dir = '/jukebox/hasson/snastase/narratives/'
stim_dir = join(base_dir, 'stimuli')
stim_fn = join(stim_dir, f'{task}_audio.wav')

# Load in wav file sample rate and data
hz, audio = read(stim_fn)

# Onset and offset for snippet
onset, offset = 15, 23
tr = 1.5

# Get parameters for full clip
clip = zscore(audio[:, 0])
duration = len(clip) / hz
seconds = np.arange(0, duration, 1 / hz)
trs = np.arange(0, duration / tr, 1 / tr / hz)

# Highlight shorter onset–offset snippet
snip = np.full(clip.shape, np.nan)
snip[np.arange(onset * hz, (offset + 1) * hz)] = clip[
     np.arange(onset * hz, (offset + 1) * hz)]

sns.set_context(context='notebook', font_scale=1.02)
fig, ax = plt.subplots(figsize=(8, .85))
ax.plot(seconds, clip, color='.8')
ax.set_xlim(0, duration)
ax.set_xlabel('seconds', va='center', ha='left')
ax.xaxis.set_label_coords(1.015, 0)
ax.axes.get_yaxis().set_ticks([])
ax.set_ylabel('amplitude')
ax.set_ylim(np.amin(clip) - 1.7, np.amax(clip) + 1)
ax1 = ax.twiny()
ax1.plot(trs, snip, color='.5')
ax1.set_xlim(0, duration / tr)
ax1.axes.get_yaxis().set_ticks([])
ax1.set_xlabel('TRs', va='center', ha='left')
ax1.xaxis.set_ticks_position("bottom")
ax1.xaxis.set_label_coords(1.015, -0.6)
ax1.spines["bottom"].set_position(("axes", -0.6))
ax.vlines([onset, offset], ymin=0, ymax=20,
          colors='darkorange', zorder=0)
sns.despine()
plt.savefig(join(base_dir, 'code', 'fig1_pieman.png'),
            transparent=True, dpi=300,
            bbox_inches='tight')


# Plot words for snippet
clip = zscore(audio[onset * hz:, 0])
duration = len(clip) / hz
seconds = np.arange(0, duration, 1 / hz) + onset
trs = np.arange(0, duration / tr, 1 / tr / hz) + onset / tr

gentle_dir = join(stim_dir, 'gentle', task)
gentle_fn = join(gentle_dir, 'align.json')

with open(gentle_fn) as f:
    gentle = json.load(f)['words']

words, starts, ends, middles = [], [], [], []
for word in gentle:
    start, end = word['start'], word['end']
    if end > offset:
        break
    middle = start + (end - start) / 2
    words.append(word['word'])
    starts.append(start)
    ends.append(end)
    middles.append(middle)
    
# Manually adjust some word placement
dodge = .045
dodges = [0, 0, 0, 0, 0, 0, 0, -dodge, dodge,
          0, -dodge, dodge, 0, -dodge, dodge,
          0, 0, 0, -dodge, dodge, 0]
assert len(words) == len(dodges)
    
sns.set_context(context='notebook', font_scale=1.02)
fig, ax = plt.subplots(figsize=(8, .65))
ax.plot(seconds, clip, color='w', alpha=1)
ax.set_xlim(onset, offset)
ax.set_xticks(np.arange(onset, offset + 1))
ax.set_xlabel('seconds', va='center', ha='left')
ax.xaxis.set_label_coords(1.015, 0)
ax.axes.get_yaxis().set_ticks([])
ax.set_ylabel('amplitude', color='w')
ax.set_ylim(np.amin(clip) + 5, np.amax(clip) - 10)
ax1 = ax.twiny()
ax1.plot(trs, clip, color='.5')
ax1.set_xlim(onset / tr, offset / tr)
ax1.axes.get_yaxis().set_ticks([])
ax1.set_xticks(np.arange(onset / tr, offset / tr, tr))
ax1.set_xlabel('TRs', va='center', ha='left')
ax1.xaxis.set_ticks_position("bottom")
ax1.xaxis.set_label_coords(1.015, -0.75)
ax1.spines['bottom'].set_position(('axes', -0.75))
for word, x, dodge in zip(words, middles, dodges):
    ax.annotate(word, xy=(x + dodge, 8), ha='left', va='center',
                rotation=40, rotation_mode='anchor', size=10.5,
                annotation_clip=False)
sns.despine()
plt.savefig(join(base_dir, 'code', 'fig1_words.png'),
            transparent=True, dpi=300,
            bbox_inches='tight')


# Load example voxel time series from example subject
duration = 300

task = 'pieman'
subject = 'sub-078'
space = 'fsaverage6'
hemi = 'L'
clean_dir = join(base_dir, 'derivatives', 'afni-smooth', subject, 'func')
clean_fn  = join(clean_dir, (f'{subject}_task-{task}_space-{space}_'
                             f'hemi-{hemi}_desc-clean.func.gii'))
clean_map = read_gifti(clean_fn)

v1 = zscore(clean_map[:, 27347])
v2 = zscore(clean_map[:, 38741])
v3 = zscore(clean_map[:, 16086])
v3 = zscore(clean_map[:, 7314])

sns.set_context(context='notebook', font_scale=1.02)
fig, axs = plt.subplots(3, 1, figsize=(8, 1.5))
axs[0].plot(np.arange(duration), v1, color='red', lw=2)
axs[1].plot(np.arange(duration), v2, color='darkorange', lw=2)
axs[2].plot(np.arange(duration), v3, color='purple', lw=2)
for ax in axs:
    ax.axes.get_yaxis().set_ticks([])
    ax.set_xlim(0, duration)
axs[0].axes.get_xaxis().set_ticks([])
axs[0].set_ylim(np.amin(v1) - .75, np.amax(v1) + .75)
axs[1].axes.get_xaxis().set_ticks([])
axs[1].set_ylabel('fMRI')
axs[1].set_xlabel('seconds', va='center', ha='left', color='w')
axs[1].xaxis.set_label_coords(1.015, 0)
axs[1].set_ylim(np.amin(v2) - .75, np.amax(v2) + .75)
axs[2].set_xlabel('TRs', va='center', ha='left')
axs[2].xaxis.set_label_coords(1.015, 0)
axs[2].set_ylim(np.amin(v3) - .75, np.amax(v3) + .75)
sns.despine()
plt.savefig(join(base_dir, 'code', 'fig1_voxels.png'),
            transparent=True, dpi=300,
            bbox_inches='tight')
