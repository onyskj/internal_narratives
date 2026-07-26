# %% Import libs and setup
import pickle

import matplotlib

matplotlib.use('TkAgg')

import pandas as pd
import seaborn as sns
from natsort import natsorted
import joblib

from _objects.model_configs import *
from _objects.configs import *
from _objects.qs_maps import QsConfig
from _objects.plot_config import *
from _objects.data_configs import p_thr

study_name = 'a_open_qs'
sampling_path = 'llm_sampling/'
analysis_path = 'main_analysis/'

from scripts.a_open_qs.main_analysis.analysis_utils import retrieve_logits_genLevel, process_logits_genLevel, \
    get_corrs_gen_wphq9, get_corrs_pvals_genq_logits, responses_totals_gen_logits, bootstrap_covs

pc = PlotConfig()
bools = Bools()
qs_config = QsConfig()
pc.ms = 10
pc.sc_lw = 2.2
n_boot = 1000  # number of bootstrapped samples
# %% Set paths and sets
paths = Paths()
paths.files_path = f'outputs/{study_name}/{sampling_path}files_logits/'
paths.data_path = f'data/{study_name}/task_data/combined/'
paths.output_path = f'outputs/{study_name}/{analysis_path}'
paths.plots_path = f'outputs/{study_name}/plots/logits_genLevel/'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)
Path(paths.output_path).mkdir(parents=True, exist_ok=True)

label_permutation = 'ABCD'

bools.loadMe = True
bools.saveMe = False
# bools.loadMe = False
# bools.saveMe = True
bools.goodSub = True

# bools.saveFig = True
bools.saveFig = False
fig_no = 'Fig3'

instr_name_str = 'instr3'
task_v = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']
model_names = ['MistralOo', 'gemma2-2b-it', 'llama32-3b-it', 'gemma2-9b-it', 'llama31-8b-it']
# model_names = ['MistralOo', 'gemma2-2b-it']
model_names = ['gemma2-9b-it']

gen_qs_list = ['sds', 'gad7', 'phq9']
gen_qs_list = ['phq9','sds', 'gad7']
# gen_qs_list = ['sds', 'gad7']
# gen_qs_list = ['sds']
# gen_qs_list = ['phq9']
# gen_qs_list = ['gad7']

notsig_colors = 'Greys'

# %% Get data by combining llm outputs into one
def get_logits_genLevel(model_names, gen_qs_list, paths, bools):
    def run_models(m_id):
        model_name = model_names[m_id]
        # model_name = model_names[0]
        print(model_name)
        sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name=instr_name_str)
        for i, gen_qs in enumerate(gen_qs_list):
            print('\t', gen_qs)
            # paths.save_responses_path = f"{files_path_new}cross/{gen_qs}/{label_permutation}/"

            # path with samped responses
            paths.gen_responses_path = f"{paths.files_path}cross/{gen_qs}/{label_permutation}/subjects/"
            # path to save combined responses
            paths.save_responses_path = f"{paths.files_path}cross/{gen_qs}/{label_permutation}/"
            Path(paths.save_responses_path).mkdir(parents=True, exist_ok=True)
            _ = retrieve_logits_genLevel(gen_qs, bools, sample_config, paths, task_v)

    if not bools.loadMe:
        joblib.Parallel(n_jobs=5)(joblib.delayed(run_models)(i) for i in range(len(model_names)))


if not bools.loadMe:
    # load and save in parallel
    get_logits_genLevel(model_names, gen_qs_list, paths, bools)
    bools.loadMe = True
    bools.saveMe = False
# %% Calculate or load bootstrapped cov diffs
if not bools.loadMe:
    diff_cov_dicts = {}
    for model_name in model_names:
        sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name=instr_name_str)
        print(model_name)
        diff_cov_dicts[model_name] = {}
        for gen_qs in gen_qs_list:
            print(gen_qs)
            # path with samped responses
            paths.gen_responses_path = f"{paths.files_path}cross/{gen_qs}/{label_permutation}/subjects/"
            # path with combined responses
            paths.save_responses_path = f"{paths.files_path}cross/{gen_qs}/{label_permutation}/"
            diff_cov_dicts[model_name][gen_qs] = bootstrap_covs(gen_qs, bools, paths, sample_config, task_v,
                                                                n_boot=n_boot)
    if bools.saveMe:
        with open(f'{paths.output_path}bootstrapped_covs.pkl', 'wb') as f:
            pickle.dump(diff_cov_dicts, f)
