from __future__ import division
from operator import itemgetter
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import tagger,pickle,string
import time
import datetime
from tagger import Tagger
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))   
stemmer = PorterStemmer()
def process_text(text, stem=True):
    """ Tokenize text and stem words removing punctuation """
    text = text.translate(string.punctuation)
    tokens = word_tokenize(text)
    
    if stem:
        tokens = [stemmer.stem(t) for t in tokens]
    return tokens

def split_content_to_sentences(content):
        content = content.replace("\n", ". ")
        return content.split(". ")

def get_content_ranks(content_list):
    tfidf_vectorizer = TfidfVectorizer(tokenizer=process_text,
                                stop_words=stopwords.words('english'),
                                 max_df=0.5,
                                 min_df=0.1,
                                 lowercase=True,use_idf=True)
    print 'content count: ',content_list.__len__()
    try:
        tfidf_matrix = tfidf_vectorizer.fit_transform(content_list)
        sent_rank_list = []
        counter = 0
        count = 1
        while counter<content_list.__len__():
            c_sim_list = cosine_similarity(tfidf_matrix[counter:counter+1], tfidf_matrix)[0]
    #         print c_sim_list
            sent_rank_list.append([sum(c_sim_list.tolist()),content_list[counter]])
            counter += 1
            if counter>=count*1000:
                print 'rank done:',counter
                count += 1
        sent_rank_list = sorted(sent_rank_list,key=itemgetter(0),reverse=True)
    except Exception,ex:
        print ex
        return []
#     print sent_rank_list
    return sent_rank_list

from Summarizer import SummaryTool
import operator 
from stream_tweets import stop_word_list,dictionary

def get_summary(data,no_of_lines):
    sen_rank_list = get_content_ranks(split_content_to_sentences(data))
    counter = 0
    index = 0
    sum_list = []
    while counter<no_of_lines and index < sen_rank_list.__len__():
        try:
            sen = sen_rank_list[index][1]
        except Exception,ex:
            print ex
            print "Exception occur"
            print counter
            print sen_rank_list.__len__()
        if sen.split().__len__()>5:
            sum_list.append(sen)
            counter += 1
        index += 1
    st = SummaryTool()
    summary = '. \n'.join(sum_list)
    #     print summary
    no_of_lines = len(st.split_content_to_sentences(data))
#     print no_of_lines
    no_of_paragraphs = len(st.split_content_to_paragraphs(data))
#     print no_of_paragraphs
    summary_lines = len(st.split_content_to_sentences(summary))
#     print summary_lines
    words = word_tokenize(data)
    total_words = words.__len__()
#     print total_words
    summary_words = word_tokenize(summary).__len__()
#     print summary_words
    summary_rate = str(round((summary_words/total_words),2)*100)
#     print summary_rate
    word_cloud = []
    words_dict = {}
    
    for word in words:
        if word not in stop_word_list and dictionary.check(word.lower()):
            if word in words_dict:
                words_dict[word] += 1
            else:
                words_dict[word] = 1
    counter = 0
    for key,val in sorted(words_dict.items(), key=operator.itemgetter(1),reverse=True):
#         if counter == 200:
#             break
        word_cloud.append({'text':key,'freq':val})
        counter += 1
        
    sum_dict = {'summary':summary,'original_content':data,'word_cloud':word_cloud,'total_words':total_words,'summary_words':summary_words,'total_no_of_sen':no_of_lines,'summary_sen':summary_lines,'summary_rate':summary_rate,'no_of_para':no_of_paragraphs}    
    return sum_dict

def get_top_tweets(tweet_list,no_of_tweets):
    top_tweets = get_content_ranks(tweet_list)
    counter = 0
    index = 0
    tweet_list = []
    while counter<no_of_tweets and index<top_tweets.__len__():
        try:
            tweet = top_tweets[index][1]
        except Exception,ex:
            print ex
            print "Exception occur"
            print counter
            print top_tweets.__len__()
        if tweet.split().__len__()>5:
            tweet_list.append(tweet)
            counter += 1
        index += 1
    return tweet_list

def Get_TweetTags(data,no_tags,multi_tag_len, dict_path=None):
    
    if dict_path is not None:
        weights = pickle.load(open(dict_path, 'rb')) # or your own dictionary
    else:
        weights = pickle.load(open(BASE_DIR+'/Summarizer_Tagger/data/dict.pkl', 'rb')) # default dictionary

    myreader = tagger.Reader() # or your own reader class
    mystemmer = tagger.Stemmer() # or your own stemmer class
    myrater = tagger.Rater(weights,multi_tag_len) # or your own... (you got the idea)
    mytagger = Tagger(myreader, mystemmer, myrater)
    best_tags = mytagger(data, no_tags)
    
    return best_tags

def build_summary(product,no_of_lines=15, no_of_tweets=300, no_of_tags=10, multi_tag_len=2,custom=False):
    client = MongoClient()
    db = client['POC_DB']
    bucket_col = db['BUCKETS']
    meta_col = db['META_DATA']
    if custom:
        buckets = bucket_col.find({'product':product,'custom':True,'is_applied':False})
    else:
        buckets = bucket_col.find({'product':product,'custom':False})
    buckets = [buc for buc in buckets]
    ful_s_time = time.time()
#     counter = 1
#     summary_list = []
    for buc in buckets:
        buc_s_time = time.time()
        print buc['bucket_name']
        documents = meta_col.find({'_id':{'$in':buc['bucket']}},{'original_word_list_low':1,'user_name':1})
        tweets = []
        users = []
        for doc in documents:
            tweets.append(" ".join(doc['original_word_list_low']))
            users.append(doc['user_name'])
        tweet_para = '\n'.join(tweets)
        print 'summary start'
        summary = get_summary(tweet_para, no_of_lines)
        print 'top tweets start'
        top_tweets = get_top_tweets(tweets, no_of_tweets)
        top_tweets_and_username = [[users[tweets.index(tweet)],tweet] for tweet in top_tweets]
        print 'tags start'
        tags = Get_TweetTags(tweet_para, no_of_tags, multi_tag_len)
        tags = [tag.string for tag in tags]
        print 'tags done'
#         summary_list.append({'buc_id':buc['_id'],'summary':summary,'top_tweets':top_tweets_and_username,'tags':tags})
        bucket_col.update({'_id':buc['_id']},{"$set":{'summary':summary,'is_applied':True,'top_tweets':top_tweets_and_username,'tags':tags}})
        seconds_elapsed = time.time() - buc_s_time
        print("bucket time elapsed: %s" % str(datetime.timedelta(seconds=seconds_elapsed)))
#     for s_dic in summary_list:
#         bucket_col.update({'_id':s_dic.pop('buc_id')},{'$set':s_dic})
    seconds_elapsed = time.time() - ful_s_time
    print("ful time elapsed: %s" % str(datetime.timedelta(seconds=seconds_elapsed)))


# build_summary('Telenor', no_of_lines=10, no_of_tweets=100, no_of_tags=10, multi_tag_len=2)