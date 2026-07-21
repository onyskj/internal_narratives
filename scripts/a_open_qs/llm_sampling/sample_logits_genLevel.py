# %% Initlialise and load
"""
    Code to sample response for pairwise generalisation
"""
import os
import random
import sys

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
    # model_name = 'gemma2-2b-it'
    model_names = ['gemma2-2b-it']
else:
    matplotlib.use('Agg')
    device_name = 'cuda'
    # model_name = 'MistralOo'
    # model_name = 'gemma2-2b-it'
    model_names = ['MistralOo', 'gemma2-2b-it', 'llama32-3b-it', 'gemma2-9b-it',
                   'llama31-8b-it']  # model_names = ['MistralOo', 'gemma2-2b-it', 'llama32-3b-it', 'gemma2-9b-it']

from scripts.a_open_qs.llm_sampling.logit_utils import setup_model, get_all_question_pairs_gen, get_sub_locs_gen, flush, \
    get_openq_data
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

# initalise LLM sampling config
context_qs = 'phq9'  # simply indicates to use PHQ9 open-ended response (currently the only option)
# which questionnaires to sample responses to
gen_qs_list = ['sds', 'phq9', 'gad7']
# gen_qs_list = ['gad7']
gen_qs_list_zip = {'phq9': True, 'sds': True, 'gad7': True}
gen_qs_list_zip = {k: v for k, v in gen_qs_list_zip.items() if k in gen_qs_list}

# Load open q data
openq_data_all = pd.read_csv(f"{paths.files_data_dir}openq_data.csv")
task_versions = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']
openq_data_all = openq_data_all[openq_data_all['task_version'].isin(task_versions)]

