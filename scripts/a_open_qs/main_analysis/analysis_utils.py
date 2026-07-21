# %% Import libs
import os
import re

import numpy as np
import pandas as pd
from natsort import natsorted
from scipy.stats import spearmanr, pearsonr

from _objects.data_configs import min_word_oq_analyse_s1
from _utils.utils import percentile, spearmanr_pval


# %% Functions used for main analysis

# Select list of subjects based on exclusion criteria
def return_good_sub(paths, task_v, report_vars=None):
    """
    Return a list of valid participants filtered based on missing data and specific conditions.

    This function processes multiple data files and identifies participants with incomplete or
    invalid data based on specified criteria (e.g., missing answers, too few words, etc.).
    It then separates valid participants from those deemed invalid. The function also updates
    statistical metrics if a `report_vars` object is provided and returns the final list
    of valid participants.

    :param paths: Object containing paths to the required data files.
    :param task_v: List of task versions to be included in the analysis.
    :param report_vars: Optional object for tracking statistical summaries of valid and invalid participants.
    :return: List of participant identifiers considered valid after data filtering.
    """
    phq9_data = pd.read_csv(f"{paths.data_path}/phq9_data.csv")
    gad7_data = pd.read_csv(f"{paths.data_path}/gad7_data.csv")
    sds_data = pd.read_csv(f"{paths.data_path}/sds_data.csv")
    openq_data_long = pd.read_csv(f'{paths.data_path}/openq_data_long.csv')
    # openq_data_long = pd.read_csv(f'{qs_str_dat_dir}/openq_data_long.csv')
    lvl1_closed_data = pd.read_csv(f"{paths.data_path}/lvl1_closed_data.csv")
    lvl2_closed_data = pd.read_csv(f"{paths.data_path}/lvl2_closed_data.csv")

    openq_data_long = openq_data_long[openq_data_long['task_version'].isin(task_v)]
    phq9_data = phq9_data[phq9_data['task_version'].isin(task_v)]
    sds_data = sds_data[sds_data['task_version'].isin(task_v)]
    gad7_data = gad7_data[gad7_data['task_version'].isin(task_v)]
    lvl1_closed_data = lvl1_closed_data[lvl1_closed_data['task_version'].isin(task_v)]
    lvl2_closed_data = lvl2_closed_data[lvl2_closed_data['task_version'].isin(task_v)]

    init_subs = list(set(phq9_data['sub'].to_list()))
    phq9_cols = [f'phq9_q{q + 1}s' for q in range(9)]
    nan_phq9_subs = phq9_data[phq9_data[phq9_cols].isna().any(axis=1)]['sub'].to_list()
    gad7_cols = [f'gad7_q{q + 1}s' for q in range(7)]
    nan_gad7_subs = gad7_data[gad7_data[gad7_cols].isna().any(axis=1)]['sub'].to_list()
    sds_cols = [f'sds_q{q + 1}s' for q in range(20)]
    nan_sds_subs = sds_data[sds_data[sds_cols].isna().any(axis=1)]['sub'].to_list()
    qs_list = ['lvl3_q1', 'lvl3_q2', 'lvl3_q3', 'lvl3_q4', 'lvl3_q5', 'lvl3_q6', 'lvl3_q7', 'lvl3_q8']
    openq_data_long = openq_data_long[openq_data_long['question'].isin(qs_list)]
    openq_data_long = openq_data_long.replace(r'\s+\.', '.', regex=True)
    openq_data_long = openq_data_long.replace(r'\s+,', ', ', regex=True)
    openq_data_long = openq_data_long.replace(r'\n+,', ' ', regex=True)
    openq_data_long['response'] = openq_data_long['response'].astype(str)
    openq_data_long['n_words'] = openq_data_long['response'].apply(lambda x: len(x.split()))
    # lvl1_closed_cols = [f'lvl1_closed_q{q + 1}s' for q in range(1)]
    # nan_lvl1_closed_subs = lvl1_closed_data[lvl1_closed_data[lvl1_closed_cols].isna().any(axis=1)]['sub'].to_list()
    # lvl2_closed_cols = [f'lvl2_closed_q{q + 1}s' for q in range(3)]
    # nan_lvl2_closed_subs = lvl2_closed_data[lvl2_closed_data[lvl2_closed_cols].isna().any(axis=1)]['sub'].to_list()
    bad_openq_subs = list(openq_data_long[openq_data_long['n_words'] < min_word_oq_analyse_s1]['sub'].unique())

    # with open(f"paper_stats/paper_stats.tex", "a") as f:  # 'a' appends to the file so you don't overwrite other vars
    #     f.write(f"\\newcommand{{\\NumBadOpenQSubs}}{{{len(bad_openq_subs)}}}\n")

    # print(f"Exported \\NumBadOpenQSubs = {num_bad_subs}")

    # bad_subs = list(
    #     set(nan_phq9_subs + nan_sds_subs + nan_gad7_subs + nan_lvl1_closed_subs + nan_lvl2_closed_subs + bad_openq_subs))
    bad_subs = list(
        set(nan_phq9_subs + nan_sds_subs + nan_gad7_subs + bad_openq_subs))
    bad_subs_ssae = list(
        set(nan_phq9_subs + bad_openq_subs))
    good_subs = [sub for sub in init_subs if sub not in bad_subs]
    good_subs_ssae = [sub for sub in init_subs if sub not in bad_subs_ssae]
    if report_vars is not None:
        report_vars.sOne_nAll = len(openq_data_long['sub'].unique())
        report_vars.sOne_nFinal = len(good_subs)
        report_vars.sSAE_nFinal = len(good_subs_ssae)
        report_vars.sOne_n_bad_openq_subs = len(bad_openq_subs)
        report_vars.sOne_nan_phq_subs = len(nan_phq9_subs)
        report_vars.sOne_nan_gad_subs = len(nan_gad7_subs)
        report_vars.sOne_nan_sds_subs = len(nan_sds_subs)

    return good_subs


