# %% Load libs
from matplotlib.lines import Line2D
import pickle
import json
import os
import re
from scipy import stats
import pandas as pd
import seaborn as sns
import gc

from scripts.a_open_qs.main_analysis.analysis_utils import get_corrs_pvals_genq_logits, process_logits_itemLevel
from scripts.b_ssae.training.prepare_model_datasets import MyDataset, MetaDataset
from scripts.b_ssae.training.training_utils import get_predictions
from scripts.b_ssae.main_analysis.analysis_utils import bootstrap_ssae_covs, get_corrs_gen_wphq9_ssae
from _objects.data_configs import p_thr

from torch.utils.data import DataLoader
import matplotlib
import matplotlib.pyplot as plt

if os.uname()[0] == 'Darwin':  # if on mac
    device_name = 'mps'
    # matplotlib.use('Qt5Agg')
    matplotlib.use('TkAgg')
    plt.ion()

else:
    matplotlib.use('Agg')
    matplotlib.get_backend()
    device_name = 'cuda'

from _objects.model_configs import *
from _objects.configs import *
from _objects.plot_config import *
from _objects.sae_models import *
from _objects.qs_maps import phq9_qs_inv_map

pc = PlotConfig()

study_name = 'b_ssae'
base_study_name = 'a_open_qs'
task_v = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']
sampling_path = 'llm_sampling/'
analysis_path = 'main_analysis/'
fig_no = 'Fig4'

bools = Bools()
# bools.saveFig = True
bools.saveFig = False
bools.do_zscores = True
bools.loadMe = True
bools.saveMe = False
# bools.loadMe = False
# bools.saveMe = True
bools.goodSub = True

paths = Paths()
paths.data_path = f'data/{study_name}/'
paths.plots_path = f'outputs/{study_name}/plots/{analysis_path}'
paths.base_output_path = f'outputs/{study_name}/training/'
paths.output_path = f'outputs/{study_name}/{analysis_path}'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)
Path(paths.output_path).mkdir(parents=True, exist_ok=True)

# %% Useful vars etc
exp_name = 'SAE_exp_v3_best'
model_name = 'gemma2-9b-it'

sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name='instr3')

phq9_q_names = ['phq9_q' + str(q + 1) + 's' for q in range(9)]
openq_names = ['lvl3_q' + str(q + 1) for q in range(8)]
with open(f'{paths.base_output_path}exp_logs/{exp_name}.json', 'r') as fp:
    exp_json_config = json.load(fp)
# %% Load winning model config and results for each layer
# get dirs
paths.model_dir = f'{paths.base_output_path}saved_models/{exp_name}/{model_name}/'
best_configs = os.listdir(paths.model_dir)
best_configs = [t.replace('.pt', '').replace('best_', '') for t in best_configs]  # [0:3]
best_config_dicts = [{s.split('-')[0]: '-'.join(s.split('-')[1:]) for s in t.split('^^')} for t in
                     best_configs]  # [0:3]

