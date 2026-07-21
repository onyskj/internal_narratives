from baukit import Trace, TraceDict
import torch


class SteerConfig:
    def __init__(self, layer_ids, steering_vectors, device, n_tokens=5, multiplier=1.0, sample_text=False,
                 run_gen=False,
                 perturb_input_only=True):
        self.layer_ids = layer_ids
        self.steering_vectors = steering_vectors
        self.multiplier = multiplier
        self.device = device

        self.run_gen = run_gen  # whether to generate text
        self.n_tokens = n_tokens
        self.sample_text = sample_text
        self.perturb_input_only = perturb_input_only


class SteerHiddenState:
    def __init__(self, steer_config, model, tokenizer):
        # self.steering_vectors = {f'model.layers.{layer_id}': [] for layer_id in steer_config.layer_ids}
        self.steering_vectors = steer_config.steering_vectors
        self.modules_to_steer = {f'model.layers.{layer_id}': model.model.layers[layer_id] for layer_id in
                                 steer_config.layer_ids}
        self.steer_config = steer_config
        self.hooks_dict = None
        self.counter = 0
        self.tokenizer = tokenizer

        self.input_ids = None
        self.attention_mask = None
        self.logits = None
        self.logits_original = None
        self.hidden_states = None
        self.hidden_states_original = None
        self.output_ids = None
        self.output_text = None
        self.output_text_original = None

    def steering_hook_fn(self, steering_vector):
        def steering_hook(output):
            """
            This hook is applied to the output of a layer.
            It adds the steering vector to the last token's activation.

            Supports both layer output formats:
            1. Tensor: hidden_states
            2. Tuple/list: (hidden_states, ...)
            """

            output_is_tuple = isinstance(output, tuple)
            output_is_list = isinstance(output, list)

            if output_is_tuple or output_is_list:
                hidden_state = output[0]
            else:
                hidden_state = output

            hidden_state = hidden_state.clone()

            if self.counter < len(self.steering_vectors) or (not self.steer_config.perturb_input_only):
                self.counter += 1

                hidden_states_norm = hidden_state[:, -1, :].norm(dim=-1, keepdim=True)
                tmp_sign = torch.sign(steering_vector @ hidden_state[:, -1, :].T)
                tmp_proj = hidden_state[:, -1, :] * (steering_vector @ hidden_state[:, -1, :].T) / (
                            hidden_states_norm ** 2)
                perturbation_vector = steering_vector - tmp_proj

                if self.steer_config.multiplier != 0:
                    hidden_state[:, -1, :] = tmp_sign * hidden_state[
                        :, -1, :] + self.steer_config.multiplier * perturbation_vector
            if output_is_tuple:
                return (hidden_state,) + output[1:]

            if output_is_list:
                return [hidden_state] + output[1:]

        return steering_hook

    def create_hooks_dict(self):
        self.hooks_dict = {
            module_name: self.steering_hook_fn(self.steering_vectors[module_name])
            for module_name in self.modules_to_steer.keys()
        }

    def steer(self, model, input, device_name, return_org=False):
        """
        Steers the behavior of the given model by manipulating activation outputs during the forward
        pass, enabling control over network responses. This function supports optional
        generation of new tokens and offers the ability to return original, unmodified outputs.

        :param model: The neural network model to be steered.
        :param input: Input text to process and steer the model's activation outputs.
        :type input: str
        :param device_name: Name of the device where the model computation is performed, e.g., 'cpu' or 'cuda'.
        :type device_name: str
        :param return_org: Flag indicating whether to return unmodified model outputs alongside the steered ones.
        :type return_org: bool
        :return: None
        """
        self.create_hooks_dict()
        input_ids = self.tokenizer(input, return_tensors='pt', padding=True, return_attention_mask=True).to(device_name)
        self.attention_mask = input_ids.attention_mask
        self.input_ids = input_ids.input_ids

        # Forward pass with activation steering
        self.counter = 0
        with TraceDict(model, self.modules_to_steer, edit_output=self.hooks_dict):
            model_output = model(self.input_ids, output_hidden_states=True, attention_mask=self.attention_mask)
            self.logits = model_output.logits[:, -1, :]
            self.hidden_states = model_output.hidden_states

        # If to generate new tokens (activations for new tokens is not steered - just the last token in input)
        if self.steer_config.run_gen:
            self.counter = 0
            with TraceDict(model, self.modules_to_steer, edit_output=self.hooks_dict):
                model_output_gen = model.generate(self.input_ids, attention_mask=self.attention_mask,
                                                  max_new_tokens=self.steer_config.n_tokens,
                                                  do_sample=self.steer_config.sample_text)
                self.output_text = self.tokenizer.batch_decode(model_output_gen, skip_special_tokens=True)

        # Forward pass (and optional geneation) without activation steering
        if return_org:
            model_output_original = model(self.input_ids, output_hidden_states=True, attention_mask=self.attention_mask)
            self.logits_original = model_output_original.logits[:, -1, :]
            self.hidden_states_original = model_output_original.hidden_states

            # Generate new tokens original
            if self.steer_config.run_gen:
                model_output_gen_original = model.generate(self.input_ids, attention_mask=self.attention_mask,
                                                           max_new_tokens=self.steer_config.n_tokens,
                                                           do_sample=self.steer_config.sample_text)
                self.output_text_original = self.tokenizer.batch_decode(model_output_gen_original,
                                                                        skip_special_tokens=True)
