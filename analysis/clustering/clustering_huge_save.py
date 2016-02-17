#Need to add parent directoy to sys.path to find 'metadataDB'
import sys
sys.path.append('../../')

# %matplotlib inline
# import matplotlib.pyplot as plt 
import time
import numpy as np
# import scipy as sp
import re
from collections import Counter
import itertools
import random
import pickle

# Natural language processing toolkit
# To use this, run nltk.download() and download 'stopwords'
# from nltk.corpus import stopwords
# s=stopwords.words('english') + ['']

# Machine learning
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.cluster import KMeans
from sklearn.decomposition import SparsePCA
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
# from sklearn import metrics
from sklearn.externals import joblib

# SQL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from metadataDB.declareDatabase import *
from sqlalchemy import or_, and_


# Load relevant articles
engine = create_engine("sqlite:///../../arXiv_metadata.db", echo=False)
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

abstract_all_tmp = {'category': [], 'abstract': []}
# category_list = sorted(['atom-ph', 'quant-ph', 'optics', 'nlin', 'str-el', 'stat'])
category_list = sorted(['quant-ph', 'str-el', 'hep-', 'mtrl-sci', 'plasm-ph'])
category_len = len(category_list)

start = time.time()
for item in category_list:
    query = session.query(Article_Category)\
                        .join(Category)\
                        .join(Article)\
                        .filter(Category.name.like('%' + item + '%'))
#     query = session.query(Article_Category)\
#                         .join(Category)\
#                         .join(Article)\
#                         .filter(Category.name.like('%' + item + '%'))
    result = [' '.join(x.article.abstract.split()) for x in query]
    abstract_all_tmp['abstract'].extend(result)
    abstract_all_tmp['category'].extend([item]*len(result))

print 'Loaded articles. %f seconds' % (time.time() - start)
print ''
# for item in query:
#     abstract_all['category'].append(item.category.name)
#     abstract_all['abstract'].append(' '.join(item.article.abstract.split()))
# print time.time() - start
# abstract_all['atom-ph'] = [x.article.abstract for x in query.all()]
# session.close_all()


##Oops! How many overlapping articles do we have? I forgot that arXiv categories aren't unique.
# Let's remove all duplicates.
# This is slow but I am tired.

counter_duplicate = Counter(abstract_all_tmp['abstract'])

abstract_all = {'category': [], 'abstract': []}
for cat, abstract in itertools.izip(abstract_all_tmp['category'], abstract_all_tmp['abstract']):
    if counter_duplicate[abstract] == 1:
        abstract_all['category'].append(cat)
        abstract_all['abstract'].append(abstract)


# Breakdown of categories

print 'Breakdown of articles (after duplicates removed):'

count = Counter(abstract_all['category'])
for key, val in count.iteritems():
    print '{:<15}{}'.format(key, val)
print '{:<15}{}'.format('Total', len(abstract_all['abstract']))

# Train on 80% of the data. Random_state ensures that we always get the same result.
x_train, x_test, y_train, y_test = train_test_split(abstract_all['abstract'],
                                                    abstract_all['category'],
                                                    random_state=42,
                                                    train_size=10000,
                                                    test_size=10000)

counter_train = Counter(y_train)



# Now, try KMeans clustering.
# See: http://scikit-learn.org/stable/auto_examples/text/document_clustering.html

n_clusters = 10
# Reduce n_init to 10 for testing purposes.
clf_unsupervised = Pipeline([('vect', CountVectorizer(ngram_range=(1,3), stop_words='english')),
                             ('tfidf', TfidfTransformer()),
                             ('clf', KMeans(n_clusters=n_clusters, n_init=1))])
start = time.time()
clf_unsupervised.fit(x_train)
print 'Trained Kmeans algorithm. %f seconds' % (time.time() - start)
print ''

# start = time.time()
# predict_train = clf_unsupervised.predict(x_train)
# predict = clf_unsupervised.predict(x_test)
# print time.time() - start




# # Which clusters most closely align with which the original categories?
# # Find the strongest correlation, and assign that cluster to the category. Iterate.
#
#
# counter_category = Counter(y_train)
# counter_cluster = Counter(predict_train)
# accuracy_train_initial = np.array(
# #     [[sum((a==cat and b==x for a,b in zip(y_train, predict_train)))*1./counter_cluster[x]
#     [[sum((a==cat and b==x for a,b in zip(y_train, predict_train)))*1./counter_category[cat]
#            for x in range(0,n_clusters)]
#            for cat in category_list])
# clusterToCategory = dict()
# # categoryToCluster = dict()
#
# for cluster, item in enumerate(np.argmax(accuracy_train_initial, axis=0).tolist()):
#     clusterToCategory[cluster] = category_list[item]

# Save model
# joblib.dump(clf_supervised, 'svm_category.pkl')
joblib.dump(clf_unsupervised, 'kmeans_category.pkl')
pickle.dump({'x_train': x_train,
             'x_test': x_test,
             'y_train': y_train,
             'y_test': y_test},
             open('train_test.pkl', 'wb'))
