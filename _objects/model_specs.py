# model specs
model_specs = {
    'MistralOo': {
        'hf_host': 'Open-Orca',
        'model_name': 'Mistral-7B-OpenOrca',
        'revision': 'main',
        'model_name_short': 'Mistral-OpenOrca',
        'L': 32,
        'model_name_plot': 'MistralOO_7B',
        'd_h': 4096
    },
    'GPT2': {
        'hf_host': 'openai-community',
        'model_name': 'gpt2',
        'revision': 'main',
        'model_name_short': 'GPT2',
        'L': 12
    },
    'gemma2-2b-it': {
        'hf_host': 'google',
        'model_name': 'gemma-2-2b-it',
        'revision': 'main',
        'model_name_short': 'gemma-2-2b-it',
        'L': 26,
        'model_name_plot': 'Gemma2_2B',
        'd_h': 2304,
    },
    'gemma2-9b-it': {
        'hf_host': 'google',
        'model_name': 'gemma-2-9b-it',
        'revision': 'main',
        'model_name_short': 'gemma-2-9b-it',
        'L': 42,
        'model_name_plot': 'Gemma2_9B',
        'd_h': 3584
    },
    'llama31-8b-it': {
        'hf_host': 'meta-llama',
        'model_name': 'Llama-3.1-8B-Instruct',
        'revision': 'main',
        'model_name_short': 'llama31-8b-it',
        'L': 32,
        'model_name_plot': 'LLama3_8B'
    },
    'llama32-3b-it': {
        'hf_host': 'meta-llama',
        'model_name': 'Llama-3.2-3B-Instruct',
        'revision': 'main',
        'model_name_short': 'llama32-3b-it',
        'L': 28,
        'model_name_plot': 'LLama3_3B'
    },

}
