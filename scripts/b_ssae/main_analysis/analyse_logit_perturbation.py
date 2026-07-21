# %% Import libs
import os, re
from scipy import stats
import pandas as pd
from natsort import natsorted
import torch
import random
import seaborn as sns

import matplotlib

torch.set_grad_enabled(False)

if os.uname()[0] == 'Darwin':  # if on mac
    # matplotlib.use('Qt5Agg')
    matplotlib.use('TkAgg')
    device_name = 'mps'
    import matplotlib.pyplot as plt

    plt.ion()
else:
    matplotlib.use('Agg')
    matplotlib.get_backend()
    device_name = 'cuda'
    import matplotlib.pyplot as plt

from _objects.model_configs import *
from _objects.configs import *
from _objects.plot_config import *
from _objects.qs_maps import maps, QsConfig
from _objects.data_configs import d_thr

from scripts.b_ssae.perturbation.perturb_utils import load_pert_logits

from _utils.utils import return_p_star

qs_config = QsConfig()
pc = PlotConfig()

bools = Bools()
bools.savePlots = True
# bools.savePlots = False
bools.do_zscores = True
bools.loadMe = True
bools.saveMe = False
# bools.loadMe = False
# bools.saveMe = True
bools.goodSub = True

study_name = 'b_ssae'
base_study_name = 'a_open_qs'
fig_no = 'Fig4'
task_versions = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']
sampling_path = 'llm_sampling/'
analysis_path = 'perturbation/'
exp_name = 'SAE_exp_v3_best'
model_name = 'gemma2-9b-it'
# model_name = 'gemma2-2b-it'
to_sample_qs = 'phq9'
phq9_q_names = ['phq9_q' + str(q + 1) + 's' for q in range(9)]

# ds_type = 'val'
ds_type = 'test'

# Set paths
paths = Paths()
paths.plots_path = f'outputs/{study_name}/plots/{analysis_path}'
paths.base_output_path = f'outputs/{study_name}/training/'
paths.model_dir = f'{paths.base_output_path}saved_models/{exp_name}/{model_name}/'
paths.data_path = f'data/{study_name}/'
paths.files_path_o = f'outputs/{base_study_name}/{sampling_path}files_logits/paired/'
paths.files_path_p = f'outputs/{study_name}/{analysis_path}files_logits_perturbed_{ds_type}/paired/'

# %% Load configs and logits
sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name='instr3')
sample_config.gen_fname = 'gb'
sample_config.permute_labels = False
sample_config.label_letters = None
label_letters = list(string.ascii_uppercase)[:qs_config.qs_n_lab[to_sample_qs]]
q_scores = list(maps[to_sample_qs].values())

if sample_config.permute_labels:
    tmp_zip = list(zip(q_scores, label_letters))
    random.shuffle(tmp_zip)
    q_scores, label_letters = zip(*tmp_zip)
sample_config.label_letters = label_letters
sample_config.q_scores = q_scores
sample_config.label_scores = {k: v for k, v in zip(label_letters, q_scores)}

paths.responses_path = f"{paths.files_path_p}{''.join(sample_config.label_letters)}/subjects"
paths.save_path = f"{paths.files_path_p}{''.join(sample_config.label_letters)}/"
Path(paths.save_path).mkdir(parents=True, exist_ok=True)

scores_logits_wide, scores_logits = load_pert_logits(paths, sample_config, bools, ds_type)

# %% Plot logit exp scores
q_names = natsorted(scores_logits['question'].unique())
q_names = [n for n in q_names if 'lvl3' in n]
steer_mlts = natsorted(scores_logits['hs_steer_mlt'].unique())
steer_mlts = [f'steer_mlt_{s}' for s in
              sorted([float(s.split('_')[-1]) for s in steer_mlts if s != 'steer_mlt_0.0'])]

ms = 110
alpha = 0.7
s_ec = '#ffedcb'
b_c = '#e19f20'
s_lw = 0.75

plt.close('all')
pc.r, pc.c, pc.mlt = len(steer_mlts), len(q_names), 1.8
pc.figsize = (pc.fw, pc.fw / 2.75)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=True, layout='constrained')
pc.i, pc.j = 0, 0
pc.onerow = False
pc.axes = axes
pc.ax_ts(6.5, 1)
ts = 6
pc.xyt_ls(ts, ts)
pc.ax_ls(6)
pc.kde_lw = 2
pc.p_lab_spec[0] = -0.1
pc.p_lab_spec[1] = 1.25
pc.plab_offset = 0

