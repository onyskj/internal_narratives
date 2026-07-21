import torch as t
import torch.nn.functional as F
from torch import nn
import einops


class SAE4(nn.Module):
    """
    Defines the Supervised Sparse Autoencoder neural network module.

    Attributes:
        cfg: Configuration object containing hyperparameters and settings.
        W_enc: Encoding weight matrix used to project inputs into latent space.
        W_proj: Projection weight matrix used to map latent space into the
            question-score space.
        b_enc: Bias applied during encoding.
        b_dec: Bias applied during decoding.
        b_proj: Bias applied to the question-score projections.
        meta_config: Stores additional metadata configuration for the module.

        :ivar cfg: Configuration object for hyperparameters and settings.
        :ivar W_enc: Weight matrix for the encoder.
        :ivar b_enc: Bias vector for the encoder.
        :ivar b_dec: Bias vector for the decoder.
        :ivar W_proj: Weight matrix for projecting into the question-score space.
        :ivar b_proj: Bias vector for the question-score projections.
        :ivar meta_config: Metadata configuration for the SAE4 model.
    """
    def __init__(self, cfg):
        super().__init__()

        self.cfg = cfg

        self.W_enc = nn.Parameter(nn.init.kaiming_uniform_(t.empty(cfg.d_in, cfg.d_sae)))
        self._W_dec = (None
                       if self.cfg.tied_weights
                       else nn.Parameter(nn.init.kaiming_uniform_(t.empty(cfg.d_sae, cfg.d_in))))
        self.b_enc = nn.Parameter(t.zeros(cfg.d_sae))
        self.b_dec = nn.Parameter(t.zeros(cfg.d_in))

        self.W_proj = nn.Parameter(nn.init.kaiming_uniform_(t.empty(cfg.d_sae, cfg.d_qs)))
        self.b_proj = nn.Parameter(t.zeros(cfg.d_qs))

        self.meta_config = None

        self.to(cfg.device)

    @property
    def W_dec(self):
        if self.cfg.tied_weights:
            return self.W_enc.transpose(-1, -2)
        else:
            return self._W_dec

    @property
    def W_dec_normalised(self):
        return self.W_dec / (self.W_dec.norm(dim=-1, keepdim=True) + self.cfg.weight_normalize_eps)

    def forward(self, h, y):
        """
        Args:
            h: true hidden states
            y: true questionnaire scores
        """
        # Centre the activations
        h_cent = h - self.b_dec

        # Latent activations
        acts_pre = (
                einops.einsum(h_cent, self.W_enc, "batch d_in, d_in d_sae -> batch d_sae")  # (B,X) x (B,X,H) = (B,H)
                + self.b_enc
        )
        acts_post = F.relu(acts_pre)

        # Project pre_activation to Question-Score space
        latent_qs = (
                einops.einsum(acts_post, self.W_proj, "batch d_sae, d_sae d_qs -> batch d_qs")
                + self.b_proj
        )

        if not self.cfg.do_zscores:
            latent_qs = latent_qs.view(-1, self.cfg.d_q, self.cfg.d_s)

        # Compute reconstructed input
        h_rec = (
                einops.einsum(
                    acts_post, self.W_dec_normalised, "batch d_sae, d_sae d_in -> batch d_in")
                + self.b_dec
        )

        # Calculate loss
        L_rec = (h_rec - h).pow(2).mean(-1)
        L_sparse = acts_post.abs().sum(-1)

        if not self.cfg.do_zscores:
            L_qs = F.cross_entropy(latent_qs.view(-1, self.cfg.d_s), y.view(-1))

            L_sev = 0
        else:
            L_qs = (latent_qs - y).pow(2).mean(-1)
            L_sev = (latent_qs.sum(-1) - y.sum(-1)).pow(2)

        loss_dict = {'L_rec': L_rec.mean(), 'L_sparse': self.cfg.sparsity_coeff * L_sparse.mean(),
                     'L_qs': L_qs.mean() * self.cfg.qs_coeff, 'L_sev': L_sev.mean() * (1 / self.cfg.d_q)}
        loss = L_rec + self.cfg.sparsity_coeff * L_sparse + L_qs * self.cfg.qs_coeff + L_sev * (1 / self.cfg.d_q)
        loss = loss.mean()

        return loss, loss_dict, latent_qs, h_rec

    def infer(self, h, delta_s=None, p_force=1):
        """
        Args:
            h: true hidden states
            y: true questionnaire scores
        """
        # Centre the activations
        h_cent = h - self.b_dec

        # Latent activations
        acts_pre = (
                einops.einsum(h_cent, self.W_enc, "batch d_in, d_in d_sae -> batch d_sae")  # (B,X) x (B,X,H) = (B,H)
                + self.b_enc
        )
        acts_post = F.relu(acts_pre)
        if delta_s is not None:
            acts_post += delta_s * p_force

        # Project pre_activation to Question-Score space
        latent_qs = (
                einops.einsum(acts_post, self.W_proj, "batch d_sae, d_sae d_qs -> batch d_qs")
                + self.b_proj
        )

        if not self.cfg.do_zscores:
            latent_qs = latent_qs.view(-1, self.cfg.d_q, self.cfg.d_s)

        # Compute reconstructed input
        h_rec = (
                einops.einsum(
                    acts_post, self.W_dec_normalised, "batch d_sae, d_sae d_in -> batch d_in")
                + self.b_dec
        )

        return latent_qs, acts_post, h_rec


