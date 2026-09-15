# %% Load libraries
import re

import matplotlib
import statsmodels.formula.api as smf
from scipy import stats

matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.ion()
import pandas as pd
import seaborn as sns

from _objects.model_configs import *
from _objects.configs import *
from _objects.qs_maps import phq9_qs_inv_map
from _objects.plot_config import *

study_name = 'a_open_qs'
sampling_path = 'llm_sampling/'
analysis_path = 'main_analysis/'

from scripts.a_open_qs.main_analysis.analysis_utils import process_logits_itemLevel

from _utils.utils import write_to_tex

report_vars = ReportVars()
pc = PlotConfig()
bools = Bools()
# %% Set paths and sets
paths = Paths()
paths.files_path = f'outputs/{study_name}/{sampling_path}files_logits/'
paths.data_path = f'data/{study_name}/task_data/combined/'
paths.output_path = f'outputs/{study_name}/{analysis_path}'
paths.plots_path = f'outputs/{study_name}/plots/logits_itemLevel/'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)
Path(paths.output_path).mkdir(parents=True, exist_ok=True)

label_permutation = 'ABCD'
paths.responses_path = f"{paths.files_path}paired/{label_permutation}/subjects/"
paths.save_responses_path = f"{paths.files_path}paired/{label_permutation}"

bools.loadMe = True
bools.saveMe = False
# bools.loadMe = False
# bools.saveMe = True
bools.saveFig = True
# bools.saveFig = False
bools.goodSub = True
bools.saveTex = False
# bools.saveTex = True
fig_no = 'Fig2'

task_v = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']
model_names = ['MistralOo', 'gemma2-2b-it', 'llama32-3b-it', 'gemma2-9b-it', 'llama31-8b-it']
# model_names = ['gemma2-9b-it']
instr_name_str = 'instr3'

phq8_labs = ["Activities", "Hopeless", "Sleep", "Energy", "Appetite", "Self-worth", "Focus", "Psychomotor", "Suicide"]

# %% Plot item level and collect correlations - MAIN A + Extra for supplement
model_corrs_df = []
for model_name in model_names:
    # model_name = 'gemma2-9b-it'
    print(model_name)
    # Load data and specs
    sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name=instr_name_str)
    responses_avg_merged, q_names = process_logits_itemLevel(sample_config, paths, bools, task_v, phq9_qs_inv_map)
    q_names = [qn for qn in q_names if 'lvl3' in qn]
    fig_rat = 0.7

    # Prep plots
    plt.close('all')
    pc.onerow = True
    pc.r, pc.c, pc.mlt = 2, 4, 1
    pc.p_lab_spec[0] = -0
    pc.p_lab_spec[1] = 1.1
    # pc.figsize = (pc.fw * fig_rat, pc.fw / 3.25)
    pc.figsize = (pc.fw * fig_rat, pc.fw / 2.25)
    # fig = plt.figure(figsize=pc.figsize)
    pc.annot_fs = 7
    afmt = '.2f'
    alpha = 0.7
    s_ec = '#ffedcb'
    b_c = '#e19f20'
    s_lw = 0.5
    f_lw = 3
    s_size = 2
    s_out_size = 3
    v_width = 1.1
    b_lw = 1

    pc.plab_offset = 0
    # Prep axes
    fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=True, sharey=False, layout='constrained')
    pc.onerow = True
    pc.axes = axes.flatten()

    pc.i = 0

    for pc.j, (q_name, ax) in enumerate(zip(q_names, pc.axes)):
        q_name_short = re.sub('lvl.*_', '', q_name).upper()
        responses_avg_merged_q = responses_avg_merged[(responses_avg_merged['q_name'] == q_name)].dropna(how='any')
        lvl_name = re.sub('_q.*', '', q_name)

        N = len(responses_avg_merged_q['sub'].unique())
        bp = sns.boxplot(data=responses_avg_merged_q, y='score_llm', x='score_sub', ax=pc.ax, width=pc.box_width,
                         linewidth=pc.box_lw, orient='v', color='black', fill=False, fliersize=pc.box_fliersize)

        sns.stripplot(data=responses_avg_merged_q, y='score_llm', x='score_sub', ax=pc.ax, linewidth=pc.dot_lw,
                      size=pc.dot_size, orient='v', alpha=pc.dot_alpha)
        r, p = stats.spearmanr(responses_avg_merged_q['score_llm'], responses_avg_merged_q['score_sub'])
        p = min(p * len(q_names), 1)
        tmp_dict = {'model': sample_config.model_name_plot, 'q_name': q_name_short, 'corr': r, 'pval': p}
        model_corrs_df.append(tmp_dict)
        # pc.t = f"{q_name_short}: r={r:.3f}\np-val: {p:.2e}"
        pc.t = f"{q_name_short} ({phq8_labs[pc.j]})\nr={r:.2f}"
        pc.ax.set_xlim([-0.75, 3.75])
        pc.ax.set_ylim([-0.75, 3.75])
        # set_scatter_axes(pc)
        pc.ax.set_title(pc.t)
        pc.ax.set_xticks(np.arange(4))
        pc.ax.set_xticklabels(np.arange(4))
        pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
                   fontweight='bold',
                   va='top', ha='right',
                   fontsize=pc.p_lab_spec[2])
        if pc.j % 4 == 0:
            pc.ax.set_yticks(np.arange(4))
            pc.ax.set_yticklabels(np.arange(4))
            # pc.ax.set_ylabel('LLM score')
            pc.ax.set_ylabel('Inferred score')
        else:
            pc.ax.set_yticks([])
            pc.ax.set_yticklabels([])
            pc.ax.set_ylabel('')

        pc.ax.set_xlabel('Participant score')
    if model_name != 'gemma2-9b-it':
        plt.suptitle(f'{sample_config.model_name_plot}')
    if bools.saveFig:
        if model_name == 'gemma2-9b-it':
            plt.savefig(
                f"{paths.plots_path}{fig_no}_item_level.pdf", dpi=300)

        plt.savefig(
            f"{paths.plots_path}scores_correlations_item_level_{sample_config.model_name}.pdf", dpi=300)

