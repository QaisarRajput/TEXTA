"""
Django settings for TextSummarization project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import pymongo
import memcache
from reverend.thomas import Bayes
from TextSummarization.rt_polarity import non_stop_tokenizer,best_tokenizer,best_bigram_tokenizer,get_best_words
Mongo_Client = pymongo.MongoClient()
Memcahce_Client = memcache.Client(['127.0.0.1:11211'])
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=i#-3nla+arm=d51vy6_+s1e)u^o)d^lk!n8*v^n#2gm&+i=l*'



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    
)

from os.path import join
TEMPLATE_DIRS = (
    join(BASE_DIR,  'templates'),
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'TextSummarization'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'TextSummarization.urls'

WSGI_APPLICATION = 'TextSummarization.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
   os.path.join(os.path.dirname(__file__),'static/').replace('\\','/'),
   os.path.join(BASE_DIR, "static"),
    '/BTA/src/static/',
)



neg_file = open(BASE_DIR+"/data/rt-polarity.neg").read()
pos_file = open(BASE_DIR+"/data/rt-polarity.pos").read()
neg_tweets_list = str(neg_file).split('\n')
pos_tweets_list = str(pos_file).split('\n')

neg_cutoff = int(neg_tweets_list.__len__()*3/4)
pos_cutoff = int(pos_tweets_list.__len__()*3/4)

neg_train = neg_tweets_list[:neg_cutoff]
pos_train = pos_tweets_list[:neg_cutoff]


neg_test = neg_tweets_list[neg_cutoff:]
pos_test = pos_tweets_list[pos_cutoff:]
tweet_data = {'neg_train':neg_train,'pos_train':pos_train,'neg_test':neg_test,'pos_test':pos_test}



bestwords = get_best_words(pos_train, neg_train)
single_classifier = Bayes()
single_classifier.load(fname=BASE_DIR+"/data/rt_polarity_classifiers/single_classifier.dat")
non_stop_classifier = Bayes(tokenizer=non_stop_tokenizer())
non_stop_classifier.load(fname=BASE_DIR+"/data/rt_polarity_classifiers/single_stop_classifier.dat")
best_classifier = Bayes(tokenizer=best_tokenizer(best_words=bestwords))
best_classifier.load(fname=BASE_DIR+"/data/rt_polarity_classifiers/single_best_classifier.dat")
bigram_best_classifier = Bayes(tokenizer=best_bigram_tokenizer(best_words=bestwords))
bigram_best_classifier.load(fname=BASE_DIR+"/data/rt_polarity_classifiers/single_bi_classifier.dat")