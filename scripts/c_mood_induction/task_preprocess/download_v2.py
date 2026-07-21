'''
Downloads data from firebase
'''
# %% Import libraries and load data
# import random
import json
import os
import pickle
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path

import firebase_admin
import numpy as np
# import types
import pandas as pd
from firebase_admin import credentials, firestore

with_ts = False
if with_ts:
    ts = '_' + str(round(datetime.timestamp(datetime.now()) * 10000))
else:
    ts = ''

# establish working directory
cwd = os.getcwd()
cwd_split = cwd.split('/')
base_task = 'qs_intervention/_tasks'
base_task_local = 'qs_intervention'
task_version = 'qs-intervention-v2'
task_subversion = 'b'
task_subversion = ''
cwd_base = '/'.join(cwd_split[:np.argwhere([p == "online_tasks" for p in cwd_split])[0][0] + 1])
os.chdir(f"{cwd_base}/{base_task}/{task_version}")

# save log to file
to_log = False

# %%
# establish connection and database
cred = credentials.Certificate("admin_sdk_key.json")
app = None
saveMe = True
try:
    app = firebase_admin.initialize_app(cred)
except:
    print('Issue logging in')
db = firestore.client()
db = db.collection('tasks').document(task_version + task_subversion)

# establish data paths
do_local = False
# do_local = True
if do_local:
    data_path = f"_data/{task_version}{task_subversion}/"
else:
    data_path = f"/Volumes/DATA/UCL/online_tasks/{base_task_local}/{task_version}/_data/{task_version}{task_subversion}/"

if to_log:
    Path(f"{data_path}_logs").mkdir(parents=True, exist_ok=True)
    with open(data_path + '_logs/log' + ts + '.txt', 'w') as f:
        f.write('')
    sys.stdout = open(data_path + '_logs/log' + ts + '.txt', 'wt')
# %% Set up column names for data frames
# common columns
pd_pre_columns = ['PID', 'UID', 'condition', 'group']
pd_post_columns = ['ST_ID', 'SE_ID', 'task_version', 'date', 'time', 'date_time']

# sub columns
sub_cols = pd_pre_columns + pd_post_columns + ['consented', 'completed', 'returned', 'code', 'attention_check1',
                                               'attention_check2', 'attention_check', 'attention_checks_bool',
                                               'warning_count', 'recent_task']

# check keys
doc_keys = ['PID', 'ST_ID', 'SE_ID', 'condition', 'group', 'task_version', 'date', 'time', 'consented', 'completed',
            'returned', 'code', 'attention_check1', 'attention_check2', 'attention_check', 'attention_checks_bool',
            'warning_count', 'recent_task']

# %%

feedback_vas_cols = [f"response_closed_q_feedback_{i}" for i in range(5)]
feedback_cols = feedback_vas_cols

# baseline and fu columns
b_phq9_acheck_i = 4
f_phq9_acheck_i = 7
baseline_mood_cols = ["responses_oq_baseline_0", "rts_oq_baseline_0", "submitted_oq_baseline_0",
                      "timeout_oq_baseline_0", "word_limit_ok_oq_baseline_0"]
baseline_energy_cols = ["responses_oq_baseline_1", "rts_oq_baseline_1", "submitted_oq_baseline_1",
                        "timeout_oq_baseline_1", "word_limit_ok_oq_baseline_1"]
baseline_phq9_cols = [f"response_phq9_baseline_{i}" for i in range(10) if i != b_phq9_acheck_i] + [
    f"rt_phq9_baseline_{i}" for i in range(10) if i != b_phq9_acheck_i]

baseline_recall_cols = ['responses_recall1', 'rts_recall1', 'timeout_recall1', 'word_list_1', 'responses_recall2',
                        'rts_recall2', 'timeout_recall2', 'word_list_2']

baseline_cols = baseline_phq9_cols + baseline_mood_cols + baseline_energy_cols + baseline_recall_cols

fu_oq_cols = ["responses_oq_pospert_0", "rts_oq_pospert_0", "submitted_oq_pospert_0", "timeout_oq_pospert_0",
              "word_limit_ok_oq_pospert_0"]