model_corrs_df = pd.DataFrame(model_corrs_df)
model_corrs_df_wide = model_corrs_df.pivot(index='model', columns='q_name', values=['corr', 'pval'])
# %% Plot diffs ECDF - MAIN B (best model)
model_name = 'gemma2-9b-it'
# Load data and specs
sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name=instr_name_str)
responses_avg_merged, q_names = process_logits_itemLevel(sample_config, paths, bools, task_v, phq9_qs_inv_map)
responses_avg_merged['score_diff'] = responses_avg_merged['score_llm'] - responses_avg_merged['score_sub']

# Only level 3
q_names = [qn for qn in q_names if 'lvl3' in qn]
responses_avg_merged = responses_avg_merged[responses_avg_merged['q_name'].isin(q_names)]
responses_avg_merged['score_sub'] = responses_avg_merged['score_sub'].astype(int)

plt.close('all')
pc.figsize = (pc.fw * (1 - fig_rat) * 0.98, (0.475) * pc.fw / 2.25)
pc.r, pc.c = 1, 1
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=False, layout='constrained')
axes = np.array([axes])
pc.onerow = True
pc.axes = axes
pc.j, pc.i = 0, 0
pc.p_lab_spec[0] = -0.075
pc.p_lab_spec[1] = 1.1
pc.plab_offset = 8
pc.l_fs(5.25)
sns.ecdfplot(data=responses_avg_merged, x='score_diff', hue='score_sub', stat='count', ax=pc.ax, legend=True,
             linewidth=pc.lw)
sns.move_legend(pc.ax, "best", title="Participant score")
# g.legend(title='',loc='best')
pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold',
           va='top', ha='right',
           fontsize=pc.p_lab_spec[2])
pc.ax.set_xlabel('Severity bias')
pc.ax.set_ylabel('Count')
pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold',
           va='top', ha='right',
           fontsize=pc.p_lab_spec[2])
pc.ax.set_title('Overall severity bias per score')
if bools.saveFig:
    # plt.savefig(
    #     f"{paths.plots_path}all_model_item_correlations.pdf", dpi=300)
    plt.savefig(
        f"{paths.plots_path}{fig_no}_bias.pdf", dpi=300)
