#!/usr/bin/env python

# Created by Alessandro Presta
# @author: Qaisar Rajput


from __future__ import division

from tagger import Stemmer
from extras import SimpleReader

def build_dict(corpus, stopwords=None, measure='IDF'):
    '''
    @param corpus:    a list of documents, represented as lists of (stemmed)
                      words
    @param stopwords: the list of (stemmed) words that should have zero weight
    @param measure:   the measure used to compute the weights ('IDF'
                      i.e. 'inverse document frequency' or 'ICF' i.e.
                      'inverse collection frequency'; defaults to 'IDF')

    @returns: a dictionary of weights in the interval [0,1]
    '''

    import collections
    import math

    dictionary = {}

    if measure == 'ICF':
        words = [w for doc in corpus for w in doc]
        
        term_count = collections.Counter(words)
        total_count = len(words)
        scale = math.log(total_count)
    
        for w, cnt in term_count.iteritems():
            dictionary[w] = math.log(total_count / (cnt + 1)) / scale

    elif measure == 'IDF':
        corpus_size = len(corpus)
        scale = math.log(corpus_size)

        term_count = collections.defaultdict(int)

        for doc in corpus:
            words = set(doc)
            for w in words:
                term_count[w] += 1

        for w, cnt in term_count.iteritems():
            dictionary[w] = math.log(corpus_size / (cnt + 1)) / scale
            
    if stopwords:
        for w in stopwords:
            dictionary[w] = 0.0
    
    return dictionary


def build_dict_from_files(output_file, corpus_files, stopwords_file=None,
                          reader=SimpleReader(), stemmer=Stemmer(),
                          measure='IDF', verbose=False):
    '''
    @param output_file:    the name of the file where the dictionary should be
                           saved
    @param corpus_files:   a list of files with words to process
    @param stopwords_file: a file containing a list of stopwords
    @param reader:         the L{Reader} object to be used
    @param stemmer:        the L{Stemmer} object to be used
    @param measure:        the measure used to compute the weights ('IDF'
                           i.e. 'inverse document frequency' or 'ICF' i.e.
                           'inverse collection frequency'; defaults to 'IDF')
    @param verbose:        whether information on the progress should be
                           printed on screen
    '''

    import pickle

    if verbose: print 'Processing corpus...'
    corpus = []
    for filename in corpus_files:
        with open(filename, 'r') as doc:
            corpus.append(reader(doc.read()))
    corpus = [[w.stem for w in map(stemmer, doc)] for doc in corpus]

    stopwords = None
    if stopwords_file:
        if verbose: print 'Processing stopwords...'
        with open(stopwords_file, 'r') as sw:
            stopwords = reader(sw.read())
        stopwords = [w.stem for w in map(stemmer, stopwords)]

    if verbose: print 'Building dictionary... '
    dictionary = build_dict(corpus, stopwords, measure)
    with open(output_file, 'wb') as out:
        pickle.dump(dictionary, out, -1) 
    

if __name__ == '__main__':

    import getopt
    import sys
    
    try:
        options = getopt.getopt(sys.argv[1:], 'o:s:')
        output_file = options[0][0][1]
        stopwords_file = options[0][1][1]
        corpus = options[1]
    except:
        print __doc__
        exit(1)

    build_dict_from_files(output_file, corpus, stopwords_file, verbose=True)
    
               
