# %% Import and initialise
import copy
import os
import re

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from _objects.qs_maps import *

if os.uname()[0] != 'Darwin':  # if not on mac
    import gc

    device_name = 'cuda'


    def flush():
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
else:
    device_name = 'mps'


    def flush():
        pass


# %% COMMON FUNCTIONS

# Loads model and tokenizer
def setup_model(sample_config):
    """
    Configures and initializes a language model and its corresponding tokenizer based on the provided
    configuration. The method supports conditional customization of tokens depending on the model name,
    ensuring compatibility and proper usage for various pretrained models.

    :param sample_config: An object defining model-related configuration properties, such as
                          model name, revision, and other specific settings.
    :return: A tuple consisting of the initialized model and its tokenizer. The tokenizer is configured
             for the specified model, and the model is set to evaluation mode.
    """
    tokenizer = AutoTokenizer.from_pretrained(sample_config.model_name_hf, use_fast=True, trust_remote_code=True)
    if sample_config.model_name not in ['gemma-2-2b-it', 'gemma2-9b-it']:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    if sample_config.model_name in ['Llama-3.1-8B-Instruct', 'Llama-3.2-3B-Instruct']:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(sample_config.model_name_hf, device_map=device_name,
                                                 trust_remote_code=True, revision=sample_config.revision,
                                                 attn_implementation='eager', torch_dtype=torch.bfloat16)
    model.eval()
    if sample_config.model_name not in ['gemma-2-2b-it', 'gemma2-9b-it']:
        model.generation_config.pad_token_id = model.generation_config.eos_token_id
    if sample_config.model_name in ['Llama-3.1-8B-Instruct', 'Llama-3.2-3B-Instruct']:
        model.generation_config.pad_token_id = tokenizer.eos_token_id

    return model, tokenizer


