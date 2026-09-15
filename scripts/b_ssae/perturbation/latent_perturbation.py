# %% Load libs and set up objects
import os,sys
import json
from tqdm import tqdm

import torch
from torch.utils.data import Dataset, DataLoader
import seaborn as sns

torch.set_grad_enabled(False)
import matplotlib
import matplotlib.pyplot as plt

if sys.platform == 'darwin':
    device_name = 'mps'
    # matplotlib.use('Qt5Agg')
    matplotlib.use('Agg')
    plt.ion()

else:
    matplotlib.use('Agg')
    matplotlib.get_backend()
    device_name = 'cuda'

from _objects.model_configs import *
from _objects.configs import *
from _objects.plot_config import *
from _objects.sae_models import *
from _objects.data_configs import q_score_change, p_force
from scripts.b_ssae.training.prepare_model_datasets import MyDataset, MetaDataset
from scripts.b_ssae.perturbation.perturb_utils import *

pc = PlotConfig()

study_name = 'b_ssae'
analysis_path = 'perturbation/'

bools = Bools()
bools.saveFig = True
# bools.saveFig = False
bools.do_zscores = True
bools.loadMe = True
bools.saveMe = False
# bools.loadMe = False
# bools.saveMe = True
bools.goodSub = True
bools.computeDelta = False
# bools.computeDelta = True

# do_zscores = True

exp_name = 'SAE_exp_v3_best'
model_name = 'gemma2-9b-it'

# Set up paths
paths = Paths()
paths.data_path = f'data/{study_name}/'
paths.plots_path = f'outputs/{study_name}/plots/{analysis_path}'
paths.base_output_path = f'outputs/{study_name}/training/'
# paths.analysis_output_path = f'outputs/{study_name}/main_analysis/'
paths.output_path = f'outputs/{study_name}/{analysis_path}'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)
Path(paths.output_path).mkdir(parents=True, exist_ok=True)
paths.model_dir = f'{paths.base_output_path}saved_models/{exp_name}/{model_name}/'
paths.delta_dir = f'{paths.output_path}saved_delta/{exp_name}/{model_name}/'
Path(paths.delta_dir).mkdir(parents=True, exist_ok=True)

# Load exp config
with open(f'{paths.base_output_path}exp_logs/{exp_name}.json', 'r') as fp:
    exp_json_config = json.load(fp)
q_idxs = np.arange(9)  # indices for latent phq9 questions

phq9_q_names = ['phq9_q' + str(q + 1) + 's' for q in range(9)]
sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name='instr3')

best_configs = os.listdir(paths.model_dir)
best_configs = [t.replace('.pt', '').replace('best_', '') for t in best_configs]  # [0:3]
best_config_dicts = [{s.split('-')[0]: '-'.join(s.split('-')[1:]) for s in t.split('^^')} for t in
                     best_configs]
