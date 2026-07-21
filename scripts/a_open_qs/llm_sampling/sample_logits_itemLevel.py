# %% Initlialise and load
import os
import random

import matplotlib
import pandas as pd
import torch.nn.functional as F
from tqdm import tqdm

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# set paths
study_name = 'a_open_qs'
analysis_path = 'llm_sampling/'
model = None
if os.uname()[0] == 'Darwin':  # if on mac
    matplotlib.use('Qt5Agg')
    device_name = 'mps'
    # device_name = 'cpu'
    model_name = 'gemma2-2b-it'
    # model_name = 'llama32-3b-it'
    model_names = ['gemma2-2b-it']  # model_names = ['gemma2-2b-it', 'llama32-3b-it']
else:  # if on gpu
    matplotlib.use('Agg')
    device_name = 'cuda'
    model_name = 'MistralOo'
    model_names = ['MistralOo', 'gemma2-2b-it', 'llama32-3b-it', 'gemma2-9b-it', 'llama31-8b-it']

from scripts.a_open_qs.llm_sampling.logit_utils import create_question_pairs_instr, setup_model, load_task_content, \
    get_all_question_pairs, get_sub_locs, get_openq_data, flush

from _objects.configs import *
from _objects.plot_config import *
from _objects.qs_maps import *
from _objects.model_configs import *

torch.set_grad_enabled(False)

# %% Set up paths and bools and other vars
bools = Bools()
pc = PlotConfig()
qs_config = QsConfig()
paths = Paths()
paths.files_dir = f'outputs/{study_name}/{analysis_path}files_logits/'
paths.files_data_dir = f'data/{study_name}/task_data/combined/'
paths.prompts_path = f'scripts/{study_name}/{analysis_path}prompts/'
paths.sub_path = f'scripts/{study_name}/{analysis_path}'

to_sample_qs = 'phq9'  # sampling PHQ9 only
task_versions = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']

# load openq and phq9 data
openq_data = pd.read_csv(f"{paths.files_data_dir}openq_data.csv")
openq_data = openq_data[openq_data['task_version'].isin(task_versions)]
phq9_data = pd.read_csv(f"{paths.files_data_dir}phq9_data.csv")
phq9_data = phq9_data[phq9_data['task_version'].isin(task_versions)]
phq9_names = [c for c in phq9_data.columns if 'phq9_q' in c]
phq9_data_long = pd.melt(phq9_data, id_vars=['sub'], value_vars=phq9_names, var_name='q_name')

