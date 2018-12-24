'''
Created on Dec 6, 2014

@author: madqasi
'''
from nltk.corpus import wordnet as wn
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def similar_word(string):
    syn_set = []
    s_list = []
    for i,j in enumerate(wn.synsets(string)):
        temp=[]
        temp.extend(j.lemma_names())
#         print temp
        
        temp.extend(list(l.lemma_names for l in j.hypernyms()))
        temp.extend(list(l.lemma_names for l in j.hyponyms()))
        
        
        
#         test = list(i.lemma_names() for i in j.hypernyms())
#         print
#         print "temp %s"%(temp)
#         
        syn_set = list(set(syn_set)|set(temp))
    
#     print "Synset %s"% (syn_set)
    syn_set = [x for x in syn_set if not str(x).startswith('<')]
#     print "Synset clean: %s"% (syn_set)
#     print "Synset clean: %s"% (syn_set.__len__())
    for s in syn_set:
        word = s.encode('ascii','ignore').replace('_',' ')
        if ' ' in word:
            word = word.split()
            s_list.extend(word)
        else:
            s_list.append(word)
    return list(set(s_list))

def similar_words(s_list):
    syno_list = []
    temp = []
    if ' ' in s_list:
        s_word = get_real_words(s_list)
#         print "Swords %s"%(s_word)
        for w in s_word:
            temp.extend(similar_word(w))
            syno_list.extend(temp)
        return list(set(syno_list))
    else:
        return similar_word(s_list)

def get_real_words(sentence):
    
    tokens = word_tokenize(sentence)
    stopset = set(stopwords.words('english'))
    w_list=[]
    for w in tokens: 
        if not w in stopset:
            w_list.append(w)
    return w_list
    
if __name__ == '__main__':     
    str = similar_words("Terror Seal Army")
    print "words %s"%(str)
    print "words len %s"%(str.__len__()) 
    