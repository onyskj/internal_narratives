# %% Import libraries and load data
import re

from textblob import TextBlob
from transformers import pipeline
import numpy as np

import pandas as pd

device_name = 'mps'

task_versions = ['v2', 'v2b', 'v3']

from _objects.configs import *
from _utils.utils import q1, q3, percentile, q2, write_to_tex
from _objects.data_configs import min_word_act_s3, min_word_recreate_s3, min_word_oq_s3, min_word_recall, \
    min_char_recall

report_vars = ReportVars()

bools = Bools()
paths = Paths(files_dir='', plots_subdir='', plots_subsubdir='')
id_cols = ['sub', 'condition', 'group', 'autobio']
sbin3_order = ['q33', 'm', 'q66']
# join_cols = id_cols + ['s_bin', 's_bin3']
join_cols = id_cols + ['s_bin', 's_bin3', 's_bin2']

# bools.runSentiment = True
bools.runSentiment = False
bools.saveMe = False
# bools.saveMe = True
bools.saveTex = False

study_name = 'c_mood_induction/'
paths.data_path = f'data/{study_name}task_data/'
paths.data_proc_dir = paths.data_path + 'combined/'
Path(f"{paths.data_proc_dir}").mkdir(parents=True, exist_ok=True)

# %% Process Mood induction texts
store_int_dfs = []
for task_version in task_versions:
    file_path = f"{paths.data_path}/qs-intervention-{task_version}/processed/int_data.csv"
    int_data_pd = pd.read_csv(file_path)
    int_data_pd = int_data_pd[int_data_pd['group'] == 'D']
    store_int_dfs.append(int_data_pd)
int_data = pd.concat(store_int_dfs).reset_index(drop=True)
int_data.insert(4, 'autobio', int_data['task_version'] == 'qs-intervention-v3')

text_cols = [c for c in int_data.columns.tolist() if 'responses_' in c]
cols_text_to_drop = [c for c in int_data.columns.tolist() if 'rts_' in c]
int_data.drop(columns=['task_version'] + cols_text_to_drop, inplace=True)

int_data[text_cols] = int_data[text_cols].replace(r'\s+\.', '.', regex=True)
int_data[text_cols] = int_data[text_cols].replace(r'\s+,', ', ', regex=True)
int_data[text_cols] = int_data[text_cols].replace(r'\n+,', ' ', regex=True)

bad_sub_int = []
bad_sub_rec = []
for col_text in text_cols:
    int_data[f'{col_text}_wc'] = int_data[col_text].str.split(' ').apply(lambda x: len(x) if type(x) == list else 0)
for col_text in text_cols:
    if 'act' in col_text:
        bad_sub_int += list(int_data[int_data[f'{col_text}_wc'] < min_word_act_s3]['sub'])
    else:
        bad_sub_rec += list(int_data[int_data[f'{col_text}_wc'] < min_word_recreate_s3]['sub'])

bad_sub_int = list(set(bad_sub_int))
bad_sub_rec = list(set(bad_sub_rec))
print('text bad sub int: ', len(bad_sub_int))
print('text bad sub rec: ', len(bad_sub_rec))
report_vars.sTwo_bad_sub_int = len(bad_sub_int)
report_vars.sTwo_bad_sub_rec = len(bad_sub_rec)

bad_sub_int = list(set(bad_sub_int + bad_sub_rec))
int_data.columns = int_data.columns.str.replace('responses_', '')

# %% Process Open-ended texts
cols_oq_to_drop = ['oq_mood_rt', 'oq_energy_rt', 'oq_pospert_rt']
cols_oq_text = ['oq_mood_text', 'oq_energy_text', 'oq_pospert_text']
store_openq_dfs = []
for task_version in task_versions:
    file_path = f"{paths.data_path}/qs-intervention-{task_version}/processed/openq_data.csv"
    openq_data_pd = pd.read_csv(file_path)
    openq_data_pd = openq_data_pd[openq_data_pd['group'] == 'D']
    store_openq_dfs.append(openq_data_pd)
openq_data = pd.concat(store_openq_dfs).reset_index(drop=True)
openq_data.insert(4, 'autobio', openq_data['task_version'] == 'qs-intervention-v3')
openq_data.drop(columns=['task_version'] + cols_oq_to_drop, inplace=True)

