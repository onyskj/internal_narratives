# %% Import libraries
import pickle
import os,sys
import pandas as pd
import statsmodels.formula.api as smf
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as cossim

from _utils.utils import return_p_star

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')
# matplotlib.use('Agg')
plt.ion()
import seaborn as sns

from _objects.plot_config import *
from _objects.configs import *
from _objects.qs_maps import phq9_qs

from _utils.utils import write_to_tex

if sys.platform == 'darwin':
    device_name = 'mps'
else:
    device_name = 'cuda'

report_vars = ReportVars()
pc = PlotConfig()
bools = Bools()

# set names
study_name = 'c_mood_induction'
analysis_path = 'similarity_analysis/'
fig_no = 'Fig5'

# set paths
paths = Paths()
paths.data_path = f'data/{study_name}/task_data/combined/'
paths.transcripts_path = f'data/{study_name}/transcripts/'
paths.output_path = f'outputs/{study_name}/{analysis_path}'
paths.plots_path = f'outputs/{study_name}/plots/{analysis_path}'
Path(paths.plots_path).mkdir(parents=True, exist_ok=True)
Path(paths.output_path).mkdir(parents=True, exist_ok=True)

# set bools
bools.saveMe = False
# bools.savePlot = False
bools.savePlot = True
# bools.loadEmb = False
# bools.saveEmb = True
bools.loadEmb = True
bools.saveEmb = False
bools.saveTex = False
bools.loadTextMeasures = True  # load saved similarity measures (text_measures.csv); no text or embeddings needed

# %% Load data
id_cols = ['sub', 'condition', 'group', 'autobio']
hue_order = ['MH', 'ML']
hue_cols = ['tab:blue', 'tab:orange']
hue_cols2 = ['tab:green', 'tab:purple']

sbin3_order = ['q33', 'm', 'q66']
join_cols = id_cols + ['s_bin', 's_bin3']
phq9_qs_lab = [f'phq9_q{q + 1}' for q in range(9)]

phq9_diff = pd.read_csv(f'{paths.data_path}phq9_diff_data_wide.csv')
mood_diff = pd.read_csv(f'{paths.data_path}mood_data.csv')
recall_data = pd.read_csv(f"{paths.data_path}recall_data_wide.csv")
if not bools.loadTextMeasures:
    int_data = pd.read_csv(f'{paths.data_path}int_data.csv')
    openq_data = pd.read_csv(f'{paths.data_path}openq_data.csv')

    # % Combine text data
    text_data = pd.merge(int_data, openq_data, on=join_cols)
    if bools.saveMe:
        text_data.to_csv(f"{paths.data_path}text_data.csv", index=False)
# %% Get embeddings of transcripts and PHQ9 statements
if bools.loadTextMeasures:
    pass  # similarity measures are loaded below
elif bools.loadEmb:
    with open(f'{paths.output_path}transcripts_embd.pkl', 'rb') as f:
        transcripts_embd = pickle.load(f)
    with open(f'{paths.output_path}phq9_embds.pkl', 'rb') as f:
        phq9_embds = pickle.load(f)
else:
    #  Load sentence transformer model
    model = SentenceTransformer("all-MiniLM-L6-v2", device=device_name)
    transcripts = {'MH': [], 'ML': []}
    transcripts_embd = {'MH': [], 'ML': []}
    for k, v in transcripts.items():
        with open(f"{paths.transcripts_path}{k}.txt") as f:
            for line in f:
                v.append(line)
        transcripts_embd[k] = model.encode(v)
    phq9_embds = {plab: e for plab, e in zip(phq9_qs_lab, model.encode(phq9_qs))}
    phq9_embds = model.encode(phq9_qs)

    if bools.saveEmb:
        with open(f'{paths.output_path}transcripts_embd.pkl', 'wb') as f:
            pickle.dump(transcripts_embd, f)
        with open(f'{paths.output_path}phq9_embds.pkl', 'wb') as f:
            pickle.dump(phq9_embds, f)

# %% Calculate/Load Text embeddings for recreate, intervention, open-ended mood, energy, positive re-eval
if bools.loadTextMeasures:
    pass  # similarity measures are loaded below
elif bools.loadEmb:
    with open(f'{paths.output_path}text_embd_autobio.pkl', 'rb') as f:
        embd_autobio = pickle.load(f)
    with open(f'{paths.output_path}text_embd_nonautobio.pkl', 'rb') as f:
        embd_nonautobio = pickle.load(f)
