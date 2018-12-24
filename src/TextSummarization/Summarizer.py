# coding=UTF-8
from __future__ import division
import re
from TextSummarization.Nltk_Word import get_real_words,similar_word , similar_words
import operator
from nltk.tokenize import word_tokenize
 
class SummaryTool(object):
 
    # Naive method for splitting a text into sentences
    def split_content_to_sentences(self, content):
        content = content.replace("\n", ". ")
        return content.split(". ")
 
    # Naive method for splitting a text into paragraphs
    def split_content_to_paragraphs(self, content):
        return content.split("\n\n")
 
    # Caculate the intersection between 2 sentences
    def sentences_intersection(self, sent1, sent2):
 
        # split the sentence into words/tokens
        s1 = set(sent1.split(" "))
        s2 = set(sent2.split(" "))
#         print s1
#         print s2
        # If there is not intersection, just return 0
        if (len(s1) + len(s2)) == 0:
            return 0
#         print s1.intersection(s2)
        # We normalize the result by the average number of words
#         print len(s1.intersection(s2)) / ((len(s1) + len(s2)) / 2)
        return len(s1.intersection(s2)) / ((len(s1) + len(s2)) / 2)
 
    # Format a sentence - remove all non-alphbetic chars from the sentence
    # We'll use the formatted sentence as a key in our sentences dictionary
    def format_sentence(self, sentence):
        sentence = re.sub(r'\W+', '', sentence)
        return sentence
 
    # Convert the content into a dictionary <K, V>
    # k = The formatted sentence
    # V = The rank of the sentence
    def get_senteces_ranks(self, content):
 
        # Split the content into sentences
        sentences = self.split_content_to_sentences(content)
 
        # Calculate the intersection of every two sentences
        n = len(sentences)
        values = [[0 for x in xrange(n)] for x in xrange(n)]
        for i in range(0, n):
            for j in range(0, n):
                values[i][j] = self.sentences_intersection(sentences[i], sentences[j])
 
        # Build the sentences dictionary
        # The score of a sentences is the sum of all its intersection
        sentences_dic = {}
        for i in range(0, n):
            score = 0
            for j in range(0, n):
                if i == j:
                    continue
                score += values[i][j]
            sentences_dic[self.format_sentence(sentences[i])] = score
        
        return sentences_dic
 
    # Return the best sentence in a paragraph
    
    def get_senteces_ranks_keyword(self, content, keyword):
 
        # Split the content into sentences
        sentences = self.split_content_to_sentences(content)
 
        # Calculate the intersection of every two sentences
        n = len(sentences)
        values = [[0 for x in xrange(n)] for x in xrange(n)]
        for i in range(0, n):
            for j in range(0, n):
                values[i][j] = self.sentences_intersection(sentences[i], sentences[j])
 
        # Build the sentences dictionary
        # The score of a sentences is the sum of all its intersection
        similar = similar_words(keyword)
        print
        print similar
        print
        sentences_dic = {}
        for i in range(0, n):
            score = 0
            
            real_words = get_real_words(sentences[i])
            s_count = 0
            for w in real_words:
                s_count += similar.count(w)
            
            for j in range(0, n):
                if i == j:
                    continue
                score += values[i][j]
#             print score
#             print s_count
            score = score + s_count
#             print score
            sentences_dic[self.format_sentence(sentences[i])] = score
#             print score + (s_count/2)
#             print "---" 
        return sentences_dic
 
    # Return the best sentence in a paragraph
 
    def get_best_sentence(self, paragraph, sentences_dic,no_line_whole):
 
        # Split the paragraph into sentences
        
        sentences = self.split_content_to_sentences(paragraph)
 
        # Ignore short paragraphs
        if len(sentences) < 2:
            return ""
 
 
        # Get the best sentence according to the sentences dictionary
        best_sentence = []
        
        
        
        sentences_dic_sorted = sorted(sentences_dic.items(), key=operator.itemgetter(1),reverse=True)
       
        
#         ranked_list = sorted(sentences_dic, key=sentences_dic.__getitem__ ,reverse=True)
#         print ranked_list
#         max_value = 0
#         for s in sentences:
#             strip_s = self.format_sentence(s)
#             if strip_s:
#                 if sentences_dic[strip_s] > max_value:
#                     max_value = sentences_dic[strip_s]
#                     best_sentence = s 
        for s in sentences:
            strip_s = self.format_sentence(s)
#                 print strip_s
            if strip_s:
                for i in xrange(no_line_whole):
                    if sentences_dic[strip_s] == sentences_dic_sorted[i][1]:
                        best_sentence.append(s)
            
        
        return best_sentence
    
    def get_best_sentence_para(self,paragraph,paragraph_dic,no_line_para):
        
        paragraph_dic_sorted = sorted(paragraph_dic.items(), key=operator.itemgetter(1),reverse=True)
        
        sentences = self.split_content_to_sentences(paragraph)
 
        # Ignore short paragraphs
        if len(sentences) < 2:
            return ""
 
 
        # Get the best sentence according to the sentences dictionary
        best_sentence = []
 
        for s in sentences:
            strip_s = self.format_sentence(s)