openq_data[cols_oq_text] = openq_data[cols_oq_text].replace(r'\s+\.', '.', regex=True)
openq_data[cols_oq_text] = openq_data[cols_oq_text].replace(r'\s+,', ', ', regex=True)
openq_data[cols_oq_text] = openq_data[cols_oq_text].replace(r'\n+,', ' ', regex=True)
bad_sub_oq = []

for col_oq_text in cols_oq_text:
    openq_data[f'{col_oq_text}_wc'] = openq_data[col_oq_text].str.split(' ').apply(
        lambda x: len(x) if type(x) == list else 0)

    bad_sub_oq += list(openq_data[openq_data[f'{col_oq_text}_wc'] < min_word_oq_s3]['sub'])

bad_sub_oq = list(set(bad_sub_oq))
report_vars.sTwo_bad_sub_oq = len(bad_sub_oq)
print('openq bad sub: ', len(bad_sub_oq))
report_vars.sTwo_bad_sub_oq_manual = 1
bad_sub_oq += ['sub109_v2b']  # manual - repeated only one words
openq_data.columns = openq_data.columns.str.replace('_text', '')
# %% Process phq9 data
store_phq9_dfs = []
for task_version in task_versions:
    file_path = f"{paths.data_path}qs-intervention-{task_version}/processed/phq9_data.csv"
    phq9_data_pd = pd.read_csv(file_path)  # [phq9_cols]
    phq9_data_pd = phq9_data_pd[phq9_data_pd['group'] == 'D']
    store_phq9_dfs.append(phq9_data_pd)
phq9_data = pd.concat(store_phq9_dfs).reset_index(drop=True)
phq9_data = phq9_data[phq9_data['group'] == 'D']
phq9_data.insert(4, 'autobio', phq9_data['task_version'] == 'qs-intervention-v3')
phq9_data.drop(columns=['task_version'], inplace=True)

# pre save numbers to tex
for cond, no in phq9_data.groupby(['autobio', 'condition'])['sub'].nunique().items():
    var_name = 'sTwo_raw_autobio' + '_'.join([str(el) for el in list(cond)])
    setattr(report_vars, var_name, no)
for cond, no in phq9_data.groupby(['condition'])['sub'].nunique().items():
    var_name = 'sTwo_raw' + '_' + cond  # .join([str(el) for el in list(cond)])
    setattr(report_vars, var_name, no)

# remove subjects with any missing phq9 score diffs
incomplete_phq9_sub = list(set(phq9_data[phq9_data.isna().any(axis=1)]['sub']))
print('incomplete phq9 sub: ', len(incomplete_phq9_sub))
report_vars.sTwo_incomplete_phq_sub = len(incomplete_phq9_sub)
phq9_data = phq9_data[~phq9_data['sub'].isin(incomplete_phq9_sub)]

# PHQ9 Totals
phq9_totals = phq9_data.groupby(id_cols, as_index=False)['score_b'].sum().rename(
    columns={'score_b': 's_total'})
phq9_totals['s_total'] = phq9_totals['s_total'] * 3

phq9_diff_data_wide = phq9_data.pivot(index=id_cols, columns='question',
                                      values='score_diff').reset_index()
phq9_diff_data_wide = pd.merge(phq9_diff_data_wide, phq9_totals, on=id_cols)

# Add phq9 bins (q1, m, q3 quantiles)
qtls = phq9_diff_data_wide['s_total'].apply({'q1': q1, 'q3': q3})
qtls2 = phq9_diff_data_wide['s_total'].apply({'q2': q2})
qtls3 = phq9_diff_data_wide['s_total'].apply({'q33': percentile(0.33), 'q66': percentile(0.66)})
phq9_diff_data_wide.insert(4, 's_bin', phq9_diff_data_wide['s_total'].apply(
    lambda x: 'q1' if x < qtls['q1'] else ('q3' if x > qtls['q3'] else 'm')))

phq9_diff_data_wide.insert(5, 's_bin3', phq9_diff_data_wide['s_total'].apply(
    lambda x: 'q33' if x < qtls3['q33'] else ('q66' if x > qtls3['q66'] else 'm')))

phq9_diff_data_wide.insert(6, 's_bin2', phq9_diff_data_wide['s_total'].apply(
    lambda x: 'l' if x <= qtls2['q2'] else ('h' if x > qtls2['q2'] else 'm')))

# Outliers for q2
pcols = ['phq9_q2']
bad_sub_phq9 = []
for (cond, autobio), g_df in phq9_diff_data_wide.groupby(['condition', 'autobio'])[['sub'] + pcols]:
    sig = g_df[pcols].std()
    mu = g_df[pcols].mean()
    tmp_thr = mu + 3 * sig
    tmp_sub_list = g_df[(g_df[pcols].abs() > tmp_thr).any(axis=1)]['sub'].to_list()
    bad_sub_phq9.extend(tmp_sub_list)
