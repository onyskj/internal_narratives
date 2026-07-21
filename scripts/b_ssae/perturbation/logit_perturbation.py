import os
import json
import torch
from tqdm import tqdm
import random
import matplotlib

torch.set_grad_enabled(False)
my_dtype = torch.bfloat16

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
from _objects.sae_models import *
from _objects.qs_maps import maps, QsConfig
from _objects.data_configs import q_score_change, p_force

from scripts.a_open_qs.llm_sampling.logit_utils import create_question_pairs_instr, setup_model, load_task_content, \
    get_all_question_pairs, get_sub_locs, get_openq_data, flush
from scripts.b_ssae.training.prepare_model_datasets import MyDataset, MetaDataset
from scripts.b_ssae.perturbation.perturb_utils import *
from _objects.steer_config import SteerConfig, SteerHiddenState

qs_config = QsConfig()
pc = PlotConfig()

bools = Bools()
# bools.saveFig = True
bools.saveFig = False
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

# whether to run on validation or test set
ds_type = 'val'
# ds_type = 'test'

model = None
end_idx = None
subs_end_idx = None
# end_idx = 10
if ds_type == 'val':
    steer_mlt_set = [-1.5, -1, -0.5, -0.25] + [0.25, 0.5, 1, 1.5]
if ds_type == 'test':
    steer_mlt_set = [-0.25, 1.5]  # final test of the best setting from validation sample
steer_mlt_set = [-1.0, 1.0]

# set paths
paths = Paths()
paths.output_path = f'outputs/{study_name}/{analysis_path}'
paths.base_output_path = f'outputs/{study_name}/training/'
paths.data_path = f'data/{study_name}/'
paths.files_data_dir = f'data/{base_study_name}/task_data/combined/'
paths.prompts_path = f'scripts/{base_study_name}/{sampling_path}prompts/'
paths.sub_path = f'scripts/{base_study_name}/{sampling_path}'
paths.files_dir = f'outputs/{study_name}/{analysis_path}files_logits_perturbed_{ds_type}/'
Path(paths.files_dir).mkdir(parents=True, exist_ok=True)
# %% Prepare for sampling logits with LLM
sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name='instr3')
sample_config.nSamples = 50
sample_config.batchSize = 1  # 20
sample_config.save_states = True
sample_config.gen_fname = 'gb'
sample_config.permute_labels = False
sample_config.label_letters = None
label_letters = list(string.ascii_uppercase)[:qs_config.qs_n_lab[to_sample_qs]]
q_scores = list(maps[to_sample_qs].values())
# q_responses = list(maps[to_sample_qs].keys())

if sample_config.permute_labels:
    tmp_zip = list(zip(q_scores, label_letters))
    random.shuffle(tmp_zip)
    q_scores, label_letters = zip(*tmp_zip)
