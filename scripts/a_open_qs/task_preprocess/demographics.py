import matplotlib
from natsort import natsorted

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches  # Required for the custom legend

plt.ion()
import os
import pandas as pd
import seaborn as sns

from _objects.plot_config import *
from _objects.configs import *
from scripts.a_open_qs.main_analysis.analysis_utils import return_good_sub
from _utils.utils import write_to_tex

study_name = 'a_open_qs'

pc = PlotConfig()
bools = Bools()
report_vars = ReportVars()

task_v = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']
paths = Paths(files_dir='', plots_subdir='', plots_subsubdir='')

paths.data_path = f'data/{study_name}/task_data/combined/'
paths.dem_path = f"/Volumes/DATA/UCL/online_tasks/ppts_ret/study1/"
paths.org_data = f"/Volumes/DATA/UCL/online_tasks/qs_structure/qs-structure-phq9-v4/_data/"
paths.plots_path = f'outputs/{study_name}/plots/prelim/'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)

# load included list of subjects
good_subs = natsorted(return_good_sub(paths, task_v, report_vars))
bools.loadMe = True
bools.goodSub = True
bools.savePlots = True
# bools.savePlots = False
bools.writeTex = True
# bools.writeTex = False
if bools.writeTex:
    write_to_tex(report_vars, overwrite=False)  # Get numbers to tex vars

# %% find Prolific ids and load demographics (from external drive)
if not bools.loadMe:
    sub_key_df = {tv: pd.read_csv(f"{paths.org_data}qs-structure-phq9-{tv}/processed/sub_keys.csv") for tv in task_v}
    sub_pid_dict = {}
    for sub in good_subs:
        sub_id = sub.split('_')[0]
        tv = '_'.join(sub.split('_')[1:])
        pid = sub_key_df[tv][sub_key_df[tv]['sub'] == sub_id]['PID'].values[0]
        sub_pid_dict[sub] = pid

    all_pids = list(sub_pid_dict.values())
    sub_pid_df = pd.DataFrame.from_dict(sub_pid_dict, orient='index', columns=['PID']).reset_index(names=['sub'])
    dem_cols = ['Participant id', 'Age', 'Sex', 'Ethnicity simplified', 'Employment status']
    dem_df = []
    for fn in os.listdir(paths.dem_path):
        tmp_df = pd.read_csv(f"{paths.dem_path}/{fn}")[dem_cols]
        dem_df.append(tmp_df)

    dem_df = pd.concat(dem_df)
    dem_df.rename(columns={dem_cols[0]: 'PID', 'Ethnicity simplified': 'ethnicity', 'Employment status': 'employment',
                           'Age': 'age', 'Sex': 'sex'}, inplace=True)

    dem_df = pd.merge(sub_pid_df, dem_df, on='PID')
    dem_df.drop(columns='PID', inplace=True)

    dem_df.to_csv(f"{paths.data_path}demographics.csv", index=False)
else:
    dem_df = pd.read_csv(f"{paths.data_path}demographics.csv")
# %% Total Scores
phq9_data = pd.read_csv(f"{paths.data_path}/phq9_data.csv")
phq9_data = phq9_data[phq9_data['sub'].isin(good_subs)]
gad7_data = pd.read_csv(f"{paths.data_path}/gad7_data.csv")
gad7_data = gad7_data[gad7_data['sub'].isin(good_subs)]
sds_data = pd.read_csv(f"{paths.data_path}/sds_data.csv")
sds_data = sds_data[sds_data['sub'].isin(good_subs)]

total_dfs = {'phq9': phq9_data, 'gad7': gad7_data, 'sds': sds_data}

p_total = phq9_data['total'].aggregate(['mean', 'std'])
g_total = gad7_data['total'].aggregate(['mean', 'std'])
s_total = sds_data['total'].aggregate(['mean', 'std'])
N_s1 = phq9_data['sub'].nunique()
ph = '-'

# %% Plot totals
plt.close('all')
pc.r, pc.c = 1, 3
pc.figsize = (pc.fw, pc.fw / 4)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, layout='constrained')

pc.p_lab_spec[0] = -.075
pc.p_lab_spec[1] = 1.05
pc.axes = axes
pc.i, pc.j = 0, 0

qs_names = ['phq9', 'gad7', 'sds']
threshold_low = 0
threshold_high = 5
cut_offs = {'phq9': [4, 9, 14, 19, 27], 'gad7': [4, 9, 14, 21], 'sds': [49, 59, 69, 80]}
cut_offs_names = {'phq9': ['Minimal', 'Mild', 'Moderate', 'Moderately severe', 'Severe'],
                  'gad7': ['Minimal', 'Mild', 'Moderate', 'Severe'], 'sds': ['Normal', 'Mild', 'Moderate', 'Severe']}

# c=sns.color_palette("rocket", as_cmap=True)
for pc.j, qs_name in enumerate(qs_names):
    g = sns.histplot(total_dfs[qs_name]['total'], ax=pc.ax, color='tab:blue', stat='density', kde=True,
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
               fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])
    if qs_name == 'phq9':
        pc.ax.set_ylim([0, 0.17])
    if qs_name == 'gad7':
        pc.ax.set_ylim([0, 0.135])
    if qs_name == 'sds':
        pc.ax.set_ylim([0, 0.079])

if bools.savePlots:
    plt.savefig(f"{paths.plots_path}{study_name}_totals.pdf", dpi=300)
