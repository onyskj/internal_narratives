# %% Import and setup
import random
import re

import pandas as pd
from natsort import natsorted
from torch.utils.data import Dataset

from _objects.configs import *
from _objects.data_configs import min_word_oq_s2
from _objects.model_configs import *
from _utils.utils import write_to_tex

device_name = 'mps'
base_study_name = 'a_open_qs'
base_sampling_path = 'llm_sampling/'
study_name = 'b_ssae'

task_v = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']
common_tasks = 'v4'

paths = Paths()
paths.files_path = f'outputs/{base_study_name}/{base_sampling_path}files_logits/paired/ABCD/subjects/'
paths.base_data_path = f'data/{base_study_name}/task_data/combined/'
paths.data_path = f'data/{study_name}/'

report_vars = ReportVars()
bools = Bools()

# model_name_set = ['MistralOo', 'gemma2-9b-it', 'llama31-8b-it', 'gemma2-2b-it', 'llama32-3b-it']
model_name_set = ['gemma2-9b-it']
# model_name = 'gemma2-9b-it'

bools.do_small_data = False
# bools.do_small_data = True
# bools.createDataset = True
# bools.saveDataset = True
bools.createDataset = False
bools.saveDataset = False
bools.do_zscores = True
bools.read_list = True
# bools.writeTex = True
bools.writeTex = False
# bools.ind_qs = True
bools.ind_qs = False
ind_qs_fn = '_ind' if bools.ind_qs else ''

# all 9 questions
q_case = '9q'
tok_loc = ['oq_ans', 2]
qs_list = ['lvl3_q1', 'lvl3_q2', 'lvl3_q3', 'lvl3_q4', 'lvl3_q5', 'lvl3_q6', 'lvl3_q7', 'lvl3_q8']
phq9_q_names = ['phq9_q' + str(q + 1) + 's' for q in range(9)]


# %% Create classes and functions

# function to get file paths and subject list
def prep_data(qs_list):
    """
    Prepares and processes data for a given set of questions by loading, filtering, and
    performing necessary preprocessing operations on hidden state tensor files, PHQ-9 data,
    and open question responses. Also manages data splits and inclusion criteria for subjects.

    :return: A tuple containing preprocessed PHQ-9 data, paths to tensor files, list of subject
        identifiers, and filtered list of question identifiers.
    """

    # Load all tensor files of hidden states
    pt_files = []
    for root, dirs, files in os.walk(f"{paths.files_path}"):
        files = [file for file in files if
                 (sample_config.model_name_rp in file) and ('.pt' in file) and (re.search(common_tasks, file))]
        pt_files.extend(files)

    # select only questions of interest (phq9)
    if len(qs_list) > 0:
        pt_files = [f for f in pt_files if any([True for q in qs_list if "^^" + q in f])]

    # select only subset of subjects
    if bools.do_small_data:
        subs = natsorted(list(set([f.split('^^')[0] for f in pt_files])))[:30]
        pt_files = [f for f in pt_files if f.split('^^')[0] in subs]
    else:
        subs = natsorted(list(set([f.split('^^')[0] for f in pt_files])))

    qs = natsorted(list(set([f.split('^^')[1] for f in pt_files])))

    # Get all paths to hidden state files
    pt_file_paths = []
    for pt_file in pt_files:
        sub, q, label_pert, model = pt_file.split('^^')
        model = model.split('_hidden_states')[0]
        pt_file_path = f"{paths.files_path}{sub}/{q}/{model}/{pt_file}"
        pt_file_paths.append(pt_file_path)

    # % Prep phq and openq
    phq9_data = pd.read_csv(f"{paths.base_data_path}phq9_data.csv")[['sub', 'task_version'] + phq9_q_names]
    phq9_data = phq9_data[phq9_data['task_version'].isin(task_v)].reset_index(drop=True)

    # get nan subjects (with any missing)
    nan_phq9_subs = phq9_data[phq9_data.isna().any(axis=1)]['sub'].to_list()

    # z-score the scores (per question)
    if bools.do_zscores:
        phq9_data[phq9_q_names] = (phq9_data[phq9_q_names] - phq9_data[phq9_q_names].mean(axis=0)) / phq9_data[
            phq9_q_names].std(axis=0)

    # apply the inclusion criteria
    min_words = min_word_oq_s2
    openq_data_long = pd.read_csv(f'{paths.base_data_path}openq_data_long.csv')
    openq_data_long = openq_data_long[openq_data_long['question'].isin(qs)]
    openq_data_long = openq_data_long[openq_data_long['sub'].isin(subs)]
    openq_data_long = openq_data_long[openq_data_long['task_version'].isin(task_v)].reset_index(drop=True)
    openq_data_long = openq_data_long.replace(r'\s+\.', '.', regex=True)
    openq_data_long = openq_data_long.replace(r'\s+,', ', ', regex=True)
    openq_data_long = openq_data_long.replace(r'\n+,', ' ', regex=True)
    openq_data_long['response'] = openq_data_long['response'].astype(str)
    openq_data_long['n_words'] = openq_data_long['response'].apply(lambda x: len(x.split()))

    openq_data_long = openq_data_long[
        (openq_data_long['n_words'] >= min_words) & (~openq_data_long['sub'].isin(nan_phq9_subs))]
    sub_with_full_set = openq_data_long.groupby(['sub'])['question'].count() == len(qs_list)
    sub_with_full_set = [s for b, s in zip(sub_with_full_set, sub_with_full_set.index) if b]
    openq_data_long = openq_data_long[openq_data_long['sub'].isin(sub_with_full_set)]
    print('n sub full set', len(sub_with_full_set))
    print('n sub', len(openq_data_long['sub'].unique()))

    subs = openq_data_long['sub'].unique().tolist()
    report_vars.sSAE_nFinal = len(subs)
    if bools.writeTex:
        write_to_tex(report_vars, overwrite=False)
    qs_list = openq_data_long['question'].unique().tolist()

    # loads a pre-shuffled list of subject - for the same split of data across train, val, test
    if bools.read_list:
        with open(f'{paths.data_path}sub_list_{q_case}_random.txt', 'r') as f:
            # subs = random.shuffle(subs)
            subs = f.read().split('^')
    else:
        random.shuffle(subs)
        subs_list = '^'.join(subs)
        with open(f'{paths.data_path}sub_list_{q_case}_random.txt', 'w') as f:
            f.write(subs_list)

    return phq9_data, pt_file_paths, subs, qs_list


