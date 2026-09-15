# %% Import libs and setup
import matplotlib
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from _utils.utils import return_p_star

from _objects.plot_config import *
from _objects.configs import *

# from _objects.sae_models import *
from _objects.model_configs import *
from _utils.utils import write_to_tex

report_vars = ReportVars()

# matplotlib.use('Qt5Agg')
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.ion()

pc = PlotConfig()

# set names
study_name = 'c_mood_induction'
ssae_scores_path = 'ssae_scores'
sim_analysis_path = 'similarity_analysis'
analysis_path = 'ssae_analysis/'
fig_no = 'Fig5'

# set paths
paths = Paths()
paths.data_path = f'data/{study_name}/task_data/combined/'
paths.output_path = f'outputs/{study_name}/{analysis_path}/'
paths.base_output_path = f'outputs/{study_name}/{ssae_scores_path}/'
paths.sim_output_path = f'outputs/{study_name}/{sim_analysis_path}/'
paths.plots_path = f'outputs/{study_name}/plots/{analysis_path}/'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)
Path(paths.output_path).mkdir(parents=True, exist_ok=True)

bools = Bools()

# bools.loadMe = True
bools.saveMe = False
# bools.saveMe = True
bools.savePlot = True
# bools.savePlot = False
bools.saveTex = False
# bools.saveTex = True

# %% Load data
id_cols = ['sub', 'condition', 'group', 'autobio']
hue_order = ['MH', 'ML']
hue_cols = ['tab:blue', 'tab:orange']
hue_cols2 = ['tab:green', 'tab:purple']
phq9_q_names = ['phq9_q' + str(q + 1) for q in range(9)]

phq9_diff = pd.read_csv(f'{paths.data_path}phq9_diff_data_wide.csv')
mood_diff = pd.read_csv(f'{paths.data_path}mood_data.csv')
recall_data = pd.read_csv(f"{paths.data_path}recall_data_wide.csv")

# %% Merge act with other measures
text_type = 'act'
model_name = 'gemma2-9b-it'
# Load sSAE prediction on diary continuations
sae_preds_df = pd.read_csv(f'{paths.base_output_path}sae_preds_{model_name}_{text_type}.csv')

sae_phq9 = pd.merge(sae_preds_df, phq9_diff, on=id_cols)
sae_mood = pd.merge(sae_preds_df, mood_diff, on=id_cols)
sae_recall = pd.merge(sae_preds_df, recall_data, on=id_cols)
if bools.saveMe:
    sae_phq9.to_csv(f"{paths.output_path}sae_phq9_{model_name}_{text_type}.csv", index=False)
    sae_mood.to_csv(f"{paths.output_path}sae_mood_{model_name}_{text_type}.csv", index=False)
    sae_recall.to_csv(f"{paths.output_path}sae_recall_{model_name}_{text_type}.csv", index=False)

sae_mood_mh = sae_mood[sae_mood['condition'] == 'MH']
sae_mood_ml = sae_mood[sae_mood['condition'] == 'ML']
sae_recall_mh = sae_recall[sae_recall['condition'] == 'MH']
sae_recall_ml = sae_recall[sae_recall['condition'] == 'ML']
sae_phq9_mh = sae_phq9[sae_phq9['condition'] == 'MH']
sae_phq9_ml = sae_phq9[sae_phq9['condition'] == 'ML']

# %% Calc FU (pospert)-baseline - averae across saes
# Open-ended Q2 sSAE scores
sae_preds_df_all_mood = pd.read_csv(f'{paths.base_output_path}sae_preds_{model_name}_mood.csv')
sae_preds_df_all_mood = sae_preds_df_all_mood[id_cols + ['t', 'text'] + ['sae_phq9_q2']].melt(
    id_vars=id_cols + ['t', 'text'], var_name='sae_var',
    value_name='sae_score')
sae_preds_df_all_mood = sae_preds_df_all_mood.groupby(id_cols, as_index=False)['sae_score'].mean()
sae_preds_df_all_mood.rename(columns={'sae_score': 'sae_score_mood'}, inplace=True)

