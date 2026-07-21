class QsConfig:
    def __init__(self):
        self.qs_max_total = {'ami': 4 * 18, 'phq9': 3 * 9, 'sds': 20 * 4, 'gad7': 3 * 7,
                             'ids30': 3 * 28, 'lvl1_closed': 3 * 1, 'lvl2_closed': 3 * 3}  # csv name, nfactors
        self.qs_min_total = {'ami': 0 * 18, 'phq9': 0 * 9, 'sds': 20 * 1, 'gad7': 0 * 7,
                             'ids30': 0 * 28, 'lvl1_closed': 0, 'lvl2_closed': 0}  # csv name, nfactors
        # self.qs_factors = {'ami': 3, 'phq9': 1, 'sds': 4, 'gad7': 1}
        self.qs_factors = {'ami': 3, 'phq9': 2, 'sds': 4, 'gad7': 1}
        self.max_factors = max(self.qs_factors.values())
        # self.qs_n_qs = {'ami': 18, 'phq9': 9, 'sds': 20, 'gad7': 7, 'ids30': 28}
        self.qs_n_qs = {'ami': 18, 'phq9': 9, 'sds': 20, 'gad7': 7, 'ids30': 28, 'lvl1_closed': 1, 'lvl2_closed': 3}
        self.qs_n_lab = {'ami': 5, 'phq9': 4, 'sds': 4, 'gad7': 4, 'ids30': 4, 'lvl1_closed': 4, 'lvl2_closed': 4}
        self.factor_colours = [['darkorange', 'brown', 'darkolivegreen', 'teal', 'indigo'],
                               ['navajowhite', 'lightcoral', 'lightgreen', 'lightblue', 'plum']]
phq9_map = {'Not at all': 0, 'Several days': 1, 'More than half the days': 2, 'Nearly every day': 3}
gad7_map = {'Not at all': 0, 'Several days': 1, 'More than half the days': 2, 'Nearly every day': 3}

sds_map = {"A little of the time": 1, "Some of the time": 2, "Good part of the time": 3, "Most of the time": 4}
sds_rev_map = {"A little of the time": 4, "Some of the time": 3, "Good part of the time": 2, "Most of the time": 1}
sds_rev_qs = [2, 5, 6, 11, 12, 14, 16, 17, 18, 20]

rev_lists = {'sds': sds_rev_qs}


lvlx_closed_map = {
    'Very Good': 0, 'Good': 1, 'Bad': 2, 'Very Bad': 3
}

maps = {'phq9': phq9_map, 'sds': sds_map, 'gad7': gad7_map}


phq9_qs_map = {'lvl3_q1': 'phq9_q1', 'lvl3_q2': 'phq9_q2', 'lvl3_q3': 'phq9_q3', 'lvl3_q4': 'phq9_q4',
               'lvl3_q5': 'phq9_q5', 'lvl3_q6': 'phq9_q6', 'lvl3_q7': 'phq9_q7', 'lvl3_q8': 'phq9_q8',
               'lvl1_q1': 'lvl1_closed_q1', 'lvl2_q1': 'lvl2_closed_q1', 'lvl2_q2': 'lvl2_closed_q2',
               'lvl2_q3': 'lvl2_closed_q3', 'rep_lvl2_q1': 'lvl2_closed_q1'}

phq9_qs_inv_map = {'phq9_q1': 'lvl3_q1', 'phq9_q2': 'lvl3_q2', 'phq9_q3': 'lvl3_q3', 'phq9_q4': 'lvl3_q4',
                   'phq9_q5': 'lvl3_q5', 'phq9_q6': 'lvl3_q6', 'phq9_q7': 'lvl3_q7', 'phq9_q8': 'lvl3_q8'}

qs_maps = {'phq9': phq9_qs_map}
qs_inv_maps = {'phq9': phq9_qs_inv_map}


qa_loc_key_names = ['oq_qs', 'oq_Answer', 'oq_ans', 'cq_qs', 'cq_Answer', 'last']
qa_loc_key_names_gen = ['cq_qs', 'cq_Answer', 'last']

phq9_q1 = "Little interest or pleasure in doing things."
phq9_q2 = "Feeling down, depressed, or hopeless."
phq9_q3 = "Trouble falling or staying asleep, or sleeping too much."
phq9_q4 = "Feeling tired or having little energy."
phq9_q5 = "Poor appetite or overeating."
phq9_q6 = "Feeling bad about yourself - or that you are a failure or have let yourself or your family down."
phq9_q7 = "Trouble concentrating on things, such as reading the newspaper or watching television."
phq9_q8 = "Moving or speaking so slowly that other people could have noticed? Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual."
phq9_q9 = "Thoughts that you would be better off dead or of hurting yourself in some way."

phq9_qs = [phq9_q1, phq9_q2, phq9_q3, phq9_q4, phq9_q5, phq9_q6, phq9_q7, phq9_q8, phq9_q9]
