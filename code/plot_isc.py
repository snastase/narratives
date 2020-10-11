from os.path import join
import json
from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Assign some directories
base_dir = '/jukebox/hasson/snastase/narratives'
afni_dir = join(base_dir, 'derivatives', 'afni-nosmooth')


# Custom mean estimator with Fisher z transformation for correlations
def fisher_mean(correlation, axis=None):
    return np.tanh(np.mean(np.arctanh(correlation), axis=axis))


# Load in EAC ROI ISC values
roi = 'EAC'
roi_fn = join(afni_dir, f'group_roi-{roi}_desc-exclude_isc.json')
with open(roi_fn) as f:
    roi_dict = json.load(f)

# Manually melt this dictionary
roi_iscs = {'ISC': [], 'hemisphere': [], 'task': [], 'subject': []}
for task in roi_dict:
    for hemi in roi_dict[task]:
        for subject in roi_dict[task][hemi]:
            for run in roi_dict[task][hemi][subject]:
                roi_iscs['ISC'].append(roi_dict[task][hemi][subject][run])
                roi_iscs['hemisphere'].append(hemi)
                roi_iscs['task'].append(task)
                roi_iscs['subject'].append(subject)

# Convert to pandas data frame
isc_df = pd.DataFrame(roi_iscs)

# Collapse related tasks
replace = {'notthefallintact': 'notthefall',
           'notthefalllongscram': 'notthefall',
           'notthefallshortscram': 'notthefall',
           'shapesphysical': 'shapes',
           'shapessocial': 'shapes',
           'slumlord': 'slumlordreach',
           'reach': 'slumlordreach'}
isc_df['task'].replace(to_replace=replace, inplace=True)

# Chronological task order
task_order = ['pieman', 'tunnel', 'lucy', 'prettymouth',
              'milkyway', 'slumlordreach', 'notthefall',
              'merlin', 'sherlock', 'shapes',
              '21styear', 'piemanpni', 'bronx',
              'black', 'forgot']

isc_all = isc_df.assign(task='all tasks')

# Plot ROI ISCs across all tasks and subjects
hemi_col = ['orange', 'purple']
hemi_pal = sns.xkcd_palette(hemi_col)

sns.set_context(context='notebook', font_scale=1.03)
fig = plt.figure(constrained_layout=True, figsize=(8, 5.92))
gs = fig.add_gridspec(10, 1)
ax0 = fig.add_subplot(gs[:8, :])
ax1 = fig.add_subplot(gs[8:, :])
v = sns.violinplot(x='ISC', y='task', data=isc_df, color='.8',
                   order=task_order, inner=None, linewidth=1,
                   cut=0, split=True, zorder=0, ax=ax0)
for i in range(len(v.collections)):
    v.collections[i].set_edgecolor('.8')
sns.stripplot(x='ISC', y='task', hue='hemisphere', data=isc_df, color='.3',
              palette=hemi_pal, jitter=False, order=task_order,
              hue_order=['R', 'L'], size=3, marker='|', alpha=.5,
              linewidth=1, zorder=1, ax=ax0)
sns.pointplot(x='ISC', y='task', hue='hemisphere', data=isc_df, join=False,
              order=task_order, hue_order=['R', 'L'], palette=hemi_pal,
              color='darkred', estimator=fisher_mean, ax=ax0)
ax0.xaxis.label.set_visible(False)
ax0.tick_params(axis='y',length=0)
ax0.get_legend().remove()
handles, labels = ax0.get_legend_handles_labels()
ax0.legend(handles[:2][::-1], labels[:2][::-1], title='hemisphere',
           loc='upper right')
ax0.set_xlim(0, 1)

v = sns.violinplot(x='ISC', y='task', data=isc_all, color='.8',
                   inner=None, linewidth=1, cut=0, split=True,
                   zorder=0, ax=ax1)
v.collections[0].set_edgecolor('.8')
sns.stripplot(x='ISC', y='task', hue='hemisphere', data=isc_all, color='.3',
              jitter=False, size=3, marker='|', alpha=.5, linewidth=1,
              hue_order=['R', 'L'], zorder=1, ax=ax1, palette=hemi_pal)