# Open-ended Q4 sSAE scores
sae_preds_df_all_energy = pd.read_csv(f'{paths.base_output_path}sae_preds_{model_name}_energy.csv')
sae_preds_df_all_energy = sae_preds_df_all_energy[id_cols + ['t', 'text'] + ['sae_phq9_q4']].melt(
    id_vars=id_cols + ['t', 'text'], var_name='sae_var',
    value_name='sae_score')
sae_preds_df_all_energy = sae_preds_df_all_energy.groupby(id_cols, as_index=False)['sae_score'].mean()
sae_preds_df_all_energy.rename(columns={'sae_score': 'sae_score_energy'}, inplace=True)

# Open-ended positive re-eval sSAE scores
sae_preds_df_all_pospert = pd.read_csv(f'{paths.base_output_path}sae_preds_{model_name}_pospert.csv')
sae_preds_df_all_pospert = sae_preds_df_all_pospert[id_cols + ['t', 'text'] + ['sae_phq9_q2', 'sae_phq9_q4']].melt(
    id_vars=id_cols + ['t', 'text'], var_name='sae_var',
    value_name='sae_score')
sae_preds_df_all_pospert = sae_preds_df_all_pospert.groupby(id_cols, as_index=False)['sae_score'].mean()
sae_preds_df_all_pospert.rename(columns={'sae_score': 'sae_score_pospert'}, inplace=True)

# merge sSAE score DFs
sae_pred_df_avg = pd.merge(sae_preds_df_all_mood, sae_preds_df_all_energy, on=id_cols)
sae_pred_df_avg = pd.merge(sae_pred_df_avg, sae_preds_df_all_pospert, on=id_cols)

# sSAE differences for positive re-eval and baselien
sae_pred_df_avg['sae_diff_fuB_mood'] = sae_pred_df_avg['sae_score_pospert'] - (sae_pred_df_avg['sae_score_mood'])
sae_pred_df_avg['sae_diff_fuB_avg'] = sae_pred_df_avg['sae_score_pospert'] - (
        sae_pred_df_avg['sae_score_mood'] + sae_pred_df_avg['sae_score_energy']) / 2

# merge with PHQ9 data totals
data_phq9_text = pd.read_csv(f'{paths.sim_output_path}phq9_diff_text.csv')
sae_pred_df_avg = pd.merge(phq9_diff[id_cols + ['s_total']], sae_pred_df_avg, on=id_cols)
sae_pred_df_avg = pd.merge(data_phq9_text[id_cols + ['avgRecAct_sim']], sae_pred_df_avg, on=id_cols)

if bools.saveMe:
    sae_pred_df_avg.to_csv(f'{paths.output_path}sae_diff_fuB_avg.csv', index=False)

# %% Prepare data for plot
sae_phq9['condition'] = pd.Categorical(sae_phq9['condition'], categories=['MH', 'ML'])
sae_mood['condition'] = pd.Categorical(sae_mood['condition'], categories=['ML', 'MH'])
sae_recall['condition'] = pd.Categorical(sae_recall['condition'], categories=['MH', 'ML'])

measures = ['mood_diff', 'recall_diffSent', 'phq9_q2']
measure_labels = ['Mood change', 'Recall sentiment change', 'PHQ9 Q2 change']
measure_dfs = {'phq9_q2': sae_phq9, 'mood_diff': sae_mood, 'recall_diffSent': sae_recall}
measure_label_fnames = ['mood', 'recall', 'phqQtwo']

cond_cols = ['#E1BE6A', '#40B0A6']

# %% Run regressions
results = {'phq9_q2': smf.ols('phq9_q2~sae_phq9_q2+s_total', data=sae_phq9).fit(),
           'mood_diff': smf.ols('mood_diff~sae_phq9_q2+s_total', data=sae_mood).fit(),
           'recall_diffSent': smf.ols('recall_diffSent~sae_phq9_q2+s_total', data=sae_recall).fit()}

for key, res in results.items():
    print('\n', key)
    print(res.summary())