# load item level response and combine + means
def process_logits_itemLevel(sample_config, paths, bools, task_v, phq9_qs_inv_map):
    """
    Processes logits at the item level by loading and processing participant responses,
    calculating mean scores, and merging LLM responses with closed responses data.

    :param sample_config: Configuration object containing model-specific settings.
    :param paths: Object containing paths for response files, save directories, and data files.
    :param bools: Object with boolean flags to control data loading, processing, and saving behaviors.
    :param task_v: Task version or identifier for filtering specific tasks.
    :param phq9_qs_inv_map: Dictionary mapping PHQ-9 question short names to descriptive names.
    :return: A tuple containing the merged DataFrame of average responses and an array of unique question names.
    """
    good_sub = return_good_sub(paths, task_v)
    if not bools.loadMe:
        # if task_v == '':
        # task_v_name = task_v
        subs = [d for d in os.listdir(paths.responses_path) if
                '.DS_Store' not in d and any([v == '_'.join(d.split('_')[1:]) for v in task_v])]

        store_responses = []
        for sub in subs:
            sub_path = f"{paths.responses_path}/{sub}"
            qs = [d for d in os.listdir(sub_path) if '.DS_Store' not in d]
            for q in qs:
                sub_q_path = f"{sub_path}/{q}/"
                spec = [d for d in os.listdir(sub_q_path) if '.DS_Store' not in d and sample_config.model_name_rp in d]
                if len(spec) > 0:
                    spec = spec[0]
                    csv_files = [f for f in os.listdir(f"{sub_q_path}/{spec}") if '.csv' in f]
                    csv_file = [f for f in csv_files if 'responses' in f]
                    if len(csv_file) > 0:
                        tmp_df = pd.read_csv(f"{sub_q_path}/{spec}/{csv_file[0]}")
                        store_responses.append(tmp_df)
                    # for csv_file in csv_files:
                    #     tmp_df = pd.read_csv(f"{sub_q_path}/{spec}/{csv_file}")
                    #     store_responses.append(tmp_df)
        store_responses = pd.concat(store_responses)
        if bools.goodSub:
            store_responses = store_responses[store_responses['sub'].isin(good_sub)]
        if bools.saveMe:
            # store_responses.to_csv(f"{files_path}responses/sub_llm_responses{task_v_name}.csv", index=False)
            store_responses.to_csv(
                f"{paths.save_responses_path}/sub_llm_responses_{sample_config.model_name}.csv",
                index=False)

    else:
        # store_responses = pd.read_csv(f"{files_path}responses/sub_llm_responses{task_v_name}.csv")
        store_responses = pd.read_csv(
            f"{paths.save_responses_path}/sub_llm_responses_{sample_config.model_name}.csv")

        if bools.goodSub:
            store_responses = store_responses[store_responses['sub'].isin(good_sub)]

    # % Calculate means scores to closed responses across all samples
    responses_mean = store_responses.groupby(['sub', 'question'], as_index=False)['score'].mean()
    responses_mean.rename(columns={'question': 'q_name'}, inplace=True)
    responses_mean = responses_mean[responses_mean['q_name'] != 'rep_lvl2_q1'].sort_values(
        by=['sub', 'q_name']).reset_index(drop=True)
    responses_mean.rename(columns={'question': 'q_name'}, inplace=True)

    # Load participant PHQ-9, LVL1, LVL2 closed responses data
    # PHQ9
    phq9_data = pd.read_csv(f"{paths.data_path}/phq9_data.csv")
    phq9_names = [c for c in phq9_data.columns if 'phq9_q' in c and 'phq9_q9' not in c and 's' in c]
    phq9_data_long = pd.melt(phq9_data, id_vars=['sub'], value_vars=phq9_names, var_name='q_name', value_name='score')
    phq9_data_long['q_name'] = phq9_data_long['q_name'].replace({k + 's': v for k, v in phq9_qs_inv_map.items()})

    # LVL1
    lvl1_closed_data = pd.read_csv(f"{paths.data_path}/lvl1_closed_data.csv")
    lvl1_closed_data_long = pd.melt(lvl1_closed_data, id_vars=['sub'], value_vars=['lvl1_closed_q1s'],
                                    var_name='q_name',
                                    value_name='score')
    lvl1_closed_data_long['q_name'] = lvl1_closed_data_long['q_name'].str.replace(r'_closed|s', '', regex=True)

    # LVL2
    lvl2_closed_data = pd.read_csv(f"{paths.data_path}lvl2_closed_data.csv")
    lvl2_closed_data_long = pd.melt(lvl2_closed_data, id_vars=['sub'],
                                    value_vars=['lvl2_closed_q1s', 'lvl2_closed_q2s', 'lvl2_closed_q3s', ],
                                    var_name='q_name', value_name='score')
    lvl2_closed_data_long['q_name'] = lvl2_closed_data_long['q_name'].str.replace(r'_closed|s', '', regex=True)

    # Concatenate all closed responses from participants
    closed_data_long = pd.concat([lvl1_closed_data_long, lvl2_closed_data_long, phq9_data_long],
                                 ignore_index=True).reset_index(drop=True)
    closed_data_long = closed_data_long.sort_values(by=['sub', 'q_name']).reset_index(drop=True)

    # Merge LLM and sub responses into one DF
    responses_avg_merged = pd.merge(responses_mean, closed_data_long, on=['sub', 'q_name'], how='left',
                                    suffixes=['_llm', '_sub'])

    if bools.goodSub:
        responses_avg_merged = responses_avg_merged[responses_avg_merged['sub'].isin(good_sub)]

    q_names = responses_avg_merged['q_name'].unique()

    return responses_avg_merged, q_names


