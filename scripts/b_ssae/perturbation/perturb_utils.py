import spgl1
import os
import pandas as pd
import torch
import numpy as np
from natsort import natsorted

# from sae_model_perturb import latent_qs_perturbed

torch.set_grad_enabled(False)



def get_perturb_delta(model_sae, deltaS_fp, q_idx_to_perturb=1, score_change=1, saveDelta=False,
                      loadDelta=True, device_name='cpu'):
    """
    Computes or retrieves a perturbation vector (`deltaS`) based on the provided parameters. The perturbation
    vector can either be loaded from a file or computed using a sparse recovery technique. The computation
    is performed based on a change in score for a specified index in the projection vector, using the SPGL solver.

    :param model_sae: Model object that contains the projection weights (`W_proj`). This parameter is used
        when computing the perturbation vector.
    :param deltaS_fp: File path for saving or loading the perturbation vector (`deltaS`). When `loadDelta`
        is set to `True`, the vector is loaded from the file at this location. Otherwise, it is saved here
        when `saveDelta` is set to `True`.
    :param q_idx_to_perturb: Index in the projection vector to apply the score change. This is used during
        the computation of the perturbation vector. Defaults to 1.
    :param score_change: Numeric value representing the magnitude of the score change to apply. This is
        relevant for computing the perturbation vector. Defaults to 1.
    :param saveDelta: If set to `True`, saves the computed perturbation vector to the file specified in
        `deltaS_fp`. Defaults to `False`.
    :param loadDelta: If set to `True`, loads the perturbation vector from the file specified in `deltaS_fp`.
        If `False`, computes the vector instead. Defaults to `True`.
    :return: The perturbation vector (`deltaS`) in the form of a `torch.Tensor`. This vector can be used for
        further downstream tasks or analysis.
    :rtype: torch.Tensor
    """
    if loadDelta:
        deltaS = torch.load(deltaS_fp, map_location=torch.device(device_name)).to(device_name)
    else:
        W_proj = model_sae.W_proj.to('cpu').detach().numpy()
        delta_q = np.zeros(model_sae.W_proj.shape[1])
        delta_q[q_idx_to_perturb] = score_change
        deltaS, resid, grad, info = spgl1.spg_bp(W_proj.T, delta_q, verbosity=0, iter_lim=5000)
        solver_status = info['stat']
        if not solver_status:
            print(f'Solver status: {solver_status == 1}, for: {deltaS}')
        deltaS = torch.tensor(deltaS).type(torch.float32).to(device_name)
        if saveDelta:
            torch.save(deltaS, deltaS_fp)

    return deltaS


