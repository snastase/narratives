from os.path import join
import json
from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Assign some directories
base_dir = '/jukebox/hasson/snastase/narratives'
mriqc_dir = join(base_dir, 'derivatives', 'mriqc')


# Load in MRIQC's group BOLD values
mriqc_fn = join(mriqc_dir, 'group_bold.tsv')
mriqc_df = pd.read_csv(mriqc_fn, sep='\t')
mriqc_df['task'] = mriqc_df['bids_name'].str.split(
    'task-').str[-1].str.split('_').str[0]

# Collapse related tasks
replace = {'notthefallintact': 'notthefall',
           'notthefalllongscram': 'notthefall',
           'notthefallshortscram': 'notthefall',
           'shapesphysical': 'shapes',
           'shapessocial': 'shapes'}
mriqc_df['task'].replace(to_replace=replace, inplace=True)

# Chronological task order
task_order = ['pieman', 'tunnel', 'lucy', 'prettymouth',
              'milkyway', 'slumlordreach', 'notthefall',
              'merlin', 'sherlock', 'schema', 'shapes',
              '21styear', 'piemanpni', 'bronx',
              'black', 'forgot']


# Organize tSNR values by task
tsnr_df = mriqc_df[['task', 'tsnr']]
tsnr_df.rename(columns={'tsnr': 'tSNR'},
               inplace=True)


# Plot tSNR across all tasks and subjects
tsnr_all = tsnr_df.assign(task='all tasks')

sns.set_context(context='notebook', font_scale=1.03)
fig = plt.figure(constrained_layout=True, figsize=(8, 5))
gs = fig.add_gridspec(10, 1)
ax0 = fig.add_subplot(gs[:8, :])
ax1 = fig.add_subplot(gs[8:, :])
v = sns.violinplot(x='tSNR', y='task', data=tsnr_df, color='.8',
                   order=task_order, inner=None, linewidth=1,
                   cut=0, split=True, zorder=0, ax=ax0)
for i in range(len(v.collections)):
    v.collections[i].set_edgecolor('.8')
sns.stripplot(x='tSNR', y='task', data=tsnr_df, color='.3',
              jitter=False, order=task_order, size=3, marker='|',
              alpha=.5, linewidth=1, zorder=1, ax=ax0)
sns.pointplot(x='tSNR', y='task', data=tsnr_df, join=False,
              order=task_order, color='darkred', ax=ax0)
ax0.xaxis.label.set_visible(False)
ax0.tick_params(axis='y',length=0)

v = sns.violinplot(x='tSNR', y='task', data=tsnr_all, color='.8',
                   inner=None, linewidth=1, cut=0, split=True,
                   zorder=0, ax=ax1)
v.collections[0].set_edgecolor('.8')
sns.stripplot(x='tSNR', y='task', data=tsnr_all, color='.3',
              jitter=False, size=3, marker='|', alpha=.5, linewidth=1,
              zorder=1, ax=ax1)
sns.pointplot(x='tSNR', y='task', data=tsnr_all, join=False,
              scale=1.2, color='darkred', ax=ax1)
ax1.tick_params(axis='y',length=0)
ax1.yaxis.label.set_visible(False)
ax1.set_xlabel('temporal signal-to-noise ratio (tSNR)')
sns.despine()
plt.tight_layout()
plt.savefig(join(base_dir, 'code', 'fig2_tsnr.png'),
            transparent=True, dpi=300,
            bbox_inches='tight')
plt.show()


# Organize FD values by task
fd_df = mriqc_df[['task', 'fd_mean']]
fd_df.rename(columns={'fd_mean': 'FD'},
             inplace=True)

# Plot FD across all tasks and subjects
fd_all = fd_df.assign(task='all tasks')

sns.set_context(context='notebook', font_scale=1.03)
fig = plt.figure(constrained_layout=True, figsize=(8, 5))
gs = fig.add_gridspec(10, 1)
ax0 = fig.add_subplot(gs[:8, :])
ax1 = fig.add_subplot(gs[8:, :])
v = sns.violinplot(x='FD', y='task', data=fd_df, color='.8',
                   order=task_order, inner=None, linewidth=1,
                   cut=0, split=True, zorder=0, ax=ax0)