# load cross piarwise responses (gen)
def retrieve_logits_genLevel(gen_qs, bools, sample_config, paths, task_v):
    """
    Retrieve and process cross (pairwise, generlaisation) logits data based on specified conditions.

    This function processes CSV files containing generation-level logits data, applies specific conditions
    for filtering and aggregation, and may save or load the processed results based on provided flags.
    The results are stored in a single data frame, which is then returned.

    :param gen_qs: Identifier for generalisatiion questionnaires
    :param bools: A container of boolean flags for controlling behavior.
    :param sample_config: Configuration object containing model-specific attributes such as
        `model_name` and `model_name_rp`.
    :param paths: Paths configuration object, including paths to generation responses,
        good subjects, and result storage directories.
    :param task_v: Task-specific identifier used for filtering or organizing data.
    :return: A data frame containing processed logits data, filtered and aggregated
        based on provided conditions.
    """
    good_sub = return_good_sub(paths, task_v)
    if not bools.loadMe:
        store_responses = []
        subs = natsorted([d for d in os.listdir(paths.gen_responses_path) if '.DS_Store' not in d])
        for sub in subs:
            sub_path = f"{paths.gen_responses_path}{sub}/"
            qs = natsorted([d for d in os.listdir(sub_path) if '.DS_Store' not in d])
            for q in qs:
                sub_q_path = f"{paths.gen_responses_path}/{sub}/{q}"
                gqs = natsorted([d for d in os.listdir(sub_q_path) if '.DS_Store' not in d])
                for gq in gqs:
                    sub_gq_path = f"{paths.gen_responses_path}/{sub}/{q}/{gq}"
                    spec = [d for d in os.listdir(sub_gq_path) if
                            '.DS_Store' not in d and sample_config.model_name_rp in d]
                    if len(spec) > 0:
                        spec = spec[0]
                        csv_file = [f for f in os.listdir(f"{sub_gq_path}/{spec}") if '.csv' in f and 'responses' in f]
                        if len(csv_file) > 0:
                            tmp_df = pd.read_csv(f"{sub_gq_path}/{spec}/{csv_file[0]}")
                            tmp_df_mean = tmp_df.groupby(
                                ['sub', 'question', 'question_gen', 'model', 'instr_name', 'qs', 'gen_qs', 'label_perm',
                                 'nSamples'], as_index=False)['score'].mean()
                            store_responses.append(tmp_df_mean)

        store_responses = pd.concat(store_responses)
        if bools.goodSub:
            store_responses = store_responses[store_responses['sub'].isin(good_sub)]
        if bools.saveMe:
            store_responses.to_csv(
                f"{paths.save_responses_path}/sub_llm_responses_gen_{gen_qs}_{sample_config.model_name}.csv",
                index=False)
    else:
        store_responses = pd.read_csv(
            f"{paths.save_responses_path}/sub_llm_responses_gen_{gen_qs}_{sample_config.model_name}.csv")

        if bools.goodSub:
            store_responses = store_responses[store_responses['sub'].isin(good_sub)]

    return store_responses