class SAE_Config:
    def __init__(self, exp_config, device, x_m=4, s_dim=4, sparse_coeff=0.2, tied_weights=True, qs_coeff=1):
        self.d_in = exp_config.d_h
        self.d_sae = self.d_in * x_m
        self.device = device
        self.weight_normalize_eps = 1e-8
        self.sparsity_coeff = sparse_coeff
        self.tied_weights = tied_weights
        self.qs_coeff = qs_coeff

        # whether 9 or 2 questions
        if exp_config.q_case == '9q':
            self.d_q = 9
        if exp_config.q_case == '2q':
            self.d_q = 2
        if exp_config.q_case == 'q2Only':
            self.d_q = 1

        # whether logits or z-scores
        self.do_zscores = exp_config.do_zscores
        if self.do_zscores:
            self.d_qs = self.d_q
        else:
            self.d_s = s_dim
            self.d_qs = self.d_q * self.d_s


class ExpConfig:
    def __init__(self, sample_config, q_case='q2Only', do_zscores=True, max_epochs=1000):
        self.q_case = q_case
        self.do_zscores = do_zscores
        self.model_name = sample_config.model_name_sshort
        self.d_h = None
        self.max_epochs = max_epochs
        dataset_fname = None

        if self.q_case == '9q':
            dataset_fname = '9q'
        if self.q_case == '2q':
            dataset_fname = '2q'
        if self.q_case == 'q2Only':
            dataset_fname = 'q2Only'

        if do_zscores:
            dataset_fname += '_zs'

        self.dataset_fname = dataset_fname + f'_{self.model_name}'


class EarlyStopper:
    def __init__(self, patience=1, min_delta=0):
        """
        Monitors validation loss improvement and triggers early stopping if the monitored metric does not improve for a
        defined number of consecutive checks. Helps prevent overfitting by stopping training when further progress
        stalls. Tracks the best loss achieved and optionally stores the model state at that point.

        :param patience: Number of iterations to wait for validation loss improvement before stopping.
        :param min_delta: Minimum change in validation loss to signify an improvement.
        """

        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = t.inf
        self.early_stop = False
        self.best_model_state = None

    def __call__(self, val_loss, model, epoch):
        """
        Monitors validation loss and determines if training should stop.
        Saves the best model state.
        """
        if self.best_loss - val_loss > self.min_delta:
            # We have a new best loss
            self.best_loss = val_loss
            self.best_epoch = epoch
            self.counter = 0
            # Save the best model
            self.best_model_state = model.state_dict()
        else:
            # No improvement
            self.counter += 1
            print(f"Early stopping counter: {self.counter} out of {self.patience}")
            if self.counter >= self.patience:
                self.early_stop = True