# get loss metrics for each layer
loss_dir = f'{paths.base_output_path}loss/{exp_name}/{model_name}/'
loss_files = os.listdir(loss_dir)
all_model_loss = pd.concat([pd.read_csv(f'{loss_dir}{l}') for l in loss_files], axis=0)
# %% Calculate (or load) final test performance of best-layer models
if not bools.loadMe:
    performance_df = []
    prediction_df = []
    prediction_gen_df = []
    for best_config_dict, best_config in zip(best_config_dicts, best_configs):
        # decode config
        q_case = best_config_dict['q_case']
        batch_size = int(best_config_dict['batch_size'])
        optim_lr = float(best_config_dict['optim_lr'])
        sparsity_coeff = float(best_config_dict['sparsity_coeff'])
        qs_coeff = int(best_config_dict['qs_coeff'])
        sae_factor = int(best_config_dict['sae_factor'])
        tied_weights = best_config_dict['tied_weights'] == 'True'
        sae_name = best_config_dict['sae_name']

        # specify layer
        layer_idx = int(best_config_dict['layer']) - 1
        layer_idxs = np.arange(sample_config.L // 2, sample_config.L)
        l = int(np.where(layer_idxs == layer_idx)[0][0])

        exp_config = ExpConfig(sample_config, q_case=q_case, do_zscores=bools.do_zscores,
                               max_epochs=exp_json_config['max_epochs'])
        exp_config.device = device_name
        exp_config.phq9_q_names = phq9_q_names

        # Get data (needs the MetaDataset class)
        meta_dataset = torch.load(f'{paths.data_path}{exp_config.dataset_fname}.pt', weights_only=False)

        # get train, val, test numbers
        n_train = int(0.7 * len(meta_dataset.subs))
        n_val = int(0.15 * len(meta_dataset.subs))
        n_test = int(0.15 * len(meta_dataset.subs))

        # hidden state dimension
        # exp_config.d_h = list(meta_dataset.avg_features.values())[0].shape[1]
        exp_config.d_h = sample_config.d_h

        # load SAE config
        sae_cfg = SAE_Config(exp_config, device=device_name, x_m=sae_factor, sparse_coeff=sparsity_coeff,
                             tied_weights=tied_weights, qs_coeff=qs_coeff)

        # get test dataset
        test_dataset = MyDataset(meta_dataset, n_train + n_val, None, l, device=device_name)
        test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

        # load model
        model = SAE4(sae_cfg).to(device_name)
        model_fp = f'{paths.model_dir}best_{best_config}.pt'
        model.load_state_dict(torch.load(model_fp, map_location=torch.device(device_name)))
        model.eval()

        # get predictions at test set from average-across questions embeddings
        y_all, preds_stats_df = get_predictions(model, test_dataloader, exp_config, best_config_dict, None, bools)
        y_all = y_all.assign(**best_config_dict)
        prediction_df.append(y_all)
        performance_df.append(preds_stats_df)

        # get test dataset for indiviudal level embeddings
        meta_dataset_ind = torch.load(f'{paths.data_path}{exp_config.dataset_fname}_ind.pt', weights_only=False)
        test_dataset_ind = MyDataset(meta_dataset_ind, n_train + n_val, None, l, device=device_name)
        test_dataloader_ind = DataLoader(test_dataset_ind, batch_size=batch_size, shuffle=False)

        # predict scores for indiviudal question embedings
        x = torch.stack(test_dataloader_ind.dataset.features).to(exp_config.device)
        y = torch.stack(test_dataloader_ind.dataset.labels).to(exp_config.device)
        ytrue = y.to('cpu').numpy()
        ytrue = pd.DataFrame(ytrue, columns=exp_config.phq9_q_names).reset_index().rename(columns={'index': 'sub'})
        ytrue['sub'] = test_dataloader_ind.dataset.subs
        ytrue = ytrue.melt(id_vars='sub', var_name='q_name', value_name='score_sub')

        store_pred_q = []
        for q, q_name in enumerate(openq_names):
            # print(q,q_name)
            preds_q = model(x[:, q, :], y)[2].to(
                'cpu').detach().numpy()  # preds = rescale_np(ytrue, preds)  # preds = model(x, y)[2].to('cpu').detach()  # preds = (preds - preds.mean(axis=0)) / preds.std(axis=0)
            preds_q_df = pd.DataFrame(preds_q, columns=exp_config.phq9_q_names).reset_index().rename(
                columns={'index': 'sub'})
            preds_q_df['sub'] = test_dataloader_ind.dataset.subs
            preds_q_df = preds_q_df.melt(id_vars='sub', var_name='q_name', value_name='score_ssae')
            preds_q_df['q_name_context'] = q_name
            preds_q_df['qs'] = 'phq9'
            preds_q_df['gen_qs'] = 'phq9'
            preds_q_df['layer'] = best_config_dict['layer']
            preds_q_df['model'] = best_config
            store_pred_q.append(preds_q_df)
        store_pred_q = pd.concat(store_pred_q)

        store_pred_q = pd.merge(store_pred_q, ytrue, on=['sub', 'q_name'], how='left')
        prediction_gen_df.append(store_pred_q)

        del model
        torch.mps.empty_cache()
        gc.collect()

    # concatenate performance and predictions
    prediction_df = pd.concat(prediction_df)
    prediction_gen_df = pd.concat(prediction_gen_df)
    performance_df = pd.concat(performance_df)
    if bools.saveMe:
        prediction_df.to_csv(f'{paths.output_path}predictions_{exp_name}.csv', index=False)
        prediction_gen_df.to_csv(f'{paths.output_path}predictions_gen_{exp_name}.csv', index=False)
        performance_df.to_csv(f'{paths.output_path}performance_{exp_name}.csv', index=False)
else:
    prediction_df = pd.read_csv(f'{paths.output_path}predictions_{exp_name}.csv')
    prediction_gen_df = pd.read_csv(f'{paths.output_path}predictions_gen_{exp_name}.csv')
    performance_df = pd.read_csv(f'{paths.output_path}performance_{exp_name}.csv')

# average performance
performance_df_average = performance_df.groupby(['layer'])['r'].mean()

# get best layer metrics and config
best_layer = performance_df_average.sort_values(ascending=False).reset_index()['layer'][0]
best_performance = performance_df[performance_df['layer'] == best_layer]

best_preds = prediction_df[prediction_df['layer'] == best_layer]
best_preds_wide = best_preds.pivot(index=['sub', 'variable'], columns='source', values='value').reset_index()
best_gen_preds = prediction_gen_df[prediction_gen_df['layer'] == best_layer].sort_values(
    by=['sub', 'q_name']).reset_index(drop=True)

best_config_dict = [d for d in best_config_dicts if d['layer'] == best_layer]
best_config = [d for d in best_configs if f'layer-{best_layer}' in d][0]
best_model_fp = f'{paths.model_dir}best_{best_config}.pt'

# %% Prepare correlation data to plot
bools.loadMe = True
bools.saveMe = False
label_permutation = 'ABCD'
paths.data_path = f'data/{base_study_name}/task_data/combined/'  # temporarily switch to study 1 path
paths.files_path = f'outputs/{base_study_name}/{sampling_path}files_logits/'
paths.save_responses_path = f"{paths.files_path}paired/{label_permutation}"
paths.responses_path = f"{paths.files_path}paired/{label_permutation}/subjects/"
responses_avg_merged, _ = process_logits_itemLevel(sample_config, paths, bools, task_v, phq9_qs_inv_map)

llm_corrs_df = []
for q, q_name in enumerate(openq_names):
    q_name_short = re.sub('lvl.*_', '', q_name).upper()
    responses_avg_merged_q = responses_avg_merged[(responses_avg_merged['q_name'] == q_name)].dropna(how='any')
    r, p = stats.spearmanr(responses_avg_merged_q['score_llm'], responses_avg_merged_q['score_sub'])
    p = min(p * len(openq_names), 1)
    tmp_dict = {'model': sample_config.model_name_plot, 'q_name': q_name_short, 'r': r, 'p': p}
    llm_corrs_df.append(tmp_dict)

best_performance.loc[:, ['source']] = f'sSAE (layer {best_layer})'
best_performance.loc[:, ['q_name_short']] = best_performance['q_name'].str.replace('phq9_|s', '',
                                                                                   regex=True).str.upper()
llm_corrs_df = pd.DataFrame(llm_corrs_df)
llm_corrs_df['q_name_short'] = llm_corrs_df['q_name']
llm_corrs_df.rename(columns={'model': 'source'}, inplace=True)
common_cols = ['source', 'r', 'p', 'q_name_short']
df_corr_joint = pd.concat([best_performance[common_cols], llm_corrs_df[common_cols]], axis=0)

paths.data_path = f'data/{study_name}/'  # back to orignal path

# %% Plot best layer correaltion vs LLM - MAIN (DONE)
plt.close('all')
fig_rat = (18 - 7.3) / 2 / 18
# fig_h= 3.92/2.54
pc.figsize = (pc.fw * fig_rat, pc.fw / 4.5)
# pc.figsize = (pc.fw * 0.25, pc.fw / 5)
pc.r, pc.c = 1, 1
pc.l_fs(5)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=False, layout='constrained')
axes = np.array([axes])
pc.onerow = True
pc.axes = axes
pc.j, pc.i = 0, 0
pc.p_lab_spec[0] = -0.225
pc.p_lab_spec[1] = 1.12
g = sns.barplot(data=df_corr_joint, x='q_name_short', y='r', hue='source',
                hue_order=sorted(df_corr_joint['source'].unique()))
