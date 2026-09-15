# %% Load libs and setup
from natsort import natsorted
from texttable import Texttable
import latextable
import numpy as np
import pandas as pd

from _objects.configs import *
from scripts.a_open_qs.main_analysis.analysis_utils import return_good_sub

bools = Bools()
bools.saveTex = True
bools.saveTex = False

# set up var names
employment_types = ['Full-Time', 'Part-Time', "Not in paid work (e.g. homemaker', 'retired or disabled)", 'Other',
                    'Unemployed (and job seeking)', 'Due to start a new job within the next month']
employment_code = ['Full-Time', 'Part-Time', 'Unpaid', 'Other', 'Unemployed', 'Starting soon']
ethnicity_types = ['White', 'Black', 'Mixed', 'Asian', 'Other']

ethnicity_code = [e[0] for e in ethnicity_types]
ethnicity_code = ['White', 'Black', 'Mixed', 'Asian', 'Other']
sex_types = ['Female', 'Male']
sex_code = ['F', "M"]


def process_dem(dem_df):
    na_val = ['CONSENT_REVOKED', 'DATA_EXPIRED']

    dem_df.replace(na_val, np.nan, inplace=True)
    dem_df['employment'] = dem_df['employment'].replace(employment_types, employment_code)
    dem_df['ethnicity'] = dem_df['ethnicity'].replace(ethnicity_types, ethnicity_code)
    dem_df['sex'] = dem_df['sex'].replace(sex_types, sex_code)

    dem_df['age'] = dem_df['age'].astype(float)
    return dem_df


# %% Load data
ph = '-'  # for latex
paths = Paths(files_dir='', plots_subdir='', plots_subsubdir='')

# Load study 1 data
study_name_a = 'a_open_qs/'
paths.data_path = f'data/{study_name_a}/task_data/combined/'

dem_df_s1 = pd.read_csv(f"{paths.data_path}demographics.csv")
dem_df_s1 = process_dem(dem_df_s1)
good_subs = natsorted(return_good_sub(paths, ['v4', 'v4_d', 'v4_dd', 'v4_ddd']))

# Total Scores
phq9_data = pd.read_csv(f"{paths.data_path}/phq9_data.csv")
phq9_data = phq9_data[phq9_data['sub'].isin(good_subs)]
gad7_data = pd.read_csv(f"{paths.data_path}/gad7_data.csv")
gad7_data = gad7_data[gad7_data['sub'].isin(good_subs)]
sds_data = pd.read_csv(f"{paths.data_path}/sds_data.csv")
sds_data = sds_data[sds_data['sub'].isin(good_subs)]

p_total_s1 = phq9_data['total'].aggregate(['mean', 'std'])
g_total_s1 = gad7_data['total'].aggregate(['mean', 'std'])
s_total_s1 = sds_data['total'].aggregate(['mean', 'std'])
N_s1 = phq9_data['sub'].nunique()

# Load study 2 data
study_name_c = 'c_mood_induction/'
paths.data_path = f'data/{study_name_c}/task_data/combined/'
dem_df_s2 = pd.read_csv(f"{paths.data_path}demographics.csv")
dem_df_s2 = process_dem(dem_df_s2)
phq9_data = pd.read_csv(f"{paths.data_path}/phq9_diff_data_wide.csv")
p_total_s2 = phq9_data.groupby(['autobio', 'condition'], as_index=True)['s_total'].aggregate(['mean', 'std'])
N_s2 = phq9_data.groupby(['autobio', 'condition'], as_index=True)['sub'].nunique()

del phq9_data, sds_data, gad7_data

# %% Study 1 demographics dicts
age_sum_s1 = dem_df_s1['age'].aggregate(['mean', 'std'])
sex_sum_s1 = dem_df_s1['sex'].value_counts(normalize=True) * 100
ethn_sum_s1 = dem_df_s1['ethnicity'].value_counts(normalize=True) * 100
employ_sum_s1 = dem_df_s1['employment'].value_counts(normalize=True) * 100

pm = "\u00B1"
s1_dem_dict = {
    'age': f"{age_sum_s1['mean']:.1f} {pm} {age_sum_s1['std']:.1f}",
    'sex': f"{sex_sum_s1['F']:.0f}\\% F",
    'ethnicity': ethn_sum_s1[ethnicity_code].round(1),
    'employment': employ_sum_s1[employment_code].round(1),
    'phq9': f"{p_total_s1['mean']:.1f} {pm} {p_total_s1['std']:.1f}",
    'gad7': f"{g_total_s1['mean']:.1f} {pm} {g_total_s1['std']:.1f}",
    'sds': f"{s_total_s1['mean']:.1f} {pm} {s_total_s1['std']:.1f}",
}
print(s1_dem_dict)

# %% Study 2 demographics dicts
age_sum_s2 = dem_df_s2.groupby(['autobio', 'condition'], as_index=True)['age'].aggregate(['mean', 'std'])
sex_sum_s2 = dem_df_s2.groupby(['autobio', 'condition'], as_index=True)['sex'].value_counts(normalize=True) * 100
ethn_sum_s2 = dem_df_s2.groupby(['autobio', 'condition'], as_index=True)['ethnicity'].value_counts(normalize=True) * 100
employ_sum_s2 = dem_df_s2.groupby(['autobio', 'condition'], as_index=True)['employment'].value_counts(
    normalize=True) * 100

