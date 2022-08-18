import numpy as np
import torch
from pyod.utils.data import evaluate_print as evaluate_print_np
from pyod.utils.data import generate_data as generate_data_pyod
from pyod.utils.utility import precision_n_scores
from sklearn.metrics import roc_auc_score
from sklearn.utils import check_consistent_length
from sklearn.utils import column_or_1d


def generate_data(n_train=1000, n_test=500, n_features=2, contamination=0.1,
                  train_only=False, offset=10,
                  random_state=None, n_nan=0, n_inf=0):
    """Utility function to generate synthesized data.
    Normal data is generated by a multivariate Gaussian distribution and
    outliers are generated by a uniform distribution.
    "X_train, X_test, y_train, y_test" are returned.

    Parameters
    ----------
    n_train : int, (default=1000)
        The number of training points to generate.

    n_test : int, (default=500)
        The number of test points to generate.

    n_features : int, optional (default=2)
        The number of features (dimensions).

    contamination : float in (0., 0.5), optional (default=0.1)
        The amount of contamination of the data set, i.e.
        the proportion of outliers in the data set. Used when fitting to
        define the threshold on the decision function.

    train_only : bool, optional (default=False)
        If true, generate train data only.

    offset : int, optional (default=10)
        Adjust the value range of Gaussian and Uniform.

    random_state : int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    n_nan : int
        The number of values that are missing (np.NaN). Defaults to zero.

    n_inf : int
        The number of values that are infinite. (np.infty). Defaults to zero.

    Returns
    -------
    X_train : numpy array of shape (n_train, n_features)
        Training data.

    X_test : numpy array of shape (n_test, n_features)
        Test data.

    y_train : numpy array of shape (n_train,)
        Training ground truth.

    y_test : numpy array of shape (n_test,)
        Test ground truth.

    """
    if train_only:
        X_train, y_train = generate_data_pyod(n_train, n_test, n_features,
                                              contamination,
                                              train_only, offset, 'new',
                                              random_state, n_nan, n_inf)
        return torch.from_numpy(X_train), torch.from_numpy(y_train)
    else:
        X_train, X_test, y_train, y_test = generate_data_pyod(n_train, n_test,
                                                              n_features,
                                                              contamination,
                                                              train_only,
                                                              offset, 'new',
                                                              random_state,
                                                              n_nan, n_inf)

        return torch.from_numpy(X_train), torch.from_numpy(
            y_train), torch.from_numpy(X_test), torch.from_numpy(y_test)


def evaluate_print(clf_name, y, y_pred):
    """Utility function for evaluating and printing the results for examples.
    Default metrics include ROC and Precision @ n

    Parameters
    ----------
    clf_name : str
        The name of the detector.

    y : list or numpy array of shape (n_samples,)
        The ground truth. Binary (0: inliers, 1: outliers).

    y_pred : list or numpy array of shape (n_samples,)
        The raw outlier scores as returned by a fitted model.

    """

    if torch.is_tensor(y):
        y = y.cpu().numpy()
        y_pred = y_pred.cpu().numpy()
    return evaluate_print_np(clf_name, y, y_pred)


def get_roc(y, y_pred):
    """Utility function for evaluating the results for examples.
        Default metrics include ROC

        Parameters
        ----------
        y : list or numpy array of shape (n_samples,)
            The ground truth. Binary (0: inliers, 1: outliers).

        y_pred : list or numpy array of shape (n_samples,)
            The raw outlier scores as returned by a fitted model.

        """
    y = column_or_1d(y)
    y_pred = column_or_1d(y_pred)
    check_consistent_length(y, y_pred)

    return np.round(roc_auc_score(y, y_pred), decimals=4)


def get_prn(y, y_pred):
    """Utility function for evaluating the results for examples.
        Default metrics include P@N

        Parameters
        ----------
        y : list or numpy array of shape (n_samples,)
            The ground truth. Binary (0: inliers, 1: outliers).

        y_pred : list or numpy array of shape (n_samples,)
            The raw outlier scores as returned by a fitted model.

        """
    y = column_or_1d(y)
    y_pred = column_or_1d(y_pred)
    check_consistent_length(y, y_pred)

    return np.round(precision_n_scores(y, y_pred), decimals=4)