else:
    with open(f'{paths.output_path}bootstrapped_covs.pkl', 'rb') as f:
        diff_cov_dicts = pickle.load(f)

# %% Plot - MAIN A + SUPP - all true, recovered and measure of structure for all questionnaires, all models
corr_diff_df = []
total_corr_df = []
abs_ci_diff_df = []
store_ppt_corrs = {}
store_llm_corrs = {}
do_annot = False
# pc.cbar_pad = -0.005 - 0.05
pc.cbar_pad = 0.005
pc.annot_fs = 5
pc.ax_l_pad = 2
wr1, wr2 = 0.175, 0.125
# pc.dot_size=2

phq8_labs = ["Activities", "Hopeless", "Sleep", "Energy", "Appetite", "Self-worth", "Focus", "Psychomotor", "Suicide"]
phq8_labs = [f"Q{q + 1}: {p}" for q, p in enumerate(phq8_labs)]
phq8_labs = 'PHQ9 - ' + '; '.join(phq8_labs)
q_labs = {
    'phq9': ["Activities", "Hopeless", "Sleep", "Energy", "Appetite", "Self-worth", "Focus", "Psychomotor", "Suicide"],
    'gad7': ['Nervous', 'WorryStop', 'MuchWorry', 'Relax', 'Restless', 'Irritable', 'Afraid'],
    'sds': ['Blue', 'Morning', 'Crying', 'Sleep', 'Appetite', 'Sex', 'Weight', 'Constipation', 'Heart', 'Tired',
            'ClearMind\n', 'EaseDoing', 'Restless', 'Hopeful', 'Irritable', 'Decision', 'Useful', 'FullLife', 'Suicide',
            'Activities']}
