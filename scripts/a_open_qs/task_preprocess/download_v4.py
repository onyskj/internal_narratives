'''
Downloads data from firebase
'''
import json
import os
import pickle
import sys
from datetime import datetime
from io import StringIO
from itertools import chain
# %% Import libraries and load data
# import random
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
base_task = 'qs_structure'
task_version = 'qs-structure-phq9-v4'
# task_subversion = '_dd'
task_subversion = '_ddd'
# task_subversion = ''
cwd_base = '/'.join(cwd_split[:np.argwhere([p == "online_tasks" for p in cwd_split])[0][0] + 1])
os.chdir(f"{cwd_base}/{base_task}/{task_version}")

# save log to file
to_log = False

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
# do_local = True
do_local = False
if do_local:
    data_path = f"_data/{task_version}{task_subversion}/"
else:
    data_path = f"/Volumes/DATA/UCL/online_tasks/{base_task}/{task_version}/_data/{task_version}{task_subversion}/"

if to_log:
    Path(f"{data_path}_logs").mkdir(parents=True, exist_ok=True)
    with open(data_path + '_logs/log' + ts + '.txt', 'w') as f:
        f.write('')
    sys.stdout = open(data_path + '_logs/log' + ts + '.txt', 'wt')
# %% Set up column names for data frames
# common columns
pd_pre_columns = ['PID', 'UID']
pd_post_columns = ['ST_ID', 'SE_ID', 'task_version', 'date', 'time', 'date_time']

# variable names
# emotion columns
emo_cols = ['emo_lvl2_q1', 'emo_lvl3_q6', 'emo_rt_lvl2_q1', 'emo_rt_lvl3_q6', 'emo_timeout_lvl2_q1',
            'emo_timeout_lvl3_q6', 'is_empty_lvl2_q1', 'is_empty_lvl3_q6']
emo_cols = pd_pre_columns + emo_cols + pd_post_columns

# open questions
oq_names = ['responses_lvl1_q1', 'responses_lvl2_q1', 'responses_lvl2_q2', 'responses_lvl2_q3', 'responses_lvl3_q1',
            'responses_lvl3_q2', 'responses_lvl3_q3', 'responses_lvl3_q4', 'responses_lvl3_q5', 'responses_lvl3_q6',
            'responses_lvl3_q7', 'responses_lvl3_q8', 'responses_rep_lvl2_q1', 'responses_lvl2_q_catch']
na_names = ['is_empty_lvl1_q1', 'is_empty_lvl2_q1', 'is_empty_lvl2_q2', 'is_empty_lvl2_q3', 'is_empty_lvl3_q1',
            'is_empty_lvl3_q2', 'is_empty_lvl3_q3', 'is_empty_lvl3_q4', 'is_empty_lvl3_q5', 'is_empty_lvl3_q6',
            'is_empty_lvl3_q7', 'is_empty_lvl3_q8', 'is_empty_rep_lvl2_q1', 'is_empty_lvl2_q_catch']
rt_names = ['rts_lvl1_q1', 'rts_lvl2_q1', 'rts_lvl2_q2', 'rts_lvl2_q3', 'rts_lvl3_q1', 'rts_lvl3_q2', 'rts_lvl3_q3',
            'rts_lvl3_q4', 'rts_lvl3_q5', 'rts_lvl3_q6', 'rts_lvl3_q7', 'rts_lvl3_q8', 'rts_rep_lvl2_q1',
            'rts_lvl2_q_catch']
timeout_names = ['timeout_lvl1_q1', 'timeout_lvl2_q1', 'timeout_lvl2_q2', 'timeout_lvl2_q3', 'timeout_lvl3_q1',
                 'timeout_lvl3_q2', 'timeout_lvl3_q3', 'timeout_lvl3_q4', 'timeout_lvl3_q5', 'timeout_lvl3_q6',
                 'timeout_lvl3_q7', 'timeout_lvl3_q8', 'timeout_rep_lvl2_q1', 'timeout_lvl2_q_catch']