for i in range(len(v.collections)):
    v.collections[i].set_edgecolor('.8')
sns.stripplot(x='FD', y='task', data=fd_df, color='.3',
              jitter=False, order=task_order, size=3, marker='|',
              alpha=.5, linewidth=1, zorder=1, ax=ax0)
sns.pointplot(x='FD', y='task', data=fd_df, join=False,
              order=task_order, color='darkred', estimator=np.median, ax=ax0)
ax0.xaxis.label.set_visible(False)
ax0.tick_params(axis='y',length=0)

v = sns.violinplot(x='FD', y='task', data=fd_all, color='.8',
                   inner=None, linewidth=1, cut=0, split=True,
                   zorder=0, ax=ax1)
v.collections[0].set_edgecolor('.8')
sns.stripplot(x='FD', y='task', data=fd_all, color='.3',
              jitter=False, size=3, marker='|', alpha=.5, linewidth=1,
              zorder=1, ax=ax1)
sns.pointplot(x='FD', y='task', data=fd_all, join=False,
              scale=1.2, color='darkred', estimator=np.median, ax=ax1)
ax1.tick_params(axis='y',length=0)
ax1.yaxis.label.set_visible(False)
ax1.set_xlabel("framewise displacement (FD)")
sns.despine()
plt.tight_layout()
plt.savefig(join(base_dir, 'code', 'fig2_fd.png'),
            transparent=True, dpi=300,
            bbox_inches='tight')
plt.show()


# Load subject metadata to get filenames
with open(join(base_dir, 'code', 'subject_meta.json')) as f:
    subject_meta = json.load(f)

# Load in FWHM smoothness estimates
afni_dir = join(base_dir, 'derivatives', 'afni-nosmooth')

fwhm_dfs = []
for subject in subject_meta:
    fwhm_fns = glob(join(afni_dir, subject, 'func',
                         f'{subject}_task-*_desc-fwhm_smoothness.tsv'))
    
    for fwhm_fn in fwhm_fns:
        task = fwhm_fn.split('task-')[-1].split('_')[0]
        
        fwhm_df = pd.read_csv(fwhm_fn, sep='\t')
        fwhm_df['subject'] = subject
        fwhm_df['task'] = task
        fwhm_dfs.append(fwhm_df)
fwhm_df = pd.concat(fwhm_dfs)

# Collapse related tasks
replace = {'notthefallintact': 'notthefall',
           'notthefalllongscram': 'notthefall',
           'notthefallshortscram': 'notthefall',
           'shapesphysical': 'shapes',
           'shapessocial': 'shapes'}
fwhm_df['task'].replace(to_replace=replace, inplace=True)

fwhm_melt = pd.melt(fwhm_df, id_vars=['subject', 'task'],
                    value_vars=['x', 'y', 'z', 'combined'],
                    value_name='FWHM',
                    var_name='axis')
fwhm_cmb = fwhm_melt[fwhm_melt['axis'] == 'combined']
fwhm_xyz = fwhm_melt[fwhm_melt['axis'].isin(['x', 'y', 'z'])]

fwhm_all_cmb = fwhm_cmb.assign(task='all tasks')
fwhm_all_xyz = fwhm_xyz.assign(task='all tasks')

xyz_col = ['orange', 'sunny yellow', 'purply']
xyz_pal = sns.xkcd_palette(xyz_col)

sns.set_context(context='notebook', font_scale=1.03)
fig = plt.figure(constrained_layout=True, figsize=(8, 5))
gs = fig.add_gridspec(10, 1)
ax0 = fig.add_subplot(gs[:8, :])
ax1 = fig.add_subplot(gs[8:, :])

