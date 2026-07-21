from pathlib import Path
import numpy as np
import os
import torch
from _objects.model_specs import model_specs


def model_params():
    gpt2_param_prefix = 'transformer.h.'
    gpt2_attn_params = ['attn.c_attn.weight', 'attn.c_proj.weight']
    gpt2_mlp_params = ['mlp.c_fc.weight', 'mlp.c_proj.weight']
    gpt2_params = {'attn': gpt2_attn_params, 'mlp': gpt2_mlp_params}
    mistral_param_prefix = 'model.layers.'
    mistral_attn_params = ['self_attn.k_proj.weight', 'self_attn.q_proj.weight', 'self_attn.v_proj.weight',
                           'self_attn.o_proj.weight']
    mistral_mlp_params = ['mlp.gate_proj.weight', 'mlp.up_proj.weight', 'mlp.down_proj.weight']
    mistral_params = {'attn': mistral_attn_params, 'mlp': mistral_mlp_params}

    model_params = {'GPT2': [gpt2_param_prefix, gpt2_params], 'MistralOo': [mistral_param_prefix, mistral_params]}
    return model_params


def get_param(model_instance, sample_config, layer_idx=0, param_type='mlp', param_idx=0):
    param_prefix = sample_config.params_dict[0]
    param_name = sample_config.params_dict[1][param_type][param_idx]
    param_name = param_prefix + f"{layer_idx}." + param_name
    print(f"Parameter name: {param_name}")
    with torch.no_grad():
        all_params = list(set(model_instance.state_dict().keys()))
    is_valid_param = param_name in all_params
    if not is_valid_param:
        print(f"\tParameter name not valid!")
        param = None
    else:
        param = model_instance.get_parameter(param_name)
        param.requires_grad = True

    return param, param_name