# Pre process open q data
def get_openq_data(openq_data, sample_config):
    """
    Preprocesses the Open-Ended Questions (OpenQ) dataset based on the specified configuration
    and extracts the relevant question responses in a structured format.

    :param openq_data: A pandas DataFrame containing OpenQ dataset to be processed.
    :param sample_config: Configuration file or dictionary used to load task content
        and determine the relevant OpenQ question names.
    :return: A pandas DataFrame where OpenQ responses are structured in a long-format
        table. Each row represents a subject's response to a specific open-ended question.
    """
    _, open_qs_dict, _ = load_task_content(sample_config)
    oq_names = list(open_qs_dict.keys())  # + list(open_qs_rep_dict.keys())

    # preprocess text
    openq_data = openq_data.replace(r'\s+\.', '.', regex=True)
    openq_data = openq_data.replace(r'\s+,', ', ', regex=True)
    openq_data = openq_data.replace(r'\n+,', ' ', regex=True)
    df_obj = openq_data.select_dtypes('object')
    openq_data[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    openq_data_long = pd.melt(openq_data, id_vars=['sub'], value_vars=oq_names, var_name='q_name').sort_values(
        by=['sub', 'q_name']).reset_index(drop=True)

    empty_resp_idx = openq_data_long['value'].apply(lambda x: len(x.split(' ')) if type(x) == str else 0) == 0
    openq_data_long = openq_data_long.loc[~empty_resp_idx, :]
    del df_obj, empty_resp_idx, oq_names  # , phq9_names

    return openq_data_long


# Load content of instructions and questions
def load_task_content(sample_config):
    """
    Loads task content from specified files based on the provided configuration and processes the data into dictionaries
    of instructions, open-ended questions, and closed-ended questions.

    :param sample_config: The configuration object containing paths and settings for loading and processing files.

    :return: A tuple containing three dictionaries:
        - instr_dict: A dictionary where keys are instruction names and values are the corresponding instruction content.
        - open_qs_dict: A dictionary where keys are open-ended question names and values are the corresponding question content.
        - closed_qs_dict: A dictionary where keys are question identifiers and values are the corresponding question content.
    """
    instructions_file = f"{sample_config.prompts_path}experiment/{sample_config.instr_name}.txt"
    openq_file = f"{sample_config.prompts_path}experiment/{sample_config.qs_name}_open_{sample_config.gen_fname}.txt"
    closed_qs_file = f"{sample_config.prompts_path}qs/custom/custom_{sample_config.gen_fname}.txt"
    qsn_qs_file = f"{sample_config.prompts_path}qs/{sample_config.qs_name}/{sample_config.qs_name}.txt"

    with open(instructions_file, encoding='utf-8') as f:
        instructions = f.read().split('^^^')  # instructions = f.read()

    instr_dict = {}
    for instr in instructions:
        instr_name = instr.split('\n')[1]
        instr_content = '\n'.join(instr.split('\n')[2:])
        instr_dict[instr_name] = instr_content

    with open(openq_file, encoding='utf-8') as f:
        open_qs = f.read().split('^^^')

    open_qs_dict = {}
    for open_q in open_qs:
        open_q_name = open_q.split('\n')[1]
        open_q_content = open_q.split('\n')[2:][0]
        open_qs_dict[open_q_name] = open_q_content

    with open(closed_qs_file, encoding='utf-8') as f:
        closed_qs = f.read()

    closed_qs_sections = closed_qs.split('\n^^\n')
    closed_qs = closed_qs_sections[1].split('\n')
    closed_qs_dict = {q.split('.')[0]: q.split('. ')[1] for q in closed_qs}

    with open(qsn_qs_file, encoding='utf-8') as f:
        qsn_qs = f.read()
    prompt_sections = qsn_qs.split('\n^^\n')
    qsn_qs = prompt_sections[2].split('\n')
    if sample_config.skip_sui:
        qsn_qs.pop()

    inv_map = qs_inv_maps[sample_config.qs_name]
    qsn_qs_dict = {inv_map[sample_config.qs_name + '_q' + q.split('.')[0]]: 'Problem: ' + q.split('. ')[1] for q in
                   qsn_qs}

    closed_qs_dict = dict(sorted((qsn_qs_dict | closed_qs_dict).items()))
    return instr_dict, open_qs_dict, closed_qs_dict


# formats prompt to fit with chat template
def format_messages(messages, toker, sample_config):
    """
    Formats messages based on the specified template associated with the model configuration. Depending on the
    model name from the sample configuration, a specific template is selected and applied to the messages. If a
    template is applied, the messages may also undergo additional processing such as tokenization and prompt
    generation before being returned in the desired format.

    :param messages: A list of message dictionaries, where each dictionary contains a "role" and "content" for
        the participant in the conversation.
    :param toker: A tokenizer object that contains methods for applying templates to the messages.
    :param sample_config: Configuration object containing key details about the model, such as the model name
        and file paths.
    :return: The formatted string of messages based on the model template or default formatting if no template
        is matched.
    """
    template_name = None
    if len(re.findall('Mistral-.*-Instruct', sample_config.model_name_hf)) > 0:
        template_name = 'mistral-instruct'
    if len(re.findall('Orca', sample_config.model_name_hf)) > 0:
        template_name = 'chatml'
    if len(re.findall('.*gemma.*-it.*', sample_config.model_name_hf)) > 0:
        template_name = 'gemma-it'
    if len(re.findall('.*CausalLM.*', sample_config.model_name_hf)) > 0:
        template_name = 'chatml'
    if len(re.findall('vicuna', sample_config.model_name_hf)) > 0:
        template_name = 'vicuna'
    if len(re.findall('Llama-3.*-Instruct', sample_config.model_name_hf)) > 0:
        template_name = 'llama-3-instruct'
    if len(re.findall('Llama-2.*-chat', sample_config.model_name_hf)) > 0:
        template_name = 'llama-2-chat'
    if len(re.findall('llama2_.*_uncensored', sample_config.model_name_hf)) > 0:
        template_name = 'llama-2-uncensored'
    if len(re.findall('.*Qwen.*-Chat.*', sample_config.model_name_hf)) > 0:
        template_name = 'chatml'
    if len(re.findall('gpt-', sample_config.model_name_hf)) > 0:
        template_name = 'gpt'

    if (template_name is not None) and (template_name != 'llama-2-uncensored') and (template_name != 'gpt'):
        chat_template = open(
            sample_config._paths.sub_path + 'ch_temp/chat_templates/' + template_name + '.jinja').read()
        chat_template = chat_template.replace('    ', '').replace('\n', '')
        toker.chat_template = chat_template
        messages_formatted = toker.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        if template_name != 'mistral-instruct':
            messages_formatted = re.sub('<s>', '', messages_formatted)
            if template_name != 'vicuna':
                messages_formatted = re.sub('</s>', '', messages_formatted)

    else:
        if template_name == 'llama-2-uncensored':
            role_map = {'system': '### HUMAN:\n', 'user': '\n### HUMAN:\n', 'assistant': '\n### RESPONSE:\n'}
            messages_formatted = ''.join([role_map[msg['role']] + msg['content'] for msg in messages])
        elif template_name == 'gpt':
            messages_formatted = messages
        else:
            role_map = {'system': '\n', 'user': '\n', 'assistant': '\n'}
            messages_formatted = ''.join([msg['content'] + role_map[msg['role']] for msg in messages])

    return messages_formatted


# function to locate subtexts in text
def find_subsequence_n(text, subtext, n=1):
    """
    Finds the nth occurrence of a given subsequence within a text string and returns its starting index.

    If the subsequence does not occur at least n times, the function will return -1.

    :param text: The main text in which the subsequence will be searched. Expected to be a string type.
    :param subtext: The subsequence that needs to be searched within the main text. Expected to be a string type.
    :param n: The occurrence number (1-based index) of the subsequence to find. Expected to be an integer type.
        Defaults to 1.
    :return: Returns an integer value corresponding to the starting index of the nth occurrence of the subsequence.
        Returns -1 if the subsequence does not occur at least n times.
    """
    text_trim = copy.deepcopy(text)
    loc_counter = 0
    id_loc = -1
    for oc in range(n):
        location = text_trim.find(subtext)  # find substring location start
        if location != -1:
            id_loc = location + loc_counter

            loc_counter += location + len(subtext) + 1  # location in text after the first occurence
            text_trim = text[loc_counter:]  # trim the string so tht the first occurence is not there
        else:
            id_loc = -1
            break
    return id_loc


# finds locations in token index space of specific questions, answers
def find_loc(input_text, to_find_text, tokenizer, n=1):
    """
    Finds the location of a substring within a tokenized input text and retrieves related
    details such as start and end token indices, as well as the decoded text of the last token.

    :param input_text: The full input text string where the search is performed.
    :param to_find_text: The substring that needs to be located within the input text.
    :param tokenizer: The tokenizer object used to tokenize the input text and compute
        necessary offsets and token mappings.
    :param n: The occurrence of the substring to find within the input text. For example,
        if n=2, the function tries to locate the second occurrence of the substring.
        Default is 1.
    :return: A tuple containing:
        - loc_start (int): The start index of the substring in the tokenized space, or -1
          if the substring is not found.
        - loc_end (int): The end index of the substring in the tokenized space, or -1
          if the substring is not found.
        - last_token_loc (int): The token index of the last character in the found substring,
          or -1 if the substring is not found.
        - last_token (str): The decoded text of the last token in the found substring, or an
          empty string if the substring is not found.
    """
    input_ids = tokenizer(input_text, return_tensors="pt", padding=True,
                          return_offsets_mapping=True)  # .input_ids[0].tolist()
    loc_start_text = find_subsequence_n(input_text, to_find_text, n)

    if loc_start_text != -1:
        loc_end_text = loc_start_text + len(to_find_text)
        token_locations = np.where((input_ids.offset_mapping[0, :, 0] >= loc_start_text) & (
                input_ids.offset_mapping[0, :, 1] <= loc_end_text))[0]
        loc_start = int(token_locations[0])
        loc_end = int(token_locations[-1] + 1)
        last_token_loc = int(token_locations[-1])
    else:
        loc_start = -1
        loc_end = -1
        last_token_loc = -1

    last_token = tokenizer.decode(input_ids.input_ids[0][last_token_loc])

    return loc_start, loc_end, last_token_loc, last_token


# %% PAIRED SAMPLING - item level
# Create creates prompt with questions and labels
def create_question_pairs_instr(sample_config):
    """
    Generates instructional question pairs along with prompts by processing and structuring input configuration.

    This function processes various textual components, including instructional prompts, question prompts,
    open and closed questions, and preambles, to generate a structured set of question pairs. Specific aspects
    like labeling scale questions and handling specific configurations (e.g., skipping questions or customizing
    files) are also managed.

    :param sample_config: Configuration object containing paths, filenames, labels, and various processing
        flags used for generating questions and instructional prompts.
    :return: A tuple containing introduction prompt, open question instructional text, open questions dictionary,
        closed questions dictionary, closed question preamble, dictionary of scaled question pairs,
        closed question instructional text, and scaled question preamble.
    :rtype: tuple
    """
    # load instructions and intro
    instr_dict, open_qs_dict, closed_qs_dict = load_task_content(sample_config)
    intro_prompt = instr_dict['intro']
    scale_instr = instr_dict['scale_instr_logit']

    # load and get questionnaire questions
    qs_prompt_file = f"{sample_config.prompts_path}qs/{sample_config.qs_name}/{sample_config.qs_name}.txt"
    with open(qs_prompt_file, encoding='utf-8') as f:
        qs_prompt = f.read()

    qsn_preamble = '\n' + instr_dict[sample_config.qs_name + '_preamble'] + '\n'
    prompt_sections = qs_prompt.split('\n^^\n')
    qsn_questions = prompt_sections[2].split('\n')

    # add letter labels to scale (Permute optionally)
    tmp_labels = prompt_sections[1].split('- ')
    tmp_labels = [l for l in tmp_labels if l != '']
    tmp_labels = [f'{ltr} - {tp}' for tp, ltr in zip(tmp_labels, sample_config.label_letters)]
    tmp_labels = ''.join(tmp_labels)
    prompt_sections[1] = tmp_labels

    qsn_questions = ['' + q + '\n\n' + scale_instr + "\n" + prompt_sections[1] + '\n\nAnswer: ' for q in qsn_questions]
    if sample_config.skip_sui:
        qsn_questions.pop()
    qsn_questions_dict = {sample_config.qs_name + '_q' + q.split('.')[0]: 'Problem: ' + q.split('. ')[1] for q in
                          qsn_questions}

    # load and get closed questions - leveled
    cq_instr = '\n\n' + instr_dict['closed_instr'] + '\n'
    cq_preamble = '\n\n' + instr_dict['closed_preamble'] + '\n'

    qs_custom_file = f"{sample_config.prompts_path}qs/custom/custom_{sample_config.gen_fname}.txt"
    with open(qs_custom_file, encoding='utf-8') as f:
        qs_custom = f.read()

    custom_sections = qs_custom.split('\n^^\n')
    closed_questions = custom_sections[1].split('\n')

    # add letter labels to scale (Permute optionally)
    tmp_labels_custom = custom_sections[0].split('- ')
    tmp_labels_custom = [l for l in tmp_labels_custom if l != '']
    tmp_labels_custom = [f'{ltr} - {tp}' for tp, ltr in zip(tmp_labels_custom, sample_config.label_letters)]
    tmp_labels_custom = ''.join(tmp_labels_custom)
    custom_sections[0] = tmp_labels_custom

    closed_questions = ['' + q + '\n\n' + scale_instr + "\n" + custom_sections[0] + '\n\nAnswer: ' for q in
                        closed_questions]
    closed_questions_dict = {q.split('.')[0]: 'Statement: \n' + q.split('. ')[1] for q in closed_questions}
    closed_questions_dict['rep_lvl2_q1'] = closed_questions_dict['lvl2_q1']

    oq_instr = instr_dict['openq_instr'] + '\n'
    return intro_prompt, oq_instr, open_qs_dict, closed_questions_dict, cq_preamble, qsn_questions_dict, cq_instr, qsn_preamble


# creates all pairs of questions for all subjects
def get_all_question_pairs(openq_data_long, sample_config, toker):
    """
    Retrieves all question pairs along with their structured formats based on the provided subject data and configuration.

    This function processes the given `openq_data_long` dataset to generate question-response pairs for each subject.
    It processes both open-ended and closed-ended questions, and optionally formats the responses in specified formats
    using a tokenizer.

    :param openq_data_long: Pandas DataFrame containing question and response data categorized by subjects. Each row
        represents a question and its associated response for a specific subject.
    :param sample_config: Configuration object containing question mapping details, instructional text, and other related
        parameters for question-response generation.
    :param toker: Tokenizer object used to format the question-response content into structured formats.
    :return: A tuple containing the following four elements:
        1. question_pairs (dict): Dictionary where keys are subject identifiers and values are dictionaries representing
           question-response pairs.
        2. question_pairs_formatted (dict): Dictionary where keys are subject identifiers and values are formatted
           question-response pairs as per specifications.
        3. question_pairs_short (dict): Placeholder dictionary for short-format question-response pairs, currently empty.
        4. question_pairs_short_formatted (dict): Placeholder dictionary for formatted short question-response pairs,
           currently empty.
    """
    # subject data
    question_pairs = {}
    question_pairs_formatted = {}
    question_pairs_short = {}
    question_pairs_short_formatted = {}
    intro_prompt, oq_instr, open_qs_dict, closed_questions_dict, cq_preamble, qsn_questions_dict, cq_instr, qsn_preamble = create_question_pairs_instr(
        sample_config)
    for sub in openq_data_long['sub'].unique():
        openq_data_sub = openq_data_long[openq_data_long['sub'] == sub].reset_index(drop=True)

        sub_responses = {}
        sub_responses_formatted = {}
        for r, row in openq_data_sub.iterrows():
            q_name = row['q_name']
            q_name_rel = qs_maps[sample_config.qs_name][q_name]
            if not ('lvl' in q_name_rel and 'v1' in sub):
                sub_responses[q_name] = []
                sub_responses_formatted[q_name] = []
                openq_text = 'Question:\n' + open_qs_dict[q_name] + '\n\nAnswer:'
                # if openq_data_sub['spec_level'][0] == 'gen':
                #     openq_text = 'Question:\n' + open_qs_dict[q_name] + '\n\nAnswer:'
                # else:
                #     openq_text = 'Question:\n' + open_spec_qs_dict[q_name] + '\n\nAnswer:'
                openq_ans = '\n' + row['value'] + '\n\n'

                if intro_prompt != '':
                    sub_responses[q_name].append({'role': 'system', 'content': intro_prompt})

                sub_responses[q_name].append({'role': 'user', 'content': oq_instr + openq_text})
                sub_responses[q_name].append({'role': 'assistant', 'content': openq_ans})
                if 'lvl' in q_name_rel:
                    closedq_text = closed_questions_dict[
                        q_name]  # if openq_data_sub['spec_level'][0] == 'gen':  #     closedq_text = closed_questions_dict[q_name]  # else:  #     closedq_text = closed_spec_questions_dict[q_name]
                else:
                    closedq_text = qsn_questions_dict[q_name_rel]

                if 'lvl' in q_name_rel:
                    sub_responses[q_name].append({'role': 'user', 'content': cq_preamble + closedq_text})
                else:
                    sub_responses[q_name].append({'role': 'user', 'content': cq_instr + qsn_preamble + closedq_text})

                sub_responses_formatted[q_name] = format_messages(sub_responses[q_name], toker, sample_config)

        question_pairs[sub] = sub_responses
        question_pairs_formatted[sub] = sub_responses_formatted

    return question_pairs, question_pairs_formatted, question_pairs_short, question_pairs_short_formatted


# find locations for all subjects
def get_sub_locs(openq_data_long, question_pairs_formatted, tokenizer, sample_config):
    """
    Processes question-answer pairs and identifies text locations based on given configurations.

    This function utilizes the provided formatted question pairs, sample configurations, and tokenized
    information to extract specific text locations and their last token positions within the sub-question
    data and open-ended question data.

    :param openq_data_long: A DataFrame containing open-ended question data along with associated values.
    :param question_pairs_formatted: A dictionary of formatted question pairs categorized by subject.
    :param tokenizer: Tokenizer instance used for tokenizing and locating text within question content.
    :param sample_config: Object containing configuration that defines the processing parameters, including
                          the subject and other relevant settings.
    :return: A tuple containing:
        - texts_to_find: Nested dictionary mapping question names to their corresponding open/closed question
          text and answers.
        - last_token_locs: Dictionary mapping question names to the last token positions for their open/closed
          questions and associated answers.
    """
    instr_dict, open_qs_dict, closed_qs_dict = load_task_content(sample_config)
    texts_to_find = {}
    last_token_locs = {}
    sub_question_data = question_pairs_formatted[sample_config.subj]
    for q_name, pair in sub_question_data.items():
        # print(f"{"----" * 10}{q_name}{"----" * 10}")
        texts_to_find[q_name] = {}
        last_token_locs[q_name] = {}

        sub_text = sub_question_data[q_name]
        oq_qs = re.sub('[^a-zA-Z0-9]+$', '', open_qs_dict[q_name])
        cq_qs = re.sub('[^a-zA-Z0-9]+$', '', closed_qs_dict[q_name])
        oq_ans = re.sub('[^a-zA-Z0-9]+$', '', openq_data_long[
            (openq_data_long['sub'] == sample_config.subj) & (openq_data_long['q_name'] == q_name)]['value'].values[0])

        # texts_to_find[q_name][q_name + '_oq_qs'] = oq_qs
        texts_to_find[q_name]['oq_qs'] = oq_qs
        texts_to_find[q_name]['oq_Answer'] = 'Answer'
        texts_to_find[q_name]['oq_ans'] = oq_ans
        texts_to_find[q_name]['cq_qs'] = cq_qs
        texts_to_find[q_name]['cq_Answer'] = 'Answer'

        loc_oq_qs, loc_e_oq_qs, loc_t_oq_qs, l_t_oq_qs = find_loc(sub_text, oq_qs, tokenizer)
        if loc_t_oq_qs == -1:
            print(f"{sample_config.subj}, {q_name} loc_t_oq_qs not found")
        # print(f"{oq_qs}")
        # print(f"\t{loc_oq_qs, loc_e_oq_qs, loc_t_oq_qs, l_t_oq_qs}")

        loc_oq_Answer, loc_e_oq_Answer, loc_t_oq_Answer, l_t_oq_Answer = find_loc(sub_text, 'Answer', tokenizer, n=1)
        if loc_t_oq_Answer == -1:
            print(f"{sample_config.subj}, {q_name} loc_t_oq_Answer not found")
        # print(f"Answer")
        # print(f"\t{loc_oq_Answer, loc_e_oq_Answer, loc_t_oq_Answer, l_t_oq_Answer}")

        loc_oq_ans, loc_e_oq_ans, loc_t_oq_ans, l_t_oq_ans = find_loc(sub_text, oq_ans, tokenizer)
        if loc_t_oq_ans == -1:
            print(f"{sample_config.subj}, {q_name} loc_t_oq_ans not found")
        # print(f"{oq_ans}")
        # print(f"\t{loc_oq_ans, loc_e_oq_ans, loc_t_oq_ans, l_t_oq_ans}")

        loc_cq_qs, loc_e_cq_qs, loc_t_cq_qs, l_t_cq_qs = find_loc(sub_text, cq_qs, tokenizer)
        if loc_t_cq_qs == -1:
            print(f"{sample_config.subj}, {q_name} loc_t_cq_qs not found")
        # print(f"{cq_qs}")
        # print(f"\t{loc_cq_qs, loc_e_cq_qs, loc_t_cq_qs, l_t_cq_qs}")

        loc_cq_Answer, loc_e_cq_Answer, loc_t_cq_Answer, l_t_cq_Answer = find_loc(sub_text, 'Answer', tokenizer, n=2)
        if loc_t_cq_Answer == -1:
            print(f"{sample_config.subj}, {q_name} loc_t_cq_Answer not found")
        # print(f"Answer")
        # print(f"\t{loc_cq_Answer, loc_e_cq_Answer, loc_t_cq_Answer, l_t_cq_Answer}")

        last_token_locs[q_name]['oq_qs'] = loc_t_oq_qs
        last_token_locs[q_name]['oq_Answer'] = loc_t_oq_Answer
        last_token_locs[q_name]['oq_ans'] = loc_t_oq_ans
        last_token_locs[q_name]['cq_qs'] = loc_t_cq_qs
        last_token_locs[q_name]['cq_Answer'] = loc_t_cq_Answer

    return texts_to_find, last_token_locs


# %% CROSS SAMPLING to other questionnaires - gen level
# load content of cross questionanires to setup prompts
def load_gen_qsn_content(sample_config):
    """
    Loads and processes questionnaire content from a predefined file, generating a dictionary of questions
    and instructional content, such as preamble and scale.

    :param sample_config: Configuration object that contains the necessary paths, names, and label letters
        for loading and processing the questionnaire.

    :return: A tuple consisting of:
        - A dictionary mapping each question identifier to its corresponding question text.
        - A dictionary containing the preamble and scale instructions for the questionnaire.
    """
    gen_qsn_qs_file = f"{sample_config.prompts_path}qs/{sample_config.gen_qs_name}/{sample_config.gen_qs_name}.txt"

    with open(gen_qsn_qs_file, encoding='utf-8') as f:
        gen_qsn_qs = f.read()
    prompt_sections = gen_qsn_qs.split('\n^^\n')
    gen_qsn_qs = prompt_sections[2].split('\n')

    # add letter labels to scale (Permute optionally)
    tmp_labels = prompt_sections[1].split('- ')
    tmp_labels = [l for l in tmp_labels if l != '']
    tmp_labels = [f'{ltr} - {tp}' for tp, ltr in zip(tmp_labels, sample_config.label_letters)]
    tmp_labels = ''.join(tmp_labels)
    prompt_sections[1] = tmp_labels

    # inv_map = qs_inv_maps[sample_config.gen_qs_name]
    if sample_config.gen_qs_name in ['sds']:
        gen_qsn_qs_dict = {sample_config.gen_qs_name + '_q' + q.split('.')[0]: 'Item: ' + q.split('. ')[1] for q in
                           gen_qsn_qs}
    if sample_config.gen_qs_name in ['phq9', 'gad7']:
        gen_qsn_qs_dict = {sample_config.gen_qs_name + '_q' + q.split('.')[0]: 'Problem: ' + q.split('. ')[1] for q in
                           gen_qsn_qs}

    gen_qsn_preamble = prompt_sections[0]
    gen_qsn_scale = prompt_sections[1]
    gen_qsn_instr_dict = {'preamble': gen_qsn_preamble, 'scale': gen_qsn_scale}

    return gen_qsn_qs_dict, gen_qsn_instr_dict


# Create creates prompt with questions and labels
def create_question_pairs_instr_gen(sample_config):
    """
    Generates question pairs and instructional prompts based on the provided configuration.

    This function processes the sample configuration to load instructions, prompts, and question
    content. It organizes and formats this content into specific structures used for generating
    questions and responses.

    :param sample_config: Configuration data used to load task content and question content.
                          The configuration determines the structure and content of instructions
                          and questions.
                          Expected to follow a specific format required by `load_task_content`
                          and `load_gen_qsn_content` functions.
    :return: A tuple containing:
        - intro_prompt (str): Introduction prompt string loaded from instruction content.
        - oq_instr (str): Instruction string for open-ended questions.
        - open_qs_dict (dict): Dictionary of open-ended questions loaded from the task content.
        - qsn_questions_dict (dict): Formatted dictionary of questions for generation with their
          associated scales and instructions.
        - qsn_preamble (str): Preamble string for question generation.
    :rtype: tuple
    """
    # load instructions and intro
    instr_dict, open_qs_dict, closed_qs_dict = load_task_content(sample_config)
    intro_prompt = instr_dict['intro']
    scale_instr = instr_dict['scale_instr_logit']

    qsn_questions, gen_instr_dict = load_gen_qsn_content(sample_config)

    qsn_preamble = '\n' + gen_instr_dict['preamble'] + '\n'
    qsn_questions_dict = {k: '' + '\n' + v + '\n\n' + scale_instr + "\n" + gen_instr_dict['scale'] + '\n\nAnswer:' for
                          k, v in qsn_questions.items()}

    oq_instr = instr_dict['openq_instr'] + '\n'
    return intro_prompt, oq_instr, open_qs_dict, qsn_questions_dict, qsn_preamble


# creates all pairs of questions for all subjects
def get_all_question_pairs_gen(openq_data_long, sample_config, toker):
    """
    Generates paired question data in different formats for analysis and processing. The function
    utilizes input data, configurations, and tokenization to construct detailed question-response
    structures per subject.

    :param openq_data_long: A pandas DataFrame containing long-format open-ended question
        data with subject identifiers and their responses.

    :param sample_config: A dictionary containing configuration parameters such as
        instructions or other prompt-related configurations for generating responses.

    :param toker: A tokenizer object used for formatting the generated messages and
        ensuring compatibility with designated models

    :return: A tuple containing three components:
        - question_pairs: A dictionary mapping each subject to their generated question
          and response data in structured form.
        - question_pairs_formatted: A dictionary with tokenized and formatted question-response
          data per subject, based on the tokenizer and configurations provided.
        - questions_df: A pandas DataFrame summarizing the generated question-response pairs,
          with fields like subject, context question, generated question, and their respective
          answers.
    """

    intro_prompt, oq_instr, open_qs_dict, qsn_gen_questions_dict, qsn_preamble = create_question_pairs_instr_gen(
        sample_config)

    # subject data
    questions_df = []
    question_pairs = {}
    question_pairs_formatted = {}
    for sub in openq_data_long['sub'].unique():
        openq_data_sub = openq_data_long[openq_data_long['sub'] == sub].reset_index(drop=True)
        sub_responses = {}
        sub_responses_formatted = {}
        for r, row in openq_data_sub.iterrows():
            q_name = row['q_name']
            sub_responses[q_name] = {}
            sub_responses_formatted[q_name] = {}

            openq_text_mid = open_qs_dict[q_name]
            openq_text = 'Question:\n' + openq_text_mid + '\n\nAnswer:'
            openq_ans = '\n' + row['value'] + '\n\n'

            for gen_q_key, gen_q in qsn_gen_questions_dict.items():
                sub_responses[q_name][gen_q_key] = []
                sub_responses_formatted[q_name][gen_q_key] = []

                if intro_prompt != '':
                    sub_responses[q_name][gen_q_key].append({'role': 'system', 'content': intro_prompt})

                sub_responses[q_name][gen_q_key].append({'role': 'user', 'content': oq_instr + openq_text})
                sub_responses[q_name][gen_q_key].append({'role': 'assistant', 'content': openq_ans})
                closedq_text = qsn_gen_questions_dict[gen_q_key]

                sub_responses[q_name][gen_q_key].append({'role': 'user', 'content': '\n' + qsn_preamble + closedq_text})

                sub_responses_formatted[q_name][gen_q_key] = format_messages(sub_responses[q_name][gen_q_key], toker,
                                                                             sample_config)

                tmp_dict = {'sub': sub, 'context_qs': q_name, 'gen_qs': gen_q_key,
                            'context_qs_q': openq_text_mid.replace('\n', ''),
                            'context_qs_ans': openq_ans.replace('\n', ''), 'gen_qs_q': closedq_text.replace('\n', '')}
                questions_df.append(tmp_dict)

        question_pairs[sub] = sub_responses
        question_pairs_formatted[sub] = sub_responses_formatted

    questions_df = pd.DataFrame(questions_df)
    return question_pairs, question_pairs_formatted, questions_df  # , question_pairs_short, question_pairs_short_formatted


# find locations for all subjects
def get_sub_locs_gen(openq_data_long, question_pairs_formatted, tokenizer, sample_config):
    """
    This function processes and retrieves specific text locations and corresponding token information
    for a given set of question pairs and textual data. The function utilizes predefined configuration
    and tokenizer to precisely locate contents in the provided data. During this process, it identifies
    locations of specific question types, answers, and related entities, and organizes them in a structured format.

    :param openq_data_long: A DataFrame containing open-ended question data with associated attributes and values.
    :param question_pairs_formatted: A dictionary holding formatted sub-question data categorized by subject.
    :param tokenizer: Tokenizer object used to process and tokenize the input texts for locating specific substrings.
    :param sample_config: A configuration object with attributes controlling the behavior of the function and specifying the subject/category.

    :return: A tuple containing:
             - A dictionary (`texts_to_find`) that maps question names and sub-question keys to their processed textual matches.
             - A dictionary (`last_token_locs`) that holds the locations of the last tokens for each corresponding question and sub-question pair.
    """
    instr_dict, open_qs_dict, closed_qs_dict = load_task_content(sample_config)
    gen_qsn_dict, gen_instr_dict = load_gen_qsn_content(sample_config)

    texts_to_find = {}
    last_token_locs = {}
    sub_question_data = question_pairs_formatted[sample_config.subj]
    for q_name, gen_q_set in sub_question_data.items():
        texts_to_find[q_name] = {}
        last_token_locs[q_name] = {}
        for gen_q_key, sub_text in gen_q_set.items():
            # print(f"{"----" * 10}{q_name}{"----" * 10}")
            texts_to_find[q_name][gen_q_key] = {}
            last_token_locs[q_name][gen_q_key] = {}

            oq_qs = re.sub('[^a-zA-Z0-9]+$', '', open_qs_dict[q_name])
            oq_ans = re.sub('[^a-zA-Z0-9]+$', '', openq_data_long[
                (openq_data_long['sub'] == sample_config.subj) & (openq_data_long['q_name'] == q_name)]['value'].values[
                0])
            cq_qs = re.sub('[^a-zA-Z0-9]+$', '', gen_qsn_dict[gen_q_key])

            texts_to_find[q_name][gen_q_key]['cq_qs'] = cq_qs
            texts_to_find[q_name][gen_q_key]['cq_Answer'] = 'Answer'

            loc_oq_qs, loc_e_oq_qs, loc_t_oq_qs, l_t_oq_qs = find_loc(sub_text, oq_qs, tokenizer)
            if loc_t_oq_qs == -1:
                print(f"{sample_config.subj}, {q_name} loc_t_oq_qs not found")
            # print(f"{oq_qs}")
            # print(f"\t{loc_oq_qs, loc_e_oq_qs, loc_t_oq_qs, l_t_oq_qs}")

            loc_oq_Answer, loc_e_oq_Answer, loc_t_oq_Answer, l_t_oq_Answer = find_loc(sub_text, 'Answer', tokenizer,
                                                                                      n=1)
            if loc_t_oq_Answer == -1:
                print(f"{sample_config.subj}, {q_name} loc_t_oq_Answer not found")
            # print(f"Answer")
            # print(f"\t{loc_oq_Answer, loc_e_oq_Answer, loc_t_oq_Answer, l_t_oq_Answer}")

            loc_oq_ans, loc_e_oq_ans, loc_t_oq_ans, l_t_oq_ans = find_loc(sub_text, oq_ans, tokenizer)
            if loc_t_oq_ans == -1:
                print(f"{sample_config.subj}, {q_name} loc_t_oq_ans not found")
            # print(f"{oq_ans}")
            # print(f"\t{loc_oq_ans, loc_e_oq_ans, loc_t_oq_ans, l_t_oq_ans}")

            loc_cq_qs, loc_e_cq_qs, loc_t_cq_qs, l_t_cq_qs = find_loc(sub_text, cq_qs, tokenizer)
            if loc_t_cq_qs == -1:
                print(f"{sample_config.subj}, {q_name} loc_t_cq_qs not found")
            # print(f"{cq_qs}")
            # print(f"\t{loc_cq_qs, loc_e_cq_qs, loc_t_cq_qs, l_t_cq_qs}")

            loc_cq_Answer, loc_e_cq_Answer, loc_t_cq_Answer, l_t_cq_Answer = find_loc(sub_text, 'Answer', tokenizer,
                                                                                      n=2)
            if loc_t_cq_Answer == -1:
                print(f"{sample_config.subj}, {q_name} loc_t_cq_Answer not found")
            # print(f"Answer")
            # print(f"\t{loc_cq_Answer, loc_e_cq_Answer, loc_t_cq_Answer, l_t_cq_Answer}")

            last_token_locs[q_name][gen_q_key]['cq_qs'] = loc_t_cq_qs
            last_token_locs[q_name][gen_q_key]['cq_Answer'] = loc_t_cq_Answer

    return texts_to_find, last_token_locs