# process cros piarwise responses (gen) - means
def process_logits_genLevel(gen_qs, bools, sample_config, paths, task_v):
    """
    Processes logits at the generalisation sampling questionnaire level by merging responses from LLMs and
    subject responses, filtering based on task versions, and organizing relevant data.

    :param gen_qs: Identifier for the generalisation questionnaire data.
    :param bools: An object containing configuration flags used for selecting good subjects.
    :param sample_config: Configuration object for llm sampling for processing the samples.
    :param paths: Object containing paths to various data files and directories.
    :param task_v: List of task versions used for filtering data.
    :return: Tuple containing the merged DataFrame of averaged responses, the long-format DataFrame of
             general questionnaire data, and a list of unique question names.
    """
    good_sub = return_good_sub(paths, task_v)
    responses_mean = retrieve_logits_genLevel(gen_qs, bools, sample_config, paths, task_v)
    responses_mean.rename(columns={'question': 'q_name_context'}, inplace=True)
    responses_mean.rename(columns={'question_gen': 'q_name'}, inplace=True)
    responses_mean = responses_mean.sort_values(by=['sub', 'q_name_context', 'q_name']).reset_index(drop=True)

    # Relevant closed questionnaire data
    gen_qs_data = pd.read_csv(f"{paths.data_path}/{gen_qs}_data.csv")
    gen_qs_data = gen_qs_data[gen_qs_data['task_version'].isin(task_v)]
    gen_qs_names = [c for c in gen_qs_data.columns if gen_qs + '_q' in c and re.search("[0-9]+s", c) is not None]
    gen_qs_data_long = pd.melt(gen_qs_data, id_vars=['sub'], value_vars=gen_qs_names, var_name='q_name',
                               value_name='score')

    gen_qs_data_long['q_name'] = gen_qs_data_long['q_name'].str.slice_replace(-1, None, '')
    gen_qs_data_long = gen_qs_data_long[~gen_qs_data_long.isna().any(axis=1)]
    if bools.goodSub:
        gen_qs_data_long = gen_qs_data_long[gen_qs_data_long['sub'].isin(good_sub)]

    # Merge LLM and sub responses into one DF
    responses_avg_merged = pd.merge(responses_mean, gen_qs_data_long, on=['sub', 'q_name'], how='left',
                                    suffixes=['_llm', '_sub'])
    responses_avg_merged = responses_avg_merged[~responses_avg_merged.isna().any(axis=1)]

    q_names = responses_avg_merged['q_name'].unique()
    return responses_avg_merged, gen_qs_data_long, q_names


# Get participant ground-truth covariance structure
def get_corrs_gen_wphq9(paths, gen_qs, closed_data_long, context_names, q_names, qs_config, task_v):
    """
    Computes Spearman correlation matrices between PHQ-9 questionnaire data and scores
    from a generalisation questionnaire dataset, along with the corresponding p-values.

    :param paths: An object containing directory paths necessary for fetching data.
    :param gen_qs: A string indicating the name of the generalisation questionnaire.
    :param closed_data_long: A pandas DataFrame containing long-format closed data with
        questionnaire scores and associated metadata.
    :param context_names: A list of strings representing context names included in the
        analysis (open ended q)
    :param q_names: A list of strings representing names of questions included in the
        analysis.
    :param qs_config: An object holding configuration related to the generalized questionnaire,
        including the number of questions (`qs_n_qs`).
    :param task_v: A list of task versions to filter the PHQ-9 data.
    :return: A tuple of four pandas DataFrames containing:
        - Full correlation matrix of Spearman correlation coefficients (`cross_corr`).
        - Subset correlation matrix for PHQ-9 and generalized questionnaire questions
          (`cross_corr_subset`).
        - Full matrix of p-values corresponding to `cross_corr` (`cross_pvals`).
        - Subset p-value matrix for PHQ-9 and generalized questionnaire questions
          (`cross_pvals_subset`).
    """
    phq9_data = pd.read_csv(f"{paths.data_path}/phq9_data.csv")
    phq9_data = phq9_data[phq9_data['task_version'].isin(task_v)]
    phq9_data = phq9_data[phq9_data['sub'].isin(closed_data_long['sub'].unique())]
    phq9_data = pd.melt(phq9_data, id_vars=['sub'], value_vars=['phq9_q' + str(q + 1) + 's' for q in range(9)],
                        var_name='q_name', value_name='score')
    phq9_data['q_name'] = phq9_data['q_name'].str.replace('s', '', )

    phq9_data = phq9_data[~phq9_data.isna().any(axis=1)]

    if gen_qs == 'phq9':
        closed_data_long['q_name'] = closed_data_long['q_name'].str.replace('phq9', 'phq9_ppt')

    closed_data_long_wphq9 = pd.concat([closed_data_long, phq9_data], axis=0)
    closed_data_wphq9 = pd.pivot(closed_data_long_wphq9, index='sub', columns='q_name', values='score')
    closed_data_wphq9 = closed_data_wphq9[~closed_data_wphq9.isna().any(axis=1)]
    closed_data_wphq9 = closed_data_wphq9[natsorted(closed_data_wphq9.columns)]

    cross_corr = closed_data_wphq9.corr(method='spearman')
    cross_pvals = closed_data_wphq9.corr(method=spearmanr_pval)
    cross_pvals *= len(q_names) * len(context_names)
    cross_pvals[cross_pvals > 1] = 1

    phq9_names = ['phq9_q' + str(q + 1) for q in range(9)]
    if gen_qs == 'phq9':
        gen_qs_names = [gen_qs + '_ppt_q' + str(q + 1) for q in range(qs_config.qs_n_qs[gen_qs])]
    else:
        gen_qs_names = [gen_qs + '_q' + str(q + 1) for q in range(qs_config.qs_n_qs[gen_qs])]
    cross_corr_subset = cross_corr.loc[phq9_names, gen_qs_names]
    cross_pvals_subset = cross_pvals.loc[phq9_names, gen_qs_names]
    return cross_corr, cross_corr_subset, cross_pvals, cross_pvals_subset