fu_phq9_cols = [f"response_phq9_fu_{i}" for i in range(10) if i != f_phq9_acheck_i] + [f"rt_phq9_fu_{i}" for i in
                                                                                       range(10) if
                                                                                       i != f_phq9_acheck_i]
fu_recall_cols = ['responses_recall3', 'rts_recall3', 'timeout_recall3']

fu_cols = fu_phq9_cols + fu_oq_cols + fu_recall_cols

# intervention columns
n_recreate = 4
act_cols = ['responses_act_0', 'rts_act_0', "submitted_act_0", "timeout_act_0", 'word_limit_ok_act_0']
recreate_cols = [f"responses_recreate_{i}" for i in range(n_recreate)] + [f"rts_recreate_{i}" for i in
                                                                          range(n_recreate)]
recreate_cols += [f"submitted_recreate_{i}" for i in range(n_recreate)] + [f"timeout_recreate_{i}" for i in
                                                                           range(n_recreate)] + [
                     f"word_limit_ok_recreate_{i}" for i in range(n_recreate)]
# %% Download all data
sub_rows = []
baseline_rows = []
fu_rows = []
feedback_rows = []
recreate_rows = []
act_rows = []

sub_ids = [s.id for s in db.collection('subjects').get()]
sub_pids = [db.collection('subjects').document(sub).get().to_dict()['PID'] for sub in sub_ids]

subs = pd.DataFrame({'UID': sub_ids, 'PID': sub_pids})

duplicates = subs.loc[subs['PID'].duplicated(), 'PID']
duplicates = subs.loc[subs['PID'].isin(duplicates), ['PID', 'UID']]
# data_path su
if len(duplicates) > 0:
    print('Duplicated ppt UIDs')
    print(duplicates)
