import gc
import random
import re
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import psutil
import torch as t
from google.cloud import storage
from scipy import stats
from sklearn.metrics.pairwise import cosine_similarity as cossim
from statsmodels.stats.multitest import multipletests

from scipy.stats import spearmanr, pearsonr


def write_to_tex(var_object, overwrite=False, tex_file=f'outputs/vars/paper_stats.tex'):
    """
    Writes variable data to a LaTeX-compatible `.tex` file by generating LaTeX commands for each
    provided variable. Existing commands in the file are preserved unless explicitly
    overwritten.

    :param var_object: Object containing attributes to be written to the `.tex` file. The
        attributes of this object must be accessible via the built-in `vars()` function.
    :param overwrite: Flag indicating whether to overwrite existing commands in the file if
        their keys match. If set to `True`, matching keys will have their values replaced
        with the new ones. Defaults to `False`.
    :param tex_file: The output `.tex` file to which the variables will be written. If the file
        does not exist, it will be created. Defaults to `'outputs/vars/paper_stats.tex'`.
    :returns: None
    """
    # write results to tex variables
    report_vars_dict = vars(var_object)

    existing_vars = {}
    Path(tex_file).parent.mkdir(parents=True, exist_ok=True)

    # 2. Load State (if file exists)
    if Path(tex_file).exists():
        with open(tex_file, 'r') as f:
            content = f.read()
            # Regex to find existing commands: \newcommand{\Key}{Value}
            # We use distinct capture groups for Key and Value
            matches = re.findall(r'\\newcommand\{\\(\w+)\}\{(.*)\}', content)
            existing_vars = {k: v for k, v in matches}
    # print(existing_vars)

    for k, v in report_vars_dict.items():
        k = ''.join(word.title() for word in k.split('_'))  # Latex friendly
        if k in existing_vars.keys() and overwrite:
            existing_vars[k] = str(v)
        if k not in existing_vars.keys():
            existing_vars[k] = str(v)

    with open(tex_file, 'w') as f:
        f.write("% Auto-generated stats file. Do not edit manually.\n")
        # Sort keys for deterministic output (version control friendly)
        for k in sorted(existing_vars.keys()):
            f.write(f"\\newcommand{{\\{k}}}{{{existing_vars[k]}}}\n")


def flush_sae(model, optimizer, early_stopper, device):
    del model, optimizer, early_stopper
    # Clear GPU cache
    if device == 'cuda':
        t.cuda.empty_cache()
        t.cuda.reset_peak_memory_stats()
    if device == 'mps':
        t.mps.empty_cache()
    gc.collect()


def get_ram():
    mem = psutil.virtual_memory()
    free = mem.available / 1024 ** 3
    total = mem.total / 1024 ** 3
    total_cubes = 24
    free_cubes = int(total_cubes * free / total)
    return f'RAM: {total - free:.2f}/{total:.2f}GB\t RAM:[' + (total_cubes - free_cubes) * '▮' + free_cubes * '▯' + ']'


def get_vram():
    free = t.cuda.mem_get_info()[0] / 1024 ** 3
    total = t.cuda.mem_get_info()[1] / 1024 ** 3
    total_cubes = 24
    free_cubes = int(total_cubes * free / total)
    return f'VRAM: {total - free:.2f}/{total:.2f}GB\t VRAM:[' + (
            total_cubes - free_cubes) * '▮' + free_cubes * '▯' + ']'


def set_seed(seed_value=42):
    """Set seed for reproducibility."""
    random.seed(seed_value)
    np.random.seed(seed_value)
    t.manual_seed(seed_value)
    if t.cuda.is_available():
        t.cuda.manual_seed_all(seed_value)
        # The following two lines are for full reproducibility with CUDA
        t.backends.cudnn.deterministic = True
        t.backends.cudnn.benchmark = False


####################
def my_iqr(x):
    res = x.quantile(0.75) - x.quantile(0.25)
    return res


def q1(x):
    res = x.quantile(0.25)
    return res


def q3(x):
    res = x.quantile(0.75)
    return res


def q2(x):
    res = x.quantile(0.5)
    return res


def spearmanr_pval(x, y):
    return spearmanr(x, y)[1]


def percentile(n):
    def percentile_(x):
        return x.quantile(n)

    percentile_.__name__ = 'q_{:02.0f}'.format(n * 100)
    return percentile_