q_names = ['_'.join(oq_name.split('_')[1:]) for oq_name in oq_names]
oq_cols = q_names + list(
    chain.from_iterable([['is_empty_' + q_name, 'rt_' + q_name, 'timeout_' + q_name] for q_name in q_names]))
oq_cols = pd_pre_columns + oq_cols + pd_post_columns

# phq9 columns
phq9_q_names = ['phq9_q1', 'phq9_q2', 'phq9_q3', 'phq9_q4', 'phq9_q5', 'phq9_q6', 'phq9_q7', 'phq9_q8', 'phq9_q9',
                'phq9_q_catch']
phq9_cols = phq9_q_names + ['phq9_rt', 'is_empty_phq9', 'timeout_phq9']
phq9_cols = pd_pre_columns + phq9_cols + pd_post_columns

# gad7 columns
gad7_q_names = ['gad7_q1', 'gad7_q2', 'gad7_q3', 'gad7_q4', 'gad7_q5', 'gad7_q6', 'gad7_q7']
gad7_cols = gad7_q_names + ['gad7_rt', 'is_empty_gad7', 'timeout_gad7']
gad7_cols = pd_pre_columns + gad7_cols + pd_post_columns

# sds columns
sds_q_names = ["sds_q1", "sds_q2", "sds_q3", "sds_q4", "sds_q5", "sds_q6", "sds_q7", "sds_q8", "sds_q9", "sds_q10",
               "sds_q11", "sds_q12", "sds_q13", "sds_q14", "sds_q15", "sds_q16", "sds_q17", "sds_q18", "sds_q19",
               "sds_q20"]
sds_cols = sds_q_names + ['sds_rt', 'is_empty_sds', 'timeout_sds']
sds_cols = pd_pre_columns + sds_cols + pd_post_columns

# lvl1_closed columns
lvl1_closed_q_names = ['lvl1_closed_q1']
lvl1_closed_cols = lvl1_closed_q_names + ['lvl1_closed_rt', 'is_empty_lvl1_closed', 'timeout_lvl1_closed']
lvl1_closed_cols = pd_pre_columns + lvl1_closed_cols + pd_post_columns

# lvl2_closed columns
lvl2_closed_q_names = ['lvl2_closed_q1', 'lvl2_closed_q2', 'lvl2_closed_q3']
lvl2_closed_cols = lvl2_closed_q_names + ['lvl2_closed_rt', 'is_empty_lvl2_closed', 'timeout_lvl2_closed']
lvl2_closed_cols = pd_pre_columns + lvl2_closed_cols + pd_post_columns

sub_cols = pd_pre_columns + pd_post_columns + ['consented', 'completed', 'returned', 'code', 'phq9_q_catch',
                                               'lvl2_attention_check', 'attention_checks_total',
                                               'attention_checks_bool', 'empty_count', 'timeout_count', 'warning_count',
                                               'feedback']

# check keys
doc_keys = ['PID', 'ST_ID', 'SE_ID', 'task_version', 'date', 'time', 'consented', 'completed', 'returned', 'code',
            'phq9_q_catch', 'lvl2_attention_check', 'attention_checks_total', 'attention_checks_bool', 'empty_count',
            'timeout_count', 'warning_count', 'feedback']
emo_keys = ['emotions_lvl2_q1', 'emotions_lvl3_q6', 'rts_emotions_lvl2_q1', 'rts_emotions_lvl3_q6',
            'timeout_emotions_lvl2_q1', 'timeout_emotions_lvl3_q6', 'is_empty_emotions_lvl2_q1',
            'is_empty_emotions_lvl3_q6']