s2_dem_dict = {}
for i in p_total_s2.index:
    cond_et = ethn_sum_s2[i[0]][i[1]].index.tolist()
    miss_eth = [i for i in ethnicity_code if i not in cond_et]
    for miss_val in miss_eth:
        ethn_sum_s2.loc[i[0], i[1], miss_val] = np.nan
    cond_em = employ_sum_s2[i[0]][i[1]].index.tolist()
    miss_employ = [i for i in employment_code if i not in cond_em]
    for miss_val in miss_employ:
        employ_sum_s2.loc[i[0], i[1], miss_val] = np.nan

    s2_dem_dict[i] = {
        'age': f"{age_sum_s2.loc[i]['mean']:.1f} {pm} {age_sum_s2.loc[i]['std']:.1f}",
        'sex': f"{sex_sum_s2.loc[i]['F']:.0f}\\% F",
        'ethnicity': ethn_sum_s2[i[0]][i[1]][ethnicity_code].round(1),
        'employment': employ_sum_s2[i[0]][i[1]][employment_code].round(1),
        'phq9': f"{p_total_s2.loc[i]['mean']:.1f} {pm} {p_total_s2.loc[i]['std']:.1f}",
    }

# %% Both studies demo dict and latex table
hrule = '__HRULE__'
rows = [["", "", "MH", "ML", "MH", "ML"],
        ["Sample size (n)", f"{N_s1}"] + [N_s2.loc[i] for i in N_s2.index],
        [f"Age (mean {pm} SD)", f"{s1_dem_dict['age']}"] + [s2_dem_dict[i]['age'] for i in N_s2.index],
        [r"Sex (\% Female)", f"{s1_dem_dict['sex']}"] + [s2_dem_dict[i]['sex'] for i in N_s2.index],
        [hrule] * 6,
        [r"Ethnicity \%"] + 5 * ['']]
for e, ec in enumerate(ethnicity_code):
    tmp_row = [r'\quad ' + ec, f"{s1_dem_dict['ethnicity'][ec]:.1f}"] + [f"{s2_dem_dict[i]['ethnicity'][ec]:.1f}" for i
                                                                        in N_s2.index]
    tmp_row = [i if i != 'nan' else ph for i in tmp_row]
    rows.append(tmp_row)
rows.append([hrule] * 6)
rows.append([r"Employment \%"] + 5 * [''])
for e, ec in enumerate(employment_code):
    tmp_row = [r'\quad ' + ec, f"{s1_dem_dict['employment'][ec]:.1f}"] + [f"{s2_dem_dict[i]['employment'][ec]:.1f}" for i
                                                                         in N_s2.index]
    tmp_row = [i if i != 'nan' else ph for i in tmp_row]
    rows.append(tmp_row)
rows.append([hrule] * 6)
rows.append([f"Total score (mean {pm} SD)"] + 5 * [''])
rows.append(["PHQ-9 (depression)", f"{s1_dem_dict['phq9']}"] + [s2_dem_dict[i]['phq9'] for i in N_s2.index])
rows.append(["GAD-7 (anxiety)", f"{s1_dem_dict['gad7']}"] + [ph for i in N_s2.index])
rows.append(["SDS (depression)", f"{s1_dem_dict['sds']}"] + [ph for i in N_s2.index])
multicolumn_header = [("", 1), ("Study 1", 1), ("Study 2 A", 2), ('Study 2 B', 2)]
table_13 = Texttable()
table_13.set_cols_dtype(["t"] * 6)
table_13.add_rows(rows)
print('\n-- Example 13: Multicolumn header with vertical and horizontal lines --')
print('Texttable Output:')
print(table_13.draw())
print('Latextable Output:')
print(latextable.draw_latex(table_13, multicolumn_header=multicolumn_header, use_booktabs=False))

# Save table to tex variable
latex_tab_str = latextable.draw_latex(table_13, multicolumn_header=multicolumn_header, use_booktabs=True)
latex_tab_str = latex_tab_str.split('\n')[8:-4]
latex_tab_str = '\n'.join(['\t\t\t\\hline' if hrule in row else row for row in latex_tab_str])
latex_tab_str = "\\newcommand{\\TableDemographics}{\n" + latex_tab_str + '\n}'
if bools.saveTex:
    with open('outputs/vars/demog_table.tex', 'w') as f:
        f.write(latex_tab_str)

# %% Study 2 only table
rows = [["", "MH", "ML", "MH", "ML"],
        ["N"] + [N_s2.loc[i] for i in N_s2.index],
        [f"Age"] + [s2_dem_dict[i]['age'] for i in N_s2.index],
        ["Sex"] + [s2_dem_dict[i]['sex'] for i in N_s2.index],
        [r"Ethnicity\%"] + 4 * ['']]
for e, ec in enumerate(ethnicity_code):
    tmp_row = [r'\quad ' + ec] + [f"{s2_dem_dict[i]['ethnicity'][ec]:.1f}" for i in N_s2.index]
    tmp_row = [i if i != 'nan' else ph for i in tmp_row]
    rows.append(tmp_row)
rows.append([r"Employment\%"] + 4 * [''])
for e, ec in enumerate(employment_code):
    tmp_row = [r'\quad ' + ec] + [f"{s2_dem_dict[i]['employment'][ec]:.1f}" for i in N_s2.index]
    tmp_row = [i if i != 'nan' else ph for i in tmp_row]
    rows.append(tmp_row)
rows.append(["PHQ-9 total"] + [s2_dem_dict[i]['phq9'] for i in N_s2.index])
multicolumn_header = [("", 1), ("Study 2 Non-Autobio", 2), ('Study 2 Autobio', 2)]
table_13 = Texttable()
table_13.set_cols_dtype(["t"] * 5)
table_13.add_rows(rows)
print('\n-- Example 13: Multicolumn header with vertical and horizontal lines --')
print('Texttable Output:')
print(table_13.draw())
print('Latextable Output:')
print(latextable.draw_latex(table_13, multicolumn_header=multicolumn_header))