bad_sub_phq9 = list(set(bad_sub_phq9))
report_vars.sTwo_outlier_phq_sub = len(bad_sub_phq9)
print('outlier phq9 q2 change: ', len(bad_sub_phq9))

# %% Process mood data
store_mood_dfs = []
for task_version in task_versions[-1:]:
    file_path = f"{paths.data_path}qs-intervention-{task_version}/processed/mood_data.csv"
    mood_data_pd = pd.read_csv(file_path)  # [mood_cols]
    mood_data_pd = mood_data_pd[mood_data_pd['group'] == 'D']
    store_mood_dfs.append(mood_data_pd)
mood_data = pd.concat(store_mood_dfs).reset_index(drop=True)
mood_data.insert(4, 'autobio', mood_data['task_version'] == 'qs-intervention-v3')
mood_data.drop(columns=['task_version', 'question'], inplace=True)

# remove subjects with any missing mood data
incomplete_mood_sub = list(set(mood_data[mood_data.isna().any(axis=1)]['sub']))
print('incomplete mood subs: ', len(incomplete_mood_sub))
report_vars.sTwo_incomplete_mood_sub = len(incomplete_mood_sub)
mood_data = mood_data[~mood_data['sub'].isin(incomplete_mood_sub)]

bad_sub_mood = []
for (cond), g_df in mood_data.groupby(['condition'])[['sub', 'mood_diff']]:
    sig = g_df['mood_diff'].std()
    mu = g_df['mood_diff'].mean()
    tmp_thr = mu + 3 * sig
    tmp_sub_list = list(set(g_df[g_df['mood_diff'].abs() > tmp_thr]['sub']))
    bad_sub_mood.extend(tmp_sub_list)
bad_sub_mood = list(set(bad_sub_mood))
report_vars.sTwo_outlier_mood_sub = len(bad_sub_mood)
print('outlier mood sub: ', len(bad_sub_mood))

# %% Process recall data
cols_to_drop = [f'rts_recall{r + 1}' for r in range(3)]
cols_rt = [f'rts_recall{r + 1}' for r in range(3)]
cols_words = [f'responses_recall{r + 1}' for r in range(3)]

store_recall_dfs = []
for task_version in task_versions:
    file_path = f"{paths.data_path}/qs-intervention-{task_version}/processed/recall_data.csv"
    recall_data_pd = pd.read_csv(file_path)
    recall_data_pd = recall_data_pd[recall_data_pd['group'] == 'D']
    store_recall_dfs.append(recall_data_pd)
recall_data = pd.concat(store_recall_dfs).reset_index(drop=True)

recall_data.insert(4, 'autobio', recall_data['task_version'] == 'qs-intervention-v3')
recall_data.drop(columns=['task_version'], inplace=True)
non_rt_cols = recall_data.columns[~recall_data.columns.isin(cols_rt)]
non_word_cols = recall_data.columns[~recall_data.columns.isin(cols_words)]

recall_data_words = recall_data[non_rt_cols].melt(id_vars=id_cols, var_name='recall_time', value_name='words')
recall_data_words['recall_time'] = recall_data_words['recall_time'].str.replace('responses_', '')
recall_data_rts = recall_data[non_word_cols].melt(id_vars=id_cols, var_name='recall_time', value_name='rts')
recall_data_rts['recall_time'] = recall_data_rts['recall_time'].str.replace('rts_', '')

# Replace NaN's with empty string
recall_data_words.loc[recall_data_words.isna().any(axis=1), 'words'] = ''

# Remove non letter characters and split into array
regex = re.compile('[^a-zA-Z]')
recall_data_words['words'] = recall_data_words['words'].apply(
    lambda x: [regex.sub('', w) for w in x.split(', ')] if ',' in x else [regex.sub('', x)])

recall_data_words['words'] = recall_data_words['words'].apply(lambda x: [w for w in x if len(w) >= min_char_recall])

recall_data_words['n_words'] = recall_data_words['words'].apply(lambda x: len(x))

bad_sub_recall = list(set(recall_data_words[recall_data_words['n_words'] < min_word_recall]['sub']))
report_vars.sTwo_bad_recall_sub = len(bad_sub_recall)
report_vars.sTwo_bad_recallSentence_sub = 3
bad_sub_recall += ['sub111_v2b', 'sub166_v3', 'sub32_v2b']  # manual - writing a setnence rather than recall
print('recall bad sub: ', len(bad_sub_recall))