# compute LLM recovered structure
def get_corrs_pvals_genq_logits(responses_avg_merged, context_names, q_names, score_col='score_llm'):
    """
    Calculates correlation coefficients, p-values, and dataset statistics for a given set of
    contexts (open-ended q) and ppts' multiple-choice scores.

    :param responses_avg_merged: A DataFrame containing merged llm response data with corresponding
                                 columns to filter on query names, context names, or other attributes.

    :param context_names: A list of context names to filter the data for correlation computation (open ended qs)

    :param q_names: A list of query names to filter the data for correlation computation (multiple choice qs)

    :param score_col: The name of the column in the DataFrame used as the dependent variable
                      for correlation calculation. Default is 'score_llm'.

    :return: A tuple containing:
             - A DataFrame with correlation coefficients, adjusted p-values, and sample sizes.
             - A pivoted wide-format DataFrame showing correlations and p-values for
               each context and query combination.
             - A string indicating the range of sample sizes across contexts and queries.
    """
    df_corr = []
    for i, context_name in enumerate(context_names):
        for j, q_name in enumerate(q_names):
            responses_avg_merged_q = responses_avg_merged[(responses_avg_merged['q_name_context'] == context_name) & (
                    responses_avg_merged[
                        'q_name'] == q_name)]  # & (responses_avg_merged['spec_level'].isin(spec_list))]

            if len(responses_avg_merged_q) > 0:
                N = len(responses_avg_merged_q['sub'].unique())
                r, p = spearmanr(responses_avg_merged_q[score_col], responses_avg_merged_q['score_sub'])
                p = min(p * len(q_names) * len(context_names), 1)
                tmp_dict = {'context_name': context_name, 'q_name': q_name, 'r': r, 'p-val': p,
                            'N': N}
                df_corr.append(tmp_dict)

    df_corr = pd.DataFrame(df_corr)
    df_corr_wide = df_corr.pivot(index='context_name', columns='q_name', values=['r', 'p-val'])
    df_corr_wide = df_corr_wide[natsorted(df_corr_wide.columns)]

    N_range = df_corr['N'].unique().min()
    if df_corr['N'].unique().max() != N_range:
        N_range = str(N_range) + '-' + str(df_corr['N'].unique().max())

    return df_corr, df_corr_wide, N_range


# calculate and compare true and recovered questionnaire totals
def responses_totals_gen_logits(responses, closed_data_long):
    """
    Calculate total scores for each subject based on LLM-response data and closed-data,
    and compute the Pearson correlation coefficient between the totals.

    This function processes response data to compute the total LLM-generated scores
    and corresponding totals from a closed dataset for each subject. It then merges
    the results and calculates the correlation between these total scores.

    :param responses: A pandas DataFrame containing LLM-generated response data. It is
        expected to have columns 'sub', 'q_name_context', and 'score_llm'.
    :param closed_data_long: A pandas DataFrame containing closed-data response scores.
        It should include columns 'sub' and 'score'.
    :return: A tuple containing:
        - totals_sub_llm (pandas DataFrame): A DataFrame with merged total scores for
          each subject from LLM responses and closed-data responses. Columns include
          'sub', 'total_llm', and 'total_sub'.
        - r (float): Pearson correlation coefficient between 'total_llm' and 'total_sub'.
        - p (float): P-value associated with the Pearson correlation.
    """
    responses_sum = \
        responses.groupby(['sub', 'q_name_context'], as_index=False)['score_llm'].sum().groupby(['sub'],
                                                                                                as_index=False)[
            'score_llm'].mean()
    responses_sum = responses_sum.rename(columns={'score_llm': 'total_llm'})

    closed_data_sum = closed_data_long.groupby(['sub'], as_index=False)['score'].sum()
    closed_data_sum.rename(columns={'score': 'total_sub'}, inplace=True)
    totals_sub_llm = pd.merge(responses_sum, closed_data_sum, on=['sub'])

    r, p = pearsonr(totals_sub_llm['total_llm'], totals_sub_llm['total_sub'])

    return totals_sub_llm, r, p


