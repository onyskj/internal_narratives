#### word limits and exclusion criteria


p_thr = 0.05
# Study 1 - Open-ended study
min_word_oq_sample_s1 = None  # for sampling
min_word_oq_analyse_s1 = 30  # TODO: for analyses

# Study 2 - sSAE
min_word_oq_s2 = 30  # for sSAE datasets from study 1
seed_value = 80  # seed for torch training
max_epochs = 1000  # total number of epochs to train for
es_patience = 30  # patient parameter for early stopping
es_delta = 0  # delta for early stopping
# perturbation details
q_score_change = 1
p_force = 1
d_thr = 0.3 # cohen d effect size threshold to detect perturbation effect
# subject removed if missing any phq9 response

# %% Study 3 - Mood induction
min_word_recall = 3

th_ratio_rec = 0.5  # Recreated diary, at least 50%
min_word_recreate_s3 = int(15 * th_ratio_rec)

th_ratio_act = 0.5  # Diary continuation, at least 50%
min_word_act_s3 = int(100 * th_ratio_act)

th_ratio_oq = 0.5  # LATEST # Open-ended response, at least 50%
min_word_oq_s3 = int(30 * th_ratio_oq)

min_char_recall = 3  # min number of chars for recalled word

min_word_rec_dict = {
    'ML': {'responses_recreate_0': int(34 * th_ratio_rec), 'responses_recreate_1': int(56 * th_ratio_rec),
           'responses_recreate_2': int(53 * th_ratio_rec), 'responses_recreate_3': int(51 * th_ratio_rec)},
    'MH': {'responses_recreate_0': int(46 * th_ratio_rec), 'responses_recreate_1': int(53 * th_ratio_rec),
           'responses_recreate_2': int(48 * th_ratio_rec), 'responses_recreate_3': int(43 * th_ratio_rec)}}

word_list = ["vigorous", "energetic", "lively", "exhausted", "tired", "drained", "joyful", "delighted", "happy",
             "unhappy", "hopeless", "miserable", "genuine", "wholesome", "ethical", "corrupt", "sloppy", "unsafe"]
word_dict = {"joyful": "mh", "delighted": "mh", "happy": "mh", "unhappy": "ml", "hopeless": "ml", "miserable": "ml",
             "exhausted": "el", "tired": "el", "drained": "el", "vigorous": "eh", "energetic": "eh", "lively": "eh",
             "genuine": "p", "wholesome": "p", "ethical": "p", "corrupt": "n", "sloppy": "n", "unsafe": "n"}

word_dict_broad = {"joyful": "h", "delighted": "h", "happy": "h", "unhappy": "l", "hopeless": "l", "miserable": "l",
                   "exhausted": "l", "tired": "l", "drained": "l", "vigorous": "h", "energetic": "h", "lively": "h",
                   "genuine": "p", "wholesome": "p", "ethical": "p", "corrupt": "n", "sloppy": "n", "unsafe": "n"}

word_dict_broadest = {"joyful": "h", "delighted": "h", "happy": "h", "unhappy": "l", "hopeless": "l", "miserable": "l",
                      "exhausted": "l", "tired": "l", "drained": "l", "vigorous": "h", "energetic": "h", "lively": "h",
                      "genuine": "h", "wholesome": "h", "ethical": "h", "corrupt": "l", "sloppy": "l", "unsafe": "l"}

wld = {'mh': ["joyful", "delighted", "happy"], 'ml': ["unhappy", "hopeless", "miserable"],
       'el': ["exhausted", "tired", "drained"], 'eh': ["vigorous", "energetic", "lively"],
       'p': ["genuine", "wholesome", "ethical"], 'n': ["corrupt", "sloppy", "unsafe"]}
word_list_broad = {'h': wld['mh'] + wld['eh'], 'l': wld['ml'] + wld['el'], 'ho': wld['p'], 'lo': wld['n']}

'''
- All mood VAS items
- All Q2 VAS items
'''

'''
Manual Exclusions
'sub109_v2b' - repeated same words in mood open ended
'sub111_v2b','sub166_v3','sub32_v2b - wrote sentence in recall

'''
