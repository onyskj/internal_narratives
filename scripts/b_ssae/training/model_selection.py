import json
import os
import pandas as pd
import matplotlib
from torch.utils.data import DataLoader

if os.uname()[0] == 'Darwin':  # if on mac
    matplotlib.use('TkAgg')
    device_name = 'mps'
    import matplotlib.pyplot as plt
else:
    matplotlib.use('Agg')
    device_name = 'cuda'
    import matplotlib.pyplot as plt

from _utils.utils import set_seed, flush_sae
from _objects.sae_models import *
from _objects.model_configs import *
from _objects.configs import *
from _objects.plot_config import *
from scripts.b_ssae.training.prepare_model_datasets import MyDataset, MetaDataset
from scripts.b_ssae.training.training_utils import train_epochs, get_loss, get_predictions
from _objects.data_configs import seed_value, max_epochs, es_patience, es_delta

set_seed(seed_value)
study_name = 'b_ssae'
sampling_path = 'llm_sampling/'
analysis_path = 'training/'

pc = PlotConfig()
bools = Bools()

paths = Paths()
paths.data_path = f'data/{study_name}/'
paths.output_path = f'outputs/{study_name}/{analysis_path}'
paths.plots_path = f'outputs/{study_name}/plots/{analysis_path}/'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)
Path(paths.output_path).mkdir(parents=True, exist_ok=True)

fnames = type('EmptyClass', (), {})
torch_v = torch.__version__  # version of torch
# bools.save_best_model = False
bools.save_best_model = True
bools.savePlots = True
bools.do_zscores = True

# %% Find the best hyperparameter setting
phq9_q_names = ['phq9_q' + str(q + 1) + 's' for q in range(9)]
exp_name_org = 'SAE_exp_v3'
model_name_set = ['gemma2-9b-it']

all_model_loss = []
for model_name in model_name_set:
    loss_dir = f'{paths.output_path}loss/{exp_name_org}/{model_name}/'
    metric_dir = f'{paths.output_path}metrics/{exp_name_org}/{model_name}/'

    # get all loss and metric files
    loss_files = os.listdir(loss_dir)
    metric_files = [f for f in os.listdir(metric_dir) if 'metric' in f]

    # decode training config
    train_configs = ['model-' + ''.join(l.split('loss_model-')).replace('.csv', '') for l in loss_files]
    train_configs = [{s.split('-')[0]: '-'.join(s.split('-')[1:]) for s in t.split('^^')} for t in train_configs]

    # create combined df of metrics
    loss_pd = pd.concat([pd.read_csv(f'{loss_dir}{l}') for l in loss_files], axis=0)
    metric_pd = pd.concat([pd.read_csv(f'{metric_dir}{l}') for l in metric_files], axis=0)
    id_vars = list(train_configs[0].keys())

    metric_avg = metric_pd.groupby(id_vars, as_index=False)[['r', 'p']].aggregate(['mean', 'std'])
    metric_avg.columns = [f'{c1}_{c2}' if c2 != '' else c1 for c1, c2 in
                          zip(metric_avg.columns.get_level_values(0), metric_avg.columns.get_level_values(1))]
    loss_pd_best = loss_pd[loss_pd['is_best']]

    loss_w_metric = pd.merge(loss_pd_best, metric_avg, on=id_vars)

    order_cols = ['epoch', 'train_loss', 'val_loss'] + list(metric_avg.columns[-4:]) + id_vars
    other_cols = [c for c in loss_w_metric.columns if c not in order_cols]
    loss_w_metric = loss_w_metric[order_cols + other_cols]

    all_model_loss.append(loss_w_metric)

# Get top performance based on loss for each layer
all_model_loss = pd.concat(all_model_loss)
loss_sorted = all_model_loss.sort_values(by=['model', 'layer', 'val_loss', 'r_mean', 'p_mean'],
                                         ascending=[False, True, True, False, True]).groupby(['model', 'layer'],
                                                                                             as_index=False).head(1)
# %% Refit the best model
exp_name = 'SAE_exp_v3_best'
exp_json_config = {'name': exp_name, 'torch_v': torch_v, 'seed_value': seed_value, 'es_patience': es_patience,
                   'max_epochs': max_epochs, 'es_delta': es_delta,
                   'model_name_set': model_name_set, 'type': 'best_each_model_each_layer'}
Path(f'{paths.output_path}exp_logs/').mkdir(parents=True, exist_ok=True)
with open(f'{paths.output_path}exp_logs/{exp_name}.json', 'w') as fp:
    json.dump(exp_json_config, fp)