def return_p_star(p):
    if p < 1e-4:
        return ' ****'
    elif p < 1e-3:
        return ' ***'
    elif p < 1e-2:
        return ' **'
    elif p < 5e-2:
        return ' *'
    else:
        return ' ns'


def return_p_star_wp(p):
    if p < 1e-4:
        return ' ****'
    elif p < 1e-3:
        return ' ***'
    elif p < 1e-2:
        return ' **'
    elif p < 5e-2:
        return ' *'
    else:
        return ' ns'
    return out_p

def prep_split_heatmap(matrix_A, matrix_B, cm1='Blues', cm2='Oranges'):
    norm_A = (matrix_A - matrix_A.min()) / (matrix_A.max() - matrix_A.min()) * 0.49
    norm_B = (matrix_B - matrix_B.min()) / (matrix_B.max() - matrix_B.min()) * 0.49 + 0.51
    N, M = matrix_A.shape
    x_coords = np.arange(N + 1)
    y_coords = np.arange(M + 1)
    x, y = np.meshgrid(x_coords, y_coords)
    x_flat = x.ravel()
    y_flat = y.ravel()
    triangles_list = []
    c_values = []
    for i in range(N):
        for j in range(M):
            # Find the 1D indices of the 4 vertices for the cell (i, j)
            # This is a standard 2D-to-1D index mapping
            v_bl = i * (M + 1) + j  # Bottom-left
            v_br = i * (M + 1) + (j + 1)  # Bottom-right
            v_tl = (i + 1) * (M + 1) + j  # Top-left
            v_tr = (i + 1) * (M + 1) + (j + 1)  # Top-right

            # --- This is the key part ---
            # Create the two triangles, split along the top-left to bottom-right diagonal

            # Triangle 1 (Bottom)
            triangles_list.append([v_bl, v_br, v_tl])
            c_values.append(norm_A[i, j])  # Assign value from matrix_A

            # Triangle 2 (Top)
            triangles_list.append([v_tl, v_br, v_tr])
            c_values.append(norm_B[i, j])  # Assign value from matrix_B

    # Convert lists to numpy arrays
    triangles_arr = np.array(triangles_list)
    c_arr = np.array(c_values)

    # Create the final Triangulation object
    triang = mtri.Triangulation(x_flat, y_flat, triangles=triangles_arr)

    # --- 4. Create Custom Segmented Colormap ---
    # Get two colormaps
    # cmap_A = matplotlib.colormaps[cm1]
    # cmap_B = matplotlib.colormaps[cm2]
    cmap_A = cm1
    cmap_B = cm2
    # matplotlib.colormaps['Blues']

    # Get 128 colors from each map
    colors_A = cmap_A(np.linspace(0, 1, 128))
    colors_B = cmap_B(np.linspace(0, 1, 128))

    # Stack them together
    all_colors = np.vstack((colors_A, colors_B))
    custom_cmap = mcolors.ListedColormap(all_colors)

    return triang, c_arr, custom_cmap, M, N



##############################
def disable_grad(model_object):
    """
    Disables the gradient computation for all parameters in the given model object.
    This function sets the model to evaluation mode and ensures all parameters
    have their `requires_grad` attribute set to False.

    :param model_object: A PyTorch model object whose gradients will be disabled.
    :type model_object: torch.nn.Module
    """
    model_object.eval()
    for p_name, param in model_object.named_parameters():
        param.requires_grad = False
        if param.requires_grad:
            print(p_name)


######################################

# Function to compute cosine similarity ignoring NaNs
def cossim_nan(matrix):
    """
    Compute cosine similarity matrix, handling NaN values.

    This function calculates the pairwise cosine similarity for a given matrix.
    If either of the vectors in a pair contains NaN values, the similarity for
    that pair is set to NaN. The resulting similarity matrix is symmetric,
    and each cell represents the cosine similarity between two rows of the
    input matrix.

    :param matrix: A 2D array-like object where each row represents a vector.
    :return: A symmetric 2D array where each element [i, j] corresponds to
        the cosine similarity between row `i` and row `j` of the input
        matrix. NaN values are propagated for pairs involving incomplete
        rows.
    :rtype: numpy.ndarray
    """
    n = matrix.shape[0]
    similarity_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            vec1 = matrix[i]
            vec2 = matrix[j]
            if not (any(np.isnan(vec1)) or any(np.isnan(vec2))):
                similarity_matrix[i, j] = cossim([vec1, vec2])[0, 1]
            else:
                similarity_matrix[i, j] = np.nan
    return similarity_matrix


