# %% Import libraries and set up objects
import pickle
import pandas as pd
import matplotlib
import statsmodels.formula.api as smf
from statannotations.Annotator import Annotator
import seaborn as sns

import matplotlib.colors as mcolors
import matplotlib.colors as clr

# matplotlib.use('Qt5Agg')
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

plt.ion()

from _objects.plot_config import *
from _objects.configs import *
from _utils.utils import return_p_star, prep_split_heatmap, write_to_tex

report_vars = ReportVars()
pc = PlotConfig()

# set names
study_name = 'c_mood_induction'
ssae_scores_path = 'ssae_scores/'
ssae_analysis_path = 'ssae_analysis/'
sim_analysis_path = 'similarity_analysis'
analysis_path = 'main_analysis/'
fig_no = 'Fig5'

# set paths
paths = Paths()
paths.data_path = f'data/{study_name}/task_data/combined/'
paths.output_path = f'outputs/{study_name}/{analysis_path}/'
paths.ssae_analysis_path = f'outputs/{study_name}/{ssae_analysis_path}/'
paths.sim_output_path = f'outputs/{study_name}/{sim_analysis_path}/'
paths.plots_path = f'outputs/{study_name}/plots/{analysis_path}/'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)
Path(paths.output_path).mkdir(parents=True, exist_ok=True)

# bools
bools = Bools()
bools.savePlot = True
bools.savePlot = False
# bools.writeTex = True
bools.writeTex = False


# %% Load data
model_name = 'gemma2-9b-it'
text_type = 'act'
cond_names = ['High mood', 'Low mood']
cond_cols = ['#E1BE6A', '#40B0A6']
id_cols = ['sub', 'condition', 'group', 'autobio']
hue_order = ['ML', 'MH']
sbin3_order = ['q33', 'm', 'q66']
join_cols = id_cols + ['s_bin', 's_bin3']

phq9_diff = pd.read_csv(f'{paths.data_path}phq9_diff_data_wide.csv')
phq9_diff.groupby(['condition', 'autobio'])['phq9_q2'].aggregate(['mean', 'std', 'count'])
mood_data = pd.read_csv(f'{paths.data_path}mood_data.csv')
recall_data_wide = pd.read_csv(f"{paths.data_path}recall_data_wide.csv")

# Split into exp types
phq9_diff_ab = phq9_diff[phq9_diff['autobio'] == True]
phq9_diff_nab = phq9_diff[phq9_diff['autobio'] == False]

# get Q2 and recall differences
measure_cols = ['phq9_q2', 'recall_diffSent']
all_data = pd.merge(phq9_diff, recall_data_wide, on=join_cols)
all_data_nab = all_data[all_data['autobio'] == False]
all_data_ab = all_data[all_data['autobio'] == True]
all_data_ab = pd.merge(all_data, mood_data, on=join_cols)
all_data_ab = all_data_ab.melt(id_vars=id_cols, value_vars=measure_cols + ['mood_diff'], var_name='measure')
all_data_nab = all_data_nab.melt(id_vars=id_cols, value_vars=measure_cols, var_name='measure')
all_data = pd.concat([all_data_ab, all_data_nab])

# Load transcript-diary similarity
with open(f'{paths.sim_output_path}rec_transcript_dict.pkl', 'rb') as f:
    rec_transcript_dict = pickle.load(f)

# % Get similairty matrices
matrix_A = rec_transcript_dict['MH']
matrix_B = rec_transcript_dict['ML']
cmap_ml = clr.LinearSegmentedColormap.from_list('ml_col', ['#f1e2bc', '#d7a939'])
cmap_mh = clr.LinearSegmentedColormap.from_list('mh_col', ['#c9ebe8', '#47bcb2'])
triang, c_arr, custom_cmap, M, N = prep_split_heatmap(matrix_A, matrix_B, cmap_mh, cmap_ml)

# Load sSAE scores
sae_phq9 = pd.read_csv(f"{paths.ssae_analysis_path}sae_phq9_{model_name}_{text_type}.csv")
sae_pred_df_avg = pd.read_csv(f'{paths.ssae_analysis_path}sae_diff_fuB_avg.csv')

# %% Regressions for main differences Q2, mood, recall
results = {'phq9_q2': smf.ols('phq9_q2~condition+s_total', data=phq9_diff).fit(),
           'mood_diff': smf.ols('mood_diff~condition+s_total', data=mood_data).fit(),
           'recall_diffSent': smf.ols('recall_diffSent~condition+s_total', data=recall_data_wide).fit()}

# %% Plot combined
bools.do_annots = True
plt.close('all')
pc.annot_fs = 5.5
pc.annot_p_fs = 7

pc.p_lab_spec[0] = -0.3
pc.p_lab_spec[1] = 1.05