plt.ylim([0.45, 0.925])
pc.plab_offset = 1

g.legend(title='')
pc.ax.set_xlabel('PHQ9 Question')
pc.ax.set_ylabel('Correlation')
pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold',
           va='top', ha='right',
           fontsize=pc.p_lab_spec[2])
pc.ax.set_title('Item-level Correlations')
if bools.saveFig:
    # plt.savefig(
    #     f"{paths.plots_path}all_model_item_correlations.pdf", dpi=300)
    plt.savefig(
        f"{paths.plots_path}{fig_no}_p2_ssae_pred_comp.pdf", dpi=300)


# %% Covariance structure comparison prepare

# set paths and load LLM results for comparison
n_boot = 1000  # number of bootstrapped samples
gen_qs = 'phq9'
q_names = best_preds_wide['variable'].unique()
paths.gen_responses_path = f"{paths.files_path}cross/{gen_qs}/{label_permutation}/subjects/"
paths.save_responses_path = f"{paths.files_path}cross/{gen_qs}/{label_permutation}/"
paths.data_path = f'data/{base_study_name}/task_data/combined/'  # temporarily switch to study 1 path
paths.base_output_path = f'outputs/{base_study_name}/main_analysis/'
cov_metrics_llm = pd.read_csv(f"{paths.base_output_path}cov_metrics_all.csv")
cov_metrics_llm = cov_metrics_llm[
    (cov_metrics_llm['model'] == sample_config.model_name_plot) & (cov_metrics_llm['gen_qs'] == gen_qs.upper())]

