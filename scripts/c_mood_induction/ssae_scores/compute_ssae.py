# %% Import and setup objects
import json
import os
import pandas as pd

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from _objects.configs import *

from _objects.sae_models import *
from _objects.model_configs import *
from scripts.b_ssae.training.prepare_model_datasets import MyDataset, MetaDataset

bools = Bools()

study_name = 'c_mood_induction'
ssae_study_name = 'b_ssae'
analysis_path = 'ssae_scores/'

# set paths
paths = Paths()
paths.base_output_path = f'outputs/{ssae_study_name}/training/'
paths.output_path = f'outputs/{study_name}/{analysis_path}'
paths.states_path = f'outputs/{study_name}/hs_sampling/'
paths.data_path = f'data/{study_name}/task_data/combined/'
paths.base_data_path = f'data/{ssae_study_name}/'
Path(paths.output_path).mkdir(parents=True, exist_ok=True)

bools.do_zscores = True
bools.loadMe = True
bools.saveMe = False
# bools.loadMe = False
# bools.saveMe = True

phq9_q_names = ['phq9_q' + str(q + 1) for q in range(9)]
# %% Set configs
model_name = 'gemma2-9b-it'
exp_name = 'SAE_exp_v3_best'
device_name = 'mps'

# LLM config
sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9')
layer_idxs = np.arange(sample_config.L // 2, sample_config.L)

# Experiment config
with open(f'{paths.base_output_path}exp_logs/{exp_name}.json', 'r') as fp:
    exp_json_config = json.load(fp)
exp_config = ExpConfig(sample_config, q_case='9q', do_zscores=bools.do_zscores,
                       max_epochs=exp_json_config['max_epochs'])
paths.model_dir = f'{paths.base_output_path}saved_models/{exp_name}/{model_name}/'

# sSAE configs
best_configs = os.listdir(paths.model_dir)
best_configs = [t.replace('.pt', '').replace('best_', '') for t in best_configs]  # [0:3]
best_config_dicts = [{s.split('-')[0]: '-'.join(s.split('-')[1:]) for s in t.split('^^')} for t in
                     best_configs]  # [0:3]

# meta_dataset = torch.load(f'{paths.base_data_path}{exp_config.dataset_fname}.pt', weights_only=False)
# # Set model hidden state dimension
exp_config.d_h = sample_config.d_h

# %% Calculate average-across-layer sae scores for each text type for each ppts
text_types = ['act', 'mood', 'energy', 'pospert']
# text_types = ['act']
for text_type in text_types:
    # load text data
    if text_type == 'act':
        text_data = pd.read_csv(f'{paths.data_path}int_data.csv')
    else:
        text_data = pd.read_csv(f'{paths.data_path}openq_data.csv')
    sae_preds_df = pd.DataFrame()
    if not bools.loadMe:
        # loop through each layer
        for l, layer_idx in enumerate(layer_idxs):
        # for l, layer_idx in enumerate(layer_idxs[0:2]):
            # get layer
            layer_idx_idx = np.where(layer_idxs == layer_idx)[0][0]
            layer_name = f'layer-{layer_idx + 1}'

            # get model config
            model_layer_config = [c for c in best_configs if layer_name in c][0]
            model_layer_config_dict = \
                [{s.split('-')[0]: '-'.join(s.split('-')[1:]) for s in t.split('^^')} for t in [model_layer_config]][0]
            model_fp = f'{paths.model_dir}best_{model_layer_config}.pt'

            # decode hyperparms
            q_case = model_layer_config_dict['q_case']
            batch_size = int(model_layer_config_dict['batch_size'])
            optim_lr = float(model_layer_config_dict['optim_lr'])
            sparsity_coeff = float(model_layer_config_dict['sparsity_coeff'])
            qs_coeff = int(model_layer_config_dict['qs_coeff'])
            sae_factor = int(model_layer_config_dict['sae_factor'])
            tied_weights = model_layer_config_dict['tied_weights'] == 'True'
            sae_name = model_layer_config_dict['sae_name']

            # set sSAE config
            sae_cfg = SAE_Config(exp_config, device=device_name, x_m=sae_factor, sparse_coeff=sparsity_coeff,
                                 tied_weights=tied_weights, qs_coeff=qs_coeff)

            # load sSAE model
            model = SAE4(sae_cfg).to(device_name)
            model.load_state_dict(torch.load(model_fp, map_location=torch.device(device_name)))
            model.eval()

            # get path to hidden states
            hs_path = f'{paths.states_path}{text_type}/'
            pt_files = [f for f in os.listdir(hs_path) if '.pt' in f and sample_config.model_name in f]

            for pt_file in pt_files:
            # for pt_file in pt_files[0:10]:
                sub = pt_file.split('^^')[0]
                if sub in text_data['sub'].unique():
                    # set group, condition, exp type
                    group = text_data[text_data['sub'] == sub]['group'].values[0]
                    condition = text_data[text_data['sub'] == sub]['condition'].values[0]
                    is_autobio = text_data[text_data['sub'] == sub]['autobio'].values[0]

                    # load hidden states
                    sub_hs_ts = torch.load(f'{hs_path}{pt_file}', weights_only=True)
                    sub_hs_ts = sub_hs_ts[layer_idx_idx, -1, :].type(torch.float).to(device_name).unsqueeze(0)
                    sub_hs_ts = sub_hs_ts / torch.linalg.norm(sub_hs_ts, axis=1, keepdims=True)

                    # get sSSAE scores
                    latent_qs, _, _ = model.infer(sub_hs_ts)
                    latent_qs = latent_qs.to('cpu').detach().numpy()

                    # store scores for a specific layer
                    tmp_dict = {'sub': sub, 'condition': condition, 'group': group, 'autobio': is_autobio,
                                'text': text_type, 'layer': layer_name}
                    for q, q_name in enumerate(phq9_q_names):
                        tmp_dict['t'] = np.arange(1, latent_qs.shape[0] + 1)
                        tmp_dict[f'sae_{q_name}'] = latent_qs[:, q]
                    tmp_pd = pd.DataFrame(tmp_dict)
                    sae_preds_df = pd.concat([sae_preds_df, tmp_pd], axis=0)
                    del sub_hs_ts

            del model

        # average scores across layers
        sae_preds_df_avg = sae_preds_df.groupby(['sub', 'condition', 'group', 'autobio', 'text', 't'], as_index=False)[
            [f'sae_phq9_q{qi + 1}' for qi in range(9)]].mean()

        # save to csv
        if bools.saveMe:
            sae_preds_df_avg.to_csv(f'{paths.output_path}sae_preds_{model_name}_{text_type}.csv', index=False)
    else:
        sae_preds_df = pd.read_csv(f'{paths.output_path}sae_preds_{model_name}_{text_type}.csv')
