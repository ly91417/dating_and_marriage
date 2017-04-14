################################################################
##	Filename: 	classifier.py				
##	Author: 	Charlotte Xue
##	Email: 		cbgitek@gmail.com
##	Create:   	2017-02-13
##	Modified: 	2017-02-13
################################################################

from pandas import read_csv
import pydotplus
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn.linear_model import SGDClassifier
from sklearn import svm
from sklearn import linear_model

from _search import ParamSearch

# Read feature vectors into numpy array
def read_vectors(filename):
	# Read raw table from file
	df = read_csv(filename,error_bad_lines=False)
	feature_keys = list(df.keys())
	# test soundex
	# feature_keys.remove('soundex')
	feature_keys.remove('is_target')
	data = []
	for i in range(len(df.values)):
		new_row = []
		for key in feature_keys:

			new_row += [df[key][i]]
		data += [new_row]
	# for d in data:
	# 	print(d)
	target = list(df['is_target'].values)
	return {'data':data, 'target':target, 'feature':feature_keys}

# Performs model training
def train_model(dataset):
	clf = svm.SVC()
	clf.fit(dataset['data'], dataset['target'])

# def model_select(clfs, X, y, scoring, numFolds):
# 	mycv = StratifiedKFold(n_splits=numFolds, shuffle=True)
# 	# test on SVC
# 	avg_scores = []
# 	std_scores = []
# 	for clf in clfs:
# 		scores = cross_val_score(clf, X, y, cv=mycv, scoring=scoring)
# 		avg_scores.append(scores.mean())
# 		std_scores.append(scores.std())
# 	return avg_scores, std_scores


# perform model selection (new version)
def model_select(param_grid, X, y, numFolds):
	verbose = param_grid.pop('verbose', False)
	warnings = param_grid.pop('warnings', True)
	processes = param_grid.pop('processes', True)
	batch_size = param_grid.pop('batch_size', True)

	mycv = StratifiedKFold(n_splits=numFolds, shuffle=True)
	best_params = {}
	for key in sorted(param_grid):
		print('-------------------------------------------------')
		print('{} classifier parameter searching'.format(key))
		print()
		clf = ParamSearch(eval(key)(), param_grid[key], cv=mycv, 
							warnings=warnings, verbose=verbose, batch_size=batch_size)
		clf.grid_search(X, y, processes=processes, key='precision')
		best_params[key] = clf.best_param
	return best_params


def param_grid_gen(tune_one_clf=False):
	# SVM Classifier
	svmList = {'kernel':['rbf'], 'gamma':[1e-5, 1e-3, 1], 'C':[0.01, 0.1, 1, 10]}

	# Random Forest Classifier
	rfList = [
		{'n_estimators': [10, 30, 50], 'criterion':['gini','entropy'],'max_features':[0.2, 0.5,'sqrt','log2',None]},
		{'max_depth': [5, 10, None], 'min_samples_split': [2, 5, 10, 20],'min_samples_leaf': [2, 5, 10, 20]},
		{'n_estimators': [10, 30, 50], 'min_weight_fraction_leaf': [0, 0.01], 'min_impurity_split': [1e-7, 1e-5, 1e-3]},
		{'n_estimators': [10, 30, 50], 'bootstrap': [True, False], 'class_weight': ['balanced', None]} ]

	# Logistic Regression Classifier
	logisList = [{'penalty':['l1','l2'], 'C':[1e-3, 1e-2,1,10],
				  'solver':['liblinear'], 'class_weight':['balanced',None]},
				  {'C':[1e-3, 1e-2,1,10], 'class_weight':['balanced',None],
				  'solver':['newton-cg','lbfgs','sag']}]

	# Decision Tree Classifier
	treeList = [{'criterion':['gini','entropy'], 'splitter':['best','random'],
				'max_features':[0.2,0.5,'sqrt','log2',None]},
				{'max_depth':[5,10,None], 'min_samples_split':[2,5,10,20],
				'min_samples_leaf':[2,5,10,20]},
				{'min_weight_fraction_leaf':[0, 0.01],
				'class_weight':['balanced',None], 'min_impurity_split':[1e-7,1e-5,1e-3]}]

	param_grid = {}
	param_grid.update({'verbose': True})
	param_grid.update({'warnings': False})
	param_grid.update({'processes': 4})
	param_grid.update({'batch_size': 20})
	if not tune_one_clf:
		param_grid.update({'svm.SVC': svmList})
		param_grid.update({'RandomForestClassifier': rfList})
		param_grid.update({'tree.DecisionTreeClassifier': treeList})
		param_grid.update({'linear_model.LogisticRegression':logisList})
	else:
		rfList = [
			{'n_estimators': [10, 70, 120], 'criterion': ['gini', 'entropy'],
			 'max_features': [0.1, 0.5, 'sqrt', 'log2', None]},
			{'max_depth':[2,4,7,None], 'min_samples_split':[2, 20],
				'min_samples_leaf':[2, 20]},
			{'n_estimators': [10, 70, 120], 'min_weight_fraction_leaf': [0, 0.01, 0.0001],
			 'min_impurity_split': [1e-7, 1e-3]},
			{'n_estimators': [10, 70, 120], 'bootstrap': [True, False], 'class_weight': ['balanced', None]}]
		param_grid.update({'RandomForestClassifier': rfList})
	return param_grid