else:
    text_keys = [c for c in text_data.columns if (('recreate_' in c) or ('oq_' in c) or ('act' in c)) and ('_wc' not in c)]
    embd_autobio = {'MH': {}, 'ML': {}}
    embd_nonautobio = {'MH': {}, 'ML': {}}
    for r, row in text_data.iterrows():
        sub = row['sub']
        condition = row['condition']
        is_autobio = row['autobio']
        if is_autobio:
            embd_autobio[condition][sub] = {tk: model.encode(row[tk]) if type(row[tk]) == str else None for tk in
                                            text_keys}
        else:
            embd_nonautobio[condition][sub] = {tk: model.encode(row[tk]) if type(row[tk]) == str else None for tk in
                                               text_keys}
    if bools.saveEmb:
        with open(f'{paths.output_path}text_embd_autobio.pkl', 'wb') as f:
            pickle.dump(embd_autobio, f)
        with open(f'{paths.output_path}text_embd_nonautobio.pkl', 'wb') as f:
            pickle.dump(embd_nonautobio, f)

# %% Calcualte text features and similarities
if not bools.loadTextMeasures:
    rec_transcript_autobio_dict = {'MH': [], 'ML': []}
    rec_transcript_nonautobio_dict = {'MH': [], 'ML': []}
    rec_transcript_sim_long = pd.DataFrame()

    text_measures = []
    for r, row in text_data.iterrows():
        sub = row['sub']
        condition = row['condition']
        is_autobio = row['autobio']
        group = row['group']
        s_bin = row['s_bin']
        s_bin3 = row['s_bin3']

        if is_autobio:
            text_embd = embd_autobio[condition][sub]
        else:
            text_embd = embd_nonautobio[condition][sub]

        rec_embs = np.array([v for k, v in text_embd.items() if 'recreate' in k])
        rec_embs_avg = rec_embs.mean(axis=0, keepdims=True)
        oq_rembs = np.array([v for k, v in text_embd.items() if ('oq_' in k) and ('pospert' not in k)])
        oq_rembs_avg = oq_rembs.mean(axis=0, keepdims=True)

        # Similarity between original transcript and recreated diary
        rec_transcript_sim = cossim(rec_embs, transcripts_embd[condition])
        off_diag_sim = np.tril(rec_transcript_sim, -1)
        diag_sim = np.diag(rec_transcript_sim)

        # convert to long
        rec_transcript_sim_long_tmp = pd.DataFrame(rec_transcript_sim, index=[f'rec_diary{d + 1}' for d in range(4)],
                                                   columns=[f'org_diary{d + 1}' for d in range(4)]).reset_index(
            names=['rec_diary'])
        rec_transcript_sim_long_tmp = rec_transcript_sim_long_tmp.melt(id_vars=['rec_diary'], var_name='org_diary',
                                                                       value_name='cos_sim')
        rec_transcript_sim_long_tmp['rec_diary'] = rec_transcript_sim_long_tmp['rec_diary'].str.replace('rec_', '')
        rec_transcript_sim_long_tmp['org_diary'] = rec_transcript_sim_long_tmp['org_diary'].str.replace('org_', '')
        rec_transcript_sim_long_tmp.insert(0, 'sub', sub)
        rec_transcript_sim_long_tmp.insert(1, 'condition', condition)
        rec_transcript_sim_long_tmp.insert(2, 'group', group)
        rec_transcript_sim_long_tmp.insert(3, 'autobio', is_autobio)
        rec_transcript_sim_long = pd.concat([rec_transcript_sim_long, rec_transcript_sim_long_tmp], axis=0)

        if is_autobio:
            rec_transcript_autobio_dict[condition].append(rec_transcript_sim)
        else:
            rec_transcript_nonautobio_dict[condition].append(rec_transcript_sim)

        # Similarity between recreated and continuation
        rec_act_sim = cossim(text_embd['act_0'][:, None].T, rec_embs_avg)[0, 0]
        # Similarity between average open-ended response (mood+energy)/2 vs positive re-eval
        oq_pospert_sim = cossim(text_embd['oq_pospert'][:, None].T, oq_rembs_avg)[0, 0]
        # Open mood vs continuation
        mood_act_sim = cossim(text_embd['act_0'][:, None].T, text_embd['oq_mood'][:, None].T)[0, 0]
        # Continuation vs positive re-eval
        act_pospert_sim = cossim(text_embd['act_0'][:, None].T, text_embd['oq_pospert'][:, None].T)[0, 0]

        # Q2 phq9 statemetn vs open mood
        q2_mood_sim = cossim(phq9_embds[1][:, None].T, text_embd['oq_mood'][:, None].T)[0, 0]
        # Q2 phq9 statemetn vs act
        q2_act_sim = cossim(phq9_embds[1][:, None].T, text_embd['act_0'][:, None].T)[0, 0]
        # Q2 phq9 statemetn vs pospoert
        q2_pospert_sim = cossim(phq9_embds[1][:, None].T, text_embd['oq_pospert'][:, None].T)[0, 0]

        # collect similarities
        tmp_dict = {'sub': sub, 'condition': condition, 'group': group, 'autobio': is_autobio, 's_bin': s_bin,
                    's_bin3': s_bin3, 'avgRecAct_sim': rec_act_sim,
                    'avgBaselinePospert_sim': oq_pospert_sim, 'moodBaselineAct_sim': mood_act_sim,
                    'actPospert_sim': act_pospert_sim, 'q2Mood_sim': q2_mood_sim, 'q2Act_sim': q2_act_sim,
                    'q2Pospert_sim': q2_pospert_sim}
        text_measures.append(tmp_dict)

    # same diary or different?
    rec_transcript_sim_long['is_same'] = rec_transcript_sim_long['rec_diary'] == rec_transcript_sim_long['org_diary']

    # Calculate average similarity between transcripts and recreated texts
    rec_transcript_dict = {'MH': rec_transcript_autobio_dict['MH'] + rec_transcript_nonautobio_dict['MH'],
                           'ML': rec_transcript_autobio_dict['ML'] + rec_transcript_nonautobio_dict['ML']}

    rec_transcript_dict['MH'] = np.array(rec_transcript_dict['MH']).mean(axis=0)
    rec_transcript_dict['ML'] = np.array(rec_transcript_dict['ML']).mean(axis=0)

    rec_transcript_nonautobio_dict['MH'] = np.array(rec_transcript_nonautobio_dict['MH']).mean(axis=0)
    rec_transcript_nonautobio_dict['ML'] = np.array(rec_transcript_nonautobio_dict['ML']).mean(axis=0)
    rec_transcript_autobio_dict['MH'] = np.array(rec_transcript_autobio_dict['MH']).mean(axis=0)
    rec_transcript_autobio_dict['ML'] = np.array(rec_transcript_autobio_dict['ML']).mean(axis=0)

    text_measures = pd.DataFrame(text_measures)
    if bools.saveMe:
        with open(f'{paths.output_path}rec_transcript_dict.pkl', 'wb') as f:
            pickle.dump(rec_transcript_dict, f)
        text_measures.to_csv(f'{paths.output_path}text_measures.csv', index=False)
        rec_transcript_sim_long.to_csv(f'{paths.output_path}rec_transcript_sim_long.csv', index=False)