# bootstrap participants covariance and compute correlations and SVD-based measures
def bootstrap_covs(gen_qs, bools, paths, sample_config, task_v, n_boot=1000, alpha=0.05):
    """
    Performs bootstrapping to compute covariance metrics and evaluates differences in covariance measures
    between subject and llm responses.

    :param gen_qs: The generalisation questionnaire.
    :param bools: Any boolean configuration or settings, generally used for processing tasks.
    :param paths: Contains paths to various data files and directories required for analysis.
    :param sample_config: Configuration settings for the sample, including model-level information.
    :param task_v: Task version identifier or associated specifier that filters the dataset.
    :param n_boot: Number of bootstrap iterations to perform. Defaults to 1000.
    :param alpha: Significance level for calculating confidence intervals. Defaults to 0.05.
    :return: Dictionary containing calculated differences and covariance metrics, with summarized and
        confidence-bound measures.
    :rtype: dict
    """
    good_sub = return_good_sub(paths, task_v)

    phq9_data = pd.read_csv(f"{paths.data_path}/phq9_data.csv")
    phq9_data = phq9_data[phq9_data['sub'].isin(good_sub)]
    phq9_names = [c for c in phq9_data.columns if 'phq9_q' in c and 'phq9_q9' not in c and 's' in c]
    phq9_data = phq9_data[['sub'] + phq9_names]
    # phq9_data[phq9_names].columns = [n+'_p' for n in phq9_names]
    phq9_data.rename(columns={k: v for k, v in zip(phq9_names, [n + '_p' for n in phq9_names])}, inplace=True)

    gen_qs_data = pd.read_csv(f"{paths.data_path}/{gen_qs}_data.csv")
    gen_qs_data = gen_qs_data[gen_qs_data['sub'].isin(good_sub)]
    gen_qs_names = [c for c in gen_qs_data.columns if gen_qs + '_q' in c and re.search("[0-9]+s", c) is not None]
    gen_qs_data = gen_qs_data[['sub'] + gen_qs_names]
    # gen_qs_data[gen_qs_names].columns = [n+'_gen' for n in gen_qs_names]
    gen_qs_data.rename(columns={k: v for k, v in zip(gen_qs_names, [n + '_gen' for n in gen_qs_names])}, inplace=True)

    q_data = pd.merge(phq9_data, gen_qs_data, on=['sub'])
    # get llm responss
    responses_mean = retrieve_logits_genLevel(gen_qs, bools, sample_config, paths, task_v)
    responses_mean.rename(columns={'question': 'q_name_context'}, inplace=True)
    responses_mean.rename(columns={'question_gen': 'q_name'}, inplace=True)
    responses_mean = responses_mean.sort_values(by=['sub', 'q_name_context', 'q_name']).reset_index(drop=True)

    # wide df of llm responses
    responses_mean_wide = responses_mean.pivot(index='sub', columns=['q_name_context', 'q_name'], values='score')
    responses_mean_wide.columns = 'llm_' + responses_mean_wide.columns.get_level_values(
        0) + '^' + responses_mean_wide.columns.get_level_values(1)
    responses_mean_wide = responses_mean_wide[natsorted(responses_mean_wide.columns)]

    # merge into one big df sub and llm
    llm_cols = responses_mean_wide.columns.tolist()
    q_data = pd.merge(q_data, responses_mean_wide, on=['sub'])

    phq9_names = [n + '_p' for n in phq9_names]
    gen_qs_names = [n + '_gen' for n in gen_qs_names]
    # do bootstrapping
    sub_covs = []
    llm_covs = []
    diff_covs = []
    space_sim_metrics = []
    for b in range(n_boot):
        q_data_boot = q_data.sample(frac=1, replace=True)

        sub_cov = q_data_boot[phq9_names + gen_qs_names].corr(method='spearman').loc[phq9_names][
            gen_qs_names].to_numpy()
        oq_qs = [f'q{q + 1}' for q in range(8)]
        llm_cov = []
        for oq_q in oq_qs:
            oq_q_cols = [c for c in llm_cols if f'lvl3_{oq_q}' in c]
            oq_q_r = np.diag(
                q_data_boot[gen_qs_names + oq_q_cols].corr(method='spearman').loc[oq_q_cols][gen_qs_names]).tolist()
            llm_cov.append(oq_q_r)

        llm_cov = pd.DataFrame(np.array(llm_cov), index=[f'lvl3_{q}' for q in oq_qs], columns=gen_qs_names).to_numpy()

        sub_covs.append(sub_cov)
        llm_covs.append(llm_cov)
        diff_covs.append(sub_cov - llm_cov)

        scm = get_sub_cov_measures(sub_cov, p_th=0.99)
        mcm = get_model_cov_measures(llm_cov)
        cov_diff_measures = compare_cov_measures(scm, mcm)
        cov_diff_measures = {'model_name': sample_config.model_name, 'gen_qs': gen_qs, 'b': b} | cov_diff_measures
        space_sim_metrics.append(cov_diff_measures)

    space_sim_metrics_df = pd.DataFrame(space_sim_metrics)
    # metric_names = ['U_avg_angle', 'U_P_sim', 'V_avg_angle', 'V_P_sim', 'sigma_error_diag', 'sigma_error']
    metric_names = ['U_avg_angle', 'U_P_sim', 'V_avg_angle', 'V_P_sim', 'sigma_error', 'sigma_error_inv']

    space_sim_metrics_df_avg = space_sim_metrics_df.groupby(['model_name', 'gen_qs', 'k', 'p_th'], as_index=False)[
        metric_names].mean()
    space_sim_metrics_df_lb = space_sim_metrics_df.groupby(['model_name', 'gen_qs', 'k', 'p_th'], as_index=False)[
        metric_names].agg(percentile(alpha / 2))
    space_sim_metrics_df_ub = space_sim_metrics_df.groupby(['model_name', 'gen_qs', 'k', 'p_th'], as_index=False)[
        metric_names].agg(percentile(1 - alpha / 2))

    space_dim_dict = {'ss_avg': space_sim_metrics_df_avg, 'ss_ub': space_sim_metrics_df_ub,
                      'ss_lb': space_sim_metrics_df_lb}

    # sub_cov_avg = np.mean(sub_covs, axis=0)
    # llm_cov_avg = np.mean(llm_covs, axis=0)
    diff_cov_avg = np.mean(diff_covs, axis=0)

    diff_covs_abs = np.abs(np.array(diff_covs))
    diff_covs_abs_avg = np.mean(diff_covs_abs, axis=0)
    diff_cov_abs_lb = np.percentile(diff_covs_abs, alpha / 2 * 100, axis=0)
    diff_cov_abs_ub = np.percentile(diff_covs_abs, (1 - alpha / 2) * 100, axis=0)

    diff_cov_dict = {'avg': diff_cov_avg, 'abs_avg': diff_covs_abs_avg, 'abs_lb': diff_cov_abs_lb,
                     'abs_ub': diff_cov_abs_ub}
    return diff_cov_dict | space_dim_dict

    # return diff_cov_avg, diff_covs_abs, diff_cov_abs_lb, diff_cov_abs_ub


