from __future__ import division
import math
from reverend.thomas import Bayes
import os
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.util import ngrams
from nltk.stem import PorterStemmer, WordNetLemmatizer

# from sentiment_analysis.views import single_classifier
# stemmer = PorterStemmer()
# lemmatizer = WordNetLemmatizer()


def get_best_words(pos_train,neg_train):
    word_fd = FreqDist()
    label_word_fd = ConditionalFreqDist()
    
    pos_feats = [word for tweet in pos_train for word in word_tokenize(clean_word(tweet).lower())]
    neg_feats = [word for tweet in neg_train for word in word_tokenize(clean_word(tweet).lower())]
    print 'pos_feats: ',pos_feats.__len__()
    print 'neg_feats: ',neg_feats.__len__()
    for word in pos_feats:
        word_fd[word.lower()] += 1
        label_word_fd['pos'][word.lower()] += 1
     
    for word in neg_feats:
        word_fd[word.lower()] += 1
        label_word_fd['neg'][word.lower()] += 1
    
    pos_word_count = label_word_fd['pos'].N()
    neg_word_count = label_word_fd['neg'].N()
    total_word_count = pos_word_count + neg_word_count
    
    word_scores = {}
     
    for word, freq in word_fd.iteritems():
        pos_score = BigramAssocMeasures.chi_sq(label_word_fd['pos'][word],
            (freq, pos_word_count), total_word_count)
    #     print 'total_count: %d pos_total_count: %d word_count: %d pos_word_count: %d'%(total_word_count,pos_word_count,freq,label_word_fd['pos'][word])
    #     print 'pos_score: ',pos_score
        neg_score = BigramAssocMeasures.chi_sq(label_word_fd['neg'][word],
            (freq, neg_word_count), total_word_count)
        word_scores[word] = pos_score + neg_score
    count_best = sorted(word_scores.iteritems(), key=lambda (w,s): s, reverse=True).__len__()    
    best = sorted(word_scores.iteritems(), key=lambda (w,s): s, reverse=True)[:17000]
    print 'total best words: ',count_best
    bestwords = set([w for w, s in best])
    return bestwords

def clean_word(dirty_word):
        clean_char_list = list()
        for char in dirty_word:
            if ord(char) <= 128:
                clean_char_list.append(char)
        return ''.join(clean_char_list)

class non_stop_tokenizer:
    
    stopset = set(stopwords.words('english'))
    
    def __init__(self, lower=True):
        self.lower = lower
        
    def tokenize(self, tweet):
        tokens = [word for word in word_tokenize(clean_word(tweet).lower()) if word in self.stopset]
        return tokens

class best_tokenizer:

    def __init__(self,best_words, lower=True):
        self.lower = lower
        self.best_words = best_words
        
    def tokenize(self, tweet):
        tokens = [word for word in word_tokenize(clean_word(tweet).lower()) if word in self.best_words]
        return tokens

class best_bigram_tokenizer:

    def __init__(self,best_words, lower=True):
        self.lower = lower
        self.best_words = best_words
        
    def tokenize(self, tweet):
        tokens = [word for word in word_tokenize(clean_word(tweet).lower()) if word in self.best_words]
        bigrams_l = [bigram for bigram in ngrams(word_tokenize(clean_word(tweet).lower()),2)]
        return tokens+bigrams_l



# def word_feats_with_no_stop_words(tweets):
#     tweets_non_stop = []
#     for tweet in tweets:
#         toknize_list = word_tokenize(clean_word(tweet).lower())
# #         print tweet
#         res = [word for word in toknize_list if word not in stopset]
# #         print " ".join(res)
#         if res.__len__()>0:
#             tweets_non_stop.append(" ".join(res))
#     return tweets_non_stop

# def stem_words(features):
#     stemmed_list = []
#     for feat in features:
#         word = stemmer.stem(feat)
# #         print tweet
#         stemmed_list.append(word)
# #         print " ".join(res)
#     return stemmed_list

# def lem_words(features):
#     lemmatize_list = []
#     for feat in features:
#         word = lemmatizer.lemmatize(feat)
# #         print tweet
#         lemmatize_list.append(word)
# #         print " ".join(res)
#     return lemmatize_list

