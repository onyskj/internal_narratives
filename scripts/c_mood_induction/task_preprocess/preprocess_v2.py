# %% Import libraries and load data
import os
from pathlib import Path

import pandas as pd

# establish working directory
cwd = os.getcwd()
cwd_split = cwd.split('/')
base_task = 'qs_intervention/_tasks'
base_task_local = 'qs_intervention'
task_version = 'qs-intervention-v2'
task_subversions = ['', 'b']

# do_local = True
do_local = False
save_external = False  # whether to save processed files on external drive as well
study_name = 'c_mood_induction'

# %% col names etc
b_phq9_acheck_i = 4
f_phq9_acheck_i = 7

common_cols = ['sub', 'task_version', 'condition', 'group']

phq9_cols = [f'phq9_q{i + 1}' for i in range(9)]
baseline_phq9_cols = [f"response_phq9_baseline_{i}" for i in range(10) if i != b_phq9_acheck_i]
b_phq9_rename = {o: n for o, n in zip(baseline_phq9_cols, phq9_cols)}
baseline_phq9_cols = common_cols + baseline_phq9_cols
# + [ f"rt_phq9_baseline_{i}" for i in range(10) if i != b_phq9_acheck_i])
fu_phq9_cols = [f"response_phq9_fu_{i}" for i in range(10) if i != f_phq9_acheck_i]
f_phq9_rename = {o: n for o, n in zip(fu_phq9_cols, phq9_cols)}
fu_phq9_cols = common_cols + fu_phq9_cols

oq_cols = ['responses_oq_baseline_0', 'responses_oq_baseline_1', 'rts_oq_baseline_0', 'rts_oq_baseline_1']
oq_rename = {o: n for o, n in zip(oq_cols, ['oq_mood_text', 'oq_energy_text', 'oq_mood_rt', 'oq_energy_rt'])}
oq_cols = common_cols + oq_cols

oq_pos_cols = ['responses_oq_pospert_0', 'rts_oq_pospert_0']
oq_pos_rename = {o: n for o, n in zip(oq_pos_cols, ['oq_pospert_text', 'oq_pospert_rt'])}
oq_pos_cols = common_cols + oq_pos_cols

feedback_cols = [f"response_closed_q_feedback_{i}" for i in range(5)]
feedback_rename_cols = ['shoes', 'mood_change', 'sim_sit', 'demand', 'mood_change2']
feedback_rename = {o: n for o, n in zip(feedback_cols, feedback_rename_cols)}
feedback_cols = common_cols + feedback_cols

n_recreate = 4
n_act = 1
int_rec_cols = common_cols + [f"responses_recreate_{i}" for i in range(n_recreate)] + [f"rts_recreate_{i}" for i in
                                                                                       range(n_recreate)]
int_act_cols = common_cols + [f"responses_act_{i}" for i in range(n_act)] + [f"rts_act_{i}" for i in range(n_act)]

baseline_recall_cols = common_cols + ['responses_recall1', 'rts_recall1', 'responses_recall2', 'rts_recall2']
fu_recall_cols = common_cols + ['responses_recall3', 'rts_recall3']

sub_cols = common_cols + ['consented', 'completed', 'returned', 'code', 'attention_checks_bool', 'warning_count',
                          'date_time']