phq9_keys = ['rt', 'phq9_q_catch', 'responses', 'timeout_phq9', 'is_empty_phq9']
gad7_keys = ['rt', 'responses', 'timeout_gad7', 'is_empty_gad7']
sds_keys = ['rt', 'responses', 'timeout_sds', 'is_empty_sds']
lvl1_closed_keys = ['rt', 'responses', 'timeout_lvl1_closed', 'is_empty_lvl1_closed']
lvl2_closed_keys = ['rt', 'responses', 'timeout_lvl2_closed', 'is_empty_lvl2_closed']
# %% Download all data
emo_rows = []
open_qs_rows = []
phq9_rows = []
gad7_rows = []
sds_rows = []
lvl1_closed_rows = []
lvl2_closed_rows = []
sub_rows = []

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

        sub_row = {'PID': pid, 'UID': sub, 'ST_ID': stid, 'SE_ID': seid, 'task_version': sub_doc['task_version'],
                   'date': date, 'time': time, 'date_time': date_time, 'consented': sub_doc['consented'],
                   'completed': sub_doc['completed'], 'returned': sub_doc['returned'], 'code': sub_doc['code'],
                   'phq9_q_catch': sub_doc['phq9_q_catch'], 'lvl2_attention_check': sub_doc['lvl2_attention_check'],
                   'attention_checks_total': sub_doc['attention_checks_total'],
                   'attention_checks_bool': sub_doc['attention_checks_bool'], 'empty_count': sub_doc['empty_count'],
                   'timeout_count': sub_doc['timeout_count'], 'warning_count': sub_doc['warning_count'],
                   'feedback': sub_doc['feedback']}
        sub_rows.append(sub_row)

        # dump data
        doc_csv = None
        doc_json = None
        if 'z_dump_csv' in sub_doc.keys():
            doc_csv = pd.read_csv(StringIO(sub_doc['z_dump_csv']), sep=',')
            # save csv
            doc_csv.to_csv(f"{data_path}raw{ts}/{sub}/_doc_{sub}.csv", index=False)
        if 'z_dump_json' in sub_doc.keys():
            doc_json = json.load(StringIO(sub_doc['z_dump_json']))
            # save json
            with open(f"{data_path}raw{ts}/{sub}/_doc_{sub}.json", 'w') as f:
                json.dump(doc_json, f, ensure_ascii=False, indent=4)

        # general data: uid, PID, STUDY and SESSION ID

        # emotions data
        # -> 2x RTs, 2x timeouts, 2x na-checked, 2x emotions array
        sub_emo_data = db.collection('subjects').document(sub).collection('questions').document(
            'emotions').get().to_dict()

        # ensure sub doc keys are there
        for emo_key in emo_keys:
            if emo_key not in sub_emo_data.keys():
                sub_emo_data[emo_key] = np.nan
                print('\t\tmissing: ' + emo_key)

        if isinstance(sub_emo_data['emotions_lvl2_q1'], dict):
            sub_emo_data['emotions_lvl2_q1'] = list(sub_emo_data['emotions_lvl2_q1'].values())[0]

        if isinstance(sub_emo_data['emotions_lvl3_q6'], dict):
            sub_emo_data['emotions_lvl3_q6'] = list(sub_emo_data['emotions_lvl3_q6'].values())[0]

        sub_emo_row = {'PID': pid, 'UID': sub, 'emo_lvl2_q1': sub_emo_data['emotions_lvl2_q1'],
                       'emo_lvl3_q6': sub_emo_data['emotions_lvl3_q6'],
                       'emo_rt_lvl2_q1': sub_emo_data['rts_emotions_lvl2_q1'],
                       'emo_rt_lvl3_q6': sub_emo_data['rts_emotions_lvl3_q6'],
                       'emo_timeout_lvl2_q1': sub_emo_data['timeout_emotions_lvl2_q1'],
                       'emo_timeout_lvl3_q6': sub_emo_data['timeout_emotions_lvl3_q6'],
                       'is_empty_lvl2_q1': sub_emo_data['is_empty_emotions_lvl2_q1'],
                       'is_empty_lvl3_q6': sub_emo_data['is_empty_emotions_lvl3_q6'], 'ST_ID': stid, 'SE_ID': seid,
                       'task_version': sub_doc['task_version'], 'date': date, 'time': time, 'date_time': date_time}
        emo_rows.append(sub_emo_row)

        # open questions data
        sub_openQs_data = db.collection('subjects').document(sub).collection('questions').document(
            'open_questions').get().to_dict()
        # open questions RTs data
        sub_openQs_rts_data = db.collection('subjects').document(sub).collection('questions').document(
            'open_questions_rts').get().to_dict()
        # open questions dump data
        sub_openQs_dump_data = db.collection('subjects').document(sub).collection('questions').document(
            'open_questions_dump').get().to_dict()

        sub_openq_row = {'PID': pid, 'UID': sub, 'ST_ID': stid, 'SE_ID': seid, 'task_version': sub_doc['task_version'],
                         'date': date, 'time': time, 'date_time': date_time}
        for oq_name in oq_names:
            q_name = '_'.join(oq_name.split('_')[1:])
            if oq_name in sub_openQs_data.keys():
                sub_openq_row[q_name] = list(sub_openQs_data[oq_name].values())[0]
            else:
                sub_openq_row[q_name] = np.nan

        for (na_val, rt_val, timeout_val) in zip(na_names, rt_names, timeout_names):
            q_name = '_'.join(timeout_val.split('_')[1:])
            if na_val in sub_openQs_data.keys():
                sub_openq_row['is_empty_' + q_name] = sub_openQs_data[na_val]
            else:
                print('\t\tmissing: ' + na_val)
                sub_openq_row['is_empty_' + q_name] = np.nan

            if rt_val in sub_openQs_rts_data.keys():
                sub_openq_row['rt_' + q_name] = sub_openQs_rts_data[rt_val]
            else:
                print('\t\tmissing: ' + rt_val)
                sub_openq_row['rt_' + q_name] = np.nan

            if timeout_val in sub_openQs_rts_data.keys():
                sub_openq_row['timeout_' + q_name] = sub_openQs_rts_data[timeout_val]
            else:
                print('\t\tmissing: ' + timeout_val)
                sub_openq_row['timeout_' + q_name] = np.nan

        open_qs_rows.append(sub_openq_row)

        # phq9 data <==========================================================================================================================
        sub_phq9_data = db.collection('subjects').document(sub).collection('questions').document(
            'phq9_questions').get().to_dict()

        # ensure sub doc keys are there
        for phq9_key in phq9_keys:
            if phq9_key not in sub_phq9_data.keys():
                print('\t\tmissing: ' + phq9_key)
                if phq9_key != 'responses':
                    sub_phq9_data[phq9_key] = np.nan
                else:
                    sub_phq9_data[phq9_key] = {}

        sub_phq9_row = {'PID': pid, 'UID': sub, 'phq9_rt': sub_phq9_data['rt'],
                        'is_empty_phq9': sub_phq9_data['is_empty_phq9'], 'timeout_phq9': sub_phq9_data['timeout_phq9'],
                        'phq9_q_catch': sub_phq9_data['phq9_q_catch'], 'ST_ID': stid, 'SE_ID': seid,
                        'task_version': sub_doc['task_version'], 'date': date, 'time': time, 'date_time': date_time}
        for phq9_q_name in phq9_q_names:
            if phq9_q_name in sub_phq9_data['responses'].keys():
                sub_phq9_row[phq9_q_name] = sub_phq9_data['responses'][phq9_q_name]
            else:
                sub_phq9_row[phq9_q_name] = np.nan

        phq9_rows.append(sub_phq9_row)

        # gad7 data <==========================================================================================================================
        sub_gad7_data = db.collection('subjects').document(sub).collection('questions').document(
            'gad7_questions').get().to_dict()

        # ensure sub doc keys are there
        for gad7_key in gad7_keys:
            if gad7_key not in sub_gad7_data.keys():
                print('\t\tmissing: ' + gad7_key)
                if gad7_key != 'responses':
                    sub_gad7_data[gad7_key] = np.nan
                else:
                    sub_gad7_data[gad7_key] = {}

        sub_gad7_row = {'PID': pid, 'UID': sub, 'gad7_rt': sub_gad7_data['rt'],
                        'is_empty_gad7': sub_gad7_data['is_empty_gad7'], 'timeout_gad7': sub_gad7_data['timeout_gad7'],
                        'ST_ID': stid, 'SE_ID': seid, 'task_version': sub_doc['task_version'], 'date': date,
                        'time': time, 'date_time': date_time}
        for gad7_q_name in gad7_q_names:
            if gad7_q_name in sub_gad7_data['responses'].keys():
                sub_gad7_row[gad7_q_name] = sub_gad7_data['responses'][gad7_q_name]
            else:
                sub_gad7_row[gad7_q_name] = np.nan

        gad7_rows.append(sub_gad7_row)

        # sds data <==========================================================================================================================
        sub_sds_data = db.collection('subjects').document(sub).collection('questions').document(
            'sds_questions').get().to_dict()

        # ensure sub doc keys are there
        for sds_key in sds_keys:
            if sds_key not in sub_sds_data.keys():
                print('\t\tmissing: ' + sds_key)
                if sds_key != 'responses':
                    sub_sds_data[sds_key] = np.nan
                else:
                    sub_sds_data[sds_key] = {}

        sub_sds_row = {'PID': pid, 'UID': sub, 'sds_rt': sub_sds_data['rt'],
                       'is_empty_sds': sub_sds_data['is_empty_sds'], 'timeout_sds': sub_sds_data['timeout_sds'],
                       'ST_ID': stid, 'SE_ID': seid, 'task_version': sub_doc['task_version'], 'date': date,
                       'time': time, 'date_time': date_time}
        for sds_q_name in sds_q_names:
            if sds_q_name in sub_sds_data['responses'].keys():
                sub_sds_row[sds_q_name] = sub_sds_data['responses'][sds_q_name]
            else:
                sub_sds_row[sds_q_name] = np.nan

        sds_rows.append(sub_sds_row)

        # lvl1_closed data <==========================================================================================================================
        sub_lvl1_closed_data = db.collection('subjects').document(sub).collection('questions').document(
            'lvl1_closed_questions').get().to_dict()

        # ensure sub doc keys are there
        for lvl1_closed_key in lvl1_closed_keys:
            if lvl1_closed_key not in sub_lvl1_closed_data.keys():
                print('\t\tmissing: ' + lvl1_closed_key)
                if lvl1_closed_key != 'responses':
                    sub_lvl1_closed_data[lvl1_closed_key] = np.nan
                else:
                    sub_lvl1_closed_data[lvl1_closed_key] = {}

        sub_lvl1_closed_row = {'PID': pid, 'UID': sub, 'lvl1_closed_rt': sub_lvl1_closed_data['rt'],
                               'is_empty_lvl1_closed': sub_lvl1_closed_data['is_empty_lvl1_closed'],
                               'timeout_lvl1_closed': sub_lvl1_closed_data['timeout_lvl1_closed'], 'ST_ID': stid,
                               'SE_ID': seid, 'task_version': sub_doc['task_version'], 'date': date, 'time': time,
                               'date_time': date_time}
        for lvl1_closed_q_name in lvl1_closed_q_names:
            if lvl1_closed_q_name in sub_lvl1_closed_data['responses'].keys():
                sub_lvl1_closed_row[lvl1_closed_q_name] = sub_lvl1_closed_data['responses'][lvl1_closed_q_name]
            else:
                sub_lvl1_closed_row[lvl1_closed_q_name] = np.nan

        lvl1_closed_rows.append(sub_lvl1_closed_row)

        # lvl2_closed data <==========================================================================================================================
        sub_lvl2_closed_data = db.collection('subjects').document(sub).collection('questions').document(
            'lvl2_closed_questions').get().to_dict()

        # ensure sub doc keys are there
        for lvl2_closed_key in lvl2_closed_keys:
            if lvl2_closed_key not in sub_lvl2_closed_data.keys():
                print('\t\tmissing: ' + lvl2_closed_key)
                if lvl2_closed_key != 'responses':
                    sub_lvl2_closed_data[lvl2_closed_key] = np.nan
                else:
                    sub_lvl2_closed_data[lvl2_closed_key] = {}

        sub_lvl2_closed_row = {'PID': pid, 'UID': sub, 'lvl2_closed_rt': sub_lvl2_closed_data['rt'],
                               'is_empty_lvl2_closed': sub_lvl2_closed_data['is_empty_lvl2_closed'],
                               'timeout_lvl2_closed': sub_lvl2_closed_data['timeout_lvl2_closed'], 'ST_ID': stid,
                               'SE_ID': seid, 'task_version': sub_doc['task_version'], 'date': date, 'time': time,
                               'date_time': date_time}
        for lvl2_closed_q_name in lvl2_closed_q_names:
            if lvl2_closed_q_name in sub_lvl2_closed_data['responses'].keys():
                sub_lvl2_closed_row[lvl2_closed_q_name] = sub_lvl2_closed_data['responses'][lvl2_closed_q_name]
            else:
                sub_lvl2_closed_row[lvl2_closed_q_name] = np.nan

        lvl2_closed_rows.append(sub_lvl2_closed_row)

        ## save raw data
        if saveMe:
            # save emo
            with open(f"{data_path}raw{ts}/{sub}/emo_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_emo_data, f)
            # save openQs
            with open(f"{data_path}raw{ts}/{sub}/openQs_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_openQs_data, f)
            # save phq9
            with open(f"{data_path}raw{ts}/{sub}/phq9_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_phq9_data, f)
            # save gad7
            with open(f"{data_path}raw{ts}/{sub}/gad7_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_gad7_data, f)
            # save sds
            with open(f"{data_path}raw{ts}/{sub}/sds_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_sds_data, f)
            # save lvl1_closed
            with open(f"{data_path}raw{ts}/{sub}/lvl1_closed_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_lvl1_closed_data, f)
            # save lvl2_closed
            with open(f"{data_path}raw{ts}/{sub}/lvl2_closed_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_lvl2_closed_data, f)
            # save openQs rts
            with open(f"{data_path}raw{ts}/{sub}/openQs_rts_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_openQs_rts_data, f)
            # save openQs dump
            with open(f"{data_path}raw{ts}/{sub}/_openQs_dump_{sub}.pickle", 'wb') as f:
                pickle.dump(sub_openQs_dump_data, f)

    # %% Save to csv
    Path(f"{data_path}all{ts}").mkdir(parents=True, exist_ok=True)
    sub_pd = pd.DataFrame(sub_rows)[sub_cols]
    emo_pd = pd.DataFrame(emo_rows)[emo_cols]
    phq9_pd = pd.DataFrame(phq9_rows)[phq9_cols]
    gad7_pd = pd.DataFrame(gad7_rows)[gad7_cols]
    sds_pd = pd.DataFrame(sds_rows)[sds_cols]
    lvl1_closed_pd = pd.DataFrame(lvl1_closed_rows)[lvl1_closed_cols]
    lvl2_closed_pd = pd.DataFrame(lvl2_closed_rows)[lvl2_closed_cols]
    open_qs_pd = pd.DataFrame(open_qs_rows)[oq_cols]

    sub_pd.to_csv(f"{data_path}all{ts}/sub_data_ALL.csv", index=False)
    emo_pd.to_csv(f"{data_path}all{ts}/emo_data_ALL.csv", index=False)
    phq9_pd.to_csv(f"{data_path}all{ts}/phq9_data_ALL.csv", index=False)
    gad7_pd.to_csv(f"{data_path}all{ts}/gad7_data_ALL.csv", index=False)
    sds_pd.to_csv(f"{data_path}all{ts}/sds_data_ALL.csv", index=False)
    lvl1_closed_pd.to_csv(f"{data_path}all{ts}/lvl1_closed_data_ALL.csv", index=False)
    lvl2_closed_pd.to_csv(f"{data_path}all{ts}/lvl2_closed_data_ALL.csv", index=False)
    open_qs_pd.to_csv(f"{data_path}all{ts}/open_qs_data_ALL.csv", index=False)
