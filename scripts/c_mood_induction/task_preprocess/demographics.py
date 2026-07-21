import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import matplotlib.patches as mpatches  # Required for the custom legend

plt.ion()
import os
import pandas as pd
import seaborn as sns

from _objects.plot_config import *
from _objects.configs import *

study_name = 'c_mood_induction'
pc = PlotConfig()

bools = Bools()
bools.savePlots = True
# bools.savePlots = False
# bools.loadMe = True
bools.loadMe = False
task_v = ['v2', 'v2b', 'v3']

paths = Paths()
paths.data_path = f'data/{study_name}/task_data/combined/'
paths.dem_path = f"/Volumes/DATA/UCL/online_tasks/ppts_ret/study2/"
paths.org_data = f"/Volumes/DATA/UCL/online_tasks/qs_intervention/"
paths.plots_path = f'outputs/{study_name}/plots/prelim/'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)

phq9_data = pd.read_csv(f"{paths.data_path}/phq9_diff_data_wide.csv")
good_subs = phq9_data['sub'].unique().tolist()

# % Total Scores
total_dfs = {'phq9': phq9_data}
p_total = phq9_data['s_total'].aggregate(['mean', 'std'])
N_s1 = phq9_data['sub'].nunique()

# %% Get demographis
if not bools.loadMe:
    sub_key_df = {
        tv: pd.read_csv(f"{paths.org_data}qs-intervention-{tv[:2]}/_data/qs-intervention-{tv}/processed/sub_keys.csv")
        for tv in task_v}
    sub_pid_dict = []
    for sub in good_subs:
        is_autobio = phq9_data[phq9_data['sub'] == sub]['autobio'].values[0]
        condition = phq9_data[phq9_data['sub'] == sub]['condition'].values[0]
        sub_id = sub.split('_')[0]
        tv = '_'.join(sub.split('_')[1:])
        pid = sub_key_df[tv][sub_key_df[tv]['sub'] == sub_id]['PID'].values[0]
        sub_pid_dict.append({'sub': sub, 'PID': pid, 'condition': condition, 'autobio': is_autobio})

    sub_pid_df = pd.DataFrame(sub_pid_dict)
    dem_cols = ['Participant id', 'Age', 'Sex', 'Ethnicity simplified', 'Employment status']
    dem_df = []
    for fn in [f for f in os.listdir(paths.dem_path) if '.csv' in f]:
        tmp_df = pd.read_csv(f"{paths.dem_path}/{fn}")[dem_cols]
        dem_df.append(tmp_df)

    dem_df = pd.concat(dem_df)
    dem_df.rename(
        columns={dem_cols[0]: 'PID', 'Ethnicity simplified': 'ethnicity', 'Employment status': 'employment',
                 'Age': 'age',
                 'Sex': 'sex'}, inplace=True)

    dem_df = pd.merge(sub_pid_df, dem_df, on='PID')
    dem_df.drop(columns='PID', inplace=True)

    dem_df.to_csv(f"{paths.data_path}demographics.csv", index=False)
else:
    dem_df = pd.read_csv(f"{paths.data_path}demographics.csv")

# %% Demographics pr# %% Plot totals
plt.close('all')
pc.r, pc.c = 1, 1
pc.figsize = (pc.fw / 3.75, pc.fw / 4)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, layout='constrained')
axes = np.array([[axes]])

pc.p_lab_spec[0] = -.075
pc.p_lab_spec[1] = 1.05
pc.axes = axes
pc.i, pc.j = 0, 0

qs_names = ['phq9']
threshold_low = 0
threshold_high = 5
cut_offs = {'phq9': [4, 9, 14, 19, 27]}
cut_offs_names = {'phq9': ['Minimal', 'Mild', 'Moderate', 'Moderately severe', 'Severe']}
for pc.j, qs_name in enumerate(qs_names):
    g = sns.histplot(total_dfs[qs_name]['s_total'], ax=pc.ax, color='tab:blue', stat='density', kde=True,
                     line_kws={'lw': pc.kde_lw})

    # colour the histogram
    for p in g.patches:
        # Calculate the centroid of the bin
        x_centroid = p.get_x() + (p.get_width() / 2)
        for t, th in enumerate(reversed(cut_offs[qs_name])):
            if x_centroid <= th:
                p.set_facecolor(sns.color_palette("rocket", len(cut_offs[qs_name]))[t])
                p.set_alpha(0.8)

    # set legend colours
    handles = [mpatches.Patch(facecolor=c, label=l) for c, l in
               zip(sns.color_palette("rocket", len(cut_offs[qs_name])), reversed(cut_offs_names['phq9']))]
    pc.ax.legend(handles=handles, title='', loc='upper right')

    pc.ax.set_xlabel(f'{qs_name.upper()} total score')
    pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
               fontweight='bold',
               va='top', ha='right',
               fontsize=pc.p_lab_spec[2])
    if qs_name == 'phq9':
        pc.ax.set_ylim([0, 0.19])

if bools.savePlots:
    plt.savefig(f"{paths.plots_path}{study_name}_totals.pdf", dpi=300)