########################################
def annotate_correlations(x, y, corr_mat, p_vals_mat):
    """
    Annotates a plot with the correlation coefficient and the corrected p-value
    associated with two variables. The annotation is added to the top-left corner
    of the current plot axes.

    :param x: The first variable for which the correlation coefficient is retrieved.
        It is expected to have a name attribute indicating its corresponding column
        in the correlation matrix.
    :param y: The second variable for which the correlation coefficient is retrieved.
        Similar to `x`, it should have a name attribute corresponding to its column
        in the matrix.
    :param corr_mat: A DataFrame containing the correlation coefficients for the
        variables. The columns and rows should correspond to the name attributes
        of `x` and `y`.
    :param p_vals_mat: A 2D array-like object containing the corrected p-values
        corresponding to the correlations in `corr_mat`. It should be indexed in
        the same order as `corr_mat`.
    """
    idx1 = corr_mat.columns.get_loc(x.name)
    idx2 = corr_mat.columns.get_loc(y.name)
    r = corr_mat.iloc[idx1, idx2]  # Get correlation from the matrix
    p_val = p_vals_mat[idx1, idx2]  # Get corrected p-value
    ax = plt.gca()
    ax.annotate(f'r: {r:.2f}; p: {p_val:.2e}', xy=(0.1, 1.1), xycoords=ax.transAxes)


def get_p_corrected(corr_mat, df_tmp):
    """
    Compute corrected p-values for pairwise correlations in a correlation matrix.

    This function calculates the p-values for all unique pairwise correlations
    in the given correlation matrix using the input DataFrame. The p-values are
    then adjusted for multiple comparisons using the Bonferroni correction.

    :param corr_mat: Correlation matrix for the dataset as a NumPy array. It is
        expected to be a symmetric matrix, where each element corresponds to the
        correlation between two variables.
    :param df_tmp: DataFrame containing the dataset. Each column should correspond
        to a variable, and rows correspond to observations. Missing data should
        be represented as NaN.
    :return: A tuple containing:
        - p_vals_corrected_mat (numpy.ndarray): Matrix of corrected p-values
          where corrections have been applied to the upper triangular part of the
          matrix using the Bonferroni method, while ensuring symmetry.
        - p_values (numpy.ndarray): Matrix of uncorrected p-values for each pair
          of variables, with symmetry maintained as in the correlation matrix.
    :rtype: tuple[numpy.ndarray, numpy.ndarray]
    """
    # Compute the p-values for the correlations
    p_values = np.zeros(corr_mat.shape)
    for i in range(len(df_tmp.columns)):
        for j in range(i + 1, len(df_tmp.columns)):
            # print(i,j)
            valid_data = df_tmp[[df_tmp.columns[i], df_tmp.columns[j]]].dropna()
            valid_data = valid_data.apply(pd.to_numeric, errors='coerce').dropna()
            # _, p = stats.pearsonr(df_tmp.iloc[:, i], df_tmp.iloc[:, j])
            # If there are not enough valid data points, assign NaN to p-values
            if len(valid_data) > 1:  # Pearson requires at least 2 data points
                _, p = stats.pearsonr(valid_data.iloc[:, 0], valid_data.iloc[:, 1])
            else:
                p = np.nan
            p_values[i, j] = p
            p_values[j, i] = p  # Symmetric matrix

    # Flatten p-values and apply multiple comparison correction
    p_vals_flat = p_values[np.triu_indices_from(p_values, 1)]
    _, p_vals_corrected, _, _ = multipletests(p_vals_flat, method='bonferroni')

    # Reshape corrected p-values back into matrix form
    p_vals_corrected_mat = np.zeros_like(p_values)
    p_vals_corrected_mat[np.triu_indices_from(p_vals_corrected_mat, 1)] = p_vals_corrected
    p_vals_corrected_mat = p_vals_corrected_mat + p_vals_corrected_mat.T  # Symmetry

    return p_vals_corrected_mat, p_values


############################
def upload_blob_from_memory(bucket_name, contents, destination_blob_name):
    """Uploads a file to the bucket."""""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(contents)

    print(f"{destination_blob_name} with contents {contents} uploaded to {bucket_name}.")


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
