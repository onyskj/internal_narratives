# %% Import libraries and load data

import math

import numpy as np
import pandas as pd
from transformers import pipeline

from _objects.configs import *
from _objects.qs_maps import phq9_qs_map
from _utils.utils import percentile

task_versions = ['v4', 'v4_d', 'v4_dd', 'v4_ddd']
openq_times = {'v4': 94, 'v4_d': 94, 'v4_dd': 94, 'v4_ddd': 94}

bools = Bools()

device_name = 'mps'
study_name = 'a_open_qs'
data_dir = 'task_data/'
data_path = f'data/{study_name}/{data_dir}'
data_path_comb = data_path + 'combined/'
Path(f"{data_path_comb}").mkdir(parents=True, exist_ok=True)

bools.saveMe = False
# bools.saveMe = True
bools.loadMe = True
# bools.loadMe = False
bools.run_sentiment = False
# %% Combine open question data
store_openq_dfs = []
for task_version in task_versions:
    file_path = f"{data_path}/qs-structure-phq9-{task_version}/processed/openq_data.csv"
    openq_data_pd = pd.read_csv(file_path)
    openq_data_pd['sub'] = openq_data_pd['sub'] + '_' + task_version
    if task_version == 'v1':
        col_ok = ~(openq_data_pd.columns.str.contains('na_') | openq_data_pd.columns.str.contains('timeout_'))
    else:
        col_ok = ~(openq_data_pd.columns.str.contains('is_empty_') | openq_data_pd.columns.str.contains('timeout_'))
    openq_data_pd = openq_data_pd.iloc[:, col_ok]
    openq_data_pd.iloc[:, openq_data_pd.columns.str.contains('rt_')] = openq_data_pd.iloc[
        :, openq_data_pd.columns.str.contains('rt_')].fillna(openq_times[task_version] * 1000)
    store_openq_dfs.append(openq_data_pd)
openq_data = pd.concat(store_openq_dfs).reset_index(drop=True)
openq_data.iloc[:, :15] = openq_data.iloc[:, :15].fillna('')
openq_data['task_version'] = openq_data['task_version'].str.replace('qs-structure-phq9-', '')

del store_openq_dfs, openq_data_pd
if bools.saveMe:
    openq_data.to_csv(f'{data_path_comb}openq_data.csv', index=False)

# %% PHQ9 questionnaire
phq9_cols = ['sub', 'total', 'phq9_rt', 'task_version'] + ['phq9_q' + str(q) for q in range(1, 10)] + [
    'phq9_q' + str(q) + 's' for q in range(1, 10)]
store_phq9_dfs = []
for task_version in task_versions:
    file_path = f"{data_path}qs-structure-phq9-{task_version}/processed/phq9_data.csv"
    phq9_data_pd = pd.read_csv(file_path)[phq9_cols]
    store_phq9_dfs.append(phq9_data_pd)
phq9_data = pd.concat(store_phq9_dfs).reset_index(drop=True)
phq9_data['task_version'] = phq9_data['task_version'].str.replace('qs-structure-phq9-', '')
phq9_data['phq9_rt'] /= 1000
phq9_data.insert(2, 'q_dur', phq9_data['phq9_rt'] / 10)
phq9_data['sub'] += '_' + phq9_data['task_version']
if bools.saveMe:
    phq9_data.to_csv(f'{data_path_comb}/phq9_data.csv', index=False)

phq9_val_mean_pd = (phq9_data.groupby(['task_version'])[['phq9_rt', 'q_dur']].agg(
    ['mean', 'median', 'std', 'max', 'min', percentile(0.05), percentile(0.1), percentile(0.90),
     percentile(0.95)]).round(2))
# print(phq9_val_mean_pd)

# %% GAD7 questionnaire
gad7_cols = ['sub', 'total', 'gad7_rt', 'task_version'] + ['gad7_q' + str(q) for q in range(1, 8)] + [
    'gad7_q' + str(q) + 's' for q in range(1, 8)]
store_gad7_dfs = []
for task_version in task_versions:
    if task_version != 'v1':
        file_path = f"{data_path}/qs-structure-phq9-{task_version}/processed/gad7_data.csv"
        gad7_data_pd = pd.read_csv(file_path)[gad7_cols]
        store_gad7_dfs.append(gad7_data_pd)