v = sns.violinplot(x='FWHM', y='task', data=fwhm_xyz, color='.8',
                   order=task_order, inner=None, linewidth=1,
                   cut=0, zorder=0, ax=ax0)
for i in range(len(v.collections)):
    v.collections[i].set_edgecolor('.8')
sns.stripplot(x='FWHM', y='task', hue='axis', data=fwhm_xyz,              
              jitter=False, order=task_order, size=3, marker='|',
              palette=xyz_pal, alpha=.5, linewidth=1, zorder=1, ax=ax0)
sns.pointplot(x='FWHM', y='task', data=fwhm_cmb, join=False,
              order=task_order, color='darkred', estimator=np.median, 
              ax=ax0)
ax0.xaxis.label.set_visible(False)
ax0.tick_params(axis='y',length=0)
ax0.yaxis.label.set_visible(False)
ax0.legend(title='axis', loc='upper left')

v = sns.violinplot(x='FWHM', y='task', data=fwhm_all_xyz, color='.8',
                   inner=None, linewidth=1, cut=0, zorder=0, ax=ax1)
v.collections[0].set_edgecolor('.8')
sns.stripplot(x='FWHM', y='task', hue='axis', data=fwhm_all_xyz, 
              jitter=False, size=3, marker='|', alpha=.5, linewidth=1,
              palette=xyz_pal, zorder=1, ax=ax1)
sns.pointplot(x='FWHM', y='task', data=fwhm_all_cmb, join=False,
              scale=1.2, color='darkred', estimator=np.median,
              legend=False, ax=ax1)
ax1.get_legend().remove()
ax1.tick_params(axis='y',length=0)
ax1.yaxis.label.set_visible(False)
ax1.set_xlabel('smoothness FWHM (mm)')
sns.despine()
plt.tight_layout()
plt.savefig(join(base_dir, 'code', 'fig2_fwhm.png'),
            transparent=True, dpi=300,
            bbox_inches='tight')
plt.show()


# Check smoothing records for SurfSmooth
afni_dir = join(base_dir, 'derivatives', 'afni-smooth')

with open(join(base_dir, 'code', 'task_meta.json')) as f:
    task_meta = json.load(f)

# Load in surface smoothing records
surf_smooth = {'FWHM': [], 'subject': [], 'task': [],
               'iterations': [], 'sigma': []}
for task in task_meta:
    for subject in task_meta[task]:
        smrec_fns = glob(join(afni_dir, subject, 'func',
                              f'{subject}_task-{task}_*.smrec'))
        for smrec_fn in smrec_fns:
            with open(smrec_fn) as f:
                last_line = f.readlines()[-1]
            i, f, s = last_line.strip().split()
            surf_smooth['FWHM'].append(float(f))
            surf_smooth['subject'].append(subject)
            surf_smooth['task'].append(task)
            surf_smooth['iterations'].append(int(i))
            surf_smooth['sigma'].append(float(s))

# Convert to pandas
surf_smooth = pd.DataFrame(surf_smooth)

# Get summary statistics about surface smoothing
print(f"Overall mean smoothness: {surf_smooth['FWHM'].mean():.3f} "
      f"(SD: {surf_smooth['FWHM'].std():.3f})")

acq_tasks = {'Skyra': ['21styear', 'lucy', 'merlin', 'milkyway',
                       'notthefallintact', 'notthefallshortscram',
                       'notthefalllongscram', 'pieman','prettymouth',
                       'sherlock','slumlordreach', 'tunnel'],
             'Prisma (2 mm)': ['schema', 'shapesphysical', 'shapessocial'],
             'Prisma (2.5 mm)': ['bronx', 'piemanpni', 'black', 'forgot']}

for acq in acq_tasks:
    acq_mean = surf_smooth[surf_smooth['task'].isin(
        acq_tasks[acq])]['FWHM'].mean()
    acq_std = surf_smooth[surf_smooth['task'].isin(
        acq_tasks[acq])]['FWHM'].std()
    print(f"{acq} mean smoothness: {acq_mean:.3f} (SD: {acq_std:.3f})")
