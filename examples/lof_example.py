# -*- coding: utf-8 -*-
"""Example of using LOF for outlier detection
"""
# Author: Yue Zhao <zhaoy@cmu.edu>
# License: BSD 2 clause

import os
import sys
import time

import torch
from pyod.models.lof import LOF as LOF_PyOD
from pyod.utils.data import evaluate_print
from pyod.utils.data import generate_data

# temporary solution for relative imports in case pyod is not installed
# if pyod is installed, no need to use the following line
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname("__file__"), '..')))

from pytod.models.lof import LOF
from pytod.utils.utility import validate_device

contamination = 0.1  # percentage of outliers
n_train = 30000  # number of training points
n_test = 5000  # number of testing points
n_features = 20
k = 10

# Generate sample data
X_train, X_test, y_train, y_test = \
    generate_data(n_train=n_train,
                  n_test=n_test,
                  n_features=n_features,
                  contamination=contamination,
                  random_state=42)

clf_name = 'LOF-PyOD'
clf = LOF_PyOD(n_neighbors=k)
start = time.time()
clf.fit(X_train)
end = time.time()
# get the prediction labels and outlier scores of the training data
y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
y_train_scores = clf.decision_scores_  # raw outlier scores

# evaluate and print the results
print("\nOn Training Data:")
evaluate_print(clf_name, y_train, y_train_scores)
pyod_time = end - start
print('PyOD execution time', pyod_time)

X_train, y_train, X_test, y_test = torch.from_numpy(X_train), \
                                   torch.from_numpy(y_train), \
                                   torch.from_numpy(X_test), \
                                   torch.from_numpy(y_test)

print()
print()
# try to access the GPU, fall back to cpu if no gpu is available
device = validate_device(0)
device = 'cpu'
clf_name = 'lof-PyTOD'
clf = LOF(n_neighbors=k, batch_size=10000, device=device)
# clf = LOF(n_neighbors=k, batch_size=None, device=device)
start = time.time()
clf.fit(X_train)
end = time.time()
# get the prediction labels and outlier scores of the training data
y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
y_train_scores = clf.decision_scores_  # raw outlier scores

# evaluate and print the results
print("\nOn Training Data:")
evaluate_print(clf_name, y_train, y_train_scores)
tod_time = end - start
print('TOD execution time', tod_time)

print('TOD is', round(pyod_time / tod_time, ndigits=2),
      'times faster than PyOD')