else:
    for sub in sub_ids:
        print(f"\nUID: {sub}")
        Path(f"{data_path}raw{ts}/{sub}").mkdir(parents=True, exist_ok=True)

        # subject main document
        sub_doc = db.collection('subjects').document(sub).get().to_dict()

        # basic info
        # ensure sub doc keys are there
        for doc_key in doc_keys:
            if doc_key not in sub_doc.keys():
                sub_doc[doc_key] = np.nan
                print('\tmissing: ' + doc_key)

        pid = sub_doc['PID']
        stid = sub_doc['ST_ID']
        seid = sub_doc['SE_ID']
        date = sub_doc['date']
        time = sub_doc['time']

        print(f"\t--->PID: {pid}")
        try:
            date_time = datetime.strptime(date + ' ' + time, '%d/%m/%Y %H:%M:%S')
        except:
            date_time = ''

        # general data: uid, PID, STUDY and SESSION ID
        sub_row = {'PID': pid, 'UID': sub, 'ST_ID': stid, 'SE_ID': seid, 'condition': sub_doc['condition'],
                   'group': sub_doc['group'], 'task_version': sub_doc['task_version'], 'date': date, 'time': time,
                   'date_time': date_time, 'consented': sub_doc['consented'], 'completed': sub_doc['completed'],
                   'returned': sub_doc['returned'], 'code': sub_doc['code'],
                   'attention_check1': sub_doc['attention_check1'], 'attention_check2': sub_doc['attention_check2'],
                   'attention_check': sub_doc['attention_check'],
                   'attention_checks_bool': sub_doc['attention_checks_bool'], 'warning_count': sub_doc['warning_count'],
                   'recent_task': sub_doc['recent_task']}
        sub_rows.append(sub_row)

        sub_info = {'PID': pid, 'UID': sub, 'ST_ID': stid, 'SE_ID': seid, 'condition': sub_doc['condition'],
                    'group': sub_doc['group'], 'task_version': sub_doc['task_version'], 'date': date, 'time': time,
                    'date_time': date_time}

        # dump data
        doc_csv = None
        doc_json = None
        if 'z_dump_csv' in sub_doc.keys():
            doc_csv = pd.read_csv(StringIO(sub_doc['z_dump_csv']), sep=',')
            # save csv
            doc_csv.to_csv(f"{data_path}raw{ts}/{sub}/data_dump_{sub}.csv", index=False)
        if 'z_dump_json' in sub_doc.keys():
            doc_json = json.load(StringIO(sub_doc['z_dump_json']))
            # save json
            with open(f"{data_path}raw{ts}/{sub}/data_dump_{sub}.json", 'w') as f:
                json.dump(doc_json, f, ensure_ascii=False, indent=4)

        # baseline <===========

        sub_baseline_phq9 = db.collection('subjects').document(sub).collection('baseline').document(
            'phq9').get().to_dict()
        sub_baseline_mood = db.collection('subjects').document(sub).collection('baseline').document(
            'open_q_mood').get().to_dict()
        sub_baseline_energy = db.collection('subjects').document(sub).collection('baseline').document(
            'open_q_energy').get().to_dict()
        sub_baseline_recall = db.collection('subjects').document(sub).collection('baseline').document(
            'recall').get().to_dict()

        for baseline_phq9_key in baseline_phq9_cols:
            if baseline_phq9_key not in sub_baseline_phq9.keys():
                sub_baseline_phq9[baseline_phq9_key] = np.nan
                print('\t\tmissing: ' + baseline_phq9_key)

        for baseline_mood_key in baseline_mood_cols:
            if baseline_mood_key not in sub_baseline_mood.keys():
                sub_baseline_mood[baseline_mood_key] = np.nan
                print('\t\tmissing: ' + baseline_mood_key)
            else:
                if 'responses_' in baseline_mood_key:
                    sub_baseline_mood[baseline_mood_key] = ' '.join(sub_baseline_mood[baseline_mood_key])

        for baseline_energy_key in baseline_energy_cols:
            if baseline_energy_key not in sub_baseline_energy.keys():
                sub_baseline_energy[baseline_energy_key] = np.nan
                print('\t\tmissing: ' + baseline_energy_key)
            else:
                if 'responses_' in baseline_energy_key:
                    sub_baseline_energy[baseline_energy_key] = ' '.join(sub_baseline_energy[baseline_energy_key])

        for baseline_recall_key in baseline_recall_cols:
            if baseline_recall_key not in sub_baseline_recall.keys():
                sub_baseline_recall[baseline_recall_key] = np.nan
                print('\t\tmissing: ' + baseline_recall_key)
            else:
                if 'responses_' in baseline_recall_key:
                    sub_baseline_recall[baseline_recall_key] = ', '.join(sub_baseline_recall[baseline_recall_key])

        sub_baseline = sub_info | sub_baseline_phq9 | sub_baseline_mood | sub_baseline_energy | sub_baseline_recall
        baseline_rows.append(sub_baseline)

        # fu <===========
        sub_fu_phq9 = db.collection('subjects').document(sub).collection('fu').document('phq9').get().to_dict()
        sub_fu_oq_pospert = db.collection('subjects').document(sub).collection('fu').document(
            'open_q_pospert').get().to_dict()
        sub_fu_recall = db.collection('subjects').document(sub).collection('fu').document('recall').get().to_dict()

        for fu_phq9_key in fu_phq9_cols:
            if fu_phq9_key not in sub_fu_phq9.keys():
                sub_fu_phq9[fu_phq9_key] = np.nan
                print('\t\tmissing: ' + fu_phq9_key)

        for fu_oq_pospert_key in fu_oq_cols:
            if fu_oq_pospert_key not in sub_fu_oq_pospert.keys():
                sub_fu_oq_pospert[fu_oq_pospert_key] = np.nan
                print('\t\tmissing: ' + fu_oq_pospert_key)
            else:
                if 'responses_' in fu_oq_pospert_key:
                    sub_fu_oq_pospert[fu_oq_pospert_key] = ' '.join(sub_fu_oq_pospert[fu_oq_pospert_key])

        for fu_recall_key in fu_recall_cols:
            if fu_recall_key not in sub_fu_recall.keys():
                sub_fu_recall[fu_recall_key] = np.nan
                print('\t\tmissing: ' + fu_recall_key)
            else:
                if 'responses_' in fu_recall_key:
                    sub_fu_recall[fu_recall_key] = ', '.join(sub_fu_recall[fu_recall_key])

        sub_fu = sub_info | sub_fu_phq9 | sub_fu_oq_pospert | sub_fu_recall
        fu_rows.append(sub_fu)

        # intervention <===========
        sub_int_act = db.collection('subjects').document(sub).collection('intervention').document('act').get().to_dict()
        sub_int_recreate = db.collection('subjects').document(sub).collection('intervention').document(
            'recreate').get().to_dict()

        for recreate_key in recreate_cols:
            if recreate_key not in sub_int_recreate.keys():
                sub_int_recreate[recreate_key] = np.nan
                print('\t\tmissing: ' + recreate_key)
            else:
                if 'responses_' in recreate_key:
                    sub_int_recreate[recreate_key] = ' '.join(sub_int_recreate[recreate_key])

        sub_int_recreate = sub_info | sub_int_recreate

        for act_key in act_cols:
            if act_key not in sub_int_act.keys():
                sub_int_act[act_key] = np.nan
                print('\t\tmissing: ' + act_key)
            else:
                if 'responses_' in act_key:
                    sub_int_act[act_key] = ' '.join(sub_int_act[act_key])

        sub_int_act = sub_info | sub_int_act

        recreate_rows.append(sub_int_recreate)
        act_rows.append(sub_int_act)

        # feedback <===========
        sub_feedback_vas = db.collection('subjects').document(sub).collection('feedback').document(
            'closed_q').get().to_dict()

        for feedback_vas_key in feedback_vas_cols:
            if feedback_vas_key not in sub_feedback_vas.keys():
                sub_feedback_vas[feedback_vas_key] = np.nan
                print('\t\tmissing: ' + feedback_vas_key)

        sub_feedback = sub_info | sub_feedback_vas
        feedback_rows.append(sub_feedback)

        # save raw data
        if saveMe:
            # save sub
            with open(f"{data_path}raw{ts}/{sub}/sub_doc_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_row, f)

            # save baseline
            with open(f"{data_path}raw{ts}/{sub}/baseline_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_baseline, f)

            # save fu
            with open(f"{data_path}raw{ts}/{sub}/fu_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_fu, f)

            # save int
            with open(f"{data_path}raw{ts}/{sub}/int_recreate_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_int_recreate, f)
            with open(f"{data_path}raw{ts}/{sub}/int_act_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_int_act, f)

            # save feedback
            with open(f"{data_path}raw{ts}/{sub}/feedback_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_feedback, f)

    # %% Save to csv
    Path(f"{data_path}all{ts}").mkdir(parents=True, exist_ok=True)
    sub_pd = pd.DataFrame(sub_rows)[sub_cols]
    baseline_pd = pd.DataFrame(baseline_rows)[pd_pre_columns + baseline_cols + pd_post_columns]
    fu_pd = pd.DataFrame(fu_rows)[pd_pre_columns + fu_cols + pd_post_columns]
    recreate_pd = pd.DataFrame(recreate_rows)[pd_pre_columns + recreate_cols + pd_post_columns]
    act_pd = pd.DataFrame(act_rows)[pd_pre_columns + act_cols + pd_post_columns]
    feedback_pd = pd.DataFrame(feedback_rows)[pd_pre_columns + feedback_cols + pd_post_columns]

    sub_pd.to_csv(f"{data_path}all{ts}/sub_data_ALL.csv", index=False)
    baseline_pd.to_csv(f"{data_path}all{ts}/baseline_data_ALL.csv", index=False)
    fu_pd.to_csv(f"{data_path}all{ts}/fu_data_ALL.csv", index=False)
    act_pd.to_csv(f"{data_path}all{ts}/act_data_ALL.csv", index=False)
    recreate_pd.to_csv(f"{data_path}all{ts}/recreate_data_ALL.csv", index=False)
    feedback_pd.to_csv(f"{data_path}all{ts}/feedback_data_ALL.csv", index=False)