store_effects = []
for pc.j, q_name in enumerate(q_names):
    q_s_resp_wide = scores_logits_wide[scores_logits_wide['question'] == q_name]
    q_name_short = re.sub('lvl.*_', '', q_name).upper()
    for pc.i, steer_mlt in enumerate(steer_mlts):

        if steer_mlt == 'steer_mlt_0.0':
            continue
        steer_mlt_val = float(steer_mlt.split('_')[-1])

        tmp_diffs = q_s_resp_wide[f'diff_{steer_mlt}'].values
        tmp_std = np.std(tmp_diffs)
        val_comp = float(steer_mlt.split('_')[-1]) < 0
        d_eff = (tmp_diffs.mean() - 0) / tmp_std
        test_type = 'less' if val_comp else 'greater'
        tv, p_res = stats.ttest_1samp(tmp_diffs, popmean=0, alternative=test_type)
        hist_col = 'tab:green' if val_comp else "tab:red"
        hist_col = hist_col if (p_res < 0.05 and np.abs(d_eff) > d_thr) else 'tab:blue'
        hist_col = hist_col if (p_res < 0.05) else 'tab:gray'

        tmp_dict = {'q_name': q_name, 'steer_value': steer_mlt_val,
                    'direction': 'More severe' if steer_mlt_val > 0 else 'Less severe', 'effect': d_eff, 'p-val': p_res}
        store_effects.append(tmp_dict)
        sns.histplot(data=q_s_resp_wide, x=f'diff_{steer_mlt}', ax=pc.ax, kde=True, stat='density',
                     color=hist_col, line_kws={'linewidth': pc.kde_lw})
        pc.ax.axvline(x=0, lw=s_lw * 3, color='k')
        pc.ax.set_xlim([-4, 4])
        pc.ax.set_xlabel(f'PHQ9 {q_name_short}')
        direction_txt = 'Positive' if steer_mlt_val >= 0 else 'Negative'
        pert_text = f"{direction_txt} perturbation strength: {steer_mlt_val}\n" if pc.j == 3 else ''
        p_val_text = [f'p={p_res:.3f}{return_p_star(p_res)}' if p_res >= 0.001 else f'p<0.001{return_p_star(p_res)}'][0]
        pc.ax.set_title(f"{pert_text}Cohen's d.: {d_eff:.2f}\n{p_val_text}")
        pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
                   fontweight='bold',
                   va='top', ha='right',
                   fontsize=pc.p_lab_spec[2])


plt.suptitle(f'Expected score difference after perturbation: {sample_config.model_name_plot}')
if bools.savePlots:
    plt.savefig(f'{paths.plots_path}logits_exp_score_pert_{ds_type}_{sample_config.model_name}.pdf', dpi=300)

store_effects = pd.DataFrame(store_effects)
# %% Plot medians bar
q_logits = scores_logits_wide[scores_logits_wide['question'].isin(q_names)]
diff_cols = [c for c in q_logits.columns if 'diff' in c]
q_logits = q_logits.melt(id_vars=['sub', 'question', 'model'], value_vars=diff_cols)
q_logits['direction'] = q_logits['variable'].apply(
    lambda x: 'Less severe' if float(x.split('_')[-1]) < 0 else 'More severe')
q_logits['strength'] = q_logits['variable'].apply(lambda x: float(x.split('_')[-1]))
store_effects['question'] = store_effects['q_name'].str.replace('lvl3_', '').str.upper()

plt.close('all')
hue_order = ['Less severe', 'More severe']
# fig_rat = (18-7.25)/3/18
fig_rat = (18 - 7.3) / 2 / 18
pc.figsize = (pc.fw * fig_rat, pc.fw / 4.5)
pc.r, pc.c = 1, 1
pc.l_fs(5)
ts = 7
pc.xyt_ls(ts, ts)
pc.ax_ls(7)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=False, layout='constrained')
axes = np.array([axes])
pc.onerow = True
pc.axes = axes
pc.j, pc.i = 0, 0
pc.p_lab_spec[0] = -0.25
pc.p_lab_spec[1] = 1.1

pc.plab_offset = 2
g = sns.barplot(data=store_effects, x='question', y='effect', hue='direction', hue_order=hue_order,
                palette=['#40B0A6', '#E1BE6A'], ax=pc.ax)
g.legend(title='', loc='best')
# g.legend(title='Perturbation direction',loc='best')
pc.ax.set_xlabel('PHQ-9 Question')
pc.ax.set_ylabel("Cohen's d effect size")
pc.ax.axhline(-0.3, color='k', linestyle='dashed', linewidth=s_lw)
pc.ax.axhline(0.3, color='k', linestyle='dashed', linewidth=s_lw)
pc.annot_fs = 5
p_vals = store_effects.groupby(['question', 'direction'])
# pc.ax.set_ylim([-0.55,1.8])
for h, container in enumerate(pc.ax.containers):
    custom_labels = []
    sev = hue_order[h]
    for j, value in enumerate(container.datavalues):
        print(value)
        p_val = store_effects[(store_effects['effect'] == value) & (store_effects['direction'] == sev)]['p-val'].values[
            0]

        if p_val >= 0.05:
            custom_labels.append('ns')
        else:
            custom_labels.append('')

    # Apply the custom labels
    pc.ax.bar_label(
        container,
        labels=custom_labels,  # Use your custom list
        padding=-0.1,  # Optional padding,
        fontsize=pc.annot_fs,
    )

pc.ax.set_title('Perturbed responses')
pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold',
           va='top', ha='right',
           fontsize=pc.p_lab_spec[2])

if bools.savePlots:
    plt.savefig(
        f"{paths.plots_path}{fig_no}_p3_logits_pert_bars.pdf", dpi=300)