#                 print strip_s
            if strip_s:
                for i in xrange(no_line_para):
                    if paragraph_dic[strip_s] == paragraph_dic_sorted[i][1]:
                        best_sentence.append(s)
        return best_sentence
        
        
    # Build the summary
    def get_summary(self, content,no_line_para,no_line_whole,keyword):
 
        # Split the content into paragraphs
        if keyword is not None:
            sentences_dic = self.get_senteces_ranks_keyword(content,keyword) 
#             print sorted(sentences_dic.items(), key=operator.itemgetter(1),reverse=True)
        else:
            sentences_dic = self.get_senteces_ranks(content)
#             print sorted(sentences_dic.items(), key=operator.itemgetter(1),reverse=True)
        paragraphs = self.split_content_to_paragraphs(content)
        # Add the title
        summary = []
#         summary.append(title.strip())
#         summary.append("")
#  
        # Add the best sentence from each paragraph
        for p in paragraphs:
            
            if keyword is not None:
                paragraph_dic = self.get_senteces_ranks_keyword(p,keyword) 
            else:
                paragraph_dic = self.get_senteces_ranks(p)
            
            sentence = self.get_best_sentence(p, sentences_dic,no_line_whole)
            Paragraphs = self.get_best_sentence_para(p,paragraph_dic,no_line_para)
            for s in sentence:
                if s:
                    summary.append(s.strip())
#             print "--j-----------------"        
            for p_line in Paragraphs:
                if p_line:
                    if not summary.__contains__(p_line.strip()):
                        summary.append(p_line.strip())
#                 print "-------------------"
        
        return ("\n").join(summary)
 
import operator 
from stream_tweets import stop_word_list,dictionary

def Summarizerr_int(data,no_line_whole,no_line_para,keyword):    
    print "i am in summarizer_int"
    st = SummaryTool()
    if (keyword!=None):
        summary = st.get_summary(data,no_line_para,no_line_whole,keyword)
        print "sumamry %s"%(summary)
    else:
        summary = st.get_summary(data,no_line_para,no_line_whole,None)
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

def RankTagger(data,no_tags):
    import tagger
    from tagger import Tagger,Stemmer
    import pickle
    
    import os
    from TextSummarization import settings
    
    path = os.path.join(settings.PROJECT_ROOT,'static/dict.pkl')
    print path
    
    weights = pickle.load(open(path, 'rb')) # or your own dictionary
    
    
#     file = open("data/dict.txt", "w")
#     file.write(pickle.dump(data1, file))
#     file.close()
    myreader = tagger.Reader() # or your own reader class
    mystemmer = tagger.Stemmer() # or your own stemmer class
    myrater = tagger.Rater(weights,0) # or your own... (you got the idea)
    mytagger = Tagger(myreader, mystemmer, myrater)
    best_tags = mytagger(data, no_tags)
    
    best_tags = [str(x.string.encode('utf-8')) for x in best_tags]
    print best_tags
    st = SummaryTool()
    
    no_of_lines = len(st.split_content_to_sentences(data))
#     print no_of_lines
    no_of_paragraphs = len(st.split_content_to_paragraphs(data))
    
    words = word_tokenize(data)
    total_words = words.__len__()
    
    
    sum_dict = {'tags':best_tags,'original_content':data,'total_words':total_words,'total_no_of_sen':no_of_lines,'no_of_para':no_of_paragraphs}
    return sum_dict

def RankTagger_t(data,no_tags):
    import tagger
    from tagger import Tagger,Stemmer
    import pickle
    
    import os
    from TextSummarization import settings
    
    path = os.path.join(settings.PROJECT_ROOT,'static/dict.pkl')
    print path
    
    weights = pickle.load(open(path, 'rb')) # or your own dictionary
    
    
#     file = open("data/dict.txt", "w")
#     file.write(pickle.dump(data1, file))
#     file.close()
    myreader = tagger.Reader() # or your own reader class
    mystemmer = tagger.Stemmer() # or your own stemmer class
    myrater = tagger.Rater(weights,0) # or your own... (you got the idea)
    mytagger = Tagger(myreader, mystemmer, myrater)
    best_tags = mytagger(data, no_tags)
    
    best_tags = [str(x.string.encode('utf-8')) for x in best_tags]
    print best_tags
    st = SummaryTool()
    
    
    words = word_tokenize(data)
    total_words = words.__len__()
    
    
    sum_dict = {'tags':best_tags,'total_words':total_words}
    return sum_dict
# if __name__ == '__main__':
    