sample_config.label_letters = label_letters
sample_config.q_scores = q_scores
sample_config.label_scores = {k: v for k, v in zip(label_letters, q_scores)}
layer_idxs = np.arange(sample_config.L // 2, sample_config.L)

### Load LLM
if model is None:
    model, tokenizer = setup_model(sample_config)

# get response labels token ids
label_ids = tokenizer(sample_config.label_letters, padding=True, return_tensors='pt',
                      return_attention_mask=True).to(device_name)
label_ids = label_ids.input_ids[:, 1:]
# %% Locate sSAE models and configs nad load dataset of embeddings
# Load exp config
with open(f'{paths.base_output_path}exp_logs/{exp_name}.json', 'r') as fp:
    exp_json_config = json.load(fp)
paths.model_dir = f'{paths.base_output_path}saved_models/{exp_name}/{model_name}/'
paths.delta_dir = f'{paths.output_path}saved_delta/{exp_name}/{model_name}/'
best_configs = os.listdir(paths.model_dir)
best_configs = [t.replace('.pt', '').replace('best_', '') for t in best_configs]  # [0:3]
best_config_dicts = [{s.split('-')[0]: '-'.join(s.split('-')[1:]) for s in t.split('^^')} for t in
                     best_configs]

exp_config = ExpConfig(sample_config, q_case='9q', do_zscores=bools.do_zscores,
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
# %% Prepare phq9 data and prompts
# get list of hidden state dataset subjects
if ds_type == 'test':
    dataset_subs = list(MyDataset(meta_dataset, n_train + n_val, None, 0, device=device_name).subs)
if ds_type == 'val':
    dataset_subs = list(MyDataset(meta_dataset, n_train, n_train + n_val, 0, device=device_name).subs)
    # dataset_subs = list(MyDataset(meta_dataset, n_train, n_train + n_val, 0, device=device_name).subs)[
    #     :subs_end_idx]
# load openq data
openq_data = pd.read_csv(f"{paths.files_data_dir}openq_data.csv")
openq_data = openq_data[openq_data['task_version'].isin(task_versions)]
openq_data = openq_data[openq_data['sub'].isin(dataset_subs)]

# preprocess openq data
openq_data_long = get_openq_data(openq_data, sample_config)
openq_data_long = openq_data_long[openq_data_long['q_name'].str.contains('lvl3')]  # only lvl3 questions

# load phq9 data
phq9_data = pd.read_csv(f"{paths.files_data_dir}phq9_data.csv")
phq9_data = phq9_data[phq9_data['task_version'].isin(task_versions)]
phq9_data = phq9_data[phq9_data['sub'].isin(dataset_subs)]
phq9_names = [c for c in phq9_data.columns if 'phq9_q' in c]
phq9_data_long = pd.melt(phq9_data, id_vars=['sub'], value_vars=phq9_names, var_name='q_name')

# prepare prompts
instr_dict, open_qs_dict, closed_qs_dict = load_task_content(sample_config)
oq_names = list(open_qs_dict.keys())  # + list(open_qs_rep_dict.keys())
oq_names = [n for n in oq_names if 'lvl3' in n]

intro_prompt, oq_instr, open_qs_dict, closed_questions_dict, cq_preamble, qsn_questions_dict, cq_instr, qsn_preamble = create_question_pairs_instr(
    sample_config)

question_pairs, question_pairs_formatted, _, _ = get_all_question_pairs(openq_data_long, sample_config, tokenizer)
# %% Perturb and sample responses for each subject, each question
for sub in tqdm(list(question_pairs.keys())[0:end_idx]):
    sample_config.subj = sub
    # find q and ans locations in tokens
    sub_texts_to_find, sub_last_token_locs = get_sub_locs(openq_data_long, question_pairs_formatted, tokenizer,
                                                          sample_config)
    for k, v in sub_last_token_locs.items():
        for k2, v2 in v.items():
            if v2 == -1:
                print(sub, k, k2, 'missing location')

    # loop through questions to perturb
    for q_idx_to_perturb, which_q in tqdm(enumerate(list(question_pairs[sub].keys())[0:end_idx])):
        # Set labels for resposnes
        sample_config.q_responses = {l: k for l, (k, v) in zip(label_letters, maps[to_sample_qs].items())}
        sample_config.qs_labels = [sample_config.q_responses[l] for l in sample_config.label_letters]

        # update config params
        sample_ts = str(round(datetime.timestamp(datetime.now()) * 10000))
        sample_config.save_states = False
        sample_config.which_q = which_q

        # Check if files are already there (based on number)
        perturbation_config_list = []
        for str_mlt in steer_mlt_set:
            perturbation_config_dict = {'latent_q_score_change': q_score_change,
                                        'latent_p_force': p_force,
                                        'q_to_perturb': f'{q_idx_to_perturb + 1}',
                                        'hs_steer_mlt': str_mlt}
            perturbation_config = '^^'.join([f'{k}-{v}' for k, v in perturbation_config_dict.items()])
            perturbation_config_list.append(perturbation_config)

        sample_config.get_remaining_samples(printMe=True, pert_config_len=len(perturbation_config_list))

        # Start the sampling and perturbing for sub and questions
        model_sae = None
        while not sample_config.currentFiles:
            sub_q_token_locs = sub_last_token_locs[sample_config.which_q]  # token locations
            sub_qs_pairs = [question_pairs_formatted[sample_config.subj][sample_config.which_q]]  # prompt

            # pass tokens through the LLM
            # inputs_ids = tokenizer(sub_qs_pairs, return_tensors="pt", padding=True).input_ids.to(device_name)
            inputs_ids = tokenizer(sub_qs_pairs, padding=True, return_tensors='pt', return_attention_mask=True).to(
                device_name)

            model_output = model(inputs_ids.input_ids, attention_mask=inputs_ids.attention_mask,
                                 output_hidden_states=True)

            # Get LLM model original hidden states - 1st pass
            hs_ts = torch.stack(model_output.hidden_states)  # (layer,batch,seq,dim)

            # get hidden state at open-ended answer location and last token location (and average across locations)
            hs_ts_sub = hs_ts[1:, 0, [sub_q_token_locs['oq_ans'], -1], :][layer_idxs].mean(dim=1)  # (layer, dim)
            del hs_ts

            # %% Get layerwise model perturbation vectors for the question
            steering_vectors = {}  # {model.layers.l: dimx1}
            for l, (layer_idx, hs_ts_sub_l) in enumerate(zip(layer_idxs, hs_ts_sub)):
                # layer and module (for steering) name
                layer_name = f'layer-{layer_idx + 1}'
                layer_module_name = f'model.layers.{layer_idx}'

                # best layer config
                best_config = [m for m in os.listdir(paths.model_dir) if layer_name in m]
                best_config = [t.replace('.pt', '').replace('best_', '') for t in best_config][0]
                best_config_dict = \
                    [{s.split('-')[0]: '-'.join(s.split('-')[1:]) for s in t.split('^^')} for t in [best_config]][0]
                best_hyper_dict = {k: v for k, v in best_config_dict.items() if k not in ['model', 'layer']}

                # decode config
                q_case = best_config_dict['q_case']
                batch_size = int(best_config_dict['batch_size'])
                optim_lr = float(best_config_dict['optim_lr'])
                sparsity_coeff = float(best_config_dict['sparsity_coeff'])
                qs_coeff = int(best_config_dict['qs_coeff'])
                sae_factor = int(best_config_dict['sae_factor'])
                tied_weights = best_config_dict['tied_weights'] == 'True'
                sae_name = best_config_dict['sae_name']

                # load SAE config
                sae_cfg = SAE_Config(exp_config, device=device_name, x_m=sae_factor, sparse_coeff=sparsity_coeff,
                                     tied_weights=tied_weights, qs_coeff=qs_coeff)

                model_fp = f'{paths.model_dir}best_{best_config}.pt'
                deltaS_fp = f'{paths.delta_dir}deltaS_{best_config}^^q_target_idx-{q_idx_to_perturb}^^s_change-{q_score_change}.pt'

                # Load SAE model
                model_sae = SAE4(sae_cfg).to(device_name)
                model_fp = f'{paths.model_dir}best_{best_config}.pt'
                model_sae.load_state_dict(torch.load(model_fp, map_location=torch.device(device_name)))

                # Load latent delta perturbation
                deltaS = get_perturb_delta(model_sae, deltaS_fp, q_idx_to_perturb=q_idx_to_perturb,
                                           score_change=q_score_change,
                                           device_name=device_name)

                # # Forward pass get original states
                # Get perturbed states
                _, _, h_rec_perturbed = model_sae.infer(hs_ts_sub_l.unsqueeze(0), delta_s=deltaS,
                                                        p_force=p_force)

                # store pertubation vectors
                steering_vectors[layer_module_name] = h_rec_perturbed.type(my_dtype)

            # %% Steer hidden states with steering vectors - 2nd pass
            for str_mlt in steer_mlt_set:
                steer_config = SteerConfig(layer_ids=layer_idxs, steering_vectors=steering_vectors, device='mps',
                                           multiplier=str_mlt, run_gen=False, sample_text=False,
                                           perturb_input_only=True, n_tokens=1)
                steer_hs = SteerHiddenState(steer_config, model, tokenizer)
                steer_hs.steer(model, sub_qs_pairs, device_name, return_org=False)

                logits_perturbed = steer_hs.logits
                label_logits_perturbed = logits_perturbed[:, label_ids].squeeze(-1).detach().cpu().type(
                    torch.float32)
                label_probs_perturbed = F.softmax(label_logits_perturbed, dim=-1).numpy()[0, :]

                sampled_perturbed_labels = np.random.choice(sample_config.label_letters, size=sample_config.nSamples,
                                                            p=label_probs_perturbed)
                sampled_perturbed_scores = [sample_config.label_scores[sl] for sl in sampled_perturbed_labels]
                sampled_perturbed_responses = [sample_config.q_responses[sl] for sl in sampled_perturbed_labels]

                # Save and sample from logits after steering
                tmp_dict = {'sub': sample_config.subj,
                            'sample_ts': [f'{sample_ts}_{s}' for s in range(sample_config.nSamples)],
                            'question': sample_config.which_q,
                            'score': sampled_perturbed_scores, 'response': sampled_perturbed_responses,
                            'model': sample_config.model_name,
                            'latent_q_score_change': q_score_change, 'latent_p_force': p_force,
                            'q_to_perturb': f'{q_idx_to_perturb + 1}', 'hs_steer_mlt': str_mlt,
                            'instr_name': sample_config.instr_name, 'qs': sample_config.qs_name,
                            'label_perm': ''.join(sample_config.label_letters),
                            'nSamples': sample_config.nSamples} | best_hyper_dict
                tmp_pd = pd.DataFrame(tmp_dict)

                tmp_logits_dict = {'sub': sample_config.subj, 'sample_ts': sample_ts,
                                   'question': sample_config.which_q,
                                   'logits': label_logits_perturbed[0], 'probs': label_probs_perturbed,
                                   'latent_q_score_change': q_score_change, 'latent_p_force': p_force,
                                   'q_to_perturb': f'{q_idx_to_perturb + 1}', 'hs_steer_mlt': str_mlt,
                                   'label_letters': sample_config.label_letters,
                                   'qs_labels': sample_config.qs_labels,
                                   'label_scores': sample_config.q_scores, 'model': sample_config.model_name,
                                   'instr_name': sample_config.instr_name, 'qs': sample_config.qs_name,
                                   'label_perm': ''.join(sample_config.label_letters),
                                   'nSamples': sample_config.nSamples} | best_hyper_dict
                tmp_logits_pd = pd.DataFrame(tmp_logits_dict)

                perturbation_config_dict = {'latent_q_score_change': q_score_change,
                                            'latent_p_force': p_force,
                                            'q_to_perturb': f'{q_idx_to_perturb + 1}',
                                            'hs_steer_mlt': str_mlt}
                perturbation_config = '^^'.join([f'{k}-{v}' for k, v in perturbation_config_dict.items()])

                tmp_fname = f"{sample_config.sample_path}{sample_config.subj}^^{sample_config.which_q}^^{''.join(sample_config.label_letters)}^^{sample_config.model_name_rp}^^{perturbation_config}"
                # hs_fname = f"{tmp_fname}_hidden_states_s-ts-{sample_ts}0.pt"
                logits_fname = f"{tmp_fname}_logits_s-ts-{sample_ts}.csv"
                responses_fname = f"{tmp_fname}_responses_s-ts-{sample_ts}.csv"

                tmp_pd.to_csv(f"{responses_fname}", index=False)
                tmp_logits_pd.to_csv(f"{logits_fname}", index=False)

            sample_config.get_remaining_samples(printMe=False, pert_config_len=len(perturbation_config_list))

        del model_sae, hs_ts_sub, hs_ts_sub_l
        flush()
    flush()
del model
flush()
