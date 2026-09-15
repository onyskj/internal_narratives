from natsort import natsorted
from _utils.utils import percentile, spearmanr_pval
from scipy.stats import spearmanr, pearsonr
from scripts.a_open_qs.main_analysis.analysis_utils import get_sub_cov_measures, get_model_cov_measures, compare_cov_measures, \
    return_good_sub

import numpy as np
import pandas as pd
import re
from _objects.qs_maps import QsConfig

qs_config = QsConfig()


# bootstrap participants covariance and compute correlations and SVD-based measures
def bootstrap_ssae_covs(best_gen_preds, gen_qs, paths, sample_config, task_v, n_boot=1000, alpha=0.05):
    """
    Generates similarity measures between model-based and participant-based covariance
    matrices through bootstrapping techniques.

    This method performs multiple operations, including data extraction, Pearson correlation
    computations, and covariance measurements. Then, a bootstrapping process is used to
    derive distributional statistics for participant and model covariance matrices. Finally,
    it calculates covariance differences and outputs both the averaged differences and
    dimensional similarity metrics.

    :param best_gen_preds: Data containing the best predictions from the generalisation sampling.
    :param gen_qs: String identifier for the generalisation questions to process.
    :param paths: Object containing paths to the required data sources.
    :param sample_config: Configuration object defining model and sample parameters.
    :param task_v: Specifies the task version to filter for in the data subset.
    :param n_boot: The number of bootstrap iterations to perform. Default is 1000.
    :param alpha: The alpha level for percentile-based confidence intervals. Default is 0.05.
    :return: A dictionary containing:
             - Differences between participant-driven and model-driven covariance matrices.
             - Dimension-specific metrics from the comparison of subspace structures.
    """
    good_sub = return_good_sub(paths, task_v)
    good_sub = set(good_sub).intersection(best_gen_preds['sub'].unique())

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

    # get totals correlations
    responses_mean = best_gen_preds.sort_values(by=['sub', 'q_name_context', 'q_name']).reset_index(drop=True)
    responses_sum = \
        responses_mean.groupby(['sub', 'q_name_context'], as_index=False)['score_ssae'].sum().groupby(['sub'],
                                                                                                      as_index=False)[
            'score_ssae'].mean()
    responses_sum = responses_sum.rename(columns={'score_ssae': 'total_ssae'})
    phq9_data_long = phq9_data.melt(id_vars=['sub'], value_name='score')

    phq9_data_sum = phq9_data_long.groupby(['sub'], as_index=False)['score'].sum()
    phq9_data_sum.rename(columns={'score': 'total_sub'}, inplace=True)
    totals_sub_llm = pd.merge(responses_sum, phq9_data_sum, on=['sub'])

    r_totals, p_totals = pearsonr(totals_sub_llm['total_ssae'], totals_sub_llm['total_sub'])

    # wide df of llm responses
    responses_mean_wide = responses_mean.pivot(index='sub', columns=['q_name_context', 'q_name'], values='score_ssae')
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
    metric_names = ['U_avg_angle', 'U_P_sim', 'V_avg_angle', 'V_P_sim', 'sigma_error', 'sigma_error_inv']

    space_sim_metrics_df_avg = space_sim_metrics_df.groupby(['model_name', 'gen_qs', 'k', 'p_th'], as_index=False)[
        metric_names].mean()
    space_sim_metrics_df_lb = space_sim_metrics_df.groupby(['model_name', 'gen_qs', 'k', 'p_th'], as_index=False)[
        metric_names].agg(percentile(alpha / 2))
    space_sim_metrics_df_ub = space_sim_metrics_df.groupby(['model_name', 'gen_qs', 'k', 'p_th'], as_index=False)[
        metric_names].agg(percentile(1 - alpha / 2))

    space_dim_dict = {'ss_avg': space_sim_metrics_df_avg, 'ss_ub': space_sim_metrics_df_ub,
                      'ss_lb': space_sim_metrics_df_lb}

    diff_cov_avg = np.mean(diff_covs, axis=0)

    diff_covs_abs = np.abs(np.array(diff_covs))
    diff_covs_abs_avg = np.mean(diff_covs_abs, axis=0)
    diff_cov_abs_lb = np.percentile(diff_covs_abs, alpha / 2 * 100, axis=0)
    diff_cov_abs_ub = np.percentile(diff_covs_abs, (1 - alpha / 2) * 100, axis=0)

    diff_cov_dict = {'avg': diff_cov_avg, 'abs_avg': diff_covs_abs_avg, 'abs_lb': diff_cov_abs_lb,
                     'abs_ub': diff_cov_abs_ub, 'r_totals': r_totals}
    return diff_cov_dict | space_dim_dict


# get item-level correlations on ground-truth dataset between phq9 and phq8 for sae preds
def get_corrs_gen_wphq9_ssae(best_gen_preds, paths, gen_qs, context_names, q_names, task_v):
    """
    Computes Spearman rank correlations and corresponding p-values between PHQ-9 scores and ssae estimated question scores
    for specific tasks and conditions.

    This function first processes PHQ-9 data to select data meeting the specified task version criteria. It then
    combines PHQ-9 scores with other related question scores and computes the Spearman rank correlations
    and their p-values. Adjusted p-values are calculated for multiple comparisons. The results include
    both complete correlation matrices and subsections specific to PHQ-9 and generated question scores.

    :param best_gen_preds: DataFrame containing the best ssae predictions for subjects.
    :param paths: Namespace of data paths required for file input.
    :param gen_qs: String indicating the type of generated questions to compute correlations with
        (e.g., 'phq9', other predefined types).
    :param context_names: List of strings representing open-ended question names used for adjusting p-values
        or interpretation in the analysis.
    :param q_names: List of question names (e.g., PHQ-9 question identifiers) included in the correlation analysis.
    :param task_v: List of task version identifiers for filtering PHQ-9 data.

    :return: Tuple containing the following elements:
        - Full Spearman rank correlation matrix as a DataFrame.
        - Subsection of the correlation matrix focusing on PHQ-9 and generated question scores as a DataFrame.
        - Full matrix of p-values corresponding to the Spearman correlation matrix as a DataFrame.
        - Subsection of the p-value matrix corresponding to the PHQ-9 and generated question subset as a DataFrame.
    """
    phq9_data = pd.read_csv(f"{paths.data_path}/phq9_data.csv")
    phq9_data = phq9_data[phq9_data['task_version'].isin(task_v)]
    phq9_data = pd.melt(phq9_data, id_vars=['sub'], value_vars=['phq9_q' + str(q + 1) + 's' for q in range(9)],
                        var_name='q_name', value_name='score')
    phq9_data['q_name'] = phq9_data['q_name'].str.replace('s', '', )

    phq9_data = phq9_data[~phq9_data.isna().any(axis=1)]
    phq9_data = phq9_data[phq9_data['sub'].isin(best_gen_preds['sub'].unique())]

    if gen_qs == 'phq9':
        closed_data_long = phq9_data.copy()
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