# %% Regression for severity bias - MAIN B results
diff_lm = smf.ols('score_diff~score_sub', data=responses_avg_merged).fit()
diff_lm = smf.ols('score_diff~score_sub*q_name', data=responses_avg_merged).fit()
print(diff_lm.summary())
scores_coeffs = ['Intercept', 'score_sub']
# scores_coeffs_labels = ['Score 0', 'Score 1', 'Score 2', 'Score 3']
p_vals = [diff_lm.pvalues[coeff] for coeff in scores_coeffs]
t_vals = [diff_lm.tvalues[coeff] for coeff in scores_coeffs]
coefs = [diff_lm.params[coeff] for coeff in scores_coeffs]
stats_text = [f'b={coef:.2f}, t({int(diff_lm.df_resid)}={t_val:.2f}, p={p_val:.3f}' if p_val >= 0.001 else
              f'b={coef:.2f}, t({int(diff_lm.df_resid)})={t_val:.2f}, p$<$0.001' for p_val, t_val, coef in
              zip(p_vals, t_vals, coefs)]

report_vars.sOne_Overall_Score_Bias_Intercept = stats_text[0]
report_vars.sOne_Overall_Score_Bias_Coeff = stats_text[1]
print(stats_text)
if bools.saveTex:
    write_to_tex(report_vars, overwrite=True)  # Get numbers to tex vars

# %% Examples of biased text
# q_filter = ['lvl3_q1', 'lvl3_q2', 'lvl3_q6']
q_filter = q_names
# bias_examples = responses_avg_merged[responses_avg_merged['score_diff'].isin([-3, -2, -1, 0, 1, 2, 3])]
bias_examples = responses_avg_merged
bias_examples = bias_examples[bias_examples['q_name'].isin(q_filter)]
openq_data = pd.read_csv(f'{paths.data_path}/openq_data_long.csv')
openq_data = openq_data[
    (openq_data['sub'].isin(bias_examples['sub'].unique())) & (openq_data['question'].isin(q_filter))]
# openq_data= pd.merge(openq_data, bias_examples, on=['sub'])
openq_data.rename(columns={'question': 'q_name'}, inplace=True)
openq_data_merge = pd.merge(openq_data, bias_examples, on=['sub', 'q_name'])
openq_data_merge = openq_data_merge[['sub', 'q_name', 'response', 'score', 'score_llm', 'score_diff']]

openq_data_merge.to_csv(f'{paths.output_path}/openq_data_bias_examples.csv', index=False)

# %% Plot question correlation across models - MAIN C
plt.close('all')
# pc.figsize = (pc.fw * (1-fig_rat)*0.98,pc.fw / 3.25)
pc.figsize = (pc.fw * (1 - fig_rat) * 0.98, (0.525) * pc.fw / 2.25)
pc.r, pc.c = 1, 1
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=False, layout='constrained')
axes = np.array([axes])
pc.onerow = True
pc.axes = axes
pc.j, pc.i = 0, 0
pc.p_lab_spec[0] = -0.025
pc.p_lab_spec[1] = 1.1
pc.plab_offset = 9
pc.l_fs(5.25)
# pc.xyt_ls(5,5)
# lw = 2
corrs_sorted = model_corrs_df_wide['corr'].mean(axis=1).sort_values(ascending=False)
model_list = corrs_sorted.index.tolist()
g = sns.lineplot(data=model_corrs_df, x='q_name', y='corr', hue='model', hue_order=model_list, ax=pc.ax,
                 palette=sns.color_palette("colorblind", 5), linewidth=pc.lw)

