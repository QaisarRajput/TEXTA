from __future__ import division
import math
import os
from nltk import word_tokenize
from TextSummarization.settings import single_classifier,non_stop_classifier,best_classifier,bigram_best_classifier
from nltk.corpus import movie_reviews

def clean_word(dirty_word):
        clean_char_list = list()
        for char in dirty_word:
            if ord(char) <= 128:
                clean_char_list.append(char)
        return ''.join(clean_char_list)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

neg_file = open(BASE_DIR+"/data/negative-words.txt").read()
pos_file = open(BASE_DIR+"/data/positive-words.txt").read()
afinn_file = open(BASE_DIR+"/data/AFINN-111.txt").read()
neg_words = str(neg_file).split('\n')
pos_words = str(pos_file).split('\n')
afinn_words = str(afinn_file).split('\n')
afinn_dict = {}
for word in afinn_words:
    sp_word = word.split()
    v = sp_word.__len__()-1 
#     print sp_word[1]
    afinn_dict[sp_word[0]] = int(sp_word[v])
     
def get_simple_sentiment(tweet):
#     print neg_words
    tokenized_tweet = word_tokenize(clean_word(tweet))
    if tokenized_tweet.__len__()>0:
        total_words_count = tokenized_tweet.__len__()
        pos_words_count = 0
        neg_words_count = 0
        for word in tokenized_tweet:
            if word in pos_words:
                pos_words_count += 1
            if word in neg_words:
                neg_words_count += 1
#         print tweet
#         print pos_words_count
#         print neg_words_count
#         print total_words_count
        
        pos_polarity = pos_words_count/total_words_count
        neg_polarity = neg_words_count/total_words_count
        if neg_words_count == 0 and pos_words_count == 0:
            return {'frequency_sentiment':{'sentiment':'neutral','pos_words':pos_words_count,'neg_words':neg_words_count,'polarity_neg':neg_polarity,'polarity_pos':pos_polarity}}
        if neg_words_count >= pos_words_count:
            return {'frequency_sentiment':{'sentiment':'negative','pos_words':pos_words_count,'neg_words':neg_words_count,'polarity_neg':neg_polarity,'polarity_pos':pos_polarity}}
        if neg_words_count < pos_words_count:
            return {'frequency_sentiment':{'sentiment':'positive','pos_words':pos_words_count,'neg_words':neg_words_count,'polarity_neg':neg_polarity,'polarity_pos':pos_polarity}}

def get_afinn_sentiment(tweet):
#     print neg_words
    tokenized_tweet = word_tokenize(clean_word(tweet))
    if tokenized_tweet.__len__()>0:
        total_words_count = tokenized_tweet.__len__()
        pos_words_count = 0
        neg_words_count = 0
        for word in tokenized_tweet:
            if word in afinn_dict:
                if afinn_dict[word]>0:
                    pos_words_count += afinn_dict[word]
                else:
                    neg_words_count += (afinn_dict[word]*-1)
#             if word in pos_words:
#                 pos_words_count += 1
#             if word in neg_words:
#                 neg_words_count += 1
#         print tweet
#         print pos_words_count
#         print neg_words_count
#         print total_words_count
        
        pos_polarity = pos_words_count/total_words_count
        neg_polarity = neg_words_count/total_words_count
        if neg_words_count == 0 and pos_words_count == 0:
            return {'afinn_sentiment':{'sentiment':'neutral','pos_words':pos_words_count,'neg_words':neg_words_count,'polarity_neg':neg_polarity,'polarity_pos':pos_polarity}}
        if neg_words_count >= pos_words_count:
            return {'afinn_sentiment':{'sentiment':'negative','pos_words':pos_words_count,'neg_words':neg_words_count,'polarity_neg':neg_polarity,'polarity_pos':pos_polarity}}
        if neg_words_count < pos_words_count:
            return {'afinn_sentiment':{'sentiment':'positive','pos_words':pos_words_count,'neg_words':neg_words_count,'polarity_neg':neg_polarity,'polarity_pos':pos_polarity}}





def get_single_sentiment(tweet):
    tweet = tweet.lower()
    result = single_classifier.guess(tweet)
    if result.__len__()>1:
        neg_score = float(result[0][1])
        pos_score = float(result[1][1])+.20
        if neg_score >= pos_score:
            return {'nb_single_sentiment':{'sentiment':'negative','polarity_neg':neg_score,'polarity_pos':pos_score}}
        else:
            return {'nb_single_sentiment':{'sentiment':'positive','polarity_neg':neg_score,'polarity_pos':pos_score}}
    else:
        return {'nb_single_sentiment':{'sentiment':'neutral','polarity_neg':0,'polarity_pos':0}}

def get_non_stop_sentiment(tweet):
    tweet = tweet.lower()
    result = non_stop_classifier.guess(tweet)
    if result.__len__()>1:
        neg_score = result[0][1]
        pos_score = result[1][1]+.20
        if pos_score >= neg_score:
            return {'nb_non_stop_sentiment':{'sentiment':'positive','polarity_neg':neg_score,'polarity_pos':pos_score}}
        else:
            return {'nb_non_stop_sentiment':{'sentiment':'negative','polarity_neg':neg_score,'polarity_pos':pos_score}}
    else:
        return {'nb_non_stop_sentiment':{'sentiment':'neutral','polarity_neg':0,'polarity_pos':0}}
    
