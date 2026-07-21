import torch
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib
from scipy import stats

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def train_epochs(model, train_dataloader, val_dataloader, train_config_dict, exp_config, early_stopper, fnames, bools):
    """
    Trains a model using given datasets and configurations for multiple epochs. Tracks and saves
    training/validation losses and implements early stopping to prevent overfitting. Optionally
    saves the best model based on validation loss.

    :param model: The model to be trained. It must implement a callable interface that returns
                  the training loss, loss components, latent representations, and reconstructions
                  when provided with input features and labels.
    :param train_dataloader: Dataloader for the training dataset. Provides training data in batches.
    :param val_dataloader: Dataloader for the validation dataset. Provides validation data in batches.
    :param train_config_dict: Dictionary containing configuration parameters for training,
                              such as learning rate (`optim_lr`) and other training-related settings.
    :param exp_config: Experiment configuration object. This object must have the attribute
                       `max_epochs` specifying the maximum number of epochs for training, and
                       `device` for determining the computation device (e.g., CPU or GPU).
    :param early_stopper: Instance of an early-stopping utility. Tracks validation loss over epochs
                          and determines when to stop training early. Optionally stores the best
                          model state and provides functionality to save it.
    :param fnames: Object containing file paths required for saving results and model state.
                   Attributes include `loss_fp` for loss CSV file path and `model_fp` for
                   best model checkpoint.
    :param bools: Object containing boolean flags for controlling training behavior. Must include
                  the attribute `save_best_model` to determine whether to save the best model to disk.
    :return: A tuple containing:
             - A pandas DataFrame storing epoch-wise training and validation losses, along with
               additional loss components and configurations.
             - The optimizer instance used during training.
    """
    gather_train_loss = []
    gather_val_loss = []
    gather_train_loss_dict = {'L_rec': [], 'L_sparse': [], 'L_qs': [], 'L_sev': []}
    gather_val_loss_dict = {'L_rec': [], 'L_sparse': [], 'L_qs': [], 'L_sev': []}
    optimizer = torch.optim.Adam(model.parameters(), lr=train_config_dict['optim_lr'])
    best_epoch_bool = []
    for epoch in tqdm(range(exp_config.max_epochs)):
        # Training
        model.train()
        train_total_loss = 0
        train_loss_dict_store = {'L_rec': 0, 'L_sparse': 0, 'L_qs': 0, 'L_sev': 0}
        # for each batch
        for (train_features, train_labels) in train_dataloader:
            # get features and labels to type and device
            train_features = train_features.type(torch.float32).to(exp_config.device)
            train_labels = train_labels.type(torch.float32).to(exp_config.device)

            # Reset gradients before each pass
            optimizer.zero_grad()

            # forward pass, get loss etc
            train_loss, train_loss_dict, latent_qs, h_rec = model(train_features, train_labels)

            # calculate gradients (backward pass)
            train_loss.backward()

            # optimize (move along the gradient)
            optimizer.step()

            # keep track of training loss (sum across batch)
            train_total_loss += train_loss.item()
            train_loss_dict_store = {k: v + train_loss_dict[k].item() for k, v in
                                     train_loss_dict_store.items()}

        # average across batch
        train_total_loss = train_total_loss / len(train_dataloader)

        # keep track of batch-average loss
        gather_train_loss.append(train_total_loss)
        train_loss_dict_store = {k: v / len(train_dataloader) for k, v in train_loss_dict_store.items()}
        gather_train_loss_dict = {k: v + [train_loss_dict_store[k]] for k, v in
                                  gather_train_loss_dict.items()}

        # Validation on validation dataset
        model.eval()
        val_total_loss = 0
        val_loss_dict_store = {'L_rec': 0, 'L_sparse': 0, 'L_qs': 0, 'L_sev': 0}
        # val_loss_dict_store = {'L_rec': 0, 'L_sparse': 0, 'L_qs': 0}
        with torch.no_grad():
            for (val_features, val_labels) in val_dataloader:
                val_features = val_features.type(torch.float32).to(exp_config.device)
                val_labels = val_labels.type(torch.float32).to(exp_config.device)

                val_loss, val_loss_dict, latent_qs, h_rec = model(val_features, val_labels)
                val_total_loss += val_loss.item()

                val_loss_dict_store = {k: v + val_loss_dict[k].item() for k, v in
                                       val_loss_dict_store.items()}

        val_total_loss = val_total_loss / len(val_dataloader)
        gather_val_loss.append(val_total_loss)

        val_loss_dict_store = {k: v / len(val_dataloader) for k, v in val_loss_dict_store.items()}
        gather_val_loss_dict = {k: v + [val_loss_dict_store[k]] for k, v in gather_val_loss_dict.items()}

        # keep track of epochs and if early stopper should kick in
        print("epoch : {}/{}, train loss = {:.6f}".format(epoch + 1, exp_config.max_epochs, train_total_loss))
        print("\t\t\t\tval loss = {:.6f}".format(val_total_loss))
        best_epoch_bool.append(False)
        early_stopper(val_total_loss, model, epoch)

        if early_stopper.early_stop:
            # do early stopping and save metrics
            gather_train_loss_dict = {k + '_train': v for k, v in gather_train_loss_dict.items()}
            gather_val_loss_dict = {k + '_val': v for k, v in gather_val_loss_dict.items()}

            print("Early stopping triggered")
            best_epoch_bool[early_stopper.best_epoch] = True
            loss_dict = {'train_loss': gather_train_loss, 'val_loss': gather_val_loss,
                         'is_best': best_epoch_bool} | gather_train_loss_dict | gather_val_loss_dict | train_config_dict
            loss_df = pd.DataFrame(loss_dict).reset_index(names='epoch')
            loss_df.to_csv(fnames.loss_fp, index=False)

            break

    # get the model params when early stopping kicked in
    if early_stopper.best_model_state is not None:
        model.load_state_dict(early_stopper.best_model_state)
        if bools.save_best_model:
            print("Saving the best model from memory to disk.")
            torch.save(early_stopper.best_model_state, fnames.model_fp)
    del train_loss_dict, train_loss

    return loss_df, optimizer