# Bootstrap covariance matrices
if not bools.loadMe:
    diff_cov_dicts = {}
    diff_cov_dicts[model_name] = {}
    diff_cov_dicts[model_name][gen_qs] = bootstrap_ssae_covs(best_gen_preds, gen_qs, paths, sample_config, task_v,
                                                             n_boot=n_boot)
    if bools.saveMe:
        with open(f'{paths.output_path}bootstrapped_ssae_covs.pkl', 'wb') as f:
            pickle.dump(diff_cov_dicts, f)
else:
    with open(f'{paths.output_path}bootstrapped_ssae_covs.pkl', 'rb') as f:
        diff_cov_dicts = pickle.load(f)

# Get covariance bootstrap metrics
cov_ms_avg_diff = {'avg_abs_diff': 1 - np.abs(diff_cov_dicts[model_name][gen_qs]['abs_avg']).mean()}
metric_names = ['U_avg_angle', 'U_P_sim', 'V_avg_angle', 'V_P_sim', 'sigma_error_inv']
cov_ms_avg_diff = cov_ms_avg_diff | diff_cov_dicts[model_name][gen_qs]['ss_avg'][metric_names].mean().to_dict()
cov_ms_avg_diff['r_totals'] = diff_cov_dicts[model_name][gen_qs]['r_totals']

metric_subset = ['r_totals', 'avg_abs_diff', 'sigma_error_inv', 'U_avg_angle', 'U_P_sim', 'V_avg_angle',
                 'V_P_sim']
metric_labels = ['Totals', 'Item corrs.', 'Singular vals.', 'O. PHQ8 basis', "O. PHQ8 proj.",
                 f'{gen_qs.upper()} basis', f'{gen_qs.upper()} proj.']
tmp_dict = {'model': sample_config.model_name_plot, 'gen_qs': gen_qs.upper()} | cov_ms_avg_diff
cov_ms_avg_diff = pd.DataFrame(cov_ms_avg_diff, index=[0])
cov_ms_avg_diff['model']=f'sSAE'
cov_ms_avg_diff['gen_qs']=gen_qs.upper()
cov_ms_avg_diff = cov_ms_avg_diff[cov_metrics_llm.columns]

cov_metrics_joint = pd.concat([cov_metrics_llm, cov_ms_avg_diff], axis=0)
cov_metrics_joint = cov_metrics_joint.melt(id_vars=['model', 'gen_qs'], var_name='metric', value_name='value')