# %% Plot SAE against  - MAIN (bottom row)
plt.close('all')
pc.annot_fs = 7
pc.dot_size = 12
pc.lw = 3
pc.p_lab_spec[0] = -0.15
pc.p_lab_spec[1] = 1.025
pc.plab_offset = 6 + 3

pc.r, pc.c, pc.mlt = 1, 3, 1
pc.figsize = (pc.fw, pc.fw / 4)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=False, layout='constrained')
pc.onerow = False
pc.axes = axes

pc.i, pc.j = 0, 0

for pc.j, (measure_name, measure_label, measure_fname) in enumerate(
        zip(measures, measure_labels, measure_label_fnames)):
    # g et measure df
    measure_df = measure_dfs[measure_name]
    measure_df_MH = measure_df[measure_df['condition'] == 'MH']
    measure_df_ML = measure_df[measure_df['condition'] == 'ML']

    # plot regplots for each condition and across conditions
    sns.regplot(measure_df_MH, x='sae_phq9_q2', y=measure_name, color=cond_cols[1], label='', ax=pc.ax, ci=95,
                fit_reg=False, scatter_kws={'s': pc.dot_size, 'alpha': pc.dot_alpha, 'edgecolors': 'none'},
                line_kws={'lw': pc.lw})
    sns.regplot(measure_df_ML, x='sae_phq9_q2', y=measure_name, color=cond_cols[0], label='', ax=pc.ax, ci=95,
                fit_reg=False, scatter_kws={'s': pc.dot_size, 'alpha': pc.dot_alpha, 'edgecolors': 'none'},
                line_kws={'lw': pc.lw})
    sns.regplot(measure_df, x='sae_phq9_q2', y=measure_name, color='gray', label='Pooled condition', ax=pc.ax,
                scatter_kws={'s': pc.dot_size, 'alpha': pc.dot_alpha, 'edgecolors': 'none'},
                line_kws={'lw': pc.lw}, scatter=False, ci=95)
    if pc.j == 2:
        pc.ax.legend(loc='best')

    # zero line
    pc.ax.axhline(y=0, color='k', linewidth=1, linestyle='--')

    pc.ax.set_xlabel('sSAE Q2 Score')
    pc.ax.set_ylabel(measure_label)
    pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
               fontweight='bold',
               va='top', ha='right',
               fontsize=pc.p_lab_spec[2])

    # get regression results (p, t values)
    p_val = results[measure_name].pvalues['sae_phq9_q2']
    t_val = results[measure_name].tvalues['sae_phq9_q2']
    coef_val = results[measure_name].params['sae_phq9_q2']
    p_val_text = [r'sSAE Q2' + f'\np={p_val:.3f}{return_p_star(p_val)} \nt={t_val:.2f}' if p_val >= 0.001 else
                  r'sSAE Q2' + f'\np<0.001{return_p_star(p_val)} \nt={t_val:.2f}'][0]

    tex_text = f'b={coef_val:.2f}, t({results[measure_name].df_resid:.0f})={t_val:.2f}, ' + \
               [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]
    setattr(report_vars, 'sThree_' + measure_fname + '_vs_sSAE', tex_text)

    if measure_name == 'recall_diffSent':
        pc.ax.set_ylim([-1, 1.55])
    if measure_name == 'phq9_q2':
        pc.ax.set_ylim([-0.4, 0.6])
    if pc.j == 2:
        pc.ax.text(0.02, 0.75, p_val_text, transform=pc.ax.transAxes, fontsize=pc.annot_fs, horizontalalignment='left')
    else:
        pc.ax.text(1 - 0.02, 0.75, p_val_text, transform=pc.ax.transAxes, fontsize=pc.annot_fs,
                   horizontalalignment='right')

if bools.savePlot:
    plt.savefig(f"{paths.plots_path}{fig_no}_p3_changeMeasures_VS_sSAEq2.pdf", dpi=300)
if bools.saveTex:
    write_to_tex(report_vars, overwrite=True)  # Get numbers to tex vars
