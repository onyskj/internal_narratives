# Repository structure

Code repository for the "Internal narratives parameterise affective states"
paper (https://arxiv.org/abs/2502.09487).

Data and analysis outputs are located on OSF, due to the size and number of intermediary files.
- https://osf.io/bs2df

Note that open-ended free text responses, as well as corresponding LLM hidden state files are not included due to
anonymity concern. We are happy to set up Data Sharing Agreement to share these instead. Please contact either:
* Jakub Onysk (jakub.onysk.22@ucl.ac.uk)
* Quentin Huys (q.huys@ucl.ac.uk)

You will have to combine the data repo with this one to match the main structure repository as follows:

```
.
├── _objects (contain classes and objects used in the analysis)
├── _utils (contains helper function)
├── data (contains raw and preprocessed data)
├── outputs (contains intermediary analysis outputs and figures)
├── requirements.txt (pip requirements for the analysis)
├── scripts (contains analysis scripts)
└── tasks (contain the JavaScript files for each behavioural task)
```

Additionally, `data/, outputs/, scripts/` are subdivided into directories that correspond to main sub-studies in the
paper:

```
  ├── a_open_qs (Open-ended LLM sampling)
  ├── b_ssae (Supervised sparse auto-encoder)
  └── c_mood_induction (Mood-induction study)
```

Below is a more detailed breakdown of the repository.

[//]: # (Utils and objects)

## _objects

A collection of classes and objects used in the analysis. Specifies dataset, questionnaires and model parameters as
well.

1. configs.py (objects to store paths, boolean flags and statistics)
2. data_configs.py (variables used throughout analyses)
3. model_configs.py (LLM sampling objects and functions)
4. model_specs.py (model spec for huggingface and layers details)
5. plot_configs.py (plotting objects)
6. qs_maps.py (questionnaire maps and objects)
7. sae_models.py (sSAE model and training objects)
8. steer_config.py (ssae steering objects)

## _utils/utils.py

A collection of helper functions


[//]: # (Online tasks)

## tasks

JavScript files for each task

### a_open_qs (Open-ended PHQ9 study)

* qs-structure-phq9-v4 (Main code for collecting open-ended responses)
    * Main version
        * No Prolfic depression filtering
    * Sub-version _d
        * Recruit particpants who answer "Yes" to "Do you experience depression?"
    * Sub-version _dd
        * Recruit particpants who answer "Yes" to "Do you experience depression?"
        * Participant answer "Depression" to "Are you currently diagnosed with any of the following mental health
          conditions?"
    * Sub-version _ddd
        * Delayed website loading
        * Save feedback on time runout
        * Recruit particpants who answer "Yes" to "Do you experience depression?"
        * Participant answer "Depression" to "Are you currently diagnosed with any of the following mental health
          conditions?"

### c_mood_induction (Mood induction study)

* qs-intervention-v2 (v2, v2b)
    * Non-autobiographical intervention, no mood VAS
* qs-intervention-v3
    * Autobiographical intervention and mood VAS

[//]: # (Data)

## data

Data for each study (a_open_qs, b_ssae, c_mood_induction). See below for detailed breakdown of data files.

### task_data and task_data/combined

Contains preprocessed data from each study from each version of online task

[//]: # (Outputs)

## outputs

Contains outputs of analysis scripts:

* LLM sampling files (.csv)
* Hidden state tensors (.pt)
* Interemediatry result files and CSVs
* sSAE training and analysis outputs and models
* plots/ - indiviudal plots
* figs/ - combined plots into figures
* vars/ - LaTeX variables for manuscript stats reporting

[//]: # (Scripts)

## scripts

Contains analysis scripts:

* Preprocessing scripts for each study task data
* Further preprocessing scripts for each study
* LLM sampling scripts
* LLM output analysis scripts
* sSAE training and analysis scripts
* Mood induction analysis scripts

### a_open_qs (Open-ended PHQ9 study)

***Data preprocess (task_preprocess/)***

1. download_v4.py (downloads data from firebase)
2. preprocess_v4.py (preprocesses data from firebase)
3. combine_data.py (combined preprocessed data across version)
4. demographics.py (extract and save demographics)

***LLM sampling (llm_sampling/)***

1. sample_logits_itemLevel.py (sample item level logits for phq9)
2. sample_logits_genLevel.py (sample pairwise generalisation logits)

***LLM main analysis (main_analysis/)***

1. analyse_logits_itemLevel.py (analyse item level predictions)
2. analyse_logits_genLevel.py (analyse covariance structure)

### b_ssae (Supervised sparse auto-encoder study)

***Training (training/)***

1. prepare_model_datasets.py (prepare open q phq9 hidden states dataset objects)
2. training_utils.py (training loop, loss and prediction saving functions)
3. model_training.py (train sSAE model for each layer across hyperparameter grid)
4. model_selection.py (find and save best model for each layer)

***Perturbartion (perturbation/)***

1. latent_perturbation.py (find latent perturbations and plot confusion matrices for supplement)
2. logit_perturbation.py (perturb hidden states to change logits of responses)
3. perturbation_selection.py (find the best perturbation strenght fo each direction across validation set)

***Main analysis (main_analysis/)***

1. analyse_model.py (best model predictions for paper, covariance structure and training loss curves)
2. analyse_logits_perturbation.py (analysis of logit perturbation on heldout set)

### c_mood_induction (Mood induction study)

***Data preprocess (task_preprocess/)***

1. download_v2.py and download_v3.py (download firebase data)
2. preprocess_v2.py and preprocess_v3.py (preprocess firebase data)
3. combine_data.py (combine preprocessed data across versions)
4. demographics.py (extract and save demographics)

***sSAE analysis (ssae_scores/)***

1. sample_hidden_states.py (obtain hidden states for each layer, each participat each open ended text)
2. compute_ssae.py (compute and save sSAE scores across hidden states for each open-ended text)

***Main analysis (main_analysis/)***

1. similarity_analysis.py (compute similiarity measures, plot intervention adherence effects - middle row)
2. main_analysis.py (plot similarity confusion matrix and difference results - top row)
3. ssae_analysis.py (plot sSAE results - botom row)

### demographics_table.py

Create demographics table for paper and save as LaTeX variable


[//]: # (Repo data structure)

## Data structure

```
a_open_qs/task_data/combined (Combined behavioural data across experiment types for open-ended PHQ-9 study)
├── demographics.csv (participant age, sex, ethinicty, employment)
├── gad7_data.csv (GAD-7 data - labels and scores, and total time duration for questionnaire)
├── lvl1_closed_data.csv (Level 1 - most general mutliple-choice question responses and time)
├── lvl2_closed_data.csv (Level 2 - semi-specific mutliple-choice question response and time)
├── openq_data_long_stats.csv (participants open-ended responses characterisitcs - mean sentiment, corresponding total score, reaction times and average word rate)
├── openq_data_long.csv (long-format dataframe of participants open-ened responses to each question, reaction time, word-rate, sentiment and corresponding mutliple-choice score)
├── openq_data.csv (wide-fromat of the above) 
├── phq9_data.csv (PHQ-9 mutliple choice responses and total questionnaire duration)
├── sds_data.csv (SDS mutliple choice responses and total questionnaire duration)
└── sub_data.csv (datetime of experiement)

b_ssae/
├── 9q_zs_gemma2-2b-it.pt (torch Dataset object of participants average gemmma2-2b-it embeddings across PHQ-8 open-ended resposnes and associated multiple-choice PHQ-9 scores) 
├── 9q_zs_gemma2-9b-it_ind.pt (torch Dataset object of participants average gemmma9-2b-it embeddings across PHQ-8 open-ended resposnes and associated multiple-choice PHQ-9 scores) 
├── 9q_zs_gemma2-9b-it.pt (torch Dataset object of participants item-level gemmma9-2b-it embeddings across PHQ-8 open-ended resposnes and associated multiple-choice PHQ-9 scores) 
└── sub_list_9q_random.txt (randomised list of participants, kept constant across analyses for train, validation, tesst splits)

c_mood_induction/task_data/combined
├── demographics.csv (participant age, sex, ethinicty, employment)
├── feedback_data_wide_mood.csv (participants end-of-study responses about demand effects, mood changes, etc., combined with phq9 scores, recall sentiment and mood ratings)
├── feedback_data_wide.csv (participants end-of-study responses about demand effects, mood changes, etc., combined with phq9 scores and recall sentiment)
├── feedback_data.csv (participants end-of-study responses about demand effects, mood changes, etc.)
├── int_data.csv (diary responses to task of recreation – "recreate_0,1,2,3" columns – and diary continuation – "act_0" columns. Includes word coutns 'wc' columns.)
├── mood_data.csv (participant mood ratings and phq-9 totals)
├── openq_data.csv (participant open-ended responses about PHQ-9 Q2 (hopeless etc.) and Q4 (energy), as well as the positive re-evaluation responses)
├── phq9_data_q2_long.csv (participant baseline phq9 totals and q2 scores)
├── phq9_data.csv (pariticipant phq-9 scores)
├── phq9_diff_data_wide.csv (phq9-9 score differences and baseline totals in wide format)
├── recall_data_wide.csv (participant average recall sentiment data and baseline phq9)
├── recall_data.csv (pariciapnt recalled words and reaction times at each timepoint, including average sentiment)
└── text_data.csv (combined and processes open-ended responses and diary recreation and continuations)

```

[//]: # (Repo tree structure)

## Tree structure

```
.
├── _objects
  ├── configs.py
  ├── data_configs.py
  ├── model_configs.py
  ├── model_specs.py
  ├── plot_config.py
  ├── qs_maps.py
  ├── sae_models.py
  └── steer_config.py
├── _utils
  └── utils.py
├── data
  ├── a_open_qs
    └── task_data
  ├── b_ssae
  └── c_mood_induction
      ├── task_data
      └── transcripts
├── outputs
  ├── a_open_qs
    ├── llm_sampling
    ├── main_analysis
    └── plots
  ├── b_ssae
    ├── main_analysis
    ├── perturbation
    ├── plots
    └── training
  ├── c_mood_induction
    ├── hs_sampling
    ├── main_analysis
    ├── plots
    ├── similarity_analysis
    ├── ssae_analysis
    └── ssae_scores
  ├── figs
    ├── fig_supp
    ├── Fig1_design_nmh_v4.pdf
    ├── fig2_combined_with_examples.pdf
    ├── Fig3_gen_level.pdf
    ├── Fig4_new_design_v2.pdf
    └── Fig5_new_v2.pdf
  └── vars
      ├── demog_table.tex
      └── paper_stats.tex
├── README.md
├── scripts
  ├── a_open_qs
    ├── llm_sampling
    ├── main_analysis
    └── task_preprocess
  ├── b_ssae
    ├── main_analysis
    ├── perturbation
    └── training
  ├── c_mood_induction
    ├── main_analysis
    ├── ssae_scores
    └── task_preprocess
  └── demographics_table.py
└── tasks
    ├── a_open_qs
      └── qs-structure-phq9-v4
    └── c_mood_induction
        ├── qs-intervention-v2
        └── qs-intervention-v3
```