# Correlation structure on held-out set to plot
cross_corr, cross_corr_subset, cross_pvals, cross_pvals_subset = get_corrs_gen_wphq9_ssae(best_gen_preds, paths, gen_qs,
                                                                                          q_names,
                                                                                          openq_names,
                                                                                          task_v, p_thr=p_thr)
no_sui_idx = [c for c in cross_corr_subset.index if c != 'phq9_q9']
df_corr, df_corr_wide, N_range = get_corrs_pvals_genq_logits(best_gen_preds, openq_names, phq9_q_names,
                                                             p_thr=p_thr, score_col='score_ssae')

vmin_val = min(df_corr_wide['r'].min().min(), cross_corr_subset.min().min())
vmax_val = max(df_corr_wide['r'].max().max(), cross_corr_subset.max().max())

paths.data_path = f'data/{study_name}/'  # back to orignal path
# %% Plot ground-truth and recovered structures and metrics - MAIN (DONE)
plt.close('all')
# fig_rat = (18 - 7.3) / 2 / 18
fig_rat = 1
# fig_h= 3.92/2.54
pc.figsize = (pc.fw * fig_rat, pc.fw / 4.25)
# pc.figsize = (pc.fw * 0.25, pc.fw / 5)
pc.r, pc.c = 1, 3
pc.l_fs(5)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=False, layout='constrained',
                         width_ratios=[1, 1, 0.15])
axes = np.array([axes])
pc.onerow = True
pc.axes = axes
pc.j, pc.i = 0, 0
pc.p_lab_spec[1] = 1.12
pc.plab_offset = 3
do_annot = False
afmt = '.2f'
pc.cbar_pad = 0.005
pc.ax_l_pad = 2

# Plot participant correlation item-level
pc.j = 0
pc.p_lab_spec[0] = -.075
sns.heatmap(cross_corr_subset.loc[no_sui_idx], cmap=pc.pos_heatmap, vmin=vmin_val, vmax=vmax_val,
            annot=do_annot, annot_kws={"size": pc.annot_fs}, ax=pc.ax, cbar=False, fmt=afmt,
            cbar_kws={'pad': pc.cbar_pad})

data_ns = cross_corr_subset[cross_pvals >= p_thr].loc[no_sui_idx]
annot_labels_ns = pd.DataFrame('', index=data_ns.index, columns=data_ns.columns)
annot_labels_ns[~data_ns.isna()] = 'ns'

sns.heatmap(data_ns, annot=annot_labels_ns, cmap=pc.pos_heatmap, vmin=vmin_val, vmax=vmax_val,
            annot_kws={"size": pc.annot_fs}, ax=pc.ax, cbar=False, fmt='')
pc.ax.set_title(f"Held-out ground-truth item pairwise correlations\n")
pc.ax.set_xlabel(f"{gen_qs.upper()} question")
pc.ax.set_ylabel('PHQ-8 question')

pc.ax.set_xticks(np.arange(len(cross_corr_subset.columns)) + 0.5)
pc.ax.set_xticklabels([f'{q + 1}' for q in range(len((cross_corr_subset.columns)))], rotation='horizontal')

pc.ax.set_yticks(np.arange(len(cross_corr_subset.loc[no_sui_idx].index)) + 0.5)
pc.ax.set_yticklabels([f'{q + 1}' for q in range(len((cross_corr_subset.loc[no_sui_idx].index)))])
pc.ax.yaxis.labelpad = pc.ax_l_pad

pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])

# Plot item-level correlations between participant score on generalised questionnaire and ssae score on that given open question
pc.j = 1
sns.heatmap(df_corr_wide['r'], cmap=pc.pos_heatmap, vmin=vmin_val, vmax=vmax_val, annot=do_annot,
            annot_kws={"size": pc.annot_fs}, ax=pc.ax, cbar=True, fmt=afmt,
            cbar_kws={'pad': pc.cbar_pad, 'label': ''})

data_ns = df_corr_wide['r'][df_corr_wide['p-val'] >= p_thr]
annot_labels_ns = pd.DataFrame('', index=data_ns.index, columns=data_ns.columns)
annot_labels_ns[~data_ns.isna()] = 'ns'