sns.pointplot(x='ISC', y='task', hue='hemisphere', data=isc_all,
              hue_order=['R', 'L'], join=False, scale=1.2,
              palette=hemi_pal, estimator=fisher_mean, ax=ax1)
ax1.get_legend().remove()
ax1.tick_params(axis='y',length=0)
ax1.yaxis.label.set_visible(False)
ax1.set_xlabel('intersubject correlation (ISC)')
ax1.set_xlim(0, 1)
sns.despine()
plt.tight_layout()
plt.savefig(join(base_dir, 'code', 'fig3_isc_ex.png'),
            transparent=True, dpi=300,
            bbox_inches='tight')
plt.show()


# Load in EAC lagged ISCs
roi = 'EAC'
hemisphere = 'L'
lags = 30
lag_fn = join(afni_dir, f'group_roi-{roi}_desc-exclude_lags.json')
with open(lag_fn) as f:
    lag_dict = json.load(f)

# Manually melt this dictionary
lag_iscs = {'ISC': [], 'hemisphere': [], 'task': [],
            'subject': [], 'lag': []}
lag_arr = []
for task in lag_dict:
    for hemi in lag_dict[task]:
        for subject in lag_dict[task][hemi]['lagged ISCs']:
            for run in lag_dict[task][hemi]['lagged ISCs'][subject]:
                if hemi == hemisphere:
                    lag_arr.append(lag_dict[task][hemi]['lagged ISCs'][subject][run])
                for lag, isc in zip(np.arange(-lags, lags + 1),
                                    lag_dict[task][hemi]['lagged ISCs'][subject][run]):
                    lag_iscs['ISC'].append(isc)
                    lag_iscs['hemisphere'].append(hemi)
                    lag_iscs['task'].append(task)
                    lag_iscs['subject'].append(subject)
                    lag_iscs['lag'].append(lag)
lag_arr = np.column_stack(lag_arr)

# Convert to pandas data frame
lag_df = pd.DataFrame(lag_iscs)
lag_df = lag_df[lag_df['hemisphere'] == hemisphere]

# Collapse related tasks
replace = {'notthefallintact': 'notthefall',
           'notthefalllongscram': 'notthefall',
           'notthefallshortscram': 'notthefall',
           'shapesphysical': 'shapes',
           'shapessocial': 'shapes',
           'slumlord': 'slumlordreach',
           'reach': 'slumlordreach'}
lag_df['task'].replace(to_replace=replace, inplace=True)

# Chronological task order
task_order = ['pieman', 'tunnel', 'lucy', 'prettymouth',
              'milkyway', 'slumlordreach', 'notthefall',
              'merlin', 'sherlock', 'shapes',
              '21styear', 'piemanpni', 'bronx',
              'black', 'forgot']

# Plot lag ISCs with seaborn
sns.set_context(context='notebook', font_scale=1.2)
fig, axs = plt.subplots(2, 1, figsize=(8, 8), sharex=True, sharey=True)
sns.lineplot(x="lag", y="ISC", hue='task', data=lag_df,
             hue_order=task_order, palette='inferno',
             estimator=fisher_mean, ax=axs[0])
axs[0].legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=False)
axs[0].axes.get_xaxis().set_visible(False)

axs[1].plot(np.arange(-lags, lags + 1), lag_arr, color='.6', alpha=.3);
sns.lineplot(x="lag", y="ISC", data=lag_df, color='darkred',
             estimator=fisher_mean, ax=axs[1])
axs[1].legend(title='all tasks', loc='upper left', frameon=False)
axs[1].set_xlabel("lag (TRs)")
sns.despine(ax=axs[0])
plt.subplots_adjust(hspace=0.05)
plt.savefig(join(base_dir, 'code', 'fig3_lags_ex.png'),
            transparent=True, dpi=300,
            bbox_inches='tight')
plt.show()