def load_pert_logits(paths, sample_config, bools, ds_type):
    """
    Loads and processes logits from CSV files for both original and perturbed data. This function processes
    response files to compute expected scores, combines data into a unified structure, and optionally saves the
    results to disk or loads them if they are already saved.

    :param paths: An object containing various directory paths, such as the paths for responses, files,
        and save locations.
    :param sample_config: A configuration object containing properties such as the label letters and model
        name required for filtering and processing responses.
    :param bools: An object with boolean flags determining whether to save or load the processed outputs.
    :param ds_type: A string representing dataset type used as part of the file naming conventions. (test/val)
    :return: A tuple containing two pandas DataFrames:
        - First dataframe contains pivoted wide-format logits responses with computed differences for
          perturbed scores.
        - Second dataframe contains combined original and perturbed logits responses in long format.
    """
    rsp_gr_cols = ['sub', 'question', 'model', 'latent_q_score_change', 'latent_p_force', 'q_to_perturb',
                   'hs_steer_mlt', 'instr_name', 'qs', 'label_perm', 'nSamples']
    rsp_gr_org_cols = ['sub', 'question', 'model', 'instr_name', 'qs', 'label_perm', 'nSamples']
    pert_cols = ['latent_q_score_change', 'latent_p_force', 'q_to_perturb', 'hs_steer_mlt']

    if not bools.loadMe:
        subs = natsorted([d for d in os.listdir(paths.responses_path) if '.DS_Store' not in d])
        original_logits_path_dir = f"{paths.files_path_o}{''.join(sample_config.label_letters)}/subjects"

        perturbed_logit_responses = []
        for sub in subs:
            sub_path = f"{paths.responses_path}/{sub}"
            qs = natsorted([d for d in os.listdir(sub_path) if '.DS_Store' not in d])
            for q in qs:
                sub_q_path = f"{sub_path}/{q}/"
                spec = [d for d in os.listdir(sub_q_path) if '.DS_Store' not in d and sample_config.model_name_rp in d]
                if len(spec) > 0:
                    spec = spec[0]
                    csv_files = [f for f in os.listdir(f"{sub_q_path}/{spec}") if '.csv' in f and 'logits' in f]
                    if len(csv_files) > 0:
                        for csv_file in csv_files:
                            tmp_df = pd.read_csv(f"{sub_q_path}/{spec}/{csv_file}")
                            tmp_expected_score = tmp_df['probs'].values.T @ tmp_df['label_scores']
                            tmp_exp_df = tmp_df[rsp_gr_cols].head(1)
                            tmp_exp_df['score'] = tmp_expected_score
                            perturbed_logit_responses.append(tmp_exp_df)
        perturbed_logit_responses = pd.concat(perturbed_logit_responses)
        perturbed_logit_responses = perturbed_logit_responses[perturbed_logit_responses['hs_steer_mlt'] != 0]

        original_logit_responses = []
        for sub in subs:
            sub_path = f"{original_logits_path_dir}/{sub}"
            qs = natsorted([d for d in os.listdir(sub_path) if '.DS_Store' not in d])
            for q in qs:
                sub_q_path = f"{sub_path}/{q}/"
                spec = [d for d in os.listdir(sub_q_path) if '.DS_Store' not in d and sample_config.model_name_rp in d]
                if len(spec) > 0:
                    spec = spec[0]
                    csv_files = [f for f in os.listdir(f"{sub_q_path}/{spec}") if '.csv' in f and 'logits' in f]
                    if len(csv_files) > 0:
                        for csv_file in csv_files:
                            tmp_df = pd.read_csv(f"{sub_q_path}/{spec}/{csv_file}")
                            tmp_expected_score = tmp_df['probs'].values.T @ tmp_df['label_scores']
                            tmp_exp_df = tmp_df[rsp_gr_org_cols].head(1)
                            tmp_exp_df['score'] = tmp_expected_score
                            original_logit_responses.append(tmp_exp_df)
        original_logit_responses = pd.concat(original_logit_responses)
        original_logit_responses[pert_cols] = 0

        logits_responses = pd.concat([original_logit_responses, perturbed_logit_responses]).sort_values(
            ['sub', 'question', 'hs_steer_mlt']).reset_index(drop=True)
        logits_responses['hs_steer_mlt'] = logits_responses['hs_steer_mlt'].apply(lambda x: 'steer_mlt_' + str(x))
        logits_responses_wide = pd.pivot(logits_responses, index=rsp_gr_org_cols, columns='hs_steer_mlt',
                                         values='score').reset_index()
        steer_cols = [c for c in logits_responses_wide.columns if 'steer_mlt' in c and c != 'steer_mlt_0.0']
        for steer_col in steer_cols:
            logits_responses_wide['diff_' + steer_col] = logits_responses_wide[steer_col] - logits_responses_wide[
                'steer_mlt_0.0']

        if bools.saveMe:
            logits_responses_wide.to_csv(
                f"{paths.save_path}logits_base_and_pert_exp_scores_wide_{ds_type}_{sample_config.model_name}.csv",
                index=False)
            logits_responses.to_csv(
                f"{paths.save_path}logits_base_and_pert_exp_scores_{ds_type}_{sample_config.model_name}.csv",
                index=False)
    else:
        logits_responses_wide = pd.read_csv(
            f"{paths.save_path}logits_base_and_pert_exp_scores_wide_{ds_type}_{sample_config.model_name}.csv")
        logits_responses = pd.read_csv(
            f"{paths.save_path}logits_base_and_pert_exp_scores_{ds_type}_{sample_config.model_name}.csv")

    return logits_responses_wide, logits_responses