# spec plots
pc.box_width = 0.8
pc.dot_size = 2
pc.dot_jitter = 0.1

# spec stuff for heatmap
x_dist_cb = 0.065
clab_lab_dist = 0
y_dist_cb = 0.08
dist_from_mid = 3.2
clab_rot = 0
cbar_labelpad = 23

pc.r, pc.c, pc.mlt = 1, 6, 1
pc.figsize = (pc.fw - .001, pc.fw / 3.75)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, width_ratios=[1.5, 1, 1, 1, 1, 1], layout='constrained')
pc.onerow = False
pc.axes = axes
pc.i, pc.j = 0, 0

if bools.do_annots:
    im = pc.ax.tripcolor(triang, c_arr, cmap=custom_cmap, vmin=0, vmax=1)
    pc.ax.set_xticks(np.arange(M) + 0.5)
    pc.ax.set_yticks(np.arange(N) + 0.5)
    pc.ax.set_xticklabels([f'Diary {t + 1}' for t in np.arange(M)])
    pc.ax.set_yticklabels([f'Diary {t + 1}' for t in np.arange(N)], rotation=75)
    pc.ax.set_xlabel("Original Transcript\n\n")
    pc.ax.set_ylabel("Recreated Diary")
    pc.ax.set_title("Average diary similarity")
    pc.ax.set_aspect('equal')
    pc.ax.set_xlim(0, M)
    pc.ax.set_ylim(N, 0)

    for i in range(N):
        for j in range(M):
            # --- Annotate Matrix A (Bottom Triangle) ---
            val_A = matrix_A[i, j]
            color_A = 'black' if val_A < 0.65 else 'white'
            pc.ax.text(j + 1 / dist_from_mid, i + 1 / dist_from_mid, f"{val_A:.2f}",
                       ha='center', va='center', fontsize=pc.annot_fs, color=color_A)

            # --- Annotate Matrix B (Top Triangle) ---
            val_B = matrix_B[i, j]
            color_B = 'black' if val_B < 0.65 else 'white'
            pc.ax.text(j + (1 - 1 / dist_from_mid), i + (1 - 1 / dist_from_mid), f"{val_B:.2f}",
                       ha='center', va='center', fontsize=pc.annot_fs, color=color_B)

    # --- Add Two Separate Colorbars ---
    # Colorbar for Matrix A
    cax_A = fig.add_axes([x_dist_cb, y_dist_cb, 0.05, 0.05])  # [left, bottom, width, height]
    norm_A_real = mcolors.Normalize(vmin=matrix_A.min(), vmax=matrix_A.max())
    cb_A = fig.colorbar(plt.cm.ScalarMappable(norm=norm_A_real, cmap=cmap_mh),
                        cax=cax_A, orientation='vertical', ax=pc.ax)
    cb_A.set_ticks([])
    cb_A.set_label('High mood', rotation=clab_rot, labelpad=cbar_labelpad, y=0.8)

    # Colorbar for Matrix B
    cax_B = fig.add_axes([x_dist_cb + clab_lab_dist * 0, y_dist_cb - 0.065, 0.05, 0.05])
    norm_B_real = mcolors.Normalize(vmin=matrix_B.min(), vmax=matrix_B.max())
    # norm_B_real = mcolors.Normalize(vmin=0.3, vmax=0.7)
    cb_B = fig.colorbar(plt.cm.ScalarMappable(norm=norm_B_real, cmap=cmap_ml),
                        cax=cax_B, orientation='vertical', ax=pc.ax)
    cb_B.set_ticks([])
    cb_B.set_label('Low mood', rotation=clab_rot, labelpad=cbar_labelpad, y=0.8)
    pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
               fontweight='bold',
               va='top', ha='right',
               fontsize=pc.p_lab_spec[2])

# --------- Plot sSAE measures (Q2)
pc.p_lab_spec[1] = 1.00
pc.j = 1
b = sns.boxplot(data=sae_phq9, x='group', y='sae_phq9_q2', hue='condition', orient='v', palette=cond_cols, legend=False,
                hue_order=hue_order, gap=pc.box_gap, ax=pc.ax, width=pc.box_width, linewidth=pc.box_lw, fill=False,
                fliersize=pc.box_fliersize, color='k')

sns.stripplot(data=sae_phq9, x='group', y='sae_phq9_q2', hue='condition', palette=cond_cols, hue_order=hue_order,
              orient='v', dodge=True, legend=False, ax=pc.ax, linewidth=pc.dot_lw, size=pc.dot_size, alpha=pc.dot_alpha,
              jitter=pc.dot_jitter)
pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold',
           va='top', ha='right',
           fontsize=pc.p_lab_spec[2])