def print_stat(clf, X, y, split_ratio=0.2, feature_names=None, printTree=False):
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split_ratio, random_state=10, stratify=y)
	clf.fit(X_train, y_train)
	# Confusion matrix on training set
	y_true, y_predict = y_train, clf.predict(X_train)
	print('Training Set Performance')
	print(confusion_matrix(y_true, y_predict))
	# Confusion matrix on testing set
	y_true, y_predict = y_test, clf.predict(X_test)
	print("Testing Set Performance")
	print(confusion_matrix(y_true, y_predict))
	print('Classification report on testing set')
	print('Scores:\n{}'.format(classification_report(y_true, y_predict)))
	## only for decision tree
	if printTree:
		dot_data = tree.export_graphviz(clf, out_file=None,feature_names=feature_names)
		graph = pydotplus.graph_from_dot_data(dot_data)
		graph.write_pdf("tree.pdf")

def linear_regression(X, y, folds=5, threshold=0.5):
	print("linear regression:")
	reg = linear_model.LinearRegression()
	skf = StratifiedKFold(n_splits=folds, shuffle=True)
	precision = []
	recall = []
	X = np.array(X)
	y = np.array(y)
	for train, test in skf.split(X, y):
		X_train, X_test, y_train, y_test = X[train], X[test], y[train], y[test]
		reg.fit(X_train,y_train)
		y_pred = reg.predict(X_test)
		y_pred[y_pred>=threshold] = 1
		y_pred[y_pred<threshold] = 0
		precision.append(precision_score(y_test, y_pred))
		recall.append(recall_score(y_test,y_pred))
		print(confusion_matrix(y_test, y_pred))
	print("{} fold cross validation score:".format(folds))
	print("precision:{:6.3f} +/-{:6.3f} recall:{:6.3f} +/-{:6.3f}".format(np.mean(precision), np.std(precision), np.mean(recall), np.std(recall)))

def test_model(X_test, y_test, clf):
	print('Testing trained model of testing set:')
	y_true, y_predict = y_test, clf.predict(X_test)
	print("Testing Set Performance")
	print(confusion_matrix(y_true, y_predict))
	print('Classification report on testing set')
	print('Scores:\n{}'.format(classification_report(y_true, y_predict)))


if __name__ == '__main__':

	# Step 1: cross validation on development set to select best model
	# development set feature_vectors
	filename = '../data/devl_set_feature_vectors.txt'
	dataSet = read_vectors(filename)
	X, y = dataSet['data'], dataSet['target']

	# print_stat(tree.DecisionTreeClassifier(), X, y, feature_names=dataSet['feature'],printTree=True)
	# linear_regression(X, y, folds=5, threshold=0.5)
	# params = param_grid_gen()
	# Step 2: fine tune parameter of the selected model using P Q subset of the development
	params = param_grid_gen(tune_one_clf=False)
	best_params = model_select(params, X, y, 5)
	print(best_params)
	# print_stat(RandomForestClassifier(),X,y,split_ratio=0.5)

	# Step 3 testing the selected model on the testing set
	# test set feature vectors
	filename = '../data/test_set_feature_vectors.txt'
	dataSet = read_vectors(filename)
	X_test, y_test = dataSet['data'], dataSet['target']
	params = best_params['RandomForestClassifier']['parameter']
	clf = RandomForestClassifier()
	clf.set_params(**params)
	clf.fit(X,y)
	test_model(X_test,y_test,clf)