q_labs = {k: f"{k.upper()} - " + '; '.join([f"Q{q + 1}: {p}" for q, p in enumerate(v)]) for k, v in q_labs.items()}
q_labs['sds'] = q_labs['sds'].replace('ClearMind\n;', 'ClearMind\n')
store_cov_metrics = []
for model_name in model_names:
    print(model_name)
    store_llm_corrs[model_name] = {}
    # Spec for plots
    pc.r, pc.c, pc.mlt = len(gen_qs_list), 4, 1
    pc.figsize = (pc.fw, pc.r * pc.fw / 5)
    # pc.onerow = True

    afmt = '.2f'
    ax_space = 5
    # Setup axes
    plt.close('all')
    pc.i, pc.j = 0, 0
    fig, axes = plt.subplots(pc.r, pc.c, width_ratios=[1, 1, wr1, wr2], figsize=pc.figsize, layout='constrained')
    # pc.axes = axes
    if pc.r == 1:
        pc.axes = np.array([axes])
    else:
        pc.axes = axes
    for pc.i, gen_qs in enumerate(gen_qs_list):
        print(gen_qs)
        pc.p_lab_spec[0] = -0.1
        pc.p_lab_spec[1] = 1.2

        # Load specs and DFs
        sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name=instr_name_str)
        paths.gen_responses_path = f"{paths.files_path}cross/{gen_qs}/{label_permutation}/subjects/"
        paths.save_responses_path = f"{paths.files_path}cross/{gen_qs}/{label_permutation}/"
        responses_mean = retrieve_logits_genLevel(gen_qs, bools, sample_config, paths, task_v)
        responses_avg_merged, closed_data_long, q_names = process_logits_genLevel(gen_qs, bools, sample_config, paths,
                                                                                  task_v)
        context_names = natsorted(responses_avg_merged['q_name_context'].unique())
        context_names = [c for c in context_names if 'lvl3' in c]
        responses_avg_merged = responses_avg_merged[responses_avg_merged['q_name_context'].isin(context_names)]
        q_names = natsorted(responses_avg_merged['q_name'].unique())

        # Get correlations with phq9
        cross_corr, cross_corr_subset, cross_pvals, cross_pvals_subset = get_corrs_gen_wphq9(paths, gen_qs,
                                                                                             closed_data_long, q_names,
                                                                                             context_names, qs_config,
                                                                                             task_v)

        no_sui_idx = [c for c in cross_corr_subset.index if c != 'phq9_q9']

        store_ppt_corrs[gen_qs] = cross_corr_subset.loc[no_sui_idx]

        # llm vs ppt gen correlations
        df_corr, df_corr_wide, N_range = get_corrs_pvals_genq_logits(responses_avg_merged, context_names, q_names)

        store_llm_corrs[model_name][gen_qs] = df_corr_wide['r']
        corr_diff = (np.tril(cross_corr_subset.iloc[:8, :]) - np.tril(df_corr_wide['r'].values)).flatten()
        corr_diff = [float(corr) for corr in corr_diff if corr != 0]
        tmp_dict_corr = {'model': sample_config.model_name_plot, 'gen_qs': gen_qs, 'corr_diff': corr_diff}
        corr_diff_df.append(pd.DataFrame(tmp_dict_corr))

        # calculate total scores for the llm samples and compare with subject data
        totals_sub_llm, r_totals, p_totals = responses_totals_gen_logits(responses_avg_merged, closed_data_long)

        tmp_dict_total = {'model': sample_config.model_name_plot, 'gen_qs': gen_qs, 'total_corr': [float(r_totals)]}
        total_corr_df.append(pd.DataFrame(tmp_dict_total))

        vmin_val = min(df_corr_wide['r'].min().min(), cross_corr_subset.min().min())
        vmax_val = max(df_corr_wide['r'].max().max(), cross_corr_subset.max().max())

        # Plot participant correlation item-level
        pc.j = 0
        pc.p_lab_spec[0] = -.025
        sns.heatmap(cross_corr_subset.loc[no_sui_idx], cmap=pc.pos_heatmap, vmin=vmin_val, vmax=vmax_val,
                    annot=do_annot, annot_kws={"size": pc.annot_fs}, ax=pc.ax, cbar=False, fmt=afmt,
                    cbar_kws={'pad': pc.cbar_pad})

        data_ns = cross_corr_subset[cross_pvals >= p_thr].loc[no_sui_idx]
        annot_labels_ns = pd.DataFrame('', index=data_ns.index, columns=data_ns.columns)
        annot_labels_ns[~data_ns.isna()] = 'ns'

        sns.heatmap(data_ns, annot=annot_labels_ns, cmap=pc.pos_heatmap, vmin=vmin_val, vmax=vmax_val,
                    annot_kws={"size": pc.annot_fs}, ax=pc.ax, cbar=False, fmt='')
        pc.ax.set_title(f"Ground-truth item pairwise correlations")
        pc.ax.set_xlabel(f"{gen_qs.upper()} question")
        pc.ax.set_ylabel('PHQ-8 question')

        pc.ax.set_xticks(np.arange(len(cross_corr_subset.columns)) + 0.5)
        pc.ax.set_xticklabels([f'{q + 1}' for q in range(len((cross_corr_subset.columns)))], rotation='horizontal')

        pc.ax.set_yticks(np.arange(len(cross_corr_subset.loc[no_sui_idx].index)) + 0.5)
        pc.ax.set_yticklabels([f'{q + 1}' for q in range(len((cross_corr_subset.loc[no_sui_idx].index)))])
        pc.ax.yaxis.labelpad = pc.ax_l_pad

        pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
                   fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])

        # Plot item-level correlations between participant score on generalised questionnaire and score on that given open question
        pc.j = 1
        sns.heatmap(df_corr_wide['r'], cmap=pc.pos_heatmap, vmin=vmin_val, vmax=vmax_val, annot=do_annot,
                    annot_kws={"size": pc.annot_fs}, ax=pc.ax, cbar=True, fmt=afmt,
                    cbar_kws={'pad': pc.cbar_pad, 'label': ''})

        data_ns = df_corr_wide['r'][df_corr_wide['p-val'] >= p_thr]
        annot_labels_ns = pd.DataFrame('', index=data_ns.index, columns=data_ns.columns)
        annot_labels_ns[~data_ns.isna()] = 'ns'

        sns.heatmap(data_ns, annot=annot_labels_ns, cmap=pc.pos_heatmap, vmin=vmin_val, vmax=vmax_val,
                    annot_kws={"size": pc.annot_fs}, ax=pc.ax, cbar=False, fmt='')

        pc.ax.set_title(f"Estimated vs ground-truth item correlations")
        pc.ax.set_xlabel(gen_qs.upper() + ' question\n')
        pc.ax.set_ylabel('Open PHQ-8 Q')
        pc.ax.set_xticks(np.arange(len(cross_corr_subset.columns)) + 0.5)
        pc.ax.set_xticklabels([f'{q + 1}' for q in range(len((cross_corr_subset.columns)))], rotation='horizontal')

        pc.ax.set_yticks([])
        pc.ax.set_yticklabels([])
        pc.ax.yaxis.labelpad = pc.ax_l_pad

        pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
                   fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])

        text_obj = pc.ax.text(0.33, -0.45, q_labs[gen_qs] + '\n', transform=pc.ax.transAxes, fontweight='bold',
                              va='top', ha='center', fontsize=pc.p_lab_spec[2])
        text_obj.set_in_layout(False)

        # Plotting total scatter
        pc.j = 2
        pc.ax.plot([qs_config.qs_min_total[gen_qs] - ax_space, qs_config.qs_max_total[gen_qs] + ax_space],
                   [qs_config.qs_min_total[gen_qs] - ax_space, qs_config.qs_max_total[gen_qs] + ax_space], color='gray',
                   linewidth=pc.lw, alpha=pc.dot_alpha)
        sns.scatterplot(totals_sub_llm, x='total_sub', y='total_llm', ax=pc.ax, s=pc.dot_size, linewidth=pc.dot_lw,
                        alpha=pc.dot_alpha)
        pc.ax.set_title(f"\n{gen_qs.upper()} totals \nr: {r_totals:.2f}")
        pc.ax.set_aspect('equal', 'box')
        pc.ax.set_xlim([qs_config.qs_min_total[gen_qs] - ax_space, qs_config.qs_max_total[gen_qs] + ax_space])
        pc.ax.set_ylim([qs_config.qs_min_total[gen_qs] - ax_space, qs_config.qs_max_total[gen_qs] + ax_space])
        pc.ax.set_xlabel('Ground-truth')
        pc.ax.set_ylabel('Estimated')
        pc.ax.text(pc.p_lab_spec[0], pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
                   fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])

        # Plot similarity metrics
        pc.j = 3
        pc.p_lab_spec[1] = 1.1
        pc.p_lab_spec[0] = -.3
        cov_ms_avg_diff = {'avg_abs_diff': 1 - np.abs(diff_cov_dicts[model_name][gen_qs]['abs_avg']).mean()}
        metric_names = ['U_avg_angle', 'U_P_sim', 'V_avg_angle', 'V_P_sim', 'sigma_error_inv']
        cov_ms_avg_diff = cov_ms_avg_diff | diff_cov_dicts[model_name][gen_qs]['ss_avg'][metric_names].mean().to_dict()
        cov_ms_avg_diff['r_totals'] = r_totals
        metric_subset = ['r_totals', 'avg_abs_diff', 'sigma_error_inv', 'U_avg_angle', 'U_P_sim', 'V_avg_angle',
                         'V_P_sim']
        metric_labels = ['Totals', 'Item corrs.', 'Singular vals.', 'O. PHQ8 basis', "O. PHQ8 proj.",
                         f'{gen_qs.upper()} basis', f'{gen_qs.upper()} proj.']
        tmp_dict = {'model': sample_config.model_name_plot, 'gen_qs': gen_qs.upper()} | cov_ms_avg_diff
        store_cov_metrics.append(pd.DataFrame(tmp_dict, index=[0]))
        cov_ms_avg_diff = pd.DataFrame(cov_ms_avg_diff, index=[0])



        sns.barplot(data=cov_ms_avg_diff[metric_subset], ax=pc.ax, orient='h', facecolor='tab:gray')
        pc.ax.set_yticks(range(len(metric_labels)))
        pc.ax.set_yticklabels(metric_labels, rotation=25)
        pc.ax.set_xlim([0, 1.05])
        if pc.i == 2:
            pc.ax.set_title('\nSimilarity    \nmetrics    ')
        else:
            pc.ax.set_title('Similarity    \nmetrics    ')
        # pc.ax.set_xlabel(gen_qs.upper())
        pc.ax.text(pc.p_lab_spec[0], pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
                   fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])

    if model_name != 'gemma2-9b-it':
        plt.suptitle(f'{sample_config.model_name_plot}')

    if bools.saveFig:
        if model_name == 'gemma2-9b-it':
            plt.savefig(f"{paths.plots_path}{fig_no}_gen_level.pdf", dpi=300)
        plt.savefig(f"{paths.plots_path}gen_qs_total_item_corrs_{sample_config.model_name}.pdf", dpi=pc.dpi_val)

    # plt.close('all')
