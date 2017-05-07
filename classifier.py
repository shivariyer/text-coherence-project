
# take a complete features file and build a classifier to predict the
# score (0 or 1 for coherent or incoherent)

import pickle
import argparse
import itertools
import numpy as np

from sklearn import linear_model, metrics, preprocessing
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold

parser = argparse.ArgumentParser()
parser.add_argument('dataset', help='Pickle file containing features for dataset')
parser.add_argument('--crossval', type=int, default=5, help='K for K-fold cross-validation')
parser.add_argument('--algo', type=int, help='The ML algo to use')
parser.add_argument('--modelfile', help='Output file name to store trained model')

args = parser.parse_args()

# ML methods to use
# 0 - Naive Bayes

with open(args.dataset, 'rb') as f:
    dataset = pickle.load(f)

if args.crossval > len(dataset):
    raise Exception('K for Cross-validation too high')
elif args.crossval < 2:
    raise Exception('K for Cross-validation should be >= 2')

# it is expected that "dataset" is a dictionary mapping file names to
# the feature set. Labels will be 0 if the word "perm" appears in the
# file name, else 1.

roletypes1 = [None, '.1', '.2',
              'Comparison.1', 'Comparison.2',
              'Contingency.1', 'Contingency.2',
              'Expansion.1', 'Expansion.2',
              'NoRel.1', 'NoRel.2',
              'Temporal.1', 'Temporal.2']
roletypes2 = [None, 'EntRel', 'Explicit', 'Implicit']

dictkeys = list(itertools.product(roletypes1, roletypes1)) + list(itertools.product(roletypes2, roletypes2))

print dictkeys
print len(dictkeys)

X = []
Y = []
for k,v in dataset.iteritems():
    if len(v) == 0:
        continue
    fdict = dict.fromkeys(dictkeys, 0)
    fdict.update(v)
    print v
    print fdict
    assert False
    fvect = fdict.items()
    fvect.sort()
    X.append([val for _,val in fvect])
    if '.perm' in k:
        Y.append(0)
    else:
        Y.append(1)

print max([len(vect) for vect in X])
print min([len(vect) for vect in X])

# X = np.array(X)
# Y = np.array(Y)

# print X.shape
# print Y.shape

# X = preprocessing.normalize(X, axis=1)
kf = KFold(n_splits=args.crossval, shuffle=True)

for train_index, test_index in kf.split(X):
    # print 'TRAIN: {}, TEST: {}'.format(train_index, test_index)
    X_train, X_test = X[train_index], X[test_index]
    Y_train, Y_test = Y[train_index], Y[test_index]
    logreg = linear_model.LogisticRegression(C=1e-5)
    logreg.fit(X_train, Y_train)
    pred = logreg.predict(X_test)
    print metrics.accuracy_score(Y_test, pred)

# import pickle
# import numpy as np
# from sklearn import linear_model, metrics, preprocessing
# dataset = 'barzilay'
# f = open('data/bz/apwsE960508.0041-2-2-0.perm-13.txt.pipe.features.pkl', 'r')
# data = pickle.loads(f.read())
# all_features = {}
# for _file in data.keys():
#    for feat in data[_file].keys():
#        all_features[feat] = 1

# train = np.zeros([len(data.keys()), len(all_features.keys())])
# label = np.ones([len(data.keys()), 1])
# for i, _file in enumerate(data.keys()):
#    train[i, :] = [data[_file][feat] if data[_file].get(feat) else 0 for feat in all_features.keys()]
#    permuted_file = 'perm-1.txt' if dataset == 'barzilay' else 'perm'
#    if permuted_file not in _file:
#        label[i, 0] = 0
# train = preprocessing.normalize(train)
# logreg = linear_model.LogisticRegression(C=1e-5)
# logreg.fit(train, label)
# pred = logreg.predict(train)
# print metrics.accuracy_score(label, pred)
