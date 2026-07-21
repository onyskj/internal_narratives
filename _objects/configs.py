from pathlib import Path
from datetime import datetime


class Paths:
    def __init__(self, files_dir='files', sub_path='', plots_subdir='', plots_subsubdir='', files_data_dir='../_data'):
        # self.prompts_path = f"{sub_path}prompts/"
        # self.prompts_path = f"{sub_path}prompts/"
        self.files_dir = files_dir


class Bools:
    def __init__(self):
        self.saveFig = False  # whether to save figs
        self.runMe = False  # whether to run analysis
        self.saveMe = False  # whether to save stuff
        self.loadMe = False  # whether to load stuff
        self.withts = True  # whether to append timestamps when savings files
        self.save_states = False  # whether to save torch .pt's

    @property
    def ts(self):
        tmp_fts = '_' + str(round(datetime.timestamp(datetime.now()) * 10000))
        if not self.withts:
            tmp_fts = ''
        return tmp_fts


class ReportVars:
    def __init__(self):
        pass