class SampleLogitsConfig:
    """
    Configuration class for handling various settings, state management, and path configurations for a specific
    model and task. This class is designed to manage the configurations necessary for controlling behaviors of
    model sampling, questionnaire generation, and related outputs.

    It provides access to critical attributes for model-specific operations, dynamically sets model specifications
    based on pre-defined configurations, and manages file paths for storing or retrieving results.

    A variety of parameters can be customized, including model type, temperature, token limits, and sampling strategy.

    Attributes:
        :ivar model_name_sshort: Short identifier for the model being used.
        :ivar instr_name: Instruction set name used for configuration.
        :ivar temp: Temperature parameter for controlling randomness in sampling.
        :ivar top_p: Nucleus sampling parameter to limit cumulative probability for token selection.
        :ivar nSamples: Number of samples to generate in each batch.
        :ivar batchSize: Batch size for processing during sampling.
        :ivar remSamples: Counter for remaining samples to process.
        :ivar remBatchSize: Counter for remaining batch size.
        :ivar remBatches: Counter for remaining number of total batches.
        :ivar currentFiles: Boolean indicating whether files are ready for further processing.
        :ivar runMe: Boolean flag indicating if processing should be executed.
        :ivar qs_name: Name of the context questionnaire.
        :ivar skip_sui: Flag to determine if suicidality should be skipped.
        :ivar gen_qs_name: Name of the questionnaire for answer sampling (generalisation)
        :ivar openq_fname: Name of the file containing open-ended questions.
        :ivar customq_fname: Name of the file containing custom closed-ended questions.
        :ivar context_name: Name of the context used during response sampling.
        :ivar gen_sample_name: Name of the sample set directory for file creation.
        :ivar max_new_tok: Maximum number of new tokens to generate in sampling.
    """
    def __init__(self, paths, model_name='GPT2', qs_name='sds', gen_qs_name=None, instr_name='instr1', skip_sui=True,
                 temp='', top_p='', max_new_tok=10):
        self._prompts_path = None
        self.subj = 'sub0'
        self.which_q = 'lvl0_q0'
        self.which_gen_q = None
        self.label_letters = None

        self._paths = paths
        # self._context_supdir = None
        self._prefix_path = None

        self.model_name_sshort = model_name
        # self.model_params = model_params()

        # set model specs for hugging face
        for k, v in model_specs[model_name].items():
            setattr(self, k, v)

        self.midL = int(self.L * 0.6)
        self.layer_list = list(set(np.append(np.arange(2, self.L, 3), self.L).tolist()))

        self.type = 'model'
        self.save_states = False

        self._model_name_r = None  # model name + revision
        self._source_name = None  # short model name (no revision)

        self.instr_name = instr_name
        self.temp = temp
        self.top_p = top_p
        self._max_new_tok = None

        self._cond = None  # condition temp^topp
        self._id_filter = None  # filter tmp^topp^model^prompt

        self._model_name_rp = None  # model name + revision  + prompt
        self._model_name_rhp = None  # model name + revision + hyper-param pair + prompt
        self._model_name_hf = None  # HuggingFace model name
        self._prompt_name = None

        self.nSamples = 2
        self.batchSize = 10

        self.remSamples = None
        self.remBatchSize = None
        self.remBatches = None
        self.currentFiles = False

        self.runMe = True
        self.qs_name = qs_name
        self.skip_sui = skip_sui
        self.gen_qs_name = gen_qs_name  # name of the questionnaire to sample answers to

        self.openq_fname = None  # name of file with open questions
        self.customq_fname = None  # name of file with custom closed questions
        self.context_name = None  # name of the context used before sampling resposne (either level or arbitrary perm.)
        self.gen_sample_name = None  # name of the set of samples for dir creation

        self._responses_path = None
        self._outputs_path = None
        self._states_path = None

        self.max_new_tok = max_new_tok

    def get_remaining_samples(self, printMe=False, pert_config_len=1):
        count_resp_el = False
        count_logit_el = False
        count_pt_el = self.save_states == False
        try:
            count_resp_el = len(
                [ol for ol in (os.listdir(self.sample_path)) if '.csv' in ol and 'responses' in ol]) >= pert_config_len
            count_logit_el = len(
                [ol for ol in (os.listdir(self.sample_path)) if '.csv' in ol and 'logits' in ol]) >= pert_config_len
            if self.save_states:
                count_pt_el = len([ol for ol in (os.listdir(self.sample_path)) if
                                   '.pt' in ol and 'hidden_states' in ol]) >= pert_config_len
        except:
            pass
        count_total_el = count_resp_el and count_logit_el and count_pt_el
        self.currentFiles = count_total_el
        if printMe:
            print(f'Files complete : {self.currentFiles}')

    @property
    def model_name_r(self):
        self._model_name_r = '^'.join([self.model_name, self.revision])
        return self._model_name_r

    @property
    def model_name_hf(self):
        self._model_name_hf = '/'.join([self.hf_host, self.model_name])
        return self._model_name_hf

    @property
    def source_name(self):
        self._source_name = self.model_name_r.split('^')[0]
        return self._source_name

    @property
    def cond(self):
        self._cond = 'tpv-' + str(self.temp) + '^topp-' + str(self.top_p)
        return self._cond

    @property
    def model_name_rp(self):
        self._model_name_rp = '^'.join([self.model_name_r, self.instr_name])
        return self._model_name_rp

    @property
    def id_filter(self):
        # self._id_filter = '^'.join([str(self.temp), str(self.top_p), self.model_name_lp])
        self._id_filter = '^'.join([self._cond, self.model_name_rp])
        return self._id_filter

    @property
    def sample_path(self):
        if self.gen_qs_name is None:
            if self.subj != 'sub0' and self.which_q != 'lvl0_q0':
                # self._outputs_path = f"{self._paths.subj_outputs_dir}{self.subj}/{self.which_q}/{self.model_name_rhp}/"
                self._sample_path = f"{self._paths.files_dir}paired/{''.join(self.label_letters)}/subjects/{self.subj}/{self.which_q}/{self.model_name_rp}/"
                Path(self._sample_path).mkdir(parents=True, exist_ok=True)
        else:
            if self.subj != 'sub0' and self.which_q != 'lvl0_q0':
                # self._outputs_path = f"{self._paths.subj_outputs_dir}{self.subj}/{self.which_q}/{self.model_name_rhp}/"
                self._sample_path = f"{self._paths.files_dir}cross/{self.gen_qs_name}/{''.join(self.label_letters)}/subjects/{self.subj}/{self.which_q}/{self.which_gen_q}/{self.model_name_rp}/"
                Path(self._sample_path).mkdir(parents=True, exist_ok=True)

        return self._sample_path

    @property
    def prompts_path(self):
        self._prompts_path = f"{self._paths.prompts_path}"
        return self._prompts_path