s_lim = {'l': 0, 'u': None}  # limit subject set
wq_lim = {'l': 0, 'u': None}  # limit context questions set
gq_lim = {'l': 0, 'u': None}  # limit predicted questions set
# s_lim = {'l': 0, 'u': 1}
# wq_lim = {'l': 0, 'u': 2}
# gq_lim = {'l': 0, 'u': None}
# %% Start sampling
try:
    for model_name in tqdm(model_names):
        print('Model:', model_name)
        sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name=context_qs, instr_name='instr3')
        sample_config.save_states = False
        sample_config.gen_fname = 'gb'
        sample_config.permute_labels = False
        sample_config.label_letters = None
        sample_config.nSamples = 50  # how many samples

        # %% Load model and tokenizer
        if model is None:
            model, tokenizer = setup_model(sample_config)
        # %% Loop through questionnaires and questions
        for to_sample_qs, to_zip in tqdm(gen_qs_list_zip.items()):  # questionnaire to answer
            print('Qs:', to_sample_qs)
            sample_config.gen_qs_name = to_sample_qs  # which questionnaire to sample responses to
            map_dict = maps[sample_config.gen_qs_name]

            sample_config.batchSize = 9  # 20 # batch size
            if model_name == 'gemma2-9b-it':
                sample_config.batchSize = 4  # 20

            # load multiple choice question data
            qs_data = pd.read_csv(f"{paths.files_data_dir}{to_sample_qs}_data.csv")
            qs_data = qs_data[qs_data['task_version'].isin(task_versions)]

            # process open q and prepare prompts
            openq_data_long = get_openq_data(openq_data_all, sample_config)
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

            # get all prompts
            question_pairs, question_pairs_formatted, questions_df = get_all_question_pairs_gen(openq_data_long,
                                                                                                sample_config,
                                                                                                tokenizer)

            for sub in tqdm(list(question_pairs.keys())[s_lim['l']:s_lim['u']]):  # loop subjects
                sample_config.subj = sub
                # find token index locations for qs and answers
                sub_texts_to_find, sub_last_token_locs = get_sub_locs_gen(openq_data_long, question_pairs_formatted,
                                                                          tokenizer, sample_config)
                # loop through which question as context
                for which_q in tqdm(list(question_pairs[sub].keys())[wq_lim['l']:wq_lim['u']]):
                    sample_config.which_q = which_q

                    # Checking how many questions left to sample and batch them accoridingly
                    gen_q_list = list(question_pairs[sub][which_q].keys())[gq_lim['l']:gq_lim['u']]
                    gen_q_list2 = []
                    for gen_q in gen_q_list:
                        sample_config.which_gen_q = gen_q
                        sample_config.get_remaining_samples(printMe=False)
                        if not sample_config.currentFiles:
                            gen_q_list2.append(gen_q)
                    gen_q_list = gen_q_list2

                    # Prepare and sample batches depending on how many q left
                    while len(gen_q_list) > 0:
                        sample_ts = str(round(datetime.timestamp(datetime.now()) * 10000))
                        # print('sampling')
                        sample_config.remBatches = int(np.ceil(len(gen_q_list) / sample_config.batchSize))
                        gen_q_batches = [gen_q_list[b * sample_config.batchSize:(b + 1) * sample_config.batchSize] for b
                                         in range(sample_config.remBatches)]

                        for gen_q_batch in gen_q_batches:
                            # print(gen_q_batch)
                            sub_qs_pairs = [question_pairs_formatted[sample_config.subj][sample_config.which_q][gen_q]
                                            for gen_q in gen_q_batch]

                            sub_q_token_locs = [sub_last_token_locs[sample_config.which_q][gen_q] for gen_q in
                                                gen_q_batch]
                            sub_q_token_locs_idx = [list(d.values()) for d in sub_q_token_locs]

                            inputs_ids = tokenizer(sub_qs_pairs, padding=True, return_tensors='pt',
                                                   return_attention_mask=True).to(device_name)

                            model_output = model(inputs_ids.input_ids, attention_mask=inputs_ids.attention_mask,
                                                 output_hidden_states=sample_config.save_states)

                            if sample_config.save_states:
                                hs_ts = torch.stack(model_output.hidden_states).permute(1, 0, 2, 3)
                                hs_ts_sub = []
                                for hs_tmp, loc in zip(hs_ts, sub_q_token_locs_idx):
                                    hs_ts_sub.append(hs_tmp[:, loc + [hs_ts.shape[2] - 1], :])
                                hs_ts_sub = torch.stack(hs_ts_sub)

                                del hs_ts, hs_tmp

                                for hs_ts_q, gen_q in zip(hs_ts_sub, gen_q_batch):
                                    # save hidden states
                                    sample_config.which_gen_q = gen_q
                                    tmp_fname = f"{sample_config.sample_path}{sample_config.subj}^^{sample_config.which_q}^^{sample_config.which_gen_q}^^{''.join(sample_config.label_letters)}^^{sample_config.model_name_rp}"
                                    hs_fname = f"{tmp_fname}_hidden_states_s-ts-{sample_ts}0.pt"
                                    torch.save(hs_ts_q.clone(), hs_fname)

                            # get and process logits
                            logits = model_output.logits[:, -1, :]
                            label_ids = tokenizer(sample_config.label_letters, padding=True, return_tensors='pt',
                                                  return_attention_mask=True).to(device_name)
                            label_ids = label_ids.input_ids[:, 1:]
                            label_logits_batch = logits[:, label_ids].squeeze(-1).detach().cpu().type(torch.float32)
                            label_probs_batch = F.softmax(label_logits_batch, dim=-1).numpy()

                            # save responses based on logits (extra step)
                            for label_probs, label_logits, gen_q in zip(label_probs_batch, label_logits_batch,
                                                                        gen_q_batch):
                                sample_config.which_gen_q = gen_q
                                sampled_labels = np.random.choice(sample_config.label_letters,
                                                                  size=sample_config.nSamples, p=label_probs)

                                sampled_scores = [sample_config.label_scores[sl] for sl in sampled_labels]
                                sampled_responses = [sample_config.q_responses[sl] for sl in sampled_labels]

                                tmp_label_scores = sample_config.q_scores

                                if sample_config.gen_qs_name in rev_lists.keys():
                                    q_idx = int(gen_q.split('_q')[-1])
                                    if q_idx in rev_lists[sample_config.gen_qs_name]:
                                        # Reverse scores if to be reversed
                                        sampled_scores = [min(map_dict.values()) + max(map_dict.values()) - tmp_score
                                                          for tmp_score in sampled_scores]
                                        tmp_label_scores = [min(map_dict.values()) + max(map_dict.values()) - tmp_score
                                                            for tmp_score in tmp_label_scores]

                                # Save responses
                                tmp_dict = {'sub': sample_config.subj,
                                            'sample_ts': [f'{sample_ts}_{s}' for s in range(sample_config.nSamples)],
                                            'question': sample_config.which_q,
                                            'question_gen': sample_config.which_gen_q, 'score': sampled_scores,
                                            'response': sampled_responses, 'model': sample_config.model_name,
                                            'instr_name': sample_config.instr_name, 'qs': sample_config.qs_name,
                                            'gen_qs': sample_config.gen_qs_name,
                                            'label_perm': ''.join(sample_config.label_letters),
                                            'nSamples': sample_config.nSamples}
                                tmp_pd = pd.DataFrame(tmp_dict)

                                tmp_logits_dict = {'sub': sample_config.subj, 'sample_ts': sample_ts,
                                                   'question': sample_config.which_q,
                                                   'question_gen': sample_config.which_gen_q, 'logits': label_logits,
                                                   'probs': label_probs, 'label_letters': sample_config.label_letters,
                                                   'qs_labels': sample_config.qs_labels,
                                                   'label_scores': tmp_label_scores, 'model': sample_config.model_name,
                                                   'instr_name': sample_config.instr_name, 'qs': sample_config.qs_name,
                                                   'gen_qs': sample_config.gen_qs_name,
                                                   'label_perm': ''.join(sample_config.label_letters),
                                                   'nSamples': sample_config.nSamples}
                                tmp_logits_pd = pd.DataFrame(tmp_logits_dict)

                                tmp_fname = f"{sample_config.sample_path}{sample_config.subj}^^{sample_config.which_q}^^{sample_config.which_gen_q}^^{''.join(sample_config.label_letters)}^^{sample_config.model_name_rp}"
                                logits_fname = f"{tmp_fname}_logits_s-ts-{sample_ts}.csv"
                                responses_fname = f"{tmp_fname}_responses_s-ts-{sample_ts}.csv"

                                tmp_pd.to_csv(f"{responses_fname}", index=False)
                                tmp_logits_pd.to_csv(f"{logits_fname}", index=False)

                        # Checking how many questions left to sample
                        gen_q_list2 = []
                        for gen_q in gen_q_list:
                            sample_config.which_gen_q = gen_q
                            sample_config.get_remaining_samples(printMe=False)
                            if not sample_config.currentFiles:
                                gen_q_list2.append(gen_q)

                        gen_q_list = gen_q_list2

        if not os.uname()[0] == 'Darwin':  # if not on mac
            del model, tokenizer
            flush()
            model = None
except KeyboardInterrupt:
    print('user interrupted')
    sys.exit(0)
except Exception as e:
    print(f"\n An unexpected code error occurred: {type(e).__name__}: {e}")
    if not os.uname()[0] == 'Darwin':  # if not on mac
        try:
            os.system("sudo shutdown -h now")
        except:
            print('shutdown issue')
    sys.exit(1)  # Exit with an error code