def evaluate_classifier(neg_train,pos_train,classifier):
    
    for tweet in neg_train:
        classifier.train('negative', tweet.lower())
        
    for tweet in pos_train:
        classifier.train('positive', tweet.lower())
    return classifier

# def find_stem_accuracy(check_classifier):
#     neg_correct = 0
#     for tweet in neg_test:
#         
#         result = sorted(check_classifier._guess(stem_words(word_tokenize(clean_word(tweet)))))
#         if result.__len__()>1:
#             neg_score = result[0][1]
#             pos_score = result[1][1]
#             if neg_score >= pos_score:
#                 neg_correct += 1
#     pos_correct = 0
#     for tweet in pos_test:
#         result = sorted(check_classifier._guess(stem_words(word_tokenize(clean_word(tweet)))))
#         if result.__len__()>1:
#             neg_score = result[0][1]
#             pos_score = result[1][1]
#             if neg_score <= pos_score:
#                 pos_correct += 1
#     print 'pos_test_data_count: ',pos_test.__len__()
#     print 'pos_test_correct_count: ',pos_correct
#     print 'neg_test_data_count: ',neg_test.__len__()
#     print 'neg_test_correct_count: ',neg_correct
#     total_correct_score = neg_correct+pos_correct
#     print 'total_correct_score: ',total_correct_score
#     total_tweets_score = neg_test.__len__()+pos_test.__len__()
#     print 'total_tweet_score: ',total_tweets_score
# #     print 'accuracy: ',(total_correct_score/total_tweets_score)*100
#     return (total_correct_score/total_tweets_score)*100

