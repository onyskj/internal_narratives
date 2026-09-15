# %% Import libs
import os, re,sys
from scipy import stats
import pandas as pd
from natsort import natsorted
import torch
import random

import matplotlib

torch.set_grad_enabled(False)

if sys.platform == 'darwin':
    # matplotlib.use('Qt5Agg')
    matplotlib.use('TkAgg')
    device_name = 'mps'
    import matplotlib.pyplot as plt

    plt.ion()
else:
    matplotlib.use('Agg')
    # matplotlib.use('TkAgg')
    matplotlib.get_backend()
    device_name = 'cuda'
    import matplotlib.pyplot as plt

from _objects.model_configs import *
from _objects.configs import *
from _objects.plot_config import *
from _objects.qs_maps import maps, QsConfig

from scripts.b_ssae.perturbation.perturb_utils import load_pert_logits

qs_config = QsConfig()
pc = PlotConfig()

bools = Bools()
bools.do_zscores = True
bools.loadMe = True
bools.saveMe = False
bools.goodSub = True

study_name = 'b_ssae'
base_study_name = 'a_open_qs'
sampling_path = 'llm_sampling/'
analysis_path = 'perturbation/'
exp_name = 'SAE_exp_v3_best'
model_name = 'gemma2-9b-it'
# model_name = 'gemma2-2b-it'
to_sample_qs = 'phq9'
phq9_q_names = ['phq9_q' + str(q + 1) + 's' for q in range(9)]

ds_type = 'val'

# Set paths
paths = Paths()
paths.plots_path = f'outputs/{study_name}/plots/{analysis_path}'
paths.base_output_path = f'outputs/{study_name}/training/'
paths.model_dir = f'{paths.base_output_path}saved_models/{exp_name}/{model_name}/'
paths.data_path = f'data/{study_name}/'
paths.files_path_o = f'outputs/{base_study_name}/{sampling_path}files_logits/paired/'
paths.files_path_p = f'outputs/{study_name}/{analysis_path}files_logits_perturbed_{ds_type}/paired/'

# %% Load configs and logits
sample_config = SampleLogitsConfig(paths, model_name=model_name, qs_name='phq9', instr_name='instr3')
sample_config.gen_fname = 'gb'
sample_config.permute_labels = False
sample_config.label_letters = None
label_letters = list(string.ascii_uppercase)[:qs_config.qs_n_lab[to_sample_qs]]
q_scores = list(maps[to_sample_qs].values())

if sample_config.permute_labels:
    tmp_zip = list(zip(q_scores, label_letters))
    random.shuffle(tmp_zip)
    q_scores, label_letters = zip(*tmp_zip)
sample_config.label_letters = label_letters
sample_config.q_scores = q_scores
sample_config.label_scores = {k: v for k, v in zip(label_letters, q_scores)}

paths.responses_path = f"{paths.files_path_p}{''.join(sample_config.label_letters)}/subjects"
paths.save_path = f"{paths.files_path_p}{''.join(sample_config.label_letters)}/"
Path(paths.save_path).mkdir(parents=True, exist_ok=True)

scores_logits_wide, scores_logits = load_pert_logits(paths, sample_config, bools, ds_type)
# %% Evaluate effect sizes
q_names = natsorted(scores_logits['question'].unique())
q_names = [n for n in q_names if 'lvl3' in n]
steer_mlts = natsorted(scores_logits['hs_steer_mlt'].unique())
steer_mlts = [f'steer_mlt_{s}' for s in
              sorted([float(s.split('_')[-1]) for s in steer_mlts if s != 'steer_mlt_0.0'])]
store_effects = []
for q, q_name in enumerate(q_names):
    q_s_resp_wide = scores_logits_wide[scores_logits_wide['question'] == q_name]
    q_name_short = re.sub('lvl.*_', '', q_name).upper()
    for pc.i, steer_mlt in enumerate(steer_mlts):

        if steer_mlt == 'steer_mlt_0.0':
            continue
        steer_mlt_val = float(steer_mlt.split('_')[-1])

        tmp_diffs = q_s_resp_wide[f'diff_{steer_mlt}'].values
        tmp_std = np.std(tmp_diffs)
        val_comp = float(steer_mlt.split('_')[-1]) < 0
        d_eff = (tmp_diffs.mean() - 0) / tmp_std
        test_type = 'less' if val_comp else 'greater'
        tv, p_res = stats.ttest_1samp(tmp_diffs, popmean=0, alternative=test_type)

        tmp_dict = {'q_name': q_name, 'steer_value': steer_mlt_val,
                    'direction': 'More severe' if steer_mlt_val > 0 else 'Less severe', 'effect': d_eff, 'p-val': p_res}
        store_effects.append(tmp_dict)
store_effects = pd.DataFrame(store_effects)

# %% Find the steer multiplier corresponding to the largest absolute effect for each direction
average_effects = store_effects.groupby(['steer_value', 'direction'], as_index=False)['effect'].mean()
idx = average_effects['effect'].abs().groupby(average_effects['direction']).idxmax()
best_effect = average_effects.loc[idx, ['direction', 'steer_value', 'effect']]
print(best_effect)