for r, row in loss_sorted.iterrows():
    # specify model config
    model_name = row['model']
    sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name='instr3')

    # specify layers
    layer_idx = row['layer'] - 1
    layer_idxs = np.arange(sample_config.L // 2, sample_config.L)
    l = int(np.where(layer_idxs == layer_idx)[0][0])

    # decode config
    best_m_l_config = row[id_vars[2:]].reset_index(drop=True).to_dict()
    best_m_l_config_str = '^^'.join([f'{k}-{v}' for k, v in best_m_l_config.items()])
    hparams = list(best_m_l_config.values())

    q_case = hparams[0]
    batch_size = hparams[1]
    optim_lr = hparams[2]
    sparsity_coeff = hparams[3]
    qs_coeff = hparams[4]
    sae_factor = hparams[5]
    tied_weights = hparams[6]
    sae_name = hparams[7]

    # Create dirs to save outputs and plots
    loss_plot_dir = f'{paths.plots_path}/loss/{exp_name}/{model_name}/'
    loss_dir = f'{paths.output_path}loss/{exp_name}/{model_name}/'
    metric_dir = f'{paths.output_path}metrics/{exp_name}/{model_name}/'
    model_dir = f'{paths.output_path}saved_models/{exp_name}/{model_name}/'
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    Path(loss_plot_dir).mkdir(parents=True, exist_ok=True)
    Path(loss_dir).mkdir(parents=True, exist_ok=True)
    Path(metric_dir).mkdir(parents=True, exist_ok=True)

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

    # current layer
    layer_name = f'layer-{layer_idx + 1}'
    print(
        f'model_name: {model_name}, layer:{layer_idx + 1}, q_case: {q_case}, batch_size: {batch_size}, optim_lr: {optim_lr}, sparsity_coeff: {sparsity_coeff}, qs_coeff:{qs_coeff}, sae_factor: {sae_factor}, tied_weights: {tied_weights}, sae_name: {sae_name}')

    # get configs
    train_config = f'model-{model_name}^^layer-{layer_idx + 1}^^q_case-{q_case}^^batch_size-{batch_size}^^optim_lr-{optim_lr}^^sparsity_coeff-{sparsity_coeff}^^qs_coeff-{qs_coeff}^^sae_factor-{sae_factor}^^tied_weights-{tied_weights}^^sae_name-{sae_name}'
    train_config_dict = {'model': model_name, 'layer': layer_idx + 1, 'q_case': q_case, 'batch_size': batch_size,
                         'optim_lr': optim_lr, 'sparsity_coeff': sparsity_coeff, 'qs_coeff': qs_coeff,
                         'sae_factor': sae_factor, 'tied_weights': tied_weights, 'sae_name': sae_name}

    # get train, val, test dataset for a given layer, based on split
    train_dataset = MyDataset(meta_dataset, None, n_train, l, device=device_name)
    val_dataset = MyDataset(meta_dataset, n_train, n_train + n_val, l, device=device_name)
    test_dataset = MyDataset(meta_dataset, n_train + n_val, None, l, device=device_name)
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=batch_size, shuffle=True)

    # loss, metric and plot file names
    fnames.loss_plot_fp = f'{loss_plot_dir}loss_{train_config}.pdf'
    fnames.loss_fp = f'{loss_dir}loss_{train_config}.csv'
    fnames.preds_fp = f'{metric_dir}preds_{train_config}.csv'
    fnames.metric_fp = f'{metric_dir}metrics_{train_config}.csv'
    fnames.model_fp = f'{model_dir}best_{train_config}.pt'

    if (Path(fnames.loss_plot_fp).exists() and Path(fnames.loss_fp).exists() and Path(
            fnames.metric_fp).exists() and Path(fnames.preds_fp).exists()):
        print('\t already done')
    else:
        print('\tTraining')

        # %% Train
        early_stopper = EarlyStopper(patience=es_patience, min_delta=es_delta)
        if 'SAE4' in sae_name:
            model = SAE4(sae_cfg)
        else:
            print('Model not found')

        # Run training with early stopping across epochs
        loss_df, optimizer = train_epochs(model, train_dataloader, val_dataloader, train_config_dict, exp_config,
                                          early_stopper, fnames, bools)

        # %% Plot loss of the optimized layer-wise-model
        item_loss_names = ['L_rec', 'L_sparse', 'L_qs', 'L_sev']
        get_loss(loss_df, item_loss_names, early_stopper, pc, fnames, bools)

        # %% Get and save predictions on validation dataset
        get_predictions(model, val_dataloader, exp_config, train_config_dict, fnames, bools)

        # %% Clean up memory
        flush_sae(model, optimizer, early_stopper, device_name)