# perform SVD on subjects covariance matrix
def get_sub_cov_measures(C, p_th=0.99):
    """
    Computes subject covariance measures of a given covariance matrix by performing
    singular value decomposition (SVD). The function calculates how many of the
    largest singular values explain a specified percentage of the variance.

    :param C: Covariance matrix to analyze
    :param p_th: Threshold for explained variance as a fraction (default is 0.99)
    :return: Dictionary containing the SVD results ('U', 'S', 'Vh'), reconstructed
        diagonal matrix ('S_full'), number of principal components that explain
        the variance threshold ('k'), and the input threshold ('p_th')
    """
    # do SVD on the sub covariance
    U, S, Vh = np.linalg.svd(C, full_matrices=True)
    # find number of top correlations that explain >99% variance
    k = int(np.where((S ** 2).cumsum() / (S ** 2).sum() > p_th)[0][0]) + 1
    # print(f'\tK={k}\n')

    # reshape the diagonal S of correlations into full matrix
    rem_dim = int(np.max(C.shape) - np.min(C.shape))
    if C.shape[0] < C.shape[1]:
        S_full = np.concat([np.diag(S), np.zeros([S.shape[0], rem_dim])], axis=1)
    elif C.shape[0] > C.shape[1]:
        S_full = np.concat([np.diag(S), np.zeros([rem_dim, S.shape[0]])], axis=0)
    else:
        S_full = np.diag(S)

    sub_cov_measures = {'U': U, 'S': S, 'S_full': S_full, 'Vh': Vh, 'k': k, 'p_th': p_th}

    return sub_cov_measures


# perform SVD on model covariance
def get_model_cov_measures(C):
    """
    Decomposes a llm response covariance matrix into its singular value decomposition (SVD)
    components and returns the result in a dictionary. This function calculates
    the SVD of the input matrix `C` and returns the original matrix along with
    its decomposed components (U, S, Vh).

    :param C: The covariance matrix to decompose.
    :return: A dictionary containing the original covariance matrix and its
             decomposed SVD components.
    """
    U, S, Vh = np.linalg.svd(C, full_matrices=True)
    model_cov_measures = {'C': C, 'U': U, 'S': S, 'Vh': Vh}

    return model_cov_measures


