# CS_838_Project

All the scripts are developed on Ubuntu 16.04; they may not run properly on Windows. Potential fixes are: 
- checking the path name, 
- install Beautifulsoup,
- install scipy stack,
- install scikit-learn package,
- get Ubuntu, etc.  

## Credit
For yelp crawler, we had been using  
https://github.com/codelucas/yelpcrawl  

## Update
2/7/2017 Added crawler script for yelp and tripadvisor  
`python crawler_tripadvisor.py --start 0 --end 3000`  
`python crawler_yelp.py --price 4 > yelp_crawling_price_4.txt`  

2/8/2017 Fixed a SSL issue that results in authentication error  

2/12/2017 Added 50 articles for place name extraction along with the crawler script  

2/12/2017 Added feature vector extraction script  
`python extract_positive_feature_vectors.py`  

2/13/2017 Added classification script, need some negative example to run the first test  
`python classifier.py`

## Comment
---------------------------------------------------------------------------------------------------------------- 
### Machine Learning Package 
 
http://scikit-learn.org/stable/tutorial/basic/tutorial.html#machine-learning-the-problem-setting 
 
The data object contains multiple field, among which the .data field is a (n_samples, m_features) array. The .target field is the ground truth for the data set. There are a few built-in examples that can be accessed by calling  
`digits = datasets.load_digits()`
 
An estimator is used to predict the classes to which an unseen sample belong. 
Sklearn.svm.SVC is an example of the estimator. 
 
We can set the parameters manually:  
`clf = svm.SVC(gamma=0.001, C=100.) `
 
The estimator instance must be fitted to the model. This is done by passing the training set to the fit() method.  
`clf.fit(digits.data[:-1], digits.target[:-1]) `
 
To save and load a model, use  
`joblib.dump(clf, 'filename.pkl')  `  
`clf = joblib.load('filename.pkl') `
 
See plot_digits_classification.py for an example. 
---------------------------------------------------------------------------------------------------------------- 
### Numpy notes 
 
Print the full array:  
```
import numpy 
numpy.set_printoptions(threshold=numpy.nan) 
print(digits.target) 
```
Read raw table from file and converting string to integer (one to one mapping) so that scikit classifier would accept  
```
	df = read_csv(filename)
	print(df.keys())
	le = preprocessing.LabelEncoder()
	names = df['name'].values
	names_norm = le.fit(names).transform(names)
 ```
 
---------------------------------------------------------------------------------------------------------------- 
### What are we going to construct 
 
Binary prediction: whether a phrase is a place name or not 
 
Data Set: pulled from http://www.travelandleisure.com/trip-ideas/best-places-to-travel-in-2017#belgrade-serbia-fortress and manually labeled 
Feature vectors:  
# dating_and_marriage
