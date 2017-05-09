
# coding: utf-8

# In[1]:

print(__doc__)


# Code source: Gaël Varoquaux
#              Andreas Müller
# Modified for documentation by Jaques Grobler
# License: BSD 3 clause

import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
from itertools import izip
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.metrics import f1_score
from sklearn.linear_model import LogisticRegression


# naming convention for original file (either 'perm-1' or nothing)
origfile_sign = None
if len(sys.argv) > 2:
    origfile_sign = sys.argv[2]

def get_data(featurefilepath):
    #dataset = 'barzilay'
    #f = open('data/doc_1.perm-1.txt-doc_99.txt.features.pkl', 'r')
    f = open(featurefilepath, 'rb')
    data = pickle.load(f)
    all_features = {}
    for _file in data.keys():
        for feat in data[_file].keys():
            all_features[feat] = 1
    train = np.zeros([len(data.keys()), len(all_features.keys())])
    label = np.ones([len(data.keys()),1])
    for i, _file in enumerate(data.keys()):
        train[i, :] = [data[_file][feat] if data[_file].get(feat) else 0 for feat in all_features.keys()]
        
        # if 'barzilay' in featurefilepath:
        #     if not 'perm-1.txt' in _file:
        #         label[i,0] = 0
        # else:
        #     if 'perm' in _file:
        #         label[i,0] = 0

        if origfile_sign == None or origfile_sign == '':
            if 'perm' in _file:
                label[i,0] = 0
        elif not origfile_sign in _file:
            label[i,0] = 0
        
    #train = preprocessing.normalize(train)
    return (train, label)


names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost", "MaxEnt",
         "Naive Bayes"]

classifiers = [
    KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1,probability=True),
    GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1),
    AdaBoostClassifier(),
    LogisticRegression(C=1e-5),
    GaussianNB(priors=[0.5,0.5])]


X, y = get_data(sys.argv[1])

# preprocess dataset, split into training and test part
X = StandardScaler().fit_transform(X)
X_train, X_test, y_train, y_test =     train_test_split(X, y, test_size=.2, random_state=42)

# iterate over classifiers
for name, clf in izip(names, classifiers):
    clf.fit(X_train, y_train.squeeze(1))
    score_train = clf.score(X_train, y_train)
    score_test = clf.score(X_test, y_test)
    
    cv_scores = cross_val_score(clf, X_train, y_train.squeeze(1), cv=5)
    f1 = f1_score(clf.predict(X_train), y_train)
    
#     if name == "RBF SVM":
#         for i, p in enumerate(clf.predict_proba(X_test)):
#             print y_test[i, :], p

    # Plot the decision boundary. For that, we will assign a color to each
    # point in the mesh [x_min, x_max]x[y_min, y_max].
#     if hasattr(clf, "decision_function"):
#         Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
#     else:
#         Z = clf.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]

    print name, score_train, score_test#, Z
    #print np.mean(cv_scores)
    #print f1


# In[20]:

#x,y = get_data()
#x.shape


# In[8]:

#get_data()


# In[ ]:

'''
Earthquake:
RBF SVM
Neural Net
Random Forest

Bad classification:
Linear SVM
Nearest Neighbours

Nearest Neighbors 0.806547619048 0.77380952381
Linear SVM 0.821428571429 0.797619047619
RBF SVM 0.860119047619 0.809523809524
Gaussian Process 0.803571428571 0.797619047619
Decision Tree 0.839285714286 0.77380952381
Random Forest 0.818452380952 0.797619047619
Neural Net 0.842261904762 0.821428571429
AdaBoost 0.863095238095 0.809523809524
Naive Bayes 0.401785714286 0.345238095238
QDA 0.550595238095 0.392857142857


Nearest Neighbors 0.827380952381 0.797619047619
Linear SVM 0.803571428571 0.797619047619
RBF SVM 0.803571428571 0.797619047619
Gaussian Process 0.803571428571 0.797619047619
Decision Tree 0.833333333333 0.797619047619
Random Forest 0.818452380952 0.797619047619
Neural Net 0.803571428571 0.797619047619
AdaBoost 0.863095238095 0.797619047619
Naive Bayes 0.419642857143 0.357142857143
'''