# def find_accuracy(check_classifier):
#     neg_correct = 0
#     for tweet in neg_test:
#         result = sorted(check_classifier.guess(tweet.lower()))
#         if result.__len__()>1:
#             neg_score = result[0][1]
#             pos_score = result[1][1]
#             if neg_score >= pos_score:
#                 neg_correct += 1
#     pos_correct = 0
#     for tweet in pos_test:
#         result = sorted(check_classifier.guess(tweet.lower()))
#         if result.__len__()>1:
#             neg_score = result[0][1]
#             pos_score = result[1][1]
#             if neg_score <= pos_score:
#                 pos_correct += 1
#     print 'pos_test_data_count: ',pos_test.__len__()
#     print 'pos_test_correct_count: ',pos_correct
#     print 'neg_test_data_count: ',neg_test.__len__()
#     print 'neg_test_correct_count: ',neg_correct
#     total_correct_score = neg_correct+pos_correct
#     print 'total_correct_score: ',total_correct_score
#     total_tweets_score = neg_test.__len__()+pos_test.__len__()
#     print 'total_tweet_score: ',total_tweets_score
# #     print 'accuracy: ',(total_correct_score/total_tweets_score)*100
#     return (total_correct_score/total_tweets_score)*100
#   
#   
#   
#   
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#  
# neg_file = open(BASE_DIR+"/sentiment_analysis/data_files/rt-polaritydata/rt-polaritydata/rt-polarity.neg").read()
# pos_file = open(BASE_DIR+"/sentiment_analysis/data_files/rt-polaritydata/rt-polaritydata/rt-polarity.pos").read()
# neg_tweets_list = str(neg_file).split('\n')
# pos_tweets_list = str(pos_file).split('\n')
#  
# neg_cutoff = int(neg_tweets_list.__len__()*3/4)
# pos_cutoff = int(pos_tweets_list.__len__()*3/4)
#  
# neg_train = neg_tweets_list[:neg_cutoff]
# pos_train = pos_tweets_list[:neg_cutoff]
#  
#  
# # pos_feats_bigram = [bigram for tweet in pos_train for bigram in ngrams(word_tokenize(clean_word(tweet).lower()),2)]
# # neg_feats_bigram = [bigram for tweet in neg_train for bigram in ngrams(word_tokenize(clean_word(tweet).lower()),2)]
#  
#  
# neg_test = neg_tweets_list[neg_cutoff:]
# pos_test = pos_tweets_list[pos_cutoff:]
# tweet_data = {'neg_train':neg_train,'pos_train':pos_train,'neg_test':neg_test,'pos_test':pos_test}
#  
# print "single features classifier"
# single_classifier = evaluate_classifier(neg_train, pos_train, Bayes())
# single_classifier.save(fname=BASE_DIR+"/sentiment_analysis/pickle_files/rt_polarity_classifiers/single_classifier.dat")
# print find_accuracy(single_classifier)
#  
# # print "with non stem words"
# # neg_stem_train = stem_words(pos_feats)
# # pos_stem_train = stem_words(neg_feats)
# # single_stem_classifier = Bayes()
# # single_stem_classifier._train(single_stem_classifier.pools.setdefault('positive',single_stem_classifier.dataClass('positive')), pos_stem_train)
# # single_stem_classifier._train(single_stem_classifier.pools.setdefault('negative',single_stem_classifier.dataClass('negative')), neg_stem_train)
# # single_stem_classifier.save(fname=BASE_DIR+"/sentiment_analysis/pickle_files/rt_polarity_classifiers/single_stem_classifier.dat")
# # print find_stem_accuracy(single_stem_classifier)
#  
#  
# print "with non stop words"
# single_stop_classifier = evaluate_classifier(neg_train,pos_train,Bayes(tokenizer=non_stop_tokenizer()))
# single_stop_classifier.save(fname=BASE_DIR+"/sentiment_analysis/pickle_files/rt_polarity_classifiers/single_stop_classifier.dat")
# print find_accuracy(single_stop_classifier)
#  
#  
# # def best_word_feats(tweets):
# #     tweets_best = []
# #     for tweet in tweets:
# #         toknize_list = word_tokenize(clean_word(tweet).lower())
# # #         print tweet
# #         res = [word for word in toknize_list if word in bestwords]
# # #         print " ".join(res)
# #         if res.__len__()>0:
# #             tweets_best.append(" ".join(res))
# #     return tweets_best
#  
#  
#  
# # print 'neg_training'
# # neg_best_train = best_word_feats(neg_train)
# # print 'pos_training'
# # pos_best_train = best_word_feats(pos_train)
# single_best_classifier = evaluate_classifier(neg_train,pos_train,Bayes(tokenizer=best_tokenizer(best_words=get_best_words(pos_train, neg_train))))
# single_best_classifier.save(fname=BASE_DIR+"/sentiment_analysis/pickle_files/rt_polarity_classifiers/single_best_classifier.dat")
# print find_accuracy(single_best_classifier)
# #     classifier._train('negative',word_tokenize(tweet))
#  
# # print neg_tweets_list[0]
# # print pos_tweets_list[0]
# # def best_bigram_tokenize(tweet):
# #     tokens = [word for word in word_tokenize(clean_word(tweet)) if word in bestwords]
# #     bigrams_l = [bigram for bigram in ngrams(word_tokenize(clean_word(tweet)),2)]
# #     return tokens+bigrams_l
#  
#  
#  
# print "with bigram and best words"
# # neg_bi_train = [word for tweet in neg_best_train for word in tweet.split()]+neg_feats_bigram
# # pos_bi_train = [word for tweet in pos_best_train for word in tweet.split()]+pos_feats_bigram
# bigram_tokenizer = best_bigram_tokenizer(best_words=get_best_words(pos_train, neg_train),lower=True)
# single_bi_classifier = evaluate_classifier(neg_train,pos_train,Bayes(tokenizer=bigram_tokenizer))
# # single_bi_classifier._train(single_bi_classifier.pools.setdefault('positive',single_bi_classifier.dataClass('positive')), neg_bi_train)
# # single_bi_classifier._train(single_bi_classifier.pools.setdefault('negative',single_bi_classifier.dataClass('negative')), pos_bi_train)
# single_bi_classifier.save(fname=BASE_DIR+"/sentiment_analysis/pickle_files/rt_polarity_classifiers/single_bi_classifier.dat")
# print find_accuracy(single_bi_classifier)