# initalise LLM sampling config
for model_name in tqdm(model_names):
    print(f'Model: {model_name}')
    sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name=to_sample_qs, instr_name='instr3')
    end_idx = -1  # all subjects
    # end_idx = 3 # few subjects
    # sample_config.nSamples = 4
    # sample_config.batchSize = 1
    sample_config.nSamples = 50  # how many samples per subjects
    sample_config.batchSize = 1  # 20
    sample_config.save_states = True
    sample_config.gen_fname = 'gb'
    sample_config.permute_labels = False
    sample_config.label_letters = None
    # do_bucket = False

    label_letters = list(string.ascii_uppercase)[:qs_config.qs_n_lab[to_sample_qs]]
    q_scores = list(maps[to_sample_qs].values())
    sample_config.q_responses = {l: k for l, (k, v) in zip(label_letters, maps[to_sample_qs].items())}

    if sample_config.permute_labels:
        tmp_zip = list(zip(q_scores, label_letters))
        random.shuffle(tmp_zip)
        q_scores, label_letters = zip(*tmp_zip)
    sample_config.label_letters = label_letters
    sample_config.q_scores = q_scores
    sample_config.label_scores = {k: v for k, v in zip(label_letters, q_scores)}
    sample_config.qs_labels = [sample_config.q_responses[l] for l in sample_config.label_letters]
    # %% Load model and tokenizer
    if model is None:
        model, tokenizer = setup_model(sample_config)  # model = model.model

    # %% Load data
    instr_dict, open_qs_dict, closed_qs_dict = load_task_content(sample_config)
    oq_names = list(open_qs_dict.keys())  # + list(open_qs_rep_dict.keys())

    # preprocess openq data
    openq_data_long = get_openq_data(openq_data, sample_config)

    intro_prompt, oq_instr, open_qs_dict, closed_questions_dict, cq_preamble, qsn_questions_dict, cq_instr, qsn_preamble = create_question_pairs_instr(
        sample_config)

    question_pairs, question_pairs_formatted, _, _ = get_all_question_pairs(openq_data_long, sample_config, tokenizer)
    # %% Sample responses
    extra_save = False
    for sub in tqdm(list(question_pairs.keys())[0:end_idx]):
        sample_config.subj = sub
        # find token index locations for qs and answers
        sub_texts_to_find, sub_last_token_locs = get_sub_locs(openq_data_long, question_pairs_formatted, tokenizer,
                                                              sample_config)
        for k, v in sub_last_token_locs.items():
            for k2, v2 in v.items():
                if v2 == -1:
                    print(sub, k, k2, 'missing location')

        for which_q in tqdm(list(question_pairs[sub].keys())[0:end_idx]):
            # sample_ts = str(round(datetime.timestamp(datetime.now()) * 10000)) + '_'
            sample_ts = str(round(datetime.timestamp(datetime.now()) * 10000))
            print(sub, which_q)
            sample_config.save_states = True
            sample_config.which_q = which_q
            sample_config.get_remaining_samples()
            while not sample_config.currentFiles:
                sub_q_token_locs = sub_last_token_locs[sample_config.which_q]
                sub_qs_pairs = [question_pairs_formatted[sample_config.subj][sample_config.which_q]]

                inputs_ids = tokenizer(sub_qs_pairs, padding=True, return_tensors='pt', return_attention_mask=True).to(
                    device_name)

                model_output = model(inputs_ids.input_ids, attention_mask=inputs_ids.attention_mask,
                                     output_hidden_states=True)
                hs_ts = torch.stack(model_output.hidden_states)
                hs_ts_sub = torch.stack(
                    [hs_ts[:, :, loc, :] for loc in list(sub_q_token_locs.values()) + [hs_ts.shape[2] - 1]],
                    dim=2).squeeze(1)
                del hs_ts

                # get and process logits
                logits = model_output.logits[:, -1, :]

                label_ids = tokenizer(sample_config.label_letters, padding=True, return_tensors='pt',
                                      return_attention_mask=True).to(device_name)
                label_ids = label_ids.input_ids[:, 1:]

                label_logits = logits[:, label_ids].squeeze(-1).detach().cpu().type(torch.float32)
                label_probs = F.softmax(label_logits, dim=-1).numpy()[0, :]

                # save responses based on logits (extra step)
                sampled_labels = np.random.choice(sample_config.label_letters, size=sample_config.nSamples,
                                                  p=label_probs)
                sampled_scores = [sample_config.label_scores[sl] for sl in sampled_labels]
                sampled_responses = [sample_config.q_responses[sl] for sl in sampled_labels]

                # Save responses
                tmp_dict = {'sub': sample_config.subj,
                            'sample_ts': [f'{sample_ts}_{s}' for s in range(sample_config.nSamples)],
                            'question': sample_config.which_q, 'score': sampled_scores, 'response': sampled_responses,
                            'model': sample_config.model_name, 'instr_name': sample_config.instr_name,
                            'qs': sample_config.qs_name, 'label_perm': ''.join(sample_config.label_letters),
                            'nSamples': sample_config.nSamples}
                tmp_pd = pd.DataFrame(tmp_dict)

                tmp_logits_dict = {'sub': sample_config.subj, 'sample_ts': sample_ts, 'question': sample_config.which_q,
                                   'logits': label_logits[0], 'probs': label_probs,
                                   'label_letters': sample_config.label_letters, 'qs_labels': sample_config.qs_labels,
                                   'label_scores': sample_config.q_scores, 'model': sample_config.model_name,
                                   'instr_name': sample_config.instr_name, 'qs': sample_config.qs_name,
                                   'label_perm': ''.join(sample_config.label_letters),
                                   'nSamples': sample_config.nSamples}
                tmp_logits_pd = pd.DataFrame(tmp_logits_dict)

                tmp_fname = f"{sample_config.sample_path}{sample_config.subj}^^{sample_config.which_q}^^{''.join(sample_config.label_letters)}^^{sample_config.model_name_rp}"
                hs_fname = f"{tmp_fname}_hidden_states_s-ts-{sample_ts}0.pt"
                logits_fname = f"{tmp_fname}_logits_s-ts-{sample_ts}.csv"
                responses_fname = f"{tmp_fname}_responses_s-ts-{sample_ts}.csv"

                tmp_pd.to_csv(f"{responses_fname}", index=False)
                tmp_logits_pd.to_csv(f"{logits_fname}", index=False)
                torch.save(hs_ts_sub.clone(), hs_fname)
                flush()
                sample_config.get_remaining_samples()

    del model, tokenizer
    flush()
    model = None

# try:
#     os.system("sudo shutdown -h now")
# except:
#     print('shutdown issue')