def get_loss(loss_df, item_loss_names, early_stopper, pc, fnames, bools):
    """
    Summarizes the process of visualizing and analyzing the training and validation loss from
    a given dataset. This function generates loss plots for each specified loss type, overlays
    visual indicators for the best epoch identified by an early stopping mechanism, and configures
    plot aesthetics based on the provided plotting configuration object. The generated plot can
    be optionally saved based on user preference.

    :param loss_df: DataFrame containing training and validation loss values for various epochs.
    :param item_loss_names: List of different loss functions or metrics to be analyzed and visualized.
    :param early_stopper: Object or instance that holds the best epoch determined by early stopping.
    :param pc: Plotting configuration object that specifies layout, sizing, and aesthetic preferences.
    :param fnames: Object containing filepath strings where the plots can be saved.
    :param bools: Boolean flags object indicating whether plots should be saved.

    :return: None
    """
    loss_names_t = ['train_loss'] + [i + '_train' for i in item_loss_names]
    loss_names_v = ['val_loss'] + [i + '_val' for i in item_loss_names]
    item_loss_names = ['L_total'] + item_loss_names
    plt.close('all')
    pc.r, pc.c, pc.mlt = 1, len(item_loss_names), 2

    pc.figsize = ((pc.c + 4.15) * pc.mlt, (pc.r + 0.75) * pc.mlt)
    fig, axes = plt.subplots(pc.r, pc.c, figsize=pc.figsize, sharey=False)
    axes = np.array([axes])
    pc.axes = axes
    # pc.onerow = True
    pc.onerow = False
    pc.i = 0
    pc.j = 0
    pc.ax_ts(10, 1.1)
    pc.l_fs(8, 0.85)
    pc.xyt_ls(16, 16)
    pc.ax_ls(16)
    pc.kde_lw = 3
    pc.p_lab_spec[2] = 14
    pc.p_lab_spec[0] = -0.05
    pc.p_lab_spec[1] = 1.05
    pc.dpi_val = 300

    for pc.j, (t_lab, val_lab) in enumerate(zip(loss_names_t, loss_names_v)):
        t_loss_df = loss_df[t_lab]
        v_loss_df = loss_df[val_lab]
        pc.ax.plot(t_loss_df, label=t_lab)
        pc.ax.plot(v_loss_df, label=val_lab)
        losses = np.array([t_loss_df + v_loss_df])
        if pc.j == 0:
            pc.ax.vlines(x=early_stopper.best_epoch, ymin=0, ymax=losses.max() * 1.1, color='r',
                         linestyle='--',
                         label=f'Best epoch {early_stopper.best_epoch}')
        pc.ax.set_xlabel('epoch')
        pc.ax.set_ylabel('loss')
        pc.ax.set_title(item_loss_names[pc.j])
        pc.ax.legend()
    plt.tight_layout()
    if bools.savePlots:
        plt.savefig(fnames.loss_plot_fp, dpi=300)