# compare subejct and llm covariance svd-based measures
def compare_cov_measures(scm, mcm):
    """
    Compares subspace similarity, mean angles of variation, and covariance projection
    differences between two singular value decomposition (SVD) models.

    The function evaluates projection matrices of subspaces, calculates principal
    angles of variation, and assesses the similarity between projected covariance
    measurements. The metrics are derived from the singular value decomposition
    components of the llm and subjects.

    :param scm: Dictionary containing the SVD components of the participant response covariance matrix. It must
        include the keys 'U', 'Vh', 'S_full' (data covariance matrix), and 'p_th'
        (threshold parameter).
    :param mcm: Dictionary containing the SVD components of the LLM response covariance matrix. It
        must include the keys 'U', 'Vh', and 'C' (data covariance matrix).

    :return: Dictionary containing comparison metrics, including:
        - 'k': Number of components considered in the comparison.
        - 'p_th': Threshold parameter from the input `scm`.
        - 'U_avg_angle': Mean angles of the left singular vector decomposition basis.
        - 'U_P_sim': Subspace similarity for left singular vectors using the Frobenius norm ratio.
        - 'V_avg_angle': Mean angles of the right singular vector decomposition basis.
        - 'V_P_sim': Subspace similarity for right singular vectors using the Frobenius norm ratio.
        - 'sigma_error': Relative error between projected covariance measures.
        - 'sigma_error_inv': Complement (1 - error) of the projected covariance relative error.
    """
    k = scm['k']

    # 1A) Compare the projection matrices of each subspace (model vs ppt)
    # Left singular vectors U
    P_U_data = scm['U'][:, :k] @ scm['U'][:, :k].T  # data projection matrix (top k components)
    P_U_model = mcm['U'][:, :k] @ mcm['U'][:, :k].T  # model projection matrix (top k components)
    P_U_delta = P_U_data - P_U_model
    P_U_delta_norm = np.linalg.norm(P_U_delta, ord='f') / np.sqrt(2 * k)  # Frobenius norm ratio

    # 1B) Right singular vectors Vh
    P_Vh_data = scm['Vh'][:, :k] @ scm['Vh'][:, :k].T  # data projection matrix (top k components)
    P_Vh_model = mcm['Vh'][:, :k] @ mcm['Vh'][:, :k].T  # model projection matrix (top k components)
    P_Vh_delta = P_Vh_data - P_Vh_model  # (0 same subspace, 1 - orthogonal)
    P_Vh_delta_norm = np.linalg.norm(P_Vh_delta, ord='f') / np.sqrt(2 * k)  # Frobenius norm ratio

    # print(f'\tU subspace similarity: {1 - P_U_delta_norm:.3f}')
    # print(f'\tVh subspace similarity: {1 - P_Vh_delta_norm:.3f}')

    # 2) Calculate the similarity between top k basis vectors - principal angles of variation
    # pairwise correlations between basis vectors
    M_U = scm['U'][:, :k].T @ mcm['U'][:, :k]
    M_Vh = scm['Vh'][:, :k].T @ mcm['Vh'][:, :k]

    # SVD on the correlations to find principal angles
    _, sM_U, _ = np.linalg.svd(M_U)
    _, sM_Vh, _ = np.linalg.svd(M_Vh)
    sM_U_mean = sM_U.mean()
    sM_Vh_mean = sM_Vh.mean()

    # print(f'\tU mean angles: {sM_U_mean:.3f}')
    # print(f'\tVh mean angles: {sM_Vh_mean:.3f}')

    # 3) Calculate correlation between data vs llm questionnaire scores using data covariance svd
    # Calculate projected llm score correlations given data solution
    S_hat = scm['U'].T @ mcm['C'] @ scm['Vh'].T
    S_delta = S_hat - scm['S_full']
    S_F_norm = np.linalg.norm(scm['S_full'] ** 2, ord='f')
    S_hat_norm = np.linalg.norm(S_hat ** 2, ord='f')
    S_delta_F_norm = np.linalg.norm(S_delta ** 2, ord='f')

    # S_delta_F_norm_diag = np.linalg.norm(np.diag(np.diag(S_delta)) ** 2, ord='f')

    # S_error_rel = (S_delta_F_norm / S_F_norm)
    S_error_rel = (S_delta_F_norm / (S_F_norm + S_hat_norm))
    # S_error_rel_diag = (S_delta_F_norm_diag / S_F_norm)

    cov_diff_measures = {'k': k, 'p_th': scm['p_th'], 'U_avg_angle': sM_U_mean,
                         'U_P_sim': 1 - P_U_delta_norm, 'V_avg_angle': sM_Vh_mean,
                         'V_P_sim': 1 - P_Vh_delta_norm,
                         'sigma_error': S_error_rel, 'sigma_error_inv': 1 - S_error_rel}

    return cov_diff_measures