gad7_data = pd.concat(store_gad7_dfs).reset_index(drop=True)[gad7_cols]
gad7_data['task_version'] = gad7_data['task_version'].str.replace('qs-structure-phq9-', '')
gad7_data['gad7_rt'] /= 1000
gad7_data['sub'] += '_' + gad7_data['task_version']
gad7_data.insert(2, 'q_dur', gad7_data['gad7_rt'] / 10)
if bools.saveMe:
    gad7_data.to_csv(f'{data_path_comb}/gad7_data.csv', index=False)

gad7_val_mean_pd = (gad7_data.groupby(['task_version'])[['gad7_rt', 'q_dur']].agg(
    ['mean', 'median', 'std', 'max', 'min', percentile(0.05), percentile(0.1), percentile(0.90),
     percentile(0.95)]).round(2))
# print(gad7_val_mean_pd)

# %% SDS questionnaire
sds_cols = ['sub', 'total', 'sds_rt', 'task_version'] + ['sds_q' + str(q) for q in range(1, 21)] + [
    'sds_q' + str(q) + 's' for q in range(1, 21)]
store_sds_dfs = []
for task_version in task_versions:
    if task_version != 'v1' and 'v2' not in task_version:
        file_path = f"{data_path}/qs-structure-phq9-{task_version}/processed/sds_data.csv"
        sds_data_pd = pd.read_csv(file_path)[sds_cols]
        store_sds_dfs.append(sds_data_pd)
sds_data = pd.concat(store_sds_dfs).reset_index(drop=True)[sds_cols]
sds_data['task_version'] = sds_data['task_version'].str.replace('qs-structure-phq9-', '')
sds_data['sds_rt'] /= 1000
sds_data.insert(2, 'q_dur', sds_data['sds_rt'] / 10)
sds_data['sub'] += '_' + sds_data['task_version']
if bools.saveMe:
    sds_data.to_csv(f'{data_path_comb}/sds_data.csv', index=False)

sds_val_mean_pd = (sds_data.groupby(['task_version'])[['sds_rt', 'q_dur']].agg(
    ['mean', 'median', 'std', 'max', 'min', percentile(0.05), percentile(0.1), percentile(0.90),
     percentile(0.95)]).round(2))
# print(sds_val_mean_pd)

# %% Level 1 closed
lvl1_closed_cols = ['sub', 'total', 'lvl1_closed_rt', 'task_version'] + ['lvl1_closed_q' + str(q) for q in
                                                                         range(1, 2)] + ['lvl1_closed_q' + str(q) + 's'
                                                                                         for q in range(1, 2)]
store_lvl1_closed_dfs = []
for task_version in task_versions:
    if task_version != 'v1':
        file_path = f"{data_path}qs-structure-phq9-{task_version}/processed/lvl1_closed_data.csv"
        lvl1_closed_data_pd = pd.read_csv(file_path)[lvl1_closed_cols]
        store_lvl1_closed_dfs.append(lvl1_closed_data_pd)
lvl1_closed_data = pd.concat(store_lvl1_closed_dfs).reset_index(drop=True)[lvl1_closed_cols]

lvl1_closed_data['task_version'] = lvl1_closed_data['task_version'].str.replace('qs-structure-phq9-', '')
lvl1_closed_data['lvl1_closed_rt'] /= 1000
lvl1_closed_data.insert(2, 'q_dur', lvl1_closed_data['lvl1_closed_rt'] / 10)
lvl1_closed_data['sub'] += '_' + lvl1_closed_data['task_version']
if bools.saveMe:
    lvl1_closed_data.to_csv(f'{data_path_comb}/lvl1_closed_data.csv', index=False)

lvl1_closed_val_mean_pd = (lvl1_closed_data.groupby(['task_version'])[['lvl1_closed_rt', 'q_dur']].agg(
    ['mean', 'median', 'std', 'max', 'min', percentile(0.05), percentile(0.1), percentile(0.90),
     percentile(0.95)]).round(2))
# print(lvl1_closed_val_mean_pd)

# %% Level 2 closed
lvl2_closed_cols = ['sub', 'total', 'lvl2_closed_rt', 'task_version'] + ['lvl2_closed_q' + str(q) for q in
                                                                         range(1, 4)] + ['lvl2_closed_q' + str(q) + 's'
                                                                                         for q in range(1, 4)]
