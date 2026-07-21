# %% Import libraries and load data
import os
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from _objects.qs_maps import *

plt.ion()

# establish working directory
cwd = os.getcwd()
cwd_split = cwd.split('/')
base_task = 'qs_structure'
task_version = 'qs-structure-phq9-v4'
task_subversions = ['', '_d', '_dd', '_ddd']
# task_subversion = task_subversions[3]


do_local = False
save_external = False  # whether to save processed files on external drive as well
study_name = 'a_open_qs'
for task_subversion in task_subversions:
    external_path = f"/Volumes/DATA/UCL/online_tasks/{base_task}/{task_version}/_data/{task_version}{task_subversion}/"
    local_path = f"data/{study_name}/task_data/{task_version}{task_subversion}/"

    if do_local:
        data_path = local_path
    else:
        data_path = external_path

    Path(f"{data_path}processed").mkdir(parents=True, exist_ok=True)
    if data_path != local_path:
        Path(f"{local_path}processed").mkdir(parents=True, exist_ok=True)

    # %% load data
    sub_data = pd.read_csv(data_path + "all/sub_data_ALL.csv")
    emo_data = pd.read_csv(data_path + "all/emo_data_ALL.csv")
    phq9_data = pd.read_csv(data_path + "all/phq9_data_ALL.csv")
    gad7_data = pd.read_csv(data_path + "all/gad7_data_ALL.csv")
    sds_data = pd.read_csv(data_path + "all/sds_data_ALL.csv")
    lvl1_closed_data = pd.read_csv(data_path + "all/lvl1_closed_data_ALL.csv")
    lvl2_closed_data = pd.read_csv(data_path + "all/lvl2_closed_data_ALL.csv")
    openq_data = pd.read_csv(data_path + "all/open_qs_data_ALL.csv")

    duplicates = sub_data.loc[sub_data['PID'].duplicated(), 'PID']
    duplicates = sub_data.loc[sub_data['PID'].isin(duplicates), ['PID', 'UID']]
    # data_path su
    if len(duplicates) > 0:
        print('Duplicated ppt UIDs')
        print(duplicates)
    else:

        completion_code = 'CSYBZRQ4'
        attention_threshold = 1
        warning_threshold = 5

        # % quality checks
        good_idx = (sub_data['consented'] == 'Yes') & (sub_data['completed'] == 'Yes') & (
                sub_data['returned'] == 'No') & (sub_data['code'] == completion_code) & (
                           sub_data['attention_checks_total'] >= attention_threshold) & (
                           sub_data['warning_count'] <= warning_threshold)

        good_pid = sub_data[good_idx]['PID']
        if good_pid.duplicated().any():
            print('duplicated')
            print(good_pid[good_pid.duplicated()])

        # subset and sort dataframes
        # subject data
        sub_data = sub_data[good_idx]
        sub_data['date_time'] = sub_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (sub_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + sub_data['PID'].str[-5:]
        sub_data.insert(0, 'sub_ts_id', sub_ts_ids)
        sub_data = sub_data.sort_values(['sub_ts_id'], ascending=True).reset_index(drop=True)
        sub_data.insert(0, 'sub', ['sub' + str(s + 1) for s in sub_data.index])

        # emo data
        emo_data['date_time'] = emo_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (emo_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + emo_data['PID'].str[-5:]
        emo_data.insert(0, 'sub_ts_id', sub_ts_ids)
        emo_data = emo_data[emo_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'], ascending=True).reset_index(
            drop=True)
        emo_data.insert(0, 'sub', ['sub' + str(s + 1) for s in emo_data.index])

        # phq9 data
        phq9_data['date_time'] = phq9_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (phq9_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + phq9_data['PID'].str[
            -5:]
        phq9_data.insert(0, 'sub_ts_id', sub_ts_ids)
        phq9_data = phq9_data[phq9_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'], ascending=True).reset_index(
            drop=True)
        phq9_data.insert(0, 'sub', ['sub' + str(s + 1) for s in phq9_data.index])

        # gad7 data
        gad7_data['date_time'] = gad7_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (gad7_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + gad7_data['PID'].str[
            -5:]
        gad7_data.insert(0, 'sub_ts_id', sub_ts_ids)
        gad7_data = gad7_data[gad7_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'], ascending=True).reset_index(
            drop=True)
        gad7_data.insert(0, 'sub', ['sub' + str(s + 1) for s in gad7_data.index])

        # sds data
        sds_data['date_time'] = sds_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (sds_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + sds_data['PID'].str[-5:]
        sds_data.insert(0, 'sub_ts_id', sub_ts_ids)
        sds_data = sds_data[sds_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'], ascending=True).reset_index(
            drop=True)
        sds_data.insert(0, 'sub', ['sub' + str(s + 1) for s in sds_data.index])

        # lvl1_closed data
        lvl1_closed_data['date_time'] = lvl1_closed_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (lvl1_closed_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + lvl1_closed_data[
            'PID'].str[-5:]
        lvl1_closed_data.insert(0, 'sub_ts_id', sub_ts_ids)
        lvl1_closed_data = lvl1_closed_data[lvl1_closed_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'],
                                                                                                ascending=True).reset_index(
            drop=True)
        lvl1_closed_data.insert(0, 'sub', ['sub' + str(s + 1) for s in lvl1_closed_data.index])

        # lvl2_closed data
        lvl2_closed_data['date_time'] = lvl2_closed_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (lvl2_closed_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + lvl2_closed_data[
            'PID'].str[-5:]
        lvl2_closed_data.insert(0, 'sub_ts_id', sub_ts_ids)
        lvl2_closed_data = lvl2_closed_data[lvl2_closed_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'],
                                                                                                ascending=True).reset_index(
            drop=True)
        lvl2_closed_data.insert(0, 'sub', ['sub' + str(s + 1) for s in lvl2_closed_data.index])

        # openq data
        openq_data['date_time'] = openq_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (openq_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + openq_data['PID'].str[
            -5:]
        openq_data.insert(0, 'sub_ts_id', sub_ts_ids)
        openq_data = openq_data[openq_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'],
                                                                              ascending=True).reset_index(drop=True)
        openq_data.insert(0, 'sub', ['sub' + str(s + 1) for s in openq_data.index])

        # save subject key file
        sub_keys = sub_data[
            ['sub', 'sub_ts_id', 'PID', 'UID', 'ST_ID', 'SE_ID', 'task_version', 'date', 'time', 'date_time']]
        # sub_keys.to_csv(f"{external_path}sub_keys.csv", index=False)
        if save_external:
            sub_keys.to_csv(f"{data_path}/processed/sub_keys.csv", index=False)

        ## remove IDs etc
        col_to_rem = ['PID', 'sub_ts_id', 'UID', 'ST_ID', 'SE_ID', 'date', 'time', 'date_time']
        col_to_rem_sub = ['PID', 'sub_ts_id', 'UID', 'ST_ID', 'SE_ID', 'date', 'time']
        sub_data = sub_data.iloc[:, ~sub_data.columns.isin(col_to_rem_sub)]
        emo_data = emo_data.iloc[:, ~emo_data.columns.isin(col_to_rem)]
        phq9_data = phq9_data.iloc[:, ~phq9_data.columns.isin(col_to_rem)]
        gad7_data = gad7_data.iloc[:, ~gad7_data.columns.isin(col_to_rem)]
        sds_data = sds_data.iloc[:, ~sds_data.columns.isin(col_to_rem)]
        lvl1_closed_data = lvl1_closed_data.iloc[:, ~lvl1_closed_data.columns.isin(col_to_rem)]
        lvl2_closed_data = lvl2_closed_data.iloc[:, ~lvl2_closed_data.columns.isin(col_to_rem)]
        openq_data = openq_data.iloc[:, ~openq_data.columns.isin(col_to_rem)]

        ## remove list characters from emotion list
        # emo_data.replace(r'\'|\[|\]', '', regex=True, inplace=True)
        emo_data[['emo_lvl2_q1', 'emo_lvl3_q6']] = emo_data[['emo_lvl2_q1', 'emo_lvl3_q6']].replace(r'\'|\[|\]', '',
                                                                                                    regex=True)

        ## process phq9 data - toal scores, plus scores for each question
        phq9_data.insert(1, 'total', 0)

        # add score columns
        for q in ['phq9_q' + str(q + 1) + 's' for q in range(9)]:
            phq9_data.insert(phq9_data.shape[1], q, np.nan)

        # add scores and totals
        for r, row in phq9_data.iterrows():
            sub_total = 0
            for q in ['phq9_q' + str(q + 1) for q in range(9)]:
                try:
                    sub_total += phq9_map[row[q]]
                    phq9_data.loc[r, q + 's'] = phq9_map[row[q]]
                except:
                    phq9_data.loc[r, q + 's'] = np.nan
            phq9_data.loc[r, 'total'] = sub_total

        ## process gad7 data - toal scores, plus scores for each question
        gad7_data.insert(1, 'total', 0)

        # add score columns
        for q in ['gad7_q' + str(q + 1) + 's' for q in range(7)]:
            gad7_data.insert(gad7_data.shape[1], q, np.nan)

        # add scores and totals
        for r, row in gad7_data.iterrows():
            sub_total = 0
            for q in ['gad7_q' + str(q + 1) for q in range(7)]:
                try:
                    sub_total += gad7_map[row[q]]
                    gad7_data.loc[r, q + 's'] = gad7_map[row[q]]
                except:
                    gad7_data.loc[r, q + 's'] = np.nan
            gad7_data.loc[r, 'total'] = sub_total

        ## process sds data - toal scores, plus scores for each question
        sds_data.insert(1, 'total', 0)
        # sds_data.replace(r'<u>|</u>', '', regex=True, inplace=True)

        # add score columns
        for q in ['sds_q' + str(q + 1) + 's' for q in range(20)]:
            sds_data.insert(sds_data.shape[1], q, np.nan)

        # add scores and totals
        for r, row in sds_data.iterrows():
            sub_total = 0
            for q in range(20):
                q_name = 'sds_q' + str(q + 1)
                if q + 1 in sds_rev_qs:
                    sds_q_map = sds_rev_map
                else:
                    sds_q_map = sds_map
                # for q in ['sds_q' + str(q + 1) for q in range(28)]:
                try:
                    sub_total += sds_q_map[row[q_name]]
                    sds_data.loc[r, q_name + 's'] = sds_q_map[row[q_name]]
                except:
                    sds_data.loc[r, q_name + 's'] = np.nan
            sds_data.loc[r, 'total'] = sub_total

        ## process lvl1_closed data - toal scores, plus scores for each question
        lvl1_closed_data.insert(1, 'total', 0)

        # add score columns
        for q in ['lvl1_closed_q' + str(q + 1) + 's' for q in range(1)]:
            lvl1_closed_data.insert(lvl1_closed_data.shape[1], q, np.nan)

        # add scores and totals
        for r, row in lvl1_closed_data.iterrows():
            sub_total = 0
            for q in ['lvl1_closed_q' + str(q + 1) for q in range(1)]:
                try:
                    sub_total += lvlx_closed_map[row[q]]
                    lvl1_closed_data.loc[r, q + 's'] = lvlx_closed_map[row[q]]
                except:
                    lvl1_closed_data.loc[r, q + 's'] = np.nan
            lvl1_closed_data.loc[r, 'total'] = sub_total

        ## process lvl2_closed data - toal scores, plus scores for each question
        lvl2_closed_data.insert(1, 'total', 0)

        # add score columns
        for q in ['lvl2_closed_q' + str(q + 1) + 's' for q in range(3)]:
            lvl2_closed_data.insert(lvl2_closed_data.shape[1], q, np.nan)

        # add scores and totals
        for r, row in lvl2_closed_data.iterrows():
            sub_total = 0
            for q in ['lvl2_closed_q' + str(q + 1) for q in range(3)]:
                try:
                    sub_total += lvlx_closed_map[row[q]]
                    lvl2_closed_data.loc[r, q + 's'] = lvlx_closed_map[row[q]]
                except:
                    lvl2_closed_data.loc[r, q + 's'] = np.nan
            lvl2_closed_data.loc[r, 'total'] = sub_total

        if save_external:
            sub_data.to_csv(f"{data_path}/processed/sub_data.csv", index=False)
            emo_data.to_csv(f"{data_path}/processed/emo_data.csv", index=False)
            phq9_data.to_csv(f"{data_path}/processed/phq9_data.csv", index=False)
            gad7_data.to_csv(f"{data_path}/processed/gad7_data.csv", index=False)
            sds_data.to_csv(f"{data_path}/processed/sds_data.csv", index=False)
            lvl1_closed_data.to_csv(f"{data_path}/processed/lvl1_closed_data.csv", index=False)
            lvl2_closed_data.to_csv(f"{data_path}/processed/lvl2_closed_data.csv", index=False)
            openq_data.to_csv(f"{data_path}/processed/openq_data.csv", index=False)

        if local_path != data_path:
            sub_data.to_csv(f"{local_path}/processed/sub_data.csv", index=False)
            emo_data.to_csv(f"{local_path}/processed/emo_data.csv", index=False)
            phq9_data.to_csv(f"{local_path}/processed/phq9_data.csv", index=False)
            gad7_data.to_csv(f"{local_path}/processed/gad7_data.csv", index=False)
            sds_data.to_csv(f"{local_path}/processed/sds_data.csv", index=False)
            lvl1_closed_data.to_csv(f"{local_path}/processed/lvl1_closed_data.csv", index=False)
            lvl2_closed_data.to_csv(f"{local_path}/processed/lvl2_closed_data.csv", index=False)
            openq_data.to_csv(f"{local_path}/processed/openq_data.csv", index=False)

    # # %% Check for any empty  # l1 = ['lvl1_q1']  # l2 = ['lvl2_q' + str(q + 1) for q in range(3)]  # l3 = ['lvl3_q' + str(q + 1) for q in range(8)]  # ls = l1 + l2 + l3  # l1c = ['lvl1_closed_q1']  # l2c = ['lvl2_closed_q' + str(q + 1) for q in range(3)]  # s_l = ['sds_q' + str(q + 1) for q in range(20)]  # p_l = ['phq9_q' + str(q + 1) for q in range(9)]  # g_l = ['gad7_q' + str(q + 1) for q in range(7)]  # sds_na = list(sds_data[pd.isnull(sds_data[s_l]).any(axis=1)]['sub'].values)  # phq9_na = list(phq9_data[pd.isnull(phq9_data[p_l]).any(axis=1)]['sub'].values)  # gad7_na = list(gad7_data[pd.isnull(gad7_data[g_l]).any(axis=1)]['sub'].values)  # lvl1c_na = list(lvl1_closed_data[pd.isnull(lvl1_closed_data[l1c]).any(axis=1)]['sub'].values)  # lvl2c_na = list(lvl2_closed_data[pd.isnull(lvl2_closed_data[l2c]).any(axis=1)]['sub'].values)  # oq_na = list(openq_data[pd.isnull(openq_data[ls]).any(axis=1)]['sub'].values)  #  # na_list = list(set(sds_na + phq9_na + gad7_na + lvl1c_na + lvl2c_na + oq_na))  # print(na_list, '\n', len(na_list))
