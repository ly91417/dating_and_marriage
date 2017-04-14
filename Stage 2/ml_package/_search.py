from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import cross_val_score
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import numpy as np
import time
import multiprocessing as mp
import warnings as wa


class ParamSearch(object):

	def __init__(self, estimator, param_grid, cv=None, verbose=False, warnings=True, batch_size=30):
		if cv is None:
			cv = StratifiedKFold(n_splits=5, shuffle=True)
		self.cv = cv
		self.estimator = estimator
		self.param_grid = param_grid
		self.best_param = None
		self.cv_scores = None
		self.verbose = verbose
		self.batch_size = batch_size
		if not warnings:
			wa.filterwarnings("ignore")


	# this method is picklable
	def __call__(self, args):
		score = self.cross_validation(args[0], args[1], args[2])
		if self.verbose:
			print('Precision {:6.3f} +/-{:6.3f}  Recall {:6.3f} +/-{:6.3f} for \n{}'.format(score['precision'],
					score['precision_std'],
					score['recall'],
					score['recall_std'],
					score['parameter']))
		return score


	def grid_search(self, X, y, processes=4, key='f1'):
		para_list = list(ParameterGrid(self.param_grid))

		# run jobs in parallel
		pool = mp.Pool(processes=processes)
		args = [[param, X, y] for param in para_list]
		self.cv_scores = pool.map(self, args, self.batch_size)

		# find the best parameter
		self.best_param = max(self.cv_scores, key=lambda x: x[key])
		print()
		print('Best {} score: {:6.3f} +/-{:6.3f}'.format(key, self.best_param[key], self.best_param['{}_std'.format(key)]))
		print('Precision {:6.3f} +/-{:6.3f}  Recall {:6.3f} +/-{:6.3f}'.format(self.best_param['precision'],
																				self.best_param['precision_std'],
																				self.best_param['recall'],
																				self.best_param['recall_std']))
		print('Best parameter found based on {}: \n{}'.format(key, self.best_param['parameter']))


	# def grid_search(self, X, y, processes=1):
	# 	para_list = list(ParameterGrid(self.param_grid))
	# 	self.cv_scores = []
	# 	# best parameter is found based on f1 score
	# 	best_score = 0
	# 	best_score_std = 0
	# 	best_param = None
	# 	start_time = time.time()
	# 	# print estimator information
	# 	for param in para_list:
	# 		cv_score = self.cross_validation(param, X, y)
	# 		if cv_score['f1'] > best_score:
	# 			best_score = cv_score['f1']
	# 			best_score_std = cv_score['f1_std']
	# 			best_param = param
	# 		self.cv_scores.append(cv_score)
	# 		# print parameter search result for every set of parameter
	# 		# print('Precision {:6.3f} +/-{:6.3f}  Recall {:6.3f} +/-{:6.3f} for {}'.format(cv_score['precision'],
	# 		# 																			cv_score['precision_std'],
	# 		# 																			cv_score['recall'],
	# 		# 																			cv_score['recall_std'],
	# 		# 																			cv_score['parameter']))
	# 	# print best parameter set
	# 	print()
	# 	print('Best parameter found based on f1 score: {}'.format(best_param))
	# 	print('Best f1 score: {:6.3f} +/-{:6.3f}'.format(best_score, best_score_std))


	def random_search(self, X, y, n_jobs=1, n_iter=10):
		return None

	def cross_validation(self, param, X, y):
		X = np.array(X)
		y = np.array(y)
		precision = []
		recall = []
		f1 = []
		for train, test in self.cv.split(X, y):
			X_train, X_test, y_train, y_test = X[train], X[test], y[train], y[test]
			estimator = clone(self.estimator)
			estimator.set_params(**param)
			estimator.fit(X_train, y_train)
			y_pred = estimator.predict(X_test)
			precision.append(precision_score(y_test, y_pred))
			recall.append(recall_score(y_test, y_pred))
			f1.append(f1_score(y_test, y_pred))
		cv_score = {'parameter':param, 'precision':np.mean(precision), 'recall':np.mean(recall),
					'precision_std':np.std(precision), 'recall_std':np.std(recall), 'f1':np.mean(f1), 'f1_std':np.std(f1)}
		return cv_score