store_lvl2_closed_dfs = []
for task_version in task_versions:
    if task_version != 'v1':
        file_path = f"{data_path}qs-structure-phq9-{task_version}/processed/lvl2_closed_data.csv"
        lvl2_closed_data_pd = pd.read_csv(file_path)[lvl2_closed_cols]
        store_lvl2_closed_dfs.append(lvl2_closed_data_pd)
lvl2_closed_data = pd.concat(store_lvl2_closed_dfs).reset_index(drop=True)[lvl2_closed_cols]

lvl2_closed_data['task_version'] = lvl2_closed_data['task_version'].str.replace('qs-structure-phq9-', '')
lvl2_closed_data['lvl2_closed_rt'] /= 1000
lvl2_closed_data.insert(2, 'q_dur', lvl2_closed_data['lvl2_closed_rt'] / 10)
lvl2_closed_data['sub'] += '_' + lvl2_closed_data['task_version']
if bools.saveMe:
    lvl2_closed_data.to_csv(f'{data_path_comb}/lvl2_closed_data.csv', index=False)

lvl2_closed_val_mean_pd = (lvl2_closed_data.groupby(['task_version'])[['lvl2_closed_rt', 'q_dur']].agg(
    ['mean', 'median', 'std', 'max', 'min', percentile(0.05), percentile(0.1), percentile(0.90),
     percentile(0.95)]).round(2))
# print(lvl2_closed_val_mean_pd)

# %% Combine subject data datetime
store_sub_dfs = []
for task_version in task_versions:
    file_path = f"{data_path}qs-structure-phq9-{task_version}/processed/sub_data.csv"
    sub_data_pd = pd.read_csv(file_path)
    sub_data_pd['sub'] = sub_data_pd['sub'] + '_' + task_version
    sub_data_pd = sub_data_pd.loc[:, ['sub', 'task_version', 'date_time']]
    sub_data_pd['date_time'] = sub_data_pd['date_time'].astype('datetime64[ns]')
    sub_data_pd['hour'] = sub_data_pd['date_time'].dt.hour + (sub_data_pd['date_time'].dt.minute / 60).round(0)
    sub_data_pd['day'] = sub_data_pd['date_time'].dt.weekday + 1
    store_sub_dfs.append(sub_data_pd)
sub_data = pd.concat(store_sub_dfs).reset_index(drop=True)
sub_data.iloc[:, :15] = sub_data.iloc[:, :15].fillna('')
sub_data['task_version'] = sub_data['task_version'].str.replace('qs-structure-phq9-', '')
del store_sub_dfs, sub_data_pd
if bools.saveMe:
    sub_data.to_csv(f'{data_path_comb}sub_data.csv', index=False)

# %% Calcuate open-ended sentiment and save to long df
# Reload data
phq9_data = pd.read_csv(f"{data_path_comb}/phq9_data.csv")
lvl1_closed_data = pd.read_csv(f"{data_path_comb}/lvl1_closed_data.csv")
lvl2_closed_data = pd.read_csv(f"{data_path_comb}/lvl2_closed_data.csv")
openq_data = pd.read_csv(f"{data_path_comb}/openq_data.csv")
col_ok = ~openq_data.columns.str.contains('catch')
openq_data = openq_data.iloc[:, col_ok]

# Long format
openq_data_long = openq_data.melt(id_vars=['sub', 'task_version'], value_name='response')
openq_data_long['type'] = 'response'
openq_data_long['question'] = openq_data_long['variable'].str.replace('rt_', '').str.replace('_word_rate', '')
openq_data_long.loc[openq_data_long['variable'].str.contains('rt_'), 'type'] = 'rt'
openq_data_long['spec_level'] = 'gen'
text_filter = openq_data_long['type'] == 'response'
openq_data_long.loc[text_filter, 'response'] = openq_data_long.loc[text_filter, 'response'].astype(str)
responses = list(openq_data_long.loc[text_filter, 'response'])

# Run sentiment
if bools.run_sentiment:
    sentiment_pipeline = pipeline("sentiment-analysis",
                                  # model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
                                  # model="distilbert/distilbert-base-uncased",
                                  model="siebert/sentiment-roberta-large-english", device=device_name)
    openq_data_long['sentiment'] = math.nan

    outputs = sentiment_pipeline(responses)
    scores = [out['score'] * {'POSITIVE': 1, 'NEGATIVE': -1}[out['label']] for out in outputs]