# Regression for sae q2 diff
res = smf.ols('sae_phq9_q2~condition+s_total', data=sae_phq9).fit()
p_val = res.pvalues['condition[T.ML]']
t_val = res.tvalues['condition[T.ML]']
coef_val = res.params['condition[T.ML]']
p_val_text = [f'p={p_val:.3f}{return_p_star(p_val)}\nt={t_val:.2f}' if p_val >= 0.001 else
              f'p<0.001{return_p_star(p_val)}\nt={t_val:.2f}'
              ]
# Save reg results to tex
tex_text = f'b={coef_val:.2f}, t({res.df_resid:.0f})={t_val:.2f}, ' + \
           [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]
report_vars.sThree_Int_Diary_sSAE = tex_text

# Annotate stat results
pairs = [[('D', 'ML'), ('D', 'MH')]]
annotator = Annotator(pc.ax, pairs, data=sae_phq9, y='sae_phq9_q2', x='group', hue='condition')
annotator.configure(fontsize=pc.annot_p_fs)
annotator.set_custom_annotations(p_val_text)
annotator.annotate()

pc.ax.set_xlabel('Intervention diary')
pc.ax.set_ylabel('\nsSAE Q2 score', labelpad=0.1)
pc.ax.set_xticks([])

# ----------- Plot measures - mood, recall, phq9 q2 change
measures = ['mood_diff', 'recall_diffSent', 'phq9_q2']
measure_labels = ['Mood', 'Recall sentiment', 'PHQ9 Q2']
measure_label_fnames = ['mood', 'recall', 'phqQtwo']

for pc.j, (measure_name, measure_label, measure_fname) in enumerate(
        zip(measures, measure_labels, measure_label_fnames)):
    pc.j += 1 + 1

    # get measure df
    all_data_measure = all_data[all_data['measure'] == measure_name]

    # plot
    sns.boxplot(all_data_measure, y='value', x='measure', hue='condition', ax=pc.ax, palette=cond_cols, legend=False,
                hue_order=hue_order, gap=pc.box_gap, width=pc.box_width, linewidth=pc.box_lw, fill=False,
                fliersize=pc.box_fliersize, color='k')

    sns.stripplot(data=all_data_measure, y='value', hue='condition', x='measure',
                  palette=cond_cols, hue_order=hue_order,
                  orient='v', dodge=True, legend=False, ax=pc.ax, linewidth=pc.dot_lw, size=pc.dot_size,
                  alpha=pc.dot_alpha,
                  jitter=pc.dot_jitter)

    ## P-value annotation
    pvals = [results[measure_name].pvalues['condition[T.ML]']]
    tvals = [results[measure_name].tvalues['condition[T.ML]']]
    coefvals = [results[measure_name].params['condition[T.ML]']]
    resid = results[measure_name].df_resid
    print(pvals, tvals)
    p_val_text = [f'p={p_val:.3f}{return_p_star(p_val)}\nt={t_val:.2f}' if p_val >= 0.001 else
                  f'p<0.001{return_p_star(p_val)}\nt={t_val:.2f}' for p_val, t_val in zip(pvals, tvals)]
    # Save to tex
    tex_text = f'b={coefvals[0]:.2f}, t({resid:.0f})={tvals[0]:.2f}, ' + \
               [f'p={pvals[0]:.3f}' if pvals[0] >= 0.001 else f'p$<$0.001'][0]
    setattr(report_vars, 'sThree_' + measure_fname + '_change', tex_text)

    pairs = [[(measure_name, 'ML'), (measure_name, 'MH')]]
    # ppars = {'data': all_data_measure, 'y': 'value', 'hue': 'condition', 'x': 'measure'}
    if bools.do_annots:
        annotator = Annotator(pc.ax, pairs, data=all_data_measure, y='value', hue='condition', x='measure',
                              fontsize=pc.p_lab_spec[2])
        annotator.configure(fontsize=pc.annot_p_fs)
        annotator.set_custom_annotations(p_val_text)
        annotator.annotate()

    if pc.j == 2:
        pc.ax.set_ylabel('\nFU - Baseline change', labelpad=0.1)
    else:
        pc.ax.set_ylabel('')
    if pc.j == 4:
        pc.ax.set_ylabel(' ', labelpad=0.1)

    pc.ax.set_xlabel(f'{measure_label} change')
    pc.ax.set_xticks([])
    pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
               fontweight='bold',
               va='top', ha='right',
               fontsize=pc.p_lab_spec[2])
    # zero line
    pc.ax.axhline(y=0, color='k', linewidth=0.5, linestyle='--', zorder=3)

# Plot sSAE Q2/Q4 change on positive re-aval
pc.j = 5
sns.boxplot(data=sae_pred_df_avg, x='group', y='sae_diff_fuB_avg', hue='condition', ax=pc.ax, palette=cond_cols,
            legend=False,
            hue_order=hue_order, gap=pc.box_gap, width=pc.box_width, linewidth=pc.box_lw, fill=False,
            fliersize=pc.box_fliersize, color='k')