sns.heatmap(data_ns, annot=annot_labels_ns, cmap=pc.pos_heatmap, vmin=vmin_val, vmax=vmax_val,
            annot_kws={"size": pc.annot_fs}, ax=pc.ax, cbar=False, fmt='')

pc.ax.set_title(f"sSAE estimated vs held-out ground-truth item correlations\n")
pc.ax.set_xlabel(gen_qs.upper() + ' question\n')
pc.ax.set_ylabel('Open PHQ-8 Q')
pc.ax.set_xticks(np.arange(len(df_corr_wide['r'].columns)) + 0.5)
pc.ax.set_xticklabels([f'{q + 1}' for q in range(len((df_corr_wide['r'].columns)))], rotation='horizontal')

pc.ax.set_yticks([])
pc.ax.set_yticklabels([])
pc.ax.yaxis.labelpad = pc.ax_l_pad

pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])


# Plot similarity metrics
pc.j = 2
pc.p_lab_spec[0] = -0.2
# sns.barplot(data=cov_ms_avg_diff[metric_subset], orient='h', facecolor='tab:gray', ax=pc.ax)
g=sns.barplot(data=cov_metrics_joint,y='metric',x='value',hue='model', orient='h', ax=pc.ax)
g.legend(title='', loc='upper left', bbox_to_anchor=(-2.45, 1.25))
pc.ax.set_ylabel('')
pc.ax.set_xlabel('')
pc.ax.set_yticks(range(len(metric_labels)))
pc.ax.set_yticklabels(metric_labels, rotation=25)
pc.ax.set_xlim([0, 1.05])
if pc.i == 1:
    pc.ax.set_title('\nSimilarity    \nmetrics    ')
else:
    pc.ax.set_title('Similarity    \nmetrics    ')
pc.ax.text(pc.p_lab_spec[0], pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold', va='top', ha='right', fontsize=pc.p_lab_spec[2])

if bools.saveFig:
    plt.savefig(
        f"{paths.plots_path}{fig_no}_p3_ssae_structure.pdf", dpi=300)
# %% Plot test prediction performance layer and question wise - SUPPLEMENT (DONE)
performance_df_wide = performance_df.pivot(index='q_name', columns='layer', values='r')
plt.close('all')
pc.r, pc.c, pc.mlt = 1, 1, 2
# pc.figsize = ((pc.c + 3.5) * pc.mlt, (pc.r + 0.5) * pc.mlt)
pc.figsize = (pc.fw, pc.fw / 3)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize)
# pc.axes = np.array([[axes]])
# pc.axes= axes
pc.onerow = False
pc.axes = np.array([[axes]])
pc.i, pc.j = 0, 0

pc.ax_ts(7, 1)
# pc.l_fs(12, 0.85)
ts = 7
pc.xyt_ls(ts, ts)
pc.ax_ls(7)
# pc.kde_lw = 3
# pc.p_lab_spec[2] = 14
pc.p_lab_spec[0] = -.065
pc.p_lab_spec[1] = 1.05
# pc.dpi_val = 300
# pc.ms = 100
ax_space = 5
hrat = 3.75
pc.annot_fs = 7
sns.heatmap(performance_df_wide, annot=True, cmap=pc.pos_heatmap, ax=pc.ax,
            annot_kws={"size": pc.annot_fs}, cbar=False, fmt='.2f')
pc.ax.set_xlabel('Layer')
pc.ax.set_ylabel('PHQ9 Latent Question')
pc.ax.set_yticklabels([f'Q{q + 1}' for q in range(9)], rotation='horizontal')
pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
           fontweight='bold',
           va='top', ha='right',
           fontsize=pc.p_lab_spec[2])
pc.ax.set_title(f'{sample_config.model_name_plot} layerwise sSAE prediction test performance')
plt.tight_layout()
if bools.saveFig:
    plt.savefig(
        f"{paths.plots_path}test_performance_{sample_config.model_name}.pdf", dpi=300)

# %% Plot best layer predictions - SUPPLEMENT (DONE)
phq9_labs = ["Activities", "Hopeless", "Sleep", "Energy", "Appetite", "Self-worth", "Focus", "Psychomotor", "Suicide"]
plt.close('all')
pc.r, pc.c, pc.mlt = 2, 5, 1.8
pc.figsize = (pc.fw, pc.fw / 2.5)