recall_data = pd.merge(recall_data_words, recall_data_rts, on=id_cols + ['recall_time'])

# %% Process Feedback data
store_feedback_dfs = []
for task_version in task_versions:
    file_path = f"{paths.data_path}qs-intervention-{task_version}/processed/feedback_data.csv"
    feedback_data_pd = pd.read_csv(file_path)
    feedback_data_pd = feedback_data_pd[feedback_data_pd['group'] == 'D']
    feedback_data_pd.insert(4, 'autobio', feedback_data_pd['task_version'] == 'qs-intervention-v3')
    feedback_data_pd.drop(columns=['task_version'], inplace=True)
    if task_version == 'v2':
        feedback_data_pd.drop(columns=['mood_change2'], inplace=True)
    feedback_data_pd_long = pd.melt(feedback_data_pd, id_vars=id_cols,
                                    value_name='score', var_name='feedback_q')
    store_feedback_dfs.append(feedback_data_pd_long)
feedback_data = pd.concat(store_feedback_dfs, axis=0).reset_index(drop=True)

# remove bad subjects

feedback_cols = ['shoes', 'sim_sit', 'mood_change_new', 'mood_change', 'demand']
feedback_data = feedback_data[feedback_data['feedback_q'].isin(feedback_cols)]
feedback_data.loc[:, 'feedback_q'] = feedback_data['feedback_q'].str.replace('mood_change_new', 'mood_change')


# %% merge dfs with phq9
phq9_data = pd.merge(phq9_diff_data_wide[join_cols], phq9_data, on=id_cols)
int_data = pd.merge(phq9_diff_data_wide[join_cols], int_data, on=id_cols)
openq_data = pd.merge(phq9_diff_data_wide[join_cols], openq_data, on=id_cols)
mood_data = pd.merge(phq9_diff_data_wide[join_cols + ['s_total']], mood_data, on=id_cols)
recall_data = pd.merge(phq9_diff_data_wide[join_cols + ['s_total']], recall_data, on=id_cols)
# %% Combine all bad subjects
phq9_data = phq9_data[
    ~phq9_data['sub'].isin(set(bad_sub_phq9 + bad_sub_int + bad_sub_mood + bad_sub_recall + bad_sub_oq))]
phq9_diff_data_wide = phq9_diff_data_wide[
    ~phq9_diff_data_wide['sub'].isin(set(bad_sub_phq9 + bad_sub_int + bad_sub_mood + bad_sub_recall + bad_sub_oq))]
int_data = int_data[~int_data['sub'].isin(bad_sub_phq9 + bad_sub_int + bad_sub_mood + bad_sub_recall + bad_sub_oq)]
openq_data = openq_data[
    ~openq_data['sub'].isin(bad_sub_phq9 + bad_sub_int + bad_sub_mood + bad_sub_recall + bad_sub_oq)]


mood_data = mood_data[
    ~mood_data['sub'].isin(set(bad_sub_mood + bad_sub_int + bad_sub_phq9 + bad_sub_recall + bad_sub_oq))]
recall_data = recall_data[
    ~recall_data['sub'].isin(bad_sub_recall + bad_sub_int + bad_sub_phq9 + bad_sub_mood + bad_sub_oq)]
sub_count = phq9_data.groupby(['autobio', 'condition'])['sub'].nunique()
print(sub_count)

print(phq9_diff_data_wide.groupby(['autobio', 'condition'])['s_total'].aggregate(['mean', 'std']))

phq9_data_q2_long = phq9_data[phq9_data['question'] == 'phq9_q2'].reset_index(drop=True)
phq9_data_q2_long = pd.merge(phq9_data_q2_long, phq9_totals, on=id_cols)
phq9_data_q2_long = phq9_data_q2_long.melt(id_vars=join_cols + ['s_total'], value_vars=['score_b', 'score_fu'],
                                           var_name='timepoint', value_name='score').reset_index()

for cond, no in sub_count.items():
    var_name = 'sTwo_final_autobio' + '_'.join([str(el) for el in list(cond)])
    setattr(report_vars, var_name, no)
for cond, no in phq9_data.groupby(['condition'])['sub'].nunique().items():
    var_name = 'sTwo_final' + '_' + cond  # .join([str(el) for el in list(cond)])
    setattr(report_vars, var_name, no)