# %% Compute/Load deltas for each layer and store diffs
if not bools.loadMe:
    store_diff_all = []
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

        # # get val dataset
        val_dataset = MyDataset(meta_dataset, n_train, n_train + n_val, l, device=device_name)
        val_dataloader = DataLoader(val_dataset, batch_size=len(val_dataset.subs), shuffle=True)
        val_features, val_labels = next(iter(val_dataloader))
        val_features = val_features.to(device_name)
        val_labels = val_labels.to(device_name)

        # load model
        model = SAE4(sae_cfg).to(device_name)
        model_fp = f'{paths.model_dir}best_{best_config}.pt'
        model.load_state_dict(torch.load(model_fp, map_location=torch.device(device_name)))
        # model.eval()

        store_diffs = []
        for q_idx_to_perturb in tqdm(q_idxs):
            # print(f'Q: {q_idx_to_perturb + 1}')
            deltaS_fp = f'{paths.delta_dir}deltaS_{best_config}^^q_target_idx-{q_idx_to_perturb}^^s_change-{q_score_change}.pt'
            # print(deltaS_fp)

            deltaS = get_perturb_delta(model, deltaS_fp, q_idx_to_perturb=q_idx_to_perturb,
                                       score_change=q_score_change, loadDelta=(not bools.computeDelta), saveDelta=True,
                                       device_name=device_name)

            # Forward pass get original states
            latent_qs, _, _ = model.infer(val_features)
            # Get perturbed states
            latent_qs_perturbed, _, h_rec_perturbed = model.infer(val_features, delta_s=deltaS,
                                                                  p_force=p_force * 1)

            tmp_diff = (latent_qs_perturbed - latent_qs).to('cpu').mean(axis=0)
            tmp_df = pd.DataFrame(tmp_diff, columns=['diff']).reset_index(names='q_idx')
            tmp_df = tmp_df.melt(id_vars='q_idx')
            tmp_df['q_idx_to_perturb'] = q_idx_to_perturb
            # tmp_df['p_force']=p_force
            store_diffs.append(tmp_df)

        store_diffs = pd.concat(store_diffs)
        store_diffs['layer'] = best_config_dict['layer']

        store_diff_all.append(store_diffs)

    store_diff_all = pd.concat(store_diff_all)
    store_diff_all.sort_values(by=['layer', 'q_idx', 'q_idx_to_perturb'], inplace=True)
    if bools.saveMe:
        store_diff_all.to_csv(f'{paths.output_path}latent_perturbation_all_layers.csv', index=False)
else:
    store_diff_all = pd.read_csv(f'{paths.output_path}latent_perturbation_all_layers.csv')

# %% Plot latent diffs for all layers
plt.close('all')
pc.r, pc.c = 3, 7
fig_rat = 1
pc.figsize = (pc.fw * fig_rat, pc.fw / 2)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, layout='constrained')
pc.onerow = True
pc.axes = np.array(axes.flat)
pc.i, pc.j = 0, 0

pc.plab_offset = 0
pc.ax_ts(6, 7 / 6)
# pc.l_fs(12, 0.85)
ts = 6
pc.xyt_ls(ts, ts)
pc.p_lab_spec[0] = -0.075
pc.p_lab_spec[1] = 1.15
pc.p_lab_spec[2] = 6
pc.dpi_val = 300
ax_space = 0
pc.annot = 5
all_layers = store_diff_all['layer'].unique().astype(int)[:]
for pc.j, layer in enumerate(all_layers):
    store_diffs = store_diff_all[store_diff_all['layer'].astype(str) == str(layer)]
    store_diffs_wide = store_diffs.pivot(index='q_idx_to_perturb', columns='q_idx', values='value')
    sns.heatmap(store_diffs_wide, annot=False, fmt='.0f', cbar=False, annot_kws={"fontsize": pc.annot_fs}, ax=pc.ax)
    pc.ax.set_xlabel('')
    pc.ax.set_ylabel('')
    if pc.j == 17:
        pc.ax.set_xlabel('Question to perturb')
    if pc.j == 7:
        pc.ax.set_ylabel('Question change')
    pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
               fontweight='bold',
               va='top', ha='right',
               fontsize=pc.p_lab_spec[2])
    pc.ax.set_xticks(np.arange(len(store_diffs_wide.columns)) + 0.5)
    # pc.ax.set_xticklabels([f'Q{q + 1}' for q in range(len((store_diffs_wide.index)))], rotation='horizontal')
    pc.ax.set_xticklabels([f'{q + 1}' for q in range(len((store_diffs_wide.index)))], rotation='horizontal')
    pc.ax.set_yticks(np.arange(len(store_diffs_wide.columns)) + 0.5)
    # pc.ax.set_yticklabels([f'Q{q + 1}' for q in range(len((store_diffs_wide.index)))], rotation='horizontal')
    pc.ax.set_yticklabels([f'{q + 1}' for q in range(len((store_diffs_wide.index)))], rotation='horizontal')
    pc.ax.set_title(f'Layer {layer}')
    pc.ax.set_box_aspect(1)
plt.suptitle(f'Latent perturbation confusion matrix')

if bools.saveFig:
    plt.savefig(
        f"{paths.plots_path}latent_perturbation_all_layers.pdf", dpi=300)