pc.p_lab_spec[0] = -0.01
pc.p_lab_spec[1] = 1.15
pc.dot_size = 3

v_cols = {'lvl1': '#1f77b4', 'lvl2': '#009ac8', 'lvl3': '#00b9c2'}

plt.close('all')
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize)
pc.axes = axes.flatten()
pc.onerow = True
pc.i = 0

v_col = '#1f77b4'
for pc.j, (q_name, ax) in enumerate(zip(q_names, pc.axes)):
    q_name_short = f'PHQ9 Q{pc.j + 1}'
    best_preds_q = best_preds_wide[best_preds_wide['variable'] == q_name]

    bp = sns.boxplot(data=best_preds_q, y='ae', x='ppt', ax=pc.ax, width=pc.box_width, color='black',
                     linewidth=pc.box_lw, orient='v', fliersize=pc.box_fliersize, fill=False)
    sns.stripplot(data=best_preds_q, y='ae', x='ppt', ax=pc.ax, linewidth=pc.dot_lw, size=pc.dot_size, orient='v',
                  alpha=pc.dot_alpha)
    r, p = stats.spearmanr(best_preds_q['ae'], best_preds_q['ppt'])
    tmp_dict = {'q_name': q_name, 'q_short': f"Q{pc.j + 1}", 'source': f'sSAE (layer {best_layer})', 'corr': r}
    p = min(p * len(q_names), 1)
    # pc.t = f"{q_name_short}: r={r:.3f}"
    pc.t = f"{q_name_short} ({phq9_labs[pc.j]})\nr={r:.2f}"
    pc.ax.set_title(pc.t)
    xv = [float(v) for v in sorted(best_preds_q['ppt'].unique())]
    pc.ax.set_xticks(range(len(xv)))
    pc.ax.set_xticklabels(np.round(xv, 1))
    pc.ax.set_xlabel('Participant score')
    # pc.ax.set_ylabel('sSAE score')
    if pc.j % 5 == 0:
        pc.ax.set_ylabel('sSAE score')
    else:
        pc.ax.set_ylabel('')
plt.suptitle(f"{sample_config.model_name_plot} best layer sSAE score predictions\n")
plt.tight_layout(pad=0)
plt.subplots_adjust(hspace=0.825, wspace=0.175)
pc.j = 9
pc.ax.remove()

if bools.saveFig:
    plt.savefig(
        f"{paths.plots_path}ssae_bestlayer_performance_{sample_config.model_name}.pdf", dpi=300)

# %% Plot training loss for each layer - SUPPLEMENT (DONE)
plt.close('all')
pc.r, pc.c, pc.mlt = 1, 1, 1
pc.figsize = (pc.fw * 1, pc.fw / 3.25)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize)
pc.onerow = False
pc.axes = np.array([[axes]])
pc.i, pc.j = 0, 0

pc.ax_ts(7, 1)
pc.l_fs(7)
ts = 7
pc.xyt_ls(ts, ts)
pc.ax_ls(7)
pc.p_lab_spec[0] = -.05
pc.p_lab_spec[1] = 1.15
pc.dpi_val = 300
pc.lw = 0.5

sns.lineplot(all_model_loss, x='epoch', y='train_loss', units='layer', ax=pc.ax, color='tab:blue', estimator=None,
             lw=pc.lw)
sns.lineplot(all_model_loss, x='epoch', y='val_loss', units='layer', ax=pc.ax, color='tab:orange', estimator=None,
             lw=pc.lw)
custom_lines = [Line2D([0], [0], color='tab:blue', lw=pc.lw * 3),
                Line2D([0], [0], color='tab:orange', lw=pc.lw * 3)]

pc.ax.legend(custom_lines, ['training loss', 'validation loss'])
# pc.ax.legend()
pc.ax.set_ylim([0, 10])
pc.ax.set_xlabel('Epoch')
pc.ax.set_ylabel('Loss')
pc.ax.set_title(f'Loss curve for each layer for {sample_config.model_name_plot}')
plt.tight_layout()
if bools.saveFig:
    plt.savefig(
        f"{paths.plots_path}ssae_loss_{sample_config.model_name}.pdf", dpi=300)