# sns.heatmap(model_corrs_df_wide['corr'].loc[model_list, :], annot=True, cmap='Oranges', ax=pc.ax,
#             annot_kws={"size": pc.annot_fs}, cbar=False, fmt=afmt)
g.legend(title='', loc='best')
pc.ax.set_xlabel('Question')
pc.ax.set_ylabel('Correlation')
pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])
pc.ax.set_title('Item-level Correlations')
# pc.ax.set_ylim([0.3,0.8])
# plt.tight_layout()
# plt.tight_layout(pad=0.1)
# plt.subplots_adjust(hspace=0.75,wspace=0.2)
# %
if bools.saveFig:
    # plt.savefig(
    #     f"{paths.plots_path}all_model_item_correlations.pdf", dpi=300)
    plt.savefig(
        f"{paths.plots_path}{fig_no}_item_level_across_models.pdf", dpi=300)

# %% Plot item level biases - SUPP for per question per model biases

pc.l_fs(6)
model_corrs_df = []
for model_name in model_names:
    # model_name = 'gemma2-9b-it'
    print(model_name)
    # Load data and specs
    sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name=instr_name_str)
    responses_avg_merged, q_names = process_logits_itemLevel(sample_config, paths, bools, task_v, phq9_qs_inv_map)
    responses_avg_merged['score_diff'] = responses_avg_merged['score_llm'] - responses_avg_merged['score_sub']

    q_names = [qn for qn in q_names if 'lvl3' in qn]
    fig_rat = 0.7

    # Prep plots
    plt.close('all')
    pc.onerow = True
    pc.r, pc.c, pc.mlt = 2, 4, 1
    pc.p_lab_spec[0] = 0.05
    pc.p_lab_spec[1] = 1.1
    # pc.figsize = (pc.fw * fig_rat, pc.fw / 3.25)
    pc.figsize = (pc.fw * 1, pc.fw / 2.25)
    # fig = plt.figure(figsize=pc.figsize)
    pc.annot_fs = 7
    afmt = '.2f'
    alpha = 0.7
    s_ec = '#ffedcb'
    b_c = '#e19f20'
    s_lw = 0.5
    f_lw = 3
    s_size = 2
    s_out_size = 3
    v_width = 1.1
    b_lw = 1

    pc.plab_offset = 0
    # Prep axes
    fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=True, sharey=False, layout='constrained')
    pc.onerow = True
    pc.axes = axes.flatten()


    pc.i = 0

    for pc.j, (q_name, ax) in enumerate(zip(q_names, pc.axes)):
        q_name_short = re.sub('lvl.*_', '', q_name).upper()
        responses_avg_merged_q = responses_avg_merged[(responses_avg_merged['q_name'] == q_name)].dropna(how='any')
        responses_avg_merged_q['score_sub'] = responses_avg_merged_q['score_sub'].astype(int)
        lvl_name = re.sub('_q.*', '', q_name)

        N = len(responses_avg_merged_q['sub'].unique())
        sns.ecdfplot(data=responses_avg_merged_q, x='score_diff', hue='score_sub', stat='count', ax=pc.ax,
                     legend=pc.j == 7, linewidth=pc.lw)
        if pc.j == 7:
            sns.move_legend(pc.ax, "best", title="Participant score")
        # g.legend(title='',loc='best')
        pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
                   fontweight='bold',
                   va='top', ha='right',
                   fontsize=pc.p_lab_spec[2])
        pc.ax.set_xlabel('Severity bias')
        pc.ax.set_ylabel('Count')
        pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
                   fontweight='bold',
                   va='top', ha='right',
                   fontsize=pc.p_lab_spec[2])

        pc.t = f"{q_name_short} ({phq8_labs[pc.j]})"
        pc.ax.set_title(pc.t)
        pc.ax.set_xlim([-3, 3])
    plt.suptitle(f'{sample_config.model_name_plot}')
    if bools.saveFig:
        plt.savefig(
            f"{paths.plots_path}scores_bias_item_level_{sample_config.model_name}.pdf", dpi=300)

# %% Totals
phq9_data = pd.read_csv(f"{paths.data_path}/phq9_data.csv")
print(phq9_data['total'].aggregate(['mean', 'std']))

sds_data = pd.read_csv(f"{paths.data_path}/sds_data.csv")
print(sds_data['total'].aggregate(['mean', 'std']))

gad7_data = pd.read_csv(f"{paths.data_path}/gad7_data.csv")
print(gad7_data['total'].aggregate(['mean', 'std']))