sns.stripplot(data=sae_pred_df_avg, x='group', y='sae_diff_fuB_avg', hue='condition',
              palette=cond_cols, hue_order=hue_order,
              orient='v', dodge=True, legend=False, ax=pc.ax, linewidth=pc.dot_lw, size=pc.dot_size,
              alpha=pc.dot_alpha,
              jitter=pc.dot_jitter)
pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold',
           va='top', ha='right',
           fontsize=pc.p_lab_spec[2])

# Regression - Q2/4 change in open-ended
res = smf.ols('sae_diff_fuB_avg~condition+s_total', data=sae_pred_df_avg).fit()
p_val = res.pvalues['condition[T.ML]']
t_val = res.tvalues['condition[T.ML]']
coef_val = res.params['condition[T.ML]']
p_val_text = [f'p={p_val:.3f}{return_p_star(p_val)}\nt={t_val:.2f}']
tex_text = f'b={coef_val:.2f}, t({res.df_resid:.0f})={t_val:.2f}, ' + \
           [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]
report_vars.sThree_sSAE_QTwoFour_change = tex_text

# Get Intercept
p_val = res.pvalues['Intercept']
t_val = res.tvalues['Intercept']
coef_val = res.params['Intercept']
tex_text = f'b={coef_val:.2f}, t({res.df_resid:.0f})={t_val:.2f}, ' + \
           [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]
report_vars.sThree_sSAE_QTwoFour_intercept = tex_text

pairs = [[('D', 'ML'), ('D', 'MH')]]
annotator = Annotator(pc.ax, pairs, data=sae_pred_df_avg, y='sae_diff_fuB_avg', hue='condition', x='group')
annotator.configure(fontsize=pc.annot_p_fs)
annotator.set_custom_annotations(p_val_text)
annotator.annotate()

pc.ax.set_ylabel('')
pc.ax.set_xlabel('sSAE Q2/4 change    ')
pc.ax.set_xticks([])

if bools.savePlot:
    plt.savefig(f"{paths.plots_path}{fig_no}_p1_diff_measures_combined.pdf", dpi=300)

# %% Feedback and demand effects analyses
feedback_data_wide_mood = pd.read_csv(f'{paths.data_path}feedback_data_wide_mood.csv')
feedback_data_wide = pd.read_csv(f'{paths.data_path}feedback_data_wide.csv')
feedback_data_wide_ssae = pd.merge(feedback_data_wide, sae_pred_df_avg, on=id_cols)

# Feedback phq9
res = smf.ols('phq9_q2~s_total_x+condition*demand', data=feedback_data_wide).fit()
p_val = res.pvalues['condition[T.ML]:demand']
t_val = res.tvalues['condition[T.ML]:demand']
coef_val = res.params['condition[T.ML]:demand']
tex_text = f'b={coef_val:.2f}; t({res.df_resid:.0f})={t_val:.2f}, ' + \
           [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]
report_vars.sThree_demand_phq = tex_text
res.summary()

# Feedback recall
res = smf.ols('recall_diffSent~s_total_x+condition*demand', data=feedback_data_wide).fit()
p_val = res.pvalues['condition[T.ML]:demand']
t_val = res.tvalues['condition[T.ML]:demand']
coef_val = res.params['condition[T.ML]:demand']
tex_text = f'b={coef_val:.2f}; t({res.df_resid:.0f})={t_val:.2f}, ' + \
           [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]
report_vars.sThree_demand_recall = tex_text
res.summary()

# Feedback mood
res = smf.ols('mood_diff~s_total_x+condition*demand', data=feedback_data_wide_mood).fit()
p_val = res.pvalues['condition[T.ML]:demand']
t_val = res.tvalues['condition[T.ML]:demand']
coef_val = res.params['condition[T.ML]:demand']
tex_text = f'b={coef_val:.2f}; t({res.df_resid:.0f})={t_val:.2f}, ' + \
           [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]
report_vars.sThree_demand_mood = tex_text
res.summary()

# Feedback ssAE
res = smf.ols('sae_diff_fuB_avg~s_total_x+condition*demand', data=feedback_data_wide_ssae).fit()
p_val = res.pvalues['condition[T.ML]:demand']
t_val = res.tvalues['condition[T.ML]:demand']
coef_val = res.params['condition[T.ML]:demand']
tex_text = f'b={coef_val:.2f}; t({res.df_resid:.0f})={t_val:.2f}, ' + \
           [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]
report_vars.sThree_demand_ssae = tex_text
res.summary()

if bools.writeTex:
    write_to_tex(report_vars, overwrite=True)  # Get numbers to tex vars