else:
    scores = np.random.uniform(-1, 1, len(responses))

# %% Combine and save
if not bools.loadMe:
    openq_data_long.loc[text_filter, 'sentiment'] = scores

    openq_data_long = openq_data_long.pivot(index=['sub', 'task_version', 'question', 'spec_level'],
                                            columns=['type']).reset_index()
    openq_data_long.columns = ['_'.join(col) if col[1] != '' else col[0] for col in openq_data_long.columns.values]
    openq_data_long.drop(['variable_response', 'variable_rt', 'sentiment_rt'], axis=1, inplace=True)
    openq_data_long.rename(
        columns={'response_response': 'response', 'response_rt': 'rt', 'sentiment_response': 'sentiment'}, inplace=True)
    openq_data_long['rt'] = round((openq_data_long['rt'] / 1000).astype(float), 3)
    # openq_data_long.insert(1, 'sub_id', openq_data_long['sub'] + '^' + openq_data_long['question'])
    openq_data_long['response'] = openq_data_long['response'].fillna('')
    openq_data_long['response'] = openq_data_long['response'].astype(str)

    openq_data_long.insert(len(openq_data_long.columns) - 1, 'word_count', openq_data_long['response'].apply(
        lambda x: float(len(x.strip().split(' '))) if x != "" else np.nan))
    openq_data_long.insert(len(openq_data_long.columns) - 1, 'word_rate',
                           openq_data_long['word_count'] / openq_data_long['rt'])

    # openq_data_long['qs_type'] = 'closed'
    openq_data_long['rel_q_name'] = str(math.nan)
    openq_data_long['score'] = math.nan
    for r, row in openq_data_long.iterrows():
        sub = row['sub']
        version = row['task_version']
        qsn_q = phq9_qs_map[row['question']] + 's'
        openq_data_long.loc[r, 'rel_q_name'] = qsn_q[:-1]
        if 'rep' in row['question']:
            openq_data_long.loc[r, 'qs_type'] = 'rep'
        if 'lvl1' in qsn_q:
            openq_data_long.loc[r, 'qs_type'] = 'lvl1'
            if version != 'v1':
                openq_data_long.loc[r, 'score'] = float(
                    lvl1_closed_data.loc[lvl1_closed_data['sub'] == sub, qsn_q].values[0])
        elif 'lvl2' in qsn_q:
            openq_data_long.loc[r, 'qs_type'] = 'lvl2'
            if version != 'v1':
                openq_data_long.loc[r, 'score'] = float(
                    lvl2_closed_data.loc[lvl2_closed_data['sub'] == sub, qsn_q].values[0])
        elif 'phq9' in qsn_q:
            openq_data_long.loc[r, 'qs_type'] = 'phq9'
            openq_data_long.loc[r, 'score'] = float(phq9_data.loc[phq9_data['sub'] == sub, qsn_q].values[0])

    openq_data_long_stats = \
        openq_data_long[~(openq_data_long['question'] == 'rep_lvl2_q1')].groupby(['sub', 'task_version', 'qs_type'],
                                                                                 dropna=False, as_index=False)[
            ['sentiment', 'score', 'word_count', 'word_rate', 'rt']].agg(['mean', 'sum'])
    openq_data_long_stats.columns = ['_'.join(col) if col[1] != '' else col[0] for col in openq_data_long_stats.columns]
    openq_data_long_stats.loc[openq_data_long_stats['score_mean'].isna(), 'score_sum'] = math.nan
    openq_data_long_stats.drop(columns=['score_mean', 'word_count_sum', 'word_rate_sum', 'rt_sum'], inplace=True)
    openq_data_long = openq_data_long[openq_data_long['task_version'].isin(task_versions)]
    openq_data_long_stats = openq_data_long_stats[openq_data_long_stats['task_version'].isin(task_versions)]

if bools.saveMe:
    openq_data_long.to_csv(f'{data_path_comb}/openq_data_long.csv', index=False)
    openq_data_long_stats.to_csv(f'{data_path_comb}/openq_data_long_stats.csv', index=False)

if bools.loadMe:
    openq_data_long_stats = pd.read_csv(f'{data_path_comb}/openq_data_long_stats.csv')
    openq_data_long = pd.read_csv(f'{data_path_comb}/openq_data_long.csv')
