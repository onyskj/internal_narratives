import re
import numpy as np
import torch

from scripts.a_open_qs.llm_sampling.logit_utils import format_messages


def texts_to_msg(text_data, sample_config, toker, rem_tag=False):
    """
    Converts a given set of text data into formatted messages based on the provided
    tokenizer and configuration, removing certain tags if specified.

    :param text_data: A DataFrame containing text data. The column 'sub' is expected
                      to contain identifiers, and the column 'text' should have the corresponding
                      textual content for each identifier.
    :param sample_config: Configuration object containing model-specific settings.
                          It is expected to have an attribute 'model_name_sshort' that
                          determines the formatting behavior.

    :param toker: The tokenizer used to process and format messages.

    :param rem_tag: A boolean flag indicating whether to remove specific tags
                    from the formatted messages. Defaults to False.

    :return: A dictionary mapping 'sub' identifiers to their respective formatted messages.
    """
    store_text = {}
    for sub in text_data['sub'].unique():
        sub_text = text_data['text'][text_data['sub'] == sub].values[0]
        sub_message = [{'role': 'user', 'content': sub_text}]
        sub_formatted_message = format_messages(sub_message, toker, sample_config)
        if rem_tag:
            if sample_config.model_name_sshort == 'MistralOo':
                sub_formatted_message = re.sub(r"<\|im_end\|>\n<\|im_start\|>assistant\n", '', sub_formatted_message)
            if 'gemma2' in sample_config.model_name_sshort:
                sub_formatted_message = re.sub(r"<end_of_turn>\n<start_of_turn>model\n", '', sub_formatted_message)

        store_text[sub] = sub_formatted_message

    return store_text


def forward_pass_whs(inputs, model, tokenizer, sample_config, device_name):
    """
    This function performs a forward pass through a given model and extracts hidden states from specific
    layers of the model's architecture. It tokenizes the input, computes the token indices of interest,
    performs the forward pass, and selects the hidden states based on a configuration provided.

    :param inputs: Input text or list of texts to be processed.
    :param model: The neural network model used for inference.
    :param tokenizer: The tokenizer instance used to compute token IDs and attention masks.
    :param sample_config: Configuration object containing parameters such as `hsT` (number of
        hidden state tokens to sample) and `L` (the number of layers in the model to consider).
    :return: A tensor containing selected hidden states from specified layers of the model.
    """
    # get token ids
    inputs_ids = tokenizer(inputs, padding=True, return_tensors='pt', return_attention_mask=True).to(device_name)
    # get token locatioins
    loc_idxs = [np.linspace(0, inputs_ids.attention_mask.sum(axis=1).detach().cpu().numpy()[ii] - 1, sample_config.hsT,
                            dtype=int)
                for ii
                in range(len(inputs_ids.input_ids.cpu().detach()))]
    # forward pass
    out_ids = model(inputs_ids.input_ids, attention_mask=inputs_ids.attention_mask, output_hidden_states=True)

    # get hidden states for specific layers
    layer_idxs = np.arange(sample_config.L // 2, sample_config.L)
    hs_ts = out_ids.hidden_states

    hs_ts_new = torch.stack([torch.stack(
        [hs_ts_l[ii, att_mask.detach().cpu() == 1, :][loc_idx, :].detach().cpu() for ii, (att_mask, loc_idx) in
         enumerate(zip(inputs_ids.attention_mask, loc_idxs))]) for hs_ts_l in hs_ts]).permute(1, 0, 2, 3)[:, 1:][
        :, layer_idxs]

    del hs_ts

    return hs_ts_new