report_vars.sTwo_finalN = sub_count.sum()
if bools.saveTex:
    write_to_tex(report_vars, overwrite=True)  # Get numbers to tex vars
# %% Save data apart from recall
if bools.saveMe:
    phq9_diff_data_wide.to_csv(f'{paths.data_proc_dir}phq9_diff_data_wide.csv', index=False)
    phq9_data.to_csv(f'{paths.data_proc_dir}phq9_data.csv', index=False)
    phq9_data_q2_long.to_csv(f'{paths.data_proc_dir}phq9_data_q2_long.csv', index=False)
    mood_data.to_csv(f'{paths.data_proc_dir}mood_data.csv', index=False)
    int_data.to_csv(f'{paths.data_proc_dir}int_data.csv', index=False)
    openq_data.to_csv(f'{paths.data_proc_dir}openq_data.csv', index=False)

# %% Calculate recall sentiment and save recall data
if bools.runSentiment:
    recall_data['avgSentiment'] = -100.0
    recall_scores = []
    sentiment_pipeline = pipeline("sentiment-analysis", model="siebert/sentiment-roberta-large-english",
                                  device=device_name)
    # for i, row in recall_data.iloc[:10, :].iterrows():
    for i, row in recall_data.iterrows():
        recall_words = row['words']
        recall_words = [str(TextBlob(w).correct()).lower() for w in recall_words]
        recall_words_bool = [(len(w) > 2) for w in recall_words]
        recall_words = [w.lower() for b, w in zip(recall_words_bool, recall_words) if b]
        outputs = sentiment_pipeline(recall_words)
        # outputs = [{'score':np.random.rand(),'label':['POSITIVE','NEGATIVE'][np.random.randint(0,2)]} for r in range(len(recall_words))]
        scores = [out['score'] * {'POSITIVE': 1, 'NEGATIVE': -1}[out['label']] for out in outputs]
        scores_avg = np.nanmean(scores)
        recall_data.loc[i, 'avgSentiment'] = scores_avg

    # % Calculate baseline and difference
    recall_data_wide = recall_data.pivot(index=join_cols + ['s_total'], columns='recall_time',
                                         values='avgSentiment').reset_index()
    recall_data_wide.columns = recall_data_wide.columns.str.replace('recall', 'avgSentiment')
    recall_data_wide['recall_baselineSent'] = (recall_data_wide['avgSentiment1'] + recall_data_wide[
        'avgSentiment2']) / 2
    recall_data_wide['recall_diffSent'] = recall_data_wide['avgSentiment3'] - recall_data_wide['recall_baselineSent']

    recall_data.to_csv(f'{paths.data_proc_dir}recall_data.csv', index=False)
    recall_data_wide.to_csv(f'{paths.data_proc_dir}recall_data_wide.csv', index=False)
else:
    recall_data_wide = pd.read_csv(f'{paths.data_proc_dir}recall_data_wide.csv')
    recall_data = pd.read_csv(f'{paths.data_proc_dir}recall_data.csv')

# %% Feedback data and summary linear reg
feedback_data_wide = feedback_data.pivot(index=id_cols, columns='feedback_q', values='score').reset_index()
feedback_data_wide = pd.merge(feedback_data_wide, phq9_diff_data_wide, on=id_cols).reset_index(drop=True)
feedback_data_wide = pd.merge(feedback_data_wide, recall_data_wide, on=id_cols).reset_index(drop=True)
feedback_data = feedback_data[
    ~feedback_data['sub'].isin(set(bad_sub_recall + bad_sub_int + bad_sub_phq9 + bad_sub_mood + bad_sub_oq))]

feedback_data_wide = feedback_data_wide[
    ~feedback_data_wide['sub'].isin(set(bad_sub_recall + bad_sub_int + bad_sub_phq9 + bad_sub_mood + bad_sub_oq))]
if bools.saveMe:
    feedback_data.to_csv(f'{paths.data_proc_dir}feedback_data.csv', index=False)
    feedback_data_wide.to_csv(f'{paths.data_proc_dir}feedback_data_wide.csv', index=False)

feedback_data_wide_mood = pd.merge(feedback_data_wide, mood_data, on=id_cols).reset_index(drop=True)
if bools.saveMe:
    feedback_data_wide_mood.to_csv(f'{paths.data_proc_dir}feedback_data_wide_mood.csv', index=False)
feedback_data_wide_mood['sub'].nunique()
feedback_data_wide['sub'].nunique()