# %% Paths
task_subversion = task_subversions[0]
for task_subversion in task_subversions:
    # local_path = f"_data/{task_version}{task_subversion}/"
    external_path = f"/Volumes/DATA/UCL/online_tasks/{base_task_local}/{task_version}/_data/{task_version}{task_subversion}/"
    local_path = f"data/{study_name}/task_data/{task_version}{task_subversion}/"
    print(local_path)
    if do_local:
        data_path = local_path
    else:
        data_path = external_path

    Path(f"{data_path}processed").mkdir(parents=True, exist_ok=True)
    if data_path != local_path:
        Path(f"{local_path}processed").mkdir(parents=True, exist_ok=True)

    # %% load data
    sub_data = pd.read_csv(data_path + 'all/sub_data_ALL.csv')
    baseline_data = pd.read_csv(data_path + 'all/baseline_data_ALL.csv')
    fu_data = pd.read_csv(data_path + 'all/fu_data_ALL.csv')
    feedback_data = pd.read_csv(data_path + 'all/feedback_data_ALL.csv')
    recreate_data = pd.read_csv(data_path + 'all/recreate_data_ALL.csv')
    act_data = pd.read_csv(data_path + 'all/act_data_ALL.csv')

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

        good_idx = (sub_data['consented'] == 'Yes') & (sub_data['completed'] == 'Yes') & (
                sub_data['returned'] == 'No') & (sub_data['code'] == completion_code) & (
                           sub_data['attention_checks_bool'] == False) & (
                           sub_data['warning_count'] <= warning_threshold)

        good_pid = sub_data[good_idx]['PID']
        if good_pid.duplicated().any():
            print('duplicated')
            print(good_pid[good_pid.duplicated()])

        # subset and sort dataframes
        # subject data
        sub_data = sub_data[good_idx]
        sub_data['date_time'] = sub_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (sub_data['date_time'].astype(int) // 10 ** 9).astype(str) + '_' + sub_data['PID'].str[-5:].astype(
            str)
        # sub_ts_ids = (sub_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + sub_data['PID'].str[-5:]
        sub_data.insert(0, 'sub_ts_id', sub_ts_ids)
        sub_data = sub_data.sort_values(['sub_ts_id'], ascending=True).reset_index(drop=True)
        sub_data.insert(0, 'sub', ['sub' + str(s + 1) for s in sub_data.index])

        # baseline data
        baseline_data['date_time'] = baseline_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (baseline_data['date_time'].astype(int) // 10 ** 9).astype(str) + '_' + baseline_data['PID'].str[
            -5:]
        # sub_ts_ids = (baseline_data['date_time'].values.astype(int) // 10 ** 9).astype(str) + '_' + baseline_data[
        #                                                                                                 'PID'].str[-5:]
        baseline_data.insert(0, 'sub_ts_id', sub_ts_ids)
        baseline_data = baseline_data[baseline_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'],
                                                                                       ascending=True).reset_index(
            drop=True)
        baseline_data.insert(0, 'sub', ['sub' + str(s + 1) for s in baseline_data.index])

        # fu data
        fu_data['date_time'] = fu_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (fu_data['date_time'].astype(int) // 10 ** 9).astype(str) + '_' + fu_data['PID'].str[-5:]
        fu_data.insert(0, 'sub_ts_id', sub_ts_ids)
        fu_data = fu_data[fu_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'], ascending=True).reset_index(
            drop=True)
        fu_data.insert(0, 'sub', ['sub' + str(s + 1) for s in fu_data.index])

        # feedback data
        feedback_data['date_time'] = feedback_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (feedback_data['date_time'].astype(int) // 10 ** 9).astype(str) + '_' + feedback_data['PID'].str[
            -5:]
        feedback_data.insert(0, 'sub_ts_id', sub_ts_ids)
        feedback_data = feedback_data[feedback_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'],
                                                                                       ascending=True).reset_index(
            drop=True)
        feedback_data.insert(0, 'sub', ['sub' + str(s + 1) for s in feedback_data.index])

        # recreate data
        recreate_data['date_time'] = recreate_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (recreate_data['date_time'].astype(int) // 10 ** 9).astype(str) + '_' + recreate_data['PID'].str[
            -5:]
        recreate_data.insert(0, 'sub_ts_id', sub_ts_ids)
        recreate_data = recreate_data[recreate_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'],
                                                                                       ascending=True).reset_index(
            drop=True)
        recreate_data.insert(0, 'sub', ['sub' + str(s + 1) for s in recreate_data.index])

        # act data
        act_data['date_time'] = act_data['date_time'].astype('datetime64[ns]')
        sub_ts_ids = (act_data['date_time'].astype(int) // 10 ** 9).astype(str) + '_' + act_data['PID'].str[-5:]
        act_data.insert(0, 'sub_ts_id', sub_ts_ids)
        act_data = act_data[act_data['PID'].isin(good_pid)].sort_values(['sub_ts_id'], ascending=True).reset_index(
            drop=True)
        act_data.insert(0, 'sub', ['sub' + str(s + 1) for s in act_data.index])

        # PHQ-9
        phq9_data_b = baseline_data[baseline_phq9_cols].rename(columns=b_phq9_rename).melt(id_vars=common_cols,
                                                                                           value_vars=phq9_cols,
                                                                                           value_name='score_b',
                                                                                           var_name='question')

        phq9_data_f = fu_data[fu_phq9_cols].rename(columns=f_phq9_rename).melt(id_vars=common_cols,
                                                                               value_vars=phq9_cols,
                                                                               value_name='score_fu',
                                                                               var_name='question')

        phq9_data = pd.merge(phq9_data_b, phq9_data_f, on=['sub', 'task_version', 'condition', 'group', 'question'])
        phq9_data.insert(phq9_data.shape[-1], 'score_diff', phq9_data['score_fu'] - phq9_data['score_b'])
        phq9_data.insert(phq9_data.shape[-1], 'score_diff_rel',
                         (phq9_data['score_fu'] - phq9_data['score_b']) / (phq9_data['score_b'] + 1e-5))

        phq9_data['sub'] = phq9_data['sub'] + '_' + phq9_data['task_version'].str.replace('qs-intervention-', '')

        # open-ended
        openq_data = baseline_data[oq_cols].rename(columns=oq_rename)
        pospert_data = fu_data[oq_pos_cols].rename(columns=oq_pos_rename)
        openq_data = pd.merge(openq_data, pospert_data, on=['sub', 'task_version', 'condition', 'group'])
        openq_data['sub'] = openq_data['sub'] + '_' + openq_data['task_version'].str.replace('qs-intervention-', '')
        reordered_cols = [c for c in openq_data.columns if '_rt' not in c] + [c for c in openq_data.columns if
                                                                              '_rt' in c]
        openq_data = openq_data[reordered_cols]

        # feedback data
        feedback_data = feedback_data[feedback_cols].rename(columns=feedback_rename)
        feedback_data['sub'] = feedback_data['sub'] + '_' + feedback_data['task_version'].str.replace(
            'qs-intervention-', '')

        # intervention data
        int_data = pd.merge(recreate_data[int_rec_cols], act_data[int_act_cols],
                            on=['sub', 'task_version', 'condition', 'group'])
        reordered_cols = [c for c in int_data.columns if 'rts_' not in c] + [c for c in int_data.columns if 'rts_' in c]
        int_data = int_data[reordered_cols]
        int_data['sub'] = int_data['sub'] + '_' + int_data['task_version'].str.replace('qs-intervention-', '')

        # recall data
        recall_data = pd.merge(baseline_data[baseline_recall_cols], fu_data[fu_recall_cols],
                               on=['sub', 'task_version', 'condition', 'group'])
        reordered_cols = [c for c in recall_data.columns if 'rts_' not in c] + [c for c in recall_data.columns if
                                                                                'rts_' in c]
        recall_data = recall_data[reordered_cols]
        recall_data['sub'] = recall_data['sub'] + '_' + recall_data['task_version'].str.replace('qs-intervention-', '')

        sub_keys = sub_data[
            ['sub', 'sub_ts_id', 'PID', 'UID', 'ST_ID', 'SE_ID', 'task_version', 'date', 'time', 'date_time']]
        if save_external:
            sub_keys.to_csv(f"{data_path}/processed/sub_keys.csv", index=False)

        sub_data = sub_data[sub_cols]
        sub_data['sub'] = sub_data['sub'] + '_' + sub_data['task_version'].str.replace('qs-intervention-', '')

        # save stuff
        if save_external:
            sub_data.to_csv(f"{data_path}/processed/sub_data.csv", index=False)
            phq9_data.to_csv(f"{data_path}/processed/phq9_data.csv", index=False)
            openq_data.to_csv(f"{data_path}/processed/openq_data.csv", index=False)
            feedback_data.to_csv(f"{data_path}/processed/feedback_data.csv", index=False)
            int_data.to_csv(f"{data_path}/processed/int_data.csv", index=False)
            recall_data.to_csv(f"{data_path}/processed/recall_data.csv", index=False)
        if local_path != data_path:
            sub_data.to_csv(f"{local_path}/processed/sub_data.csv", index=False)
            phq9_data.to_csv(f"{local_path}/processed/phq9_data.csv", index=False)
            openq_data.to_csv(f"{local_path}/processed/openq_data.csv", index=False)
            feedback_data.to_csv(f"{local_path}/processed/feedback_data.csv", index=False)
            int_data.to_csv(f"{local_path}/processed/int_data.csv", index=False)
            recall_data.to_csv(f"{local_path}/processed/recall_data.csv", index=False)