# Create dataset classes
class MetaDataset:
    """
    MetaDataset is responsible for preprocessing and managing dataset embeddings and labels.

    This class initializes and organizes data for multiple subjects by loading and processing their
    embeddings and associated PHQ9 questionnaire data. The goal is to compute normalized average
    embeddings and corresponding labels for each subject for subsequent modeling tasks.

    :ivar avg_features: A dictionary mapping subject identifiers to their normalized average embeddings.
    :ivar avg_labels: A dictionary mapping subject identifiers to their corresponding PHQ9 labels.
    :ivar subs: A list of subject identifiers processed for the dataset.
    """

    def __init__(self, device_name, qs_list, ind_qs=False):
        x_avg, ys = {}, {}
        xs = {}
        # get phq9 data, and tensor file paths, as well as pre-randomised, set list of subject
        phq9_data, pt_file_paths, subs, qs_list = prep_data(qs_list)

        # for each subject and each question, load hidden state and phq9 responses

        for sub in subs:
            sub_phq9 = list(phq9_data[phq9_data['sub'] == sub][phq9_q_names].values[0])
            sub_phq9 = torch.tensor(sub_phq9)
            sub_pts = []
            for q in qs_list:
                pt_file_path = [p for p in pt_file_paths if f'{sub}/{q}/{sample_config.model_name_rp}' in p]
                if len(pt_file_path) == 1:
                    pt_file_path = pt_file_path[0]
                    # load the embedding of the last token of the open-ended response
                    sub_q_pt = \
                        torch.load(f"{pt_file_path}", weights_only=True, map_location=torch.device(device_name)).type(
                            torch.FloatTensor)[
                            1 + layer_idx_start:, tok_loc[1], :]  # remve the embedding layer  as well

                    # normalise the embedding (length 1)
                    sub_q_pt /= torch.linalg.norm(sub_q_pt, axis=1, keepdims=True)
                    # print('sub q pt shape', sub_q_pt.shape)

                    sub_pts.append(sub_q_pt)

            # get the average and normalise
            sub_pts = torch.stack(sub_pts)
            # print('sub pts shape', sub_pts.shape)
            sub_avg_pt = sub_pts.mean(dim=0)
            # print('sub avg pts shape', sub_avg_pt.shape)
            sub_avg_pt /= torch.linalg.norm(sub_avg_pt, axis=1, keepdims=True)
            # print('sub avg pts norm shape', sub_avg_pt.shape)

            ys[sub] = sub_phq9
            if ind_qs:
                xs[sub] = sub_pts.permute(1, 0, 2)
                # print('xs shape', xs[sub].shape)
            else:
                if sub_avg_pt is not None:
                    x_avg[sub] = sub_avg_pt

        self.subs = subs
        self.avg_labels = ys
        if ind_qs:
            self.avg_features = xs
        else:
            self.avg_features = x_avg


# %% Create dataset with all subjects
for model_name in model_name_set:
    sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name='instr3')

    # create dataset_name
    dataset_fname = q_case
    if bools.do_zscores:
        dataset_fname += '_zs'
    dataset_fname += f'_{sample_config.model_name_sshort}{ind_qs_fn}'

    # only extract from middle layer onwards
    layer_idx_start = sample_config.L // 2

    # create and save hidden states and scores for phq9
    if bools.createDataset:
        meta_dataset = MetaDataset(device_name, qs_list, ind_qs=bools.ind_qs)
        if bools.saveDataset:
            torch.save(meta_dataset, f'{paths.data_path}/{dataset_fname}.pt')


# %% Data splitter class
# This used the pre-randomised dictinary of average embeddings and scores for each subject
# returns a subste of the dataset depending on whether it's train, val or test set
class MyDataset(Dataset):
    def __init__(self, dataset, i_start, i_end, layer_index, device):
        self.subs = dataset.subs[i_start:i_end]
        self.features = [dataset.avg_features[sub] for sub in self.subs]
        self.labels = [dataset.avg_labels[sub] for sub in self.subs]

        self.features = [f[layer_index].type(torch.float32) for f in self.features]
        if device == 'mps':
            self.features = [f.type(torch.float32) for f in self.features]
            self.labels = [l.type(torch.float32) for l in self.labels]

        # shuffle
        tmp_pairs = list(zip(self.features, self.labels, self.subs))
        random.shuffle(tmp_pairs)
        self.features, self.labels, self.subs = zip(*tmp_pairs)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]