def get_predictions(model, data_loader, exp_config, train_config_dict, fnames, bools):
    """
    Generates predictions using a model and evaluates its performance by calculating per-question
    correlations and associated p-values. The results, including true values, predictions, and
    statistical metrics, are saved in specified file paths.

    :param model: The trained model used for generating predictions.
    :param data_loader: DataLoader containing the dataset with features and labels.
    :param exp_config: Experiment configuration object, expected to have the following attributes:
        - phq9_q_names: List of question names used for labeling predictions and true values.
        - device: The computational device (e.g., 'cpu' or 'cuda') for processing data.
    :param train_config_dict: Dictionary containing configuration details related to training;
        merged with statistical results for output.
    :param fnames: A structure containing file paths for saving predictions and metric results.
        Expected to have the following attributes:
        - preds_fp: File path to save the predictions and true values as a CSV.
        - metric_fp: File path to save the statistical analysis results as a CSV.
    :param bools: A structure holding boolean flags for additional processing.
        Expected to have the following attributes:
        - do_zscores: Indicates whether to compute z-scores for normalization.
    :return: None

    """
    x = torch.stack(data_loader.dataset.features).to(exp_config.device)
    y = torch.stack(data_loader.dataset.labels).to(exp_config.device)
    ytrue = y.to('cpu').numpy()

    preds = model(x, y)[2].to(
        'cpu').detach().numpy()  # preds = rescale_np(ytrue, preds)  # preds = model(x, y)[2].to('cpu').detach()  # preds = (preds - preds.mean(axis=0)) / preds.std(axis=0)
    ytruedf = pd.DataFrame(ytrue, columns=exp_config.phq9_q_names).reset_index().rename(columns={'index': 'sub'})
    ytpreddf = pd.DataFrame(preds, columns=exp_config.phq9_q_names).reset_index().rename(columns={'index': 'sub'})
    ytruedf['source'] = 'ppt'
    ytpreddf['source'] = 'ae'
    ytpreddf_m = pd.melt(ytpreddf, id_vars=['sub', 'source'])
    ytruedf_m = pd.melt(ytruedf, id_vars=['sub', 'source'])
    y_all = pd.concat([ytpreddf_m, ytruedf_m], axis=0)
    if fnames is not None:
        y_all.to_csv(f'{fnames.preds_fp}', index=False)

    # get per question correlations and p-values
    pred_stats = []
    for q, (q_name) in enumerate(exp_config.phq9_q_names):
        ys = y_all[y_all['variable'] == q_name]
        ys = ys.pivot(index='sub', columns='source', values='value')
        if bools.do_zscores:
            r, p = stats.spearmanr(ys['ppt'], ys['ae'])
            p = min(p * len(exp_config.phq9_q_names), 1)
            stat_dict = {'q_name': q_name, 'r': r, 'p': p}

        pred_stats.append(stat_dict | train_config_dict)
    preds_stats_df = pd.DataFrame(pred_stats)
    if fnames is not None:
        preds_stats_df.to_csv(f'{fnames.metric_fp}', index=False)
    return y_all, preds_stats_df
