from __future__ import division

import collections
from nltk.stem import PorterStemmer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import string
from nltk import word_tokenize
from pymongo import MongoClient
from TextSummarization.stream_tweets import clean_word
client = MongoClient()

db = client["Text_Analysis"]
stemmer = PorterStemmer()
def process_text(text, stem=True):
    """ Tokenize text and stem words removing punctuation """
    text = text.translate(string.punctuation)
    tokens = word_tokenize(text)
    
    if stem:
        tokens = [stemmer.stem(t) for t in tokens]
    return tokens

def cluster_texts(texts,clusters=20):
    """ Transform texts to Tf-Idf coordinates and cluster texts using K-Means """
    vectorizer = TfidfVectorizer(tokenizer=process_text,
                                 max_df=0.5,
                                 min_df=0.1,
                                 lowercase=True,use_idf=True)
    
    tfidf_model = vectorizer.fit_transform(texts)
    km_model = KMeans(n_clusters=clusters)
    km_model.fit(tfidf_model)
    clustering = collections.defaultdict(list)
    for idx, label in enumerate(km_model.labels_):
        clustering[label].append(idx)
 
    return clustering

import datetime,time
from Summarizer import SummaryTool
def get_clusters_file(source,file_text,n_clusters):
    st = SummaryTool()
    documents = st.split_content_to_sentences(file_text)
    documents = [doc for doc in documents if doc.__len__()>2]
    total_sent = len(documents)
    total_words = len(word_tokenize(clean_word(file_text)))
    clusters = cluster_texts(documents, clusters=n_clusters)
    dic_clusters = dict(clusters)
    today = datetime.date.today()
    start_time= time.time()
#     db.drop_collection('n_clusters')
    col = db["cluster"]
    counter = 0
    cluster_doc = {}
    nodes_cluster = []
    cluster_n = []
    index_count = 0
    while counter<n_clusters:
        bucket = dic_clusters.pop(counter)
        bucket = [documents[index] for index in bucket]
        cluster_doc["cluster_"+str(counter+1)] = bucket
        cluster_n.append({'name':"cluster_"+str(counter+1),'count':len(bucket)})
#         for tweet in bucket:
#             nodes_cluster.append({
#                   "id":counter,
#                   "index":index_count,
#                   "title":tweet
#                   })
#             index_count += 1
        counter += 1
        
        print counter
    
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    col.insert({'source':source,'cluster_names':cluster_n,'nodes_cluster':nodes_cluster,'total_tweets':total_sent,'total_words':total_words,'date_time':str(today),'time_elapsed':str(endtime),'no_of_clusters':n_clusters,'clusters':cluster_doc,'isFile':True})

def get_clusters_tweets(source,documents,n_clusters):
    tweets = [doc['content_title'] for doc in documents]
    words = [word for doc in documents for word in word_tokenize(doc['content_title'])]
    total_tweets = len(tweets)
    total_words = len(words)
    clusters = cluster_texts(tweets, clusters=n_clusters)
    dic_clusters = dict(clusters)
    today = datetime.date.today()
    start_time= time.time()
#     db.drop_collection('n_clusters')
    col = db["cluster"]
    counter = 0
    cluster_doc = {}
    nodes_cluster = []
    index_count = 0
    cluster_n = []
    while counter<n_clusters:
        bucket_1 = dic_clusters.pop(counter)
        bucket = [documents[index]['_id'] for index in bucket_1]
        tweets_c = [documents[index]['content_title'] for index in bucket_1]
        cluster_doc["cluster_"+str(counter+1)] = bucket
        cluster_n.append({'name':"cluster_"+str(counter+1),'count':len(bucket)})
#         for tweet in tweets_c:
#             nodes_cluster.append({
#                   "id":counter,
#                   "index":index_count,
#                   "title":tweet
#                   })
#             index_count += 1
        counter += 1
        print counter
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    col.insert({'source':source,'cluster_names':cluster_n,'nodes_cluster':nodes_cluster,'total_tweets':total_tweets,'total_words':total_words,'date_time':str(today),'time_elapsed':str(endtime),'no_of_clusters':n_clusters,'clusters':cluster_doc,'isFile':False})