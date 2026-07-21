# Load libs and objects

import matplotlib
from tqdm import tqdm
import os
import pandas as pd
import torch

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
torch.set_grad_enabled(False)

model = None
if os.uname()[0] == 'Darwin':  # if on mac
    matplotlib.use('Agg')
    device_name = 'mps'
    model_name = 'gemma2-2b-it'
else:
    matplotlib.use('Agg')
    device_name = 'cuda'
    model_name = 'gemma2-9b-it'

from scripts.a_open_qs.llm_sampling.logit_utils import flush, setup_model
from scripts.c_mood_induction.ssae_scores.hs_utils import forward_pass_whs, texts_to_msg

from _objects.configs import *
from _objects.model_configs import *

bools = Bools()

study_name = 'c_mood_induction'
base_study_name = 'a_open_qs'
sampling_path = 'hs_sampling/'
base_sampling_path = 'llm_sampling/'

paths = Paths()
paths.sub_path = f'scripts/{base_study_name}/{base_sampling_path}'
paths.files_dir = f'outputs/{study_name}/{sampling_path}'
paths.data_path = f'data/{study_name}/task_data/combined'
# %% initalise LLM sampling config
to_sample_qs = 'phq9'
sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name=to_sample_qs, instr_name='none')
sample_config.nSamples = 4
sample_config.batchSize = 1
sample_config.save_states = True
sample_config.hsT = 20

sample_config.gen_fname = 'gb'
do_bucket = False

to_idx = -1
# to_idx = 5
# %% Load model and tokenizer
if model is None:
    model, tokenizer = setup_model(sample_config)
    model.to(device_name)

# %% Load intervention text data
int_data = pd.read_csv(f'{paths.data_path}/int_data.csv')
act_data = int_data[['sub', 'condition', 'group', 'act_0']]
act_data = act_data.rename(columns={'act_0': 'act_text'})
act_data['text'] = act_data['act_text'].apply(lambda x: x.strip())

# %% Load open text data and split into mood, energy, pospert
openq_data = pd.read_csv(f'{paths.data_path}/openq_data.csv')

mood_data = openq_data[['sub', 'condition', 'group', 'oq_mood']]
mood_data = mood_data.rename(columns={'oq_mood': 'mood_text'})
mood_data['text'] = mood_data['mood_text'].apply(lambda x: x.strip())

energy_data = openq_data[['sub', 'condition', 'group', 'oq_energy']]
energy_data = energy_data.rename(columns={'oq_energy': 'energy_text'})
energy_data['text'] = energy_data['energy_text'].apply(lambda x: x.strip())

pospert_data = openq_data[['sub', 'condition', 'group', 'oq_pospert']]
pospert_data = pospert_data.rename(columns={'oq_pospert': 'pospert_text'})
pospert_data['text'] = pospert_data['pospert_text'].apply(lambda x: x.strip())

texts_dict = {'act': act_data, 'pospert': pospert_data, 'mood': mood_data, 'energy': energy_data}
# %% Prepare prompts and sample hidden states
for text_name, text_data in tqdm(texts_dict.items()):
    # get prompts
    formatted_texts = texts_to_msg(texts_dict[text_name], sample_config, tokenizer, rem_tag=True)
    sample_config.batchSize = 1
    sample_config.tmpRemBatches = int(np.ceil((len(formatted_texts) / sample_config.batchSize)))

    # split subject texts into batches
    texts_batch_idx = [[b * sample_config.batchSize, (b + 1) * sample_config.batchSize] for b in
                       range(sample_config.tmpRemBatches)]
    texts_batches = [list(formatted_texts.items())[batch_idx[0]:batch_idx[1]] for batch_idx in texts_batch_idx]
    texts_batches = texts_batches[:to_idx]

    # forward pass and save hidden states
    for text_batch in tqdm(texts_batches):  # go through batche
        sample_ts = str(round(datetime.timestamp(datetime.now()) * 10000)) + '_'
        sub_list = [sub_text[0] for sub_text in text_batch]
        sub_texts = [sub_text[1] for sub_text in text_batch]
        hs_ts = forward_pass_whs(sub_texts, model, tokenizer, sample_config, device_name)

        ## Save hidden states
        paths.hs_path = f'{paths.files_dir}{text_name}/'
        Path(paths.hs_path).mkdir(parents=True, exist_ok=True)

        for sub, hs in zip(sub_list, hs_ts):
            hs_fname = f'{paths.hs_path}{sub}^^{sample_config.model_name_rp}^^hsT-{sample_config.hsT}^^{text_name}_text-hs.pt'
            torch.save(hs.clone(), hs_fname)
        del hs_ts
        flush()