def get_best_sentiment(tweet):
    tweet = tweet.lower()
    result = best_classifier.guess(tweet)
    if result.__len__()>1:
        neg_score = result[0][1]
        pos_score = result[1][1]+.20
        if pos_score >= neg_score:
            return {'nb_best_sentiment':{'sentiment':'positive','polarity_neg':neg_score,'polarity_pos':pos_score}}
        else:
            return {'nb_best_sentiment':{'sentiment':'negative','polarity_neg':neg_score,'polarity_pos':pos_score}}
    else:
        return {'nb_best_sentiment':{'sentiment':'neutral','polarity_neg':0,'polarity_pos':0}}
    
def get_bigram_best_sentiment(tweet):
    tweet = tweet.lower()
    result = bigram_best_classifier.guess(tweet)
    if result.__len__()>1:
        neg_score = result[0][1]
        pos_score = result[1][1]+.20
        if pos_score >= neg_score:
            return {'nb_bigram_best_sentiment':{'sentiment':'positive','polarity_neg':neg_score,'polarity_pos':pos_score}}
        else:
            return {'nb_bigram_best_sentiment':{'sentiment':'negative','polarity_neg':neg_score,'polarity_pos':pos_score}}
    else:
        return {'nb_bigram_best_sentiment':{'sentiment':'neutral','polarity_neg':0,'polarity_pos':0}}



# neg_file = open(BASE_DIR+"/sentiment_analysis/data_files/rt-polaritydata/rt-polaritydata/rt-polarity.neg").read()
# pos_file = open(BASE_DIR+"/sentiment_analysis/data_files/rt-polaritydata/rt-polaritydata/rt-polarity.pos").read()
# neg_tweets = str(neg_file).split('\n')
# pos_tweets = str(pos_file).split('\n')
# 
# total_tweets_count = neg_tweets.__len__() + pos_tweets.__len__()
# pos_tweets_count = pos_tweets.__len__()
# neg_tweets_count = neg_tweets.__len__()
# correct_tweets_count = 0
# 
# for tweet in neg_tweets:
#     tokenized_tweet = word_tokenize(clean_word(tweet))
#     if tokenized_tweet.__len__()>0:
#         total_words_count = tokenized_tweet.__len__()
#         pos_words_count = 0
#         neg_words_count = 0
#         for word in tokenized_tweet:
#             if word in pos_words:
#                 pos_words_count += 1
#             if word in neg_words:
#                 neg_words_count += 1
#         pos_polarity = math.floor(pos_words_count/total_words_count)
#         neg_polarity = math.floor(neg_words_count/total_words_count)
#         if neg_words_count >= pos_words_count:
#             correct_tweets_count += 1
# 
# for tweet in pos_tweets:
#     tokenized_tweet = word_tokenize(clean_word(tweet))
#     if tokenized_tweet.__len__()>0:
#         total_words_count = tokenized_tweet.__len__()
#         pos_words_count = 0
#         neg_words_count = 0
#         for word in tokenized_tweet:
#             if word in pos_words:
#                 pos_words_count += 1
#             if word in neg_words:
#                 neg_words_count += 1
#         pos_polarity = math.floor(pos_words_count/total_words_count)
#         neg_polarity = math.floor(neg_words_count/total_words_count)
#         if pos_words_count >= neg_words_count:
#             correct_tweets_count += 1
#         
# print "tweets accuracy: ",correct_tweets_count/total_tweets_count
# 
# negids = movie_reviews.fileids('neg')
# posids = movie_reviews.fileids('pos')
# neg_reviews = [movie_reviews.raw(fileids=[f]) for f in negids]
# pos_reviews = [movie_reviews.raw(fileids=[f]) for f in posids]
# # print movie_reviews
# total_reviews_count = neg_reviews.__len__() + pos_reviews.__len__()
# pos_reviews_count = pos_reviews.__len__()
# neg_reviews_count = neg_reviews.__len__()
# print neg_reviews_count
# print pos_reviews_count
# correct_reviews_count = 0
# counter = 0
# count = 1
# for review in neg_reviews:
#     tokenized_review = word_tokenize(clean_word(review))
#     if tokenized_review.__len__()>0:
#         total_words_count = tokenized_review.__len__()
#         pos_words_count = 0
#         neg_words_count = 0
#         for word in tokenized_review:
#             if word in pos_words:
#                 pos_words_count += 1
#             if word in neg_words:
#                 neg_words_count += 1
#         pos_polarity = math.floor(pos_words_count/total_words_count)
#         neg_polarity = math.floor(neg_words_count/total_words_count)
#         if neg_words_count >= pos_words_count:
#             correct_reviews_count += 1
#     counter += 1
#     if counter>=count*10:
#         print 'neg count:',counter
#         count += 1
# counter = 0
# count = 1        
# for review in pos_reviews:
#     tokenized_review = word_tokenize(clean_word(review))
#     if tokenized_review.__len__()>0:
#         total_words_count = tokenized_review.__len__()
#         pos_words_count = 0
#         neg_words_count = 0
#         for word in tokenized_review:
#             if word in pos_words:
#                 pos_words_count += 1
#             if word in neg_words:
#                 neg_words_count += 1
#         pos_polarity = math.floor(pos_words_count/total_words_count)
#         neg_polarity = math.floor(neg_words_count/total_words_count)
#         if pos_words_count >= neg_words_count:
#             correct_reviews_count += 1
#     counter += 1
#     if counter>=count*10:
#         print 'pos count:',counter
#         count += 1
# print "reviews accuracy: ",correct_reviews_count/total_reviews_count   