else:
    # load the saved per-participant similarity measures
    text_measures = pd.read_csv(f'{paths.output_path}text_measures.csv')

# %% Merge text measures and save
phq9_diff_text = pd.merge(text_measures, phq9_diff, on=join_cols)
mood_diff_text = pd.merge(text_measures, mood_diff, on=join_cols)
recall_text = pd.merge(text_measures, recall_data, on=join_cols)
if bools.saveMe:
    phq9_diff_text.to_csv(f'{paths.output_path}phq9_diff_text.csv', index=False)
    mood_diff_text.to_csv(f'{paths.output_path}mood_diff_text.csv', index=False)
    recall_text.to_csv(f'{paths.output_path}recall_text.csv', index=False)

# %% Prepare data for plottting
phq9_diff_text['condition'] = pd.Categorical(phq9_diff_text['condition'], categories=['MH', 'ML'])
recall_text['condition'] = pd.Categorical(recall_text['condition'], categories=['ML', 'MH'])
mood_diff_text['condition'] = pd.Categorical(mood_diff_text['condition'], categories=['ML', 'MH'])

measures = ['mood_diff', 'recall_diffSent', 'phq9_q2']
measure_labels = ['Mood', 'Recall sentiment', 'PHQ9 Q2']
measure_label_fnames = ['mood', 'recall', 'phqQtwo']
measure_dfs = {'phq9_q2': phq9_diff_text, 'mood_diff': mood_diff_text, 'recall_diffSent': recall_text}

# %% Run and store regressions
results = {'phq9_q2': smf.ols('phq9_q2~condition*avgRecAct_sim+s_total', data=phq9_diff_text).fit(),
           'mood_diff': smf.ols('mood_diff~condition*avgRecAct_sim+s_total', data=mood_diff_text).fit(),
           'recall_diffSent': smf.ols('recall_diffSent~condition*avgRecAct_sim+s_total', data=recall_text).fit()}