store_cov_metrics = pd.concat(store_cov_metrics)
# %%% Save metrics to csv
if bools.saveMe:
    store_cov_metrics.to_csv(f"{paths.output_path}cov_metrics_all.csv", index=False)
else:
    store_cov_metrics = pd.read_csv(f"{paths.output_path}cov_metrics_all.csv")
cov_metrics = pd.pivot(store_cov_metrics, index='model', columns='gen_qs')
# %% Gather covariance-match metrics - SUPP -  across models and questionnaires - comparision
metric_subset = ['r_totals', 'avg_abs_diff', 'sigma_error_inv', 'U_avg_angle', 'U_P_sim', 'V_avg_angle', 'V_P_sim']
plt.close('all')
pc.onerow = True
pc.r, pc.c = 1, len(metric_subset)
pc.figsize = (pc.fw, pc.fw / 5)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=True, layout='constrained')
# pc.axes = axes.flatten()
axes = np.array([axes])
pc.axes = axes
pc.i = 0
pc.j = 0

pc.p_lab_spec[0] = -0.05
pc.p_lab_spec[1] = 1.05
pc.annot_fs = 6
pc.ax_ts(7, 1)
ts = 5
pc.xyt_ls(ts, ts)
pc.ax_ls(7)

metric_labels_broad = ['Totals', 'Item corrs.', 'Singular vals.', 'O. PHQ8 basis', 'O. PHQ8 proj.', '[Qs.] basis',
                       '[Qs.] proj.']
model_order = cov_metrics['sigma_error_inv'].sort_values(by='GAD7', ascending=False).index.tolist()
for pc.j, (metric_name, metric_label) in enumerate(zip(metric_subset, metric_labels_broad)):
    sns.heatmap(cov_metrics[metric_name].loc[model_order], annot=True, cmap=pc.pos_heatmap, ax=pc.ax,
                annot_kws={"size": pc.annot_fs}, cbar=False, fmt='.2f')

    if pc.j == 0:
        pc.ax.set_ylabel(f"Model")
    else:
        pc.ax.set_ylabel(f"")

    pc.ax.set_title(f"{metric_label}")
    pc.ax.set_xlabel("Questionnaire")
    pc.ax.text(pc.p_lab_spec[0], pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes, fontweight='bold',
               va='top', ha='right', fontsize=pc.p_lab_spec[2])
if bools.saveFig:
    plt.savefig(f"{paths.plots_path}gen_qs_metric_heatmap.pdf", dpi=pc.dpi_val)
