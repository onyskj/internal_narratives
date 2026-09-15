# Internal narratives

Code for **"Metareasoning constraints couple narratives, affect and cognition"**
(preprint: https://arxiv.org/abs/2502.09487).

- Code: https://github.com/onyskj/internal_narratives
- Data and intermediate outputs: https://osf.io/bs2df
- License: MIT (see `LICENSE`)

This repository contains all analysis code for the manuscript, and the code of the online experiments. With
the publicly shared data, you can reproduce every figure and every statistic that does not need
participants' free text. The parts that need free text (under a Data Sharing Agreement) or a GPU are listed
in section 8, with instructions to run them in section 9.

---

## Contents

1. [Quick start](#1-quick-start)
2. [Repository structure](#2-repository-structure)
3. [Data](#3-data)
4. [System requirements](#4-system-requirements)
5. [Installation](#5-installation)
6. [Reproduce the figures and statistics](#6-reproduce-the-figures-and-statistics)
7. [Figure index](#7-figure-index)
8. [Parts that need DSA data, a GPU, or raw data](#8-parts-that-need-dsa-data-a-gpu-or-raw-data)
9. [Running the LLM sampling and sSAE pipelines](#9-running-the-llm-sampling-and-ssae-pipelines)
10. [Troubleshooting](#10-troubleshooting)
11. [Data sharing and contact](#11-data-sharing-and-contact)

---

## 1. Quick start

```bash
# 1. Get the code and the data (see section 3), so that data/ and outputs/ are in the repository root
git clone https://github.com/onyskj/internal_narratives.git
cd internal_narratives
# ... download the OSF archive (https://osf.io/bs2df) and merge its data/ and outputs/ folders here

# 2. Create the environment (1–10 min depending on the connection, see section 5)
conda create -n int_narr python=3.13.5 -y
conda activate int_narr
pip install -r requirements.txt
pip install --no-deps sentence-transformers==5.1.1

# 3. Run the analyses (all commands from the repository root; about 2–4 min in total)
export PYTHONPATH=.
python scripts/a_open_qs/task_preprocess/demographics.py
python scripts/a_open_qs/main_analysis/analyse_logits_itemLevel.py
python scripts/a_open_qs/main_analysis/analyse_logits_genLevel.py
python scripts/b_ssae/main_analysis/analyse_model.py
python scripts/b_ssae/main_analysis/analyse_logit_perturbation.py
python scripts/b_ssae/perturbation/latent_perturbation.py
python scripts/b_ssae/perturbation/perturbation_selection.py
python scripts/c_mood_induction/task_preprocess/demographics.py
python scripts/demographics_table.py
python scripts/c_mood_induction/main_analysis/similarity_analysis.py
python scripts/c_mood_induction/ssae_scores/compute_ssae.py
python scripts/c_mood_induction/main_analysis/ssae_analysis.py
python scripts/c_mood_induction/main_analysis/main_analysis.py
```

The figure panels are written to `outputs/<study>/plots/`, with the file names listed in
[section 7](#7-figure-index). **The scripts overwrite the PDFs that come with the data archive.**

> **Windows:** the commands above were tested on macOS only. On Windows, set the path variable with
> `set PYTHONPATH=.` (Command Prompt) or `$env:PYTHONPATH="."` (PowerShell) instead of `export PYTHONPATH=.`.
> The GPU and training scripts in section 9 do not run on native Windows (section 10); use WSL2 or Linux
> for them.

---

## 2. Repository structure

```
.
├── _objects/            configuration classes and model definitions
├── _utils/utils.py      helper functions (statistics, LaTeX variable export)
├── data/                preprocessed data (from OSF)
├── outputs/             intermediate results, plots and LaTeX variables (from OSF)
├── scripts/             analysis code
├── tasks/               JavaScript (jsPsych) code of the online experiments
├── requirements.txt     exact package versions used for the analyses
└── LICENSE
```

`data/`, `outputs/` and `scripts/` have one sub-folder per study. The folder names differ from the study
names in the manuscript:

| Folder               | Manuscript                                                                                              |
|----------------------|---------------------------------------------------------------------------------------------------------|
| `a_open_qs`          | **Study 1** – open-ended PHQ-8 narratives and LLM sampling (Figs 2–3; Methods 4.2; Supplementary B)     |
| `b_ssae`             | **Supervised sparse auto-encoder (sSAE)** trained on Study 1 data (Fig 4; Methods 4.3; Supplementary C) |
| `c_mood_induction`   | **Study 2** – narrative exposure / mood induction (Fig 5; Methods 4.4; Supplementary D)                 |

Every script is a plain Python file organised in `# %%` cells. It runs from the command line, or cell by
cell in an IDE (PyCharm, VS Code). Each script has boolean flags near the top (`bools.loadMe`,
`bools.saveMe`, `bools.saveFig`/`savePlot`, `bools.saveTex`). With the default settings, the scripts
**load precomputed intermediate results** and do not refit models or sample LLMs.

### `_objects/`

| File               | Content                                                                    |
|--------------------|----------------------------------------------------------------------------|
| `configs.py`       | `Paths`, `Bools` (flags) and `ReportVars` (statistics for LaTeX) objects   |
| `data_configs.py`  | exclusion thresholds, word lists, seeds and training constants             |
| `model_configs.py` | LLM sampling configuration (`SampleLogitsConfig`)                          |
| `model_specs.py`   | Hugging Face model names and layer details                                 |
| `plot_config.py`   | plotting sizes and styles                                                  |
| `qs_maps.py`       | questionnaire items, response maps and question-name maps                  |
| `sae_models.py`    | sSAE model (`SAE4`), its configuration and early stopping                  |
| `steer_config.py`  | hidden-state steering with sSAE perturbations (uses `baukit`)              |

### `scripts/`

**`a_open_qs/` (Study 1)**

| Sub-folder         | Script                        | Purpose                                                                 |
|--------------------|-------------------------------|-------------------------------------------------------------------------|
| `task_preprocess/` | `download_v4.py`              | download the experiment data from Firebase                              |
|                    | `preprocess_v4.py`            | preprocess the raw data of each task version                            |
|                    | `combine_data.py`             | combine the task versions; free-text word counts and sentiment          |
|                    | `demographics.py`             | demographics and questionnaire total-score histograms                   |
| `llm_sampling/`    | `sample_logits_itemLevel.py`  | item-level LLM sampling of PHQ-9 scores from open-ended responses       |
|                    | `sample_logits_genLevel.py`   | generalisation sampling of PHQ-9, SDS and GAD-7 item scores             |
|                    | `logit_utils.py`              | model loading, prompt construction, token locations                     |
|                    | `prompts/`, `ch_temp/`        | prompt texts, chat templates                                            |
| `main_analysis/`   | `analyse_logits_itemLevel.py` | item-level correlations and severity biases (Fig 2)                     |
|                    | `analyse_logits_genLevel.py`  | covariance-structure recovery (Fig 3)                                   |
|                    | `analysis_utils.py`           | exclusion criteria, correlations, bootstrap and SVD-based measures      |

**`b_ssae/` (sSAE)**

| Sub-folder        | Script                           | Purpose                                                                  |
|-------------------|----------------------------------|--------------------------------------------------------------------------|
| `training/`       | `prepare_model_datasets.py`      | build hidden-state datasets of Study 1 responses and PHQ-9 scores        |
|                   | `training_utils.py`              | training loop, loss plots and predictions                                |
|                   | `model_training.py`              | train the sSAE for each layer over a hyper-parameter grid                |
|                   | `model_selection.py`             | select and refit the best model per layer                                |
| `perturbation/`   | `latent_perturbation.py`         | sparse latent perturbations and their confusion matrices                 |
|                   | `logit_perturbation.py`          | steer LLM hidden states and sample perturbed responses                   |
|                   | `perturbation_selection.py`      | select the steering strength on the validation set                       |
|                   | `perturb_utils.py`               | perturbation vectors (SPGL1) and loading of perturbed outputs            |
| `main_analysis/`  | `analyse_model.py`               | test-set predictions and covariance structure (Fig 4B, D–F)              |
|                   | `analyse_logit_perturbation.py`  | effect of perturbations on held-out responses (Fig 4C)                   |
|                   | `analysis_utils.py`              | bootstrap and correlation functions for sSAE predictions                 |

**`c_mood_induction/` (Study 2)**

| Sub-folder         | Script                                   | Purpose                                                            |
|--------------------|------------------------------------------|--------------------------------------------------------------------|
| `task_preprocess/` | `download_v2.py`, `download_v3.py`       | download the experiment data from Firebase                         |
|                    | `preprocess_v2.py`, `preprocess_v3.py`   | preprocess the raw data of each task version                       |
|                    | `combine_data.py`                        | combine versions, exclusion criteria, recall sentiment             |
|                    | `demographics.py`                        | demographics and PHQ-9 total-score histogram                       |
| `ssae_scores/`     | `sample_hidden_states.py`                | LLM hidden states of every participant text                        |
|                    | `compute_ssae.py`                        | sSAE scores of these hidden states                                 |
|                    | `hs_utils.py`                            | prompt formatting and forward pass                                 |
| `main_analysis/`   | `main_analysis.py`                       | diary similarity, condition effects and demand effects (Fig 5A–F)  |
|                    | `similarity_analysis.py`                 | text similarity and narrative state induction (Fig 5G–I)           |
|                    | `ssae_analysis.py`                       | sSAE Q2 scores against affective change (Fig 5J–L)                 |

**`scripts/demographics_table.py`** creates the demographics table of both studies (Supplementary Table A1).

### `tasks/`

JavaScript (jsPsych) code of the online experiments.

- `a_open_qs/qs-structure-phq9-v4` (Study 1). The data folder names give the recruitment version:
  - `v4`: no Prolific depression filter.
  - `v4_d`: participants who answered "Yes" to "Do you experience depression?".
  - `v4_dd`: as `v4_d`, and currently diagnosed with depression.
  - `v4_ddd`: as `v4_dd`, with delayed website loading and feedback saved on time-out.
- `c_mood_induction/qs-intervention-v2` (versions `v2`, `v2b`): non-autobiographical narrative exposure,
  no mood VAS.
- `c_mood_induction/qs-intervention-v3`: autobiographical narrative exposure, with mood VAS.

### `outputs/`

| Folder                                   | Content                                                                         |
|------------------------------------------|---------------------------------------------------------------------------------|
| `a_open_qs/llm_sampling/`                | combined LLM sampling outputs per model                                         |
| `a_open_qs/main_analysis/`               | bootstrapped covariance measures                                                |
| `b_ssae/training/`                       | experiment logs, loss curves, metrics and the best sSAE model per layer         |
| `b_ssae/perturbation/`                   | perturbation vectors and perturbed LLM outputs (validation and test sets)       |
| `b_ssae/main_analysis/`                  | test-set predictions, performance and bootstraps                                |
| `c_mood_induction/similarity_analysis/`  | text-similarity measures, diary-similarity matrices, embeddings of the stimulus transcripts and PHQ-9 items |
| `c_mood_induction/ssae_scores/`, `ssae_analysis/` | sSAE scores of Study 2 texts and merged measures                       |
| `*/plots/`                               | individual figure panels (section 7)                                            |
| `figs/`                                  | composite figures, assembled from the panels outside the code                   |
| `vars/`                                  | `paper_stats.tex` (statistics in the text), `demog_table.tex` (Table A1)        |

---

## 3. Data

The GitHub repository contains the code. The OSF archive (https://osf.io/bs2df) contains `data/` and
`outputs/` (3.7 GB). Merge both, so that `data/` and `outputs/` are in the repository root.

### What is shared

| Type                                                                                                      | Status                                                                                                                                                                                                                  |
|-----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Multiple-choice questionnaires (PHQ-9, GAD-7, SDS, custom level 1/2 items), mood ratings, recall sentiment, end-of-study ratings, demographics (age, sex, ethnicity, employment) | Shared                                                                                                                    |
| LLM outputs: sampled multiple-choice scores for every participant, question and model (combined CSVs)    | Shared (`outputs/a_open_qs/llm_sampling/files_logits/**/sub_llm_responses_*.csv`)                                                                                                                                        |
| sSAE: trained best model per layer, loss curves, metrics, test predictions, perturbation vectors, perturbed LLM outputs | Shared (`outputs/b_ssae/`)                                                                                                                                                |
| Study 2: sSAE scores of the texts, per-participant text-similarity measures (`text_measures.csv`), average diary-similarity matrices, sentence embeddings of the stimulus transcripts and PHQ-9 items | Shared (`outputs/c_mood_induction/`)                                                                                                                        |
| Free-text files needed by the analysis code (`openq_data_long.csv`, Study 2 `int_data.csv`, `openq_data.csv`) | **Shared in redacted form.** Every word is replaced by `x`, and the word count is kept (e.g. `x x x x`). All other columns are unchanged. The scripts use these files only for word-count exclusion criteria and for participant/condition rows, so the results are identical. |
| Participants' original free text                                                                          | **Not shared** (Data Sharing Agreement, section 11)                                                                                                                                                                     |
| LLM hidden states (per-participant `.pt` tensors and the sSAE training datasets `data/b_ssae/9q_zs_*.pt`) | **Not shared** (Data Sharing Agreement). They encode the free text.                                                                                                                                                     |
| Sentence embeddings of participants' Study 2 texts (`text_embd_autobio.pkl`, `text_embd_nonautobio.pkl`)  | **Not shared** (Data Sharing Agreement). They encode the free text. The similarity measures computed from them (`text_measures.csv`) are shared, and `similarity_analysis.py` loads these by default (`loadTextMeasures = True`). |
| Per-participant, per-question LLM output files (`.../subjects/...`) for Study 1                          | Not shared (size). The combined CSVs above contain the same scores.                                                                                                                                                     |
| Raw Firebase exports and Prolific demographic exports                                                     | Not shared                                                                                                                                                                                                              |

### Data files

**`data/a_open_qs/task_data/combined/`** (Study 1, all task versions combined)

| File                         | Content                                                                                                     |
|------------------------------|-------------------------------------------------------------------------------------------------------------|
| `demographics.csv`           | age, sex, ethnicity, employment                                                                             |
| `phq9_data.csv`              | PHQ-9 responses, item scores, total and questionnaire duration                                              |
| `gad7_data.csv`              | GAD-7 responses, item scores, total and questionnaire duration                                              |
| `sds_data.csv`               | SDS responses, item scores, total and questionnaire duration                                                |
| `lvl1_closed_data.csv`       | level 1 (most general) multiple-choice item and response time                                               |
| `lvl2_closed_data.csv`       | level 2 (semi-specific) multiple-choice items and response time                                             |
| `openq_data_long.csv`        | long format, one row per participant and open-ended question: response (**redacted**), response time, word count, word rate, sentiment and the corresponding multiple-choice score |
| `openq_data_long_stats.csv`  | per-participant summaries of the open-ended responses: mean sentiment, corresponding total score, response time and word rate |
| `sub_data.csv`               | date and time of the experiment                                                                             |

`data/a_open_qs/task_data/qs-structure-phq9-v4*/processed/` contains the same measures per task version,
and `emo_data.csv` (predefined emotion responses).

**`data/b_ssae/`**

| File                      | Content                                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------------------|
| `sub_list_9q_random.txt`  | fixed random order of participants, used for the same train/validation/test split in all sSAE analyses     |

The hidden-state datasets `9q_zs_gemma2-9b-it.pt` and `9q_zs_gemma2-9b-it_ind.pt` belong here, but are not
shared (see above).

**`data/c_mood_induction/task_data/combined/`** (Study 2, all task versions combined)

| File                          | Content                                                                                                     |
|-------------------------------|-------------------------------------------------------------------------------------------------------------|
| `demographics.csv`            | age, sex, ethnicity, employment, condition                                                                  |
| `phq9_data.csv`               | PHQ-9 item scores at baseline and follow-up                                                                  |
| `phq9_diff_data_wide.csv`     | PHQ-9 item score changes and baseline totals (wide format)                                                  |
| `phq9_data_q2_long.csv`       | baseline and follow-up PHQ-9 Q2 scores with baseline totals                                                 |
| `mood_data.csv`               | mood ratings and PHQ-9 totals                                                                               |
| `recall_data_wide.csv`        | average sentiment of recalled words at each time point, and baseline PHQ-9                                  |
| `feedback_data.csv`           | end-of-study ratings (demand effects, mood change, etc.)                                                    |
| `feedback_data_wide.csv`      | the same ratings with PHQ-9 scores and recall sentiment                                                     |
| `feedback_data_wide_mood.csv` | as above, with mood ratings                                                                                 |
| `int_data.csv`                | recreated diaries (`recreate_0`–`3`) and diary continuation (`act_0`), **redacted**, with word counts (`*_wc`) |
| `openq_data.csv`              | open-ended responses about mood (PHQ-9 Q2), energy (Q4) and the positive re-evaluation, **redacted**, with word counts |

`data/c_mood_induction/task_data/qs-intervention-v*/processed/` contains the same measures per task version.
`data/c_mood_induction/transcripts/` contains the diary transcripts used as stimuli (`mh.txt` high mood,
`ml.txt` low mood).

---

## 4. System requirements

### Tested environment

| Item               | Version                                                                   |
|--------------------|---------------------------------------------------------------------------|
| Operating system   | macOS 15.7.9 (Apple Silicon, arm64)                                       |
| Python             | 3.13.5 (conda environment `int_narr`)                                     |
| Hardware           | Standard laptop/desktop CPU; no GPU needed                                |
| Disk space         | about 4 GB for `data/` + `outputs/`, about 1.1 GB for the Python environment |

The analyses in section 6 were run end to end on this system, in a new conda environment installed as in
section 5. Linux is expected to work (the scripts select their device per operating system, and the plotting
scripts in section 6 use the non-interactive `Agg` backend, so no display is needed), but was not tested for
this guide. Native Windows was not tested; the scripts in section 6 contain no Unix-only calls, but the GPU and
training scripts in section 9 do (see section 10).

### Python packages (exact tested versions)

These are pinned in `requirements.txt`:

| Package                 | Version     | Package              | Version     |
|-------------------------|-------------|----------------------|-------------|
| torch                   | 2.6.0       | seaborn              | 0.13.2      |
| transformers            | 5.12.1      | statsmodels          | 0.14.5      |
| accelerate              | 1.10.1      | statannotations      | 0.7.2       |
| sentence-transformers   | 5.1.1       | scikit-learn         | 1.7.1       |
| baukit                  | 0.0.1 (GitHub commit `9d51abd`) | scipy     | 1.16.1      |
| einops                  | 0.8.1       | spgl1                | 0.0.3       |
| numpy                   | 2.3.2       | natsort              | 8.4.0       |
| pandas                  | 2.3.1       | joblib               | 1.5.1       |
| matplotlib              | 3.10.5      | tqdm                 | 4.67.1      |
| google-cloud-storage    | 3.3.1       | psutil               | 7.0.0       |
| firebase_admin          | 7.4.0       | protobuf             | 6.33.6      |
| textblob                | 0.19.0      | latextable / texttable | 1.0.1 / 1.7.0 |

Notes:

- `sentence-transformers 5.1.1` declares `transformers<5`, but the analyses were run with
  `transformers 5.12.1`. Install it with `--no-deps` to get the tested combination. The analyses in section 6
  only import it; the text-similarity measures are precomputed.
- `google-cloud-storage` is imported by `_utils/utils.py`, so every script needs it.
  `firebase_admin` is only used by the data download scripts.

### Non-standard hardware

- **Reproducing the figures and statistics (section 6):** none.
- **LLM sampling and hidden-state extraction (section 9):** a CUDA GPU. The models are run in bfloat16.
  Gemma-2-9B alone needs about 18.5 GB of GPU memory for its weights, so we recommend a GPU with at least
  24 GB (40 GB or more for the batched generalisation sampling). These numbers are estimates from the model
  sizes. The sampling pipeline can also be tested on a local machine with a smaller model, for example
  Gemma-2-2B (about 5 GB in bfloat16) on an Apple Silicon Mac (MPS) or a consumer GPU. On macOS, the sampling
  scripts use Gemma-2-2B by default (section 9.2).
- **sSAE training (section 9):** small models (at most about 52 M parameters) on about 700 samples. A GPU
  helps but is not required; Apple MPS or CPU also works.

---

## 5. Installation

```bash
conda create -n int_narr python=3.13.5 -y
conda activate int_narr
pip install -r requirements.txt
pip install --no-deps sentence-transformers==5.1.1
```

A plain `python3.13 -m venv` environment works as well.

**Typical install time:** 52 seconds on the tested Mac with a fast internet connection and an empty pip
cache (94 packages, 1.1 GB installed; measured in a fresh environment, which then ran the analysis scripts
successfully). Allow 5–10 minutes on a slower connection. On Linux with CUDA, the PyTorch wheels are several
GB larger, so the download takes longer.

No GPU drivers are needed for section 6. For section 9, install a PyTorch build that matches your CUDA
version (https://pytorch.org/get-started/previous-versions/, PyTorch 2.6.0).

---

## 6. Reproduce the figures and statistics

- Run every script **from the repository root** with `PYTHONPATH=.` (the scripts use relative paths and
  import `_objects`, `_utils` and `scripts.*` as packages). The commands are in section 1.
- Default flags load precomputed results. Plot saving is switched on (`saveFig`/`savePlot = True`), and
  writing to `outputs/vars/paper_stats.tex` is switched off.
- Plots are written as PDF files with the non-interactive `Agg` backend; no plot windows open, and no
  display is needed.
- No script in this section fits a model, samples an LLM, or needs internet access.

---

## 7. Figure index

### Main figures

Composite figures were assembled from the panel PDFs below outside the code (`outputs/figs/`).

| Figure | Panels | File (`outputs/...`)                                                   | Script                                                  |
|--------|--------|------------------------------------------------------------------------|---------------------------------------------------------|
| Fig 1  | A–B    | study design schematic, no code                                        | –                                                       |
| Fig 2  | A–H    | `a_open_qs/plots/logits_itemLevel/Fig2_item_level.pdf`                 | `a_open_qs/main_analysis/analyse_logits_itemLevel.py`   |
|        | I      | `a_open_qs/plots/logits_itemLevel/Fig2_bias.pdf`                       | same                                                    |
|        | J      | `a_open_qs/plots/logits_itemLevel/Fig2_item_level_across_models.pdf`   | same                                                    |
|        | K      | example narratives (free text, not shared)                             | same (`openq_data_bias_examples.csv`)                   |
| Fig 3  | A–L    | `a_open_qs/plots/logits_genLevel/Fig3_gen_level.pdf`                   | `a_open_qs/main_analysis/analyse_logits_genLevel.py`    |
| Fig 4  | A      | sSAE schematic, no code                                                | –                                                       |
|        | B      | `b_ssae/plots/main_analysis/Fig4_p2_ssae_pred_comp.pdf`                | `b_ssae/main_analysis/analyse_model.py`                 |
|        | C      | `b_ssae/plots/perturbation/Fig4_p3_logits_pert_bars.pdf`               | `b_ssae/main_analysis/analyse_logit_perturbation.py`    |
|        | D–F    | `b_ssae/plots/main_analysis/Fig4_p3_ssae_structure.pdf`                | `b_ssae/main_analysis/analyse_model.py`                 |
| Fig 5  | A–F    | `c_mood_induction/plots/main_analysis/Fig5_p1_diff_measures_combined.pdf` | `c_mood_induction/main_analysis/main_analysis.py`    |
|        | G–I    | `c_mood_induction/plots/similarity_analysis/Fig5_p2_changeMeasures_VS_diarySim.pdf` | `c_mood_induction/main_analysis/similarity_analysis.py` |
|        | J–L    | `c_mood_induction/plots/ssae_analysis/Fig5_p3_changeMeasures_VS_sSAEq2.pdf` | `c_mood_induction/main_analysis/ssae_analysis.py`  |

### Supplementary figures and table

| Supp.   | Content                                            | File (`outputs/...`)                                                            | Script                                  |
|---------|----------------------------------------------------|----------------------------------------------------------------------------------|-----------------------------------------|
| Table A1| Demographics                                       | `vars/demog_table.tex`                                                           | `demographics_table.py`                 |
| A1      | Study 1 severity histograms                        | `a_open_qs/plots/prelim/a_open_qs_totals.pdf`                                    | `a_open_qs/task_preprocess/demographics.py` |
| A2      | Study 2 PHQ-9 histogram                            | `c_mood_induction/plots/prelim/c_mood_induction_totals.pdf`                      | `c_mood_induction/task_preprocess/demographics.py` |
| B3–B6   | Item-level scores, other LLMs                      | `a_open_qs/plots/logits_itemLevel/scores_correlations_item_level_<model>.pdf`    | `analyse_logits_itemLevel.py`           |
| B7–B11  | Item-level severity biases, all LLMs               | `a_open_qs/plots/logits_itemLevel/scores_bias_item_level_<model>.pdf`            | `analyse_logits_itemLevel.py`           |
| B12–B15 | Generalisation structure, other LLMs               | `a_open_qs/plots/logits_genLevel/gen_qs_total_item_corrs_<model>.pdf`            | `analyse_logits_genLevel.py`            |
| B16     | Structure-match metrics, all LLMs                  | `a_open_qs/plots/logits_genLevel/gen_qs_metric_heatmap.pdf`                      | `analyse_logits_genLevel.py`            |
| C17     | sSAE loss curves per layer                         | `b_ssae/plots/main_analysis/ssae_loss_gemma-2-9b-it.pdf`                         | `b_ssae/main_analysis/analyse_model.py` |
| C18     | Best-layer sSAE predictions                        | `b_ssae/plots/main_analysis/ssae_bestlayer_performance_gemma-2-9b-it.pdf`        | `analyse_model.py`                      |
| C19     | Layer-wise test performance                        | `b_ssae/plots/main_analysis/test_performance_gemma-2-9b-it.pdf`                  | `analyse_model.py`                      |
| C20     | Latent perturbation confusion matrices             | `b_ssae/plots/perturbation/latent_perturbation_all_layers.pdf`                   | `b_ssae/perturbation/latent_perturbation.py` |
| C21     | Perturbed expected-score differences               | `b_ssae/plots/perturbation/logits_exp_score_pert_test_gemma-2-9b-it.pdf`         | `b_ssae/main_analysis/analyse_logit_perturbation.py` |
| D22–D23 | Mood and PHQ-9 VAS task screenshots                | `figs/fig_supp/mood_vas.png`, `figs/fig_supp/phq9_vas.png`                       | – (screenshots)                         |

The per-epoch training loss plots of every sSAE fit are in `outputs/b_ssae/plots/training/`
(written by `b_ssae/training/model_training.py` and `model_selection.py`; not in the paper).

---

## 8. Parts that need DSA data, a GPU, or raw data

| Step                                                                 | Script(s)                                                                                                  | Needs                                                                                       |
|----------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| Download and preprocess the raw experiment data                      | `*/task_preprocess/download_v*.py`, `preprocess_v*.py`                                                     | Firebase credentials, raw exports (not shareable)                                           |
| Combine preprocessed data, exclusion criteria, sentiment of free text | `a_open_qs/task_preprocess/combine_data.py`, `c_mood_induction/task_preprocess/combine_data.py`           | Original free text (DSA)                                                                     |
| Study 1 LLM sampling (item level, generalisation)                    | `a_open_qs/llm_sampling/sample_logits_itemLevel.py`, `sample_logits_genLevel.py`                           | Original free text (DSA), GPU, Hugging Face access                                          |
| sSAE training datasets                                               | `b_ssae/training/prepare_model_datasets.py` (`createDataset=True`)                                         | Hidden states from item-level sampling (DSA)                                                 |
| sSAE training and model selection                                    | `b_ssae/training/model_training.py`, `model_selection.py`                                                  | `data/b_ssae/9q_zs_gemma2-9b-it.pt` (DSA)                                                     |
| sSAE test predictions and bootstraps (recompute)                     | `b_ssae/main_analysis/analyse_model.py` with `loadMe=False`                                                | `data/b_ssae/9q_zs_gemma2-9b-it.pt` and `..._ind.pt` (DSA)                                    |
| Latent perturbation vectors (recompute)                              | `b_ssae/perturbation/latent_perturbation.py` with `loadMe=False`, `computeDelta=True`                      | `data/b_ssae/9q_zs_gemma2-9b-it.pt` (DSA)                                                     |
| LLM steering with sSAE perturbations                                 | `b_ssae/perturbation/logit_perturbation.py`                                                                | Original free text + hidden-state dataset (DSA), GPU                                          |
| Study 2 hidden states and sSAE scores                                | `c_mood_induction/ssae_scores/sample_hidden_states.py`, `compute_ssae.py` with `loadMe=False`              | Original free text (DSA), GPU                                                                |
| Study 2 sentence embeddings and similarity measures (recompute)      | `c_mood_induction/main_analysis/similarity_analysis.py` with `loadTextMeasures=False`, `loadEmb=False`     | Original free text (DSA)                                                                     |

All outputs of these steps that do not contain free text are shared, so every downstream analysis in
section 6 runs.

---

## 9. Running the LLM sampling and sSAE pipelines

These pipelines were run on a Google Cloud GPU virtual machine (Linux, CUDA). They were not rerun for this
guide. The instructions below describe how to set them up on your own machine, with the original data (DSA)
or with your own open-ended responses.

### 9.1 Before you start

1. **Hugging Face access.** Gemma 2 and Llama 3.x are gated models. Accept their licenses on Hugging Face,
   then log in with `hf auth login`. The models are:
   `google/gemma-2-2b-it`, `google/gemma-2-9b-it`, `meta-llama/Llama-3.2-3B-Instruct`,
   `meta-llama/Llama-3.1-8B-Instruct`, `Open-Orca/Mistral-7B-OpenOrca` (see `_objects/model_specs.py`).
   Model weights have their own license terms; the MIT license of this code does not cover them.
2. **Install PyTorch for your CUDA version** (see section 5).
3. **Work on a copy of `outputs/`.** Sampling writes one file per participant and question, and it skips
   files that already exist (the scripts can resume after an interruption).

### 9.2 Device selection

Most scripts choose the device from the operating system: `mps` on macOS, `cuda` on any other system. On
Linux, CUDA is therefore used automatically. Check or change these lines:

| File:line                                                        | Setting                        | Change for a CUDA machine                                    |
|------------------------------------------------------------------|--------------------------------|--------------------------------------------------------------|
| `scripts/a_open_qs/llm_sampling/logit_utils.py:13-24`            | `cuda` if not macOS            | none (use `cpu` on Linux without a GPU)                      |
| `scripts/a_open_qs/llm_sampling/sample_logits_itemLevel.py:16-27`| macOS: only `gemma2-2b-it`; else all 5 models | edit `model_names` to choose models         |
| `scripts/a_open_qs/llm_sampling/sample_logits_genLevel.py:20-32` | same                           | same                                                         |
| `scripts/b_ssae/training/prepare_model_datasets.py:14`           | `device_name = 'mps'` (fixed)  | set `'cuda'` or `'cpu'`                                      |
| `scripts/b_ssae/training/model_training.py:11-18`, `model_selection.py:7-14` | `cuda` if not macOS | `cpu` if no GPU                                          |
| `scripts/b_ssae/main_analysis/analyse_model.py:180`              | `torch.mps.empty_cache()`      | replace with `torch.cuda.empty_cache()` (only with `loadMe=False`) |
| `scripts/c_mood_induction/ssae_scores/sample_hidden_states.py:14-21` | macOS: `gemma2-2b-it`; else `gemma2-9b-it` | the sSAE was trained on `gemma2-9b-it`       |
| `scripts/c_mood_induction/ssae_scores/compute_ssae.py:39`        | `device_name = 'mps'` (fixed)  | set `'cuda'` or `'cpu'`                                      |
| `scripts/*/task_preprocess/combine_data.py:10` / `:18`           | sentiment model on `mps`       | set `'cuda'` or `'cpu'`                                      |

On a Mac with Apple Silicon, the sampling scripts run Gemma-2-2B on MPS by default; this is suitable for
trying the pipeline on a few participants (set `end_idx` in `sample_logits_itemLevel.py:64`, or `s_lim` in
`sample_logits_genLevel.py:66`).

> **Warning:** `sample_logits_genLevel.py:255-262` runs `sudo shutdown -h now` when an error occurs on a
> non-macOS machine (this was for the cloud VM). Remove these lines before running on your own computer.

### 9.3 Pipeline order and flags

**Study 1: LLM sampling**

1. `scripts/a_open_qs/llm_sampling/sample_logits_itemLevel.py` – 50 samples per participant and question
   from the label probabilities (`nSamples = 50`); also saves the hidden states that the sSAE uses
   (`save_states = True`).
2. `scripts/a_open_qs/llm_sampling/sample_logits_genLevel.py` – for each open-ended response, samples
   answers to every PHQ-9, SDS and GAD-7 item.
3. Combine the per-file outputs: in `analyse_logits_itemLevel.py` and `analyse_logits_genLevel.py` set
   `bools.loadMe = False` and `bools.saveMe = True` (this recreates the combined CSVs and the bootstrap
   files), then run them.

**sSAE**

4. `scripts/b_ssae/training/prepare_model_datasets.py` – set `createDataset = True`, `saveDataset = True`;
   run once with `ind_qs = False` (average embedding) and once with `ind_qs = True` (`_ind` dataset, used
   by `analyse_model.py`). The participant split is fixed by `data/b_ssae/sub_list_9q_random.txt`.
5. `scripts/b_ssae/training/model_training.py` – hyper-parameter grid (2 learning rates × 3 sparsity
   coefficients × 3 expansion factors) for each of the 21 upper layers of Gemma-2-9B (378 fits; early
   stopping, patience 30, at most 1000 epochs; seed 80 in `_objects/data_configs.py`).
6. `scripts/b_ssae/training/model_selection.py` – selects the best setting per layer and refits it
   (`SAE_exp_v3_best`).
7. `scripts/b_ssae/main_analysis/analyse_model.py` with `loadMe = False`, `saveMe = True`.
8. `scripts/b_ssae/perturbation/latent_perturbation.py` with `loadMe = False`, `saveMe = True`,
   `computeDelta = True`.
9. Steering on the validation set, selection of the strength, then steering on the test set. The data
   split is chosen with `ds_type` (`'val'` or `'test'`), and the steering strengths γ (`steer_mlt_set`)
   follow from it (`logit_perturbation.py:70-73`):

   | Run | Script and setting                                                               | γ                          | Output folder (`outputs/b_ssae/perturbation/`) |
   |-----|----------------------------------------------------------------------------------|----------------------------|------------------------------------------------|
   | a   | `logit_perturbation.py` with `ds_type = 'val'` (line 63)                          | ±0.25, ±0.5, ±1, ±1.5      | `files_logits_perturbed_val/`                  |
   | b   | `perturbation_selection.py` (`ds_type = 'val'`, line 53) with `loadMe = False`, `saveMe = True` | prints the γ with the largest mean effect per direction | combined CSVs in the same folder |
   | c   | `logit_perturbation.py` with `ds_type = 'test'` (comment out line 63, uncomment line 64) | −0.25, 1.5 (selected in b; Methods 4.3.5) | `files_logits_perturbed_test/`   |

   If step b selects other strengths, change the `ds_type == 'test'` line (`logit_perturbation.py:73`).
   Sampling skips a participant and question when enough output files already exist, so use an empty
   output folder when you change the strengths.
10. `scripts/b_ssae/main_analysis/analyse_logit_perturbation.py` (`ds_type = 'test'`) with
    `loadMe = False`, `saveMe = True`.

**Study 2**

11. `scripts/c_mood_induction/ssae_scores/sample_hidden_states.py`.
12. `scripts/c_mood_induction/ssae_scores/compute_ssae.py` with `loadMe = False`, `saveMe = True`.
13. `scripts/c_mood_induction/main_analysis/similarity_analysis.py` with `loadTextMeasures = False`,
    `loadEmb = False`, `saveEmb = True`, `saveMe = True`; then `ssae_analysis.py` with `saveMe = True`; then
    `main_analysis.py`.

### 9.4 Using your own open-ended responses

The sampling scripts read `data/a_open_qs/task_data/combined/openq_data.csv` (one row per participant)
and the multiple-choice files next to it (`phq9_data.csv`, and `sds_data.csv`/`gad7_data.csv` for the
generalisation sampling). To run the pipeline on your own text, create `openq_data.csv` with:

| Column                                 | Content                                                                                  |
|----------------------------------------|------------------------------------------------------------------------------------------|
| `sub`                                  | participant id in the form `sub<N>_<version>`, e.g. `sub1_v4`                             |
| `task_version`                         | one of `v4`, `v4_d`, `v4_dd`, `v4_ddd` (see `task_versions` in the scripts)              |
| `lvl1_q1`, `lvl2_q1`–`lvl2_q3`, `lvl3_q1`–`lvl3_q8`, `rep_lvl2_q1` | the free-text answer to each open-ended question (empty cells are skipped) |

The question wording is in `scripts/a_open_qs/llm_sampling/prompts/experiment/phq9_open_gb.txt`, the
instructions in `prompts/experiment/instr3.txt`, and the multiple-choice items in `prompts/qs/`. A full
example prompt is in the Supplementary Information (B.3).

---

## 10. Troubleshooting

| Problem                                                                | Solution                                                                                                  |
|------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| `ModuleNotFoundError: No module named '_objects'` or `'scripts'`       | Run from the repository root with `PYTHONPATH=.`                                                          |
| `FileNotFoundError` for `data/...` or `outputs/...`                    | Run from the repository root, and check that the OSF archive is merged (section 3)                        |
| `Cannot load backend 'TkAgg'` or `ValueError: height and width must be > 0` (macOS without a display session) | Only in the macOS branch of `perturbation_selection.py`, `model_selection.py` and `logit_perturbation.py`. Change `matplotlib.use('TkAgg')` to `matplotlib.use('Agg')` in that script |
| `AttributeError: module 'os' has no attribute 'uname'` (native Windows, section 9 scripts) | Use WSL2, Linux or macOS. Or, in the script, replace `os.uname()[0] == 'Darwin'` with `sys.platform == 'darwin'` (and add `import sys`); this gives the same result on macOS and Linux and also works on Windows. Affected: `llm_sampling/logit_utils.py`, `sample_logits_itemLevel.py`, `sample_logits_genLevel.py` (3 lines), `model_training.py`, `model_selection.py`, `logit_perturbation.py`, `sample_hidden_states.py` |
| `ModuleNotFoundError: No module named 'google'`                        | `pip install google-cloud-storage==3.3.1` (imported by `_utils/utils.py`)                                  |
| pip reports a conflict between `sentence-transformers` and `transformers` | Expected; install `sentence-transformers` with `--no-deps` (section 5)                                  |

---

## 11. Data sharing and contact

Participants' open-ended free-text responses and the corresponding LLM hidden states and sentence embeddings are not shared publicly
because of anonymity concerns. We are happy to set up a Data Sharing Agreement to share them. Please
contact:

- Jakub Onysk (jakub.onysk.22@ucl.ac.uk)
- Quentin Huys (q.huys@ucl.ac.uk)