for key, res in results.items():
    print('\n', key)
    print(res.summary())
# %% Plot measures against text similiarity - MAIN (middle row)
plt.close('all')
pc.annot_fs = 7
pc.p_lab_spec[0] = -0.1
pc.p_lab_spec[1] = 1.
pc.plab_offset = 6
cond_cols = ['#E1BE6A', '#40B0A6']
pc.dot_size = 12
pc.lw = 3

pc.r, pc.c, pc.mlt = 1, 3, 1
pc.figsize = (pc.fw, pc.fw / 4)
fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharex=False, sharey=False, layout='constrained')
pc.onerow = False
pc.axes = axes

pc.i, pc.j = 0, 0

for pc.j, (measure_name, measure_label, measure_fname) in enumerate(
        zip(measures, measure_labels, measure_label_fnames)):
    # get measure df
    measure_df = measure_dfs[measure_name]
    measure_df_MH = measure_df[measure_df['condition'] == 'MH']
    measure_df_ML = measure_df[measure_df['condition'] == 'ML']

    # plot regplots for each condition
    sns.regplot(measure_df_MH, x='avgRecAct_sim', y=measure_name, color=cond_cols[1], label='MH', ci=95, ax=pc.ax,
                scatter_kws={'s': pc.dot_size, 'alpha': pc.dot_alpha, 'edgecolors': 'none'}, line_kws={'lw': pc.lw})
    sns.regplot(measure_df_ML, x='avgRecAct_sim', y=measure_name, color=cond_cols[0], label='ML', ci=95, ax=pc.ax,
                scatter_kws={'s': pc.dot_size, 'alpha': pc.dot_alpha, 'edgecolors': 'none'}, line_kws={'lw': pc.lw})

    # add zero line
    pc.ax.axhline(y=0, color='k', linewidth=1, linestyle='--')

    # pc.ax.set_xlabel('Intervention Adherence')
    pc.ax.set_xlabel('Narrative state induction')
    pc.ax.set_ylabel(f'{measure_label} change')
    pc.ax.text(pc.p_lab_spec[0] + 0.05, pc.p_lab_spec[1], pc.p_labs[pc.i, pc.j], transform=pc.ax.transAxes,
               fontweight='bold',
               va='top', ha='right',
               fontsize=pc.p_lab_spec[2])

    # get regression results (p, t values)
    if pc.j == 2:  # phq9
        p_val = results[measure_name].pvalues['condition[T.ML]:avgRecAct_sim']
        t_val = results[measure_name].tvalues['condition[T.ML]:avgRecAct_sim']
        coef_val = results[measure_name].params['condition[T.ML]:avgRecAct_sim']
        p_val_text = r'Similarity $\times$ "Low mood"' + f'\n   p={p_val:.2f}{return_p_star(p_val)}\n   t={t_val:.2f}'
        pc.ax.set_ylim([-0.37, 0.55])
    elif pc.j == 0 or pc.j == 1:  # mood, sentiment
        p_val = results[measure_name].pvalues['condition[T.MH]:avgRecAct_sim']
        t_val = results[measure_name].tvalues['condition[T.MH]:avgRecAct_sim']
        coef_val = results[measure_name].params['condition[T.MH]:avgRecAct_sim']
        p_val_text = r'Similarity $\times$ "High mood"' + f'\n   p={p_val:.2f}{return_p_star(p_val)}\n   t={t_val:.2f}'

    tex_text = f'b={coef_val:.2f}, t({results[measure_name].df_resid:.0f})={t_val:.2f}, ' + \
               [f'p={p_val:.3f}' if p_val >= 0.001 else f'p$<$0.001'][0]

    # store for tex var
    setattr(report_vars, 'sThree_' + measure_fname + '_vs_IntSim', tex_text)
    if pc.j == 0:  # mood
        pc.ax.set_ylim([-0.37, 0.55])
    if pc.j == 1:  # sentiment
        pc.ax.set_ylim([-1, 1.47])
    pc.ax.text(0.02, 0.75, p_val_text, transform=pc.ax.transAxes, fontsize=pc.annot_fs)

if bools.savePlot:
    plt.savefig(f"{paths.plots_path}{fig_no}_p2_changeMeasures_VS_diarySim.pdf", dpi=300)
if bools.saveTex:
    write_to_tex(report_vars, overwrite=True)  # Get numbers to tex vars
