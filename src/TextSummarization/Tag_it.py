'''
Created on Dec 4, 2014

@author: madqasi
'''
import pprint, pickle
from debian.changelog import change
from _ast import keyword


def Convert_pickle_to_csv(file_name,output_file):
    data1 = pickle.load(open(file_name, 'rb'))
    import csv
    w = csv.writer(open(output_file, "w"))
    for key, val in data1.items():
        try:
            w.writerow([key, val])
        except:
            pass


def Summarizerr_old(file_name,no_tags,no_line_whole,no_line_para,keyword=None):    
    import tagger
    from tagger import Tagger,Stemmer
    import pickle
    
    data = file_name
    
    import os
    from TextSummarization import settings
    
    path = os.path.join(settings.PROJECT_ROOT,'static/dict.pkl')
    print path
    
    weights = pickle.load(open(path, 'rb')) # or your own dictionary
    
    
#     file = open("data/dict.txt", "w")
#     file.write(pickle.dump(data1, file))
#     file.close()
    print no_tags
    myreader = tagger.Reader() # or your own reader class
    mystemmer = tagger.Stemmer() # or your own stemmer class
    myrater = tagger.Rater(weights,3) # or your own... (you got the idea)
    mytagger = Tagger(myreader, mystemmer, myrater)
    best_tags = mytagger(data, no_tags)
    
    print best_tags
    print "\n"
     
    from Summarizer import SummaryTool
    
    # Create a SummaryTool object
    st = SummaryTool()
    
         
    summary = 'Tags :'
  
    for i in best_tags:
        summary += str(i).title().replace("'"," ")
    summary += '\n\n'
    
    summary += "Summary :\n\n"
    summary += st.get_summary(data,no_line_para,no_line_whole,keyword)
 
    # Print the summary
    ratio = 100*(float(len(summary)) / len(data))

    summary += "\n\n"
    summary +="Original Length :"
    summary +=str(len(data))
    summary +="\n"
    summary +="Summary Length :"
    summary +=str(len(summary))
    summary +="\n"
    summary +="Summary Ratio :"
    summary +=str(ratio)
    summary +="%"
    
    print ""
    print "Original Length %s" % len(data)
    print "Summary Length %s" % len(summary)
    print "Summary Ratio: %s" % ratio ,'%'
    
    return summary
    
#     # Print the ratio between the summary length and the original length
    
    
if __name__ == '__main__':
    
    '''
        Summarizerr (File, Tags_Count, Sentences_whole, Sentences_per_para, Keyword ) 
        
        @param File:                File Path
                                    
        @param Tags_Count:          Tags count on the file
                                    
        @param: Sentences_whole     No of sentences to summarize on the basis of whole file
        
        @param Sentences_per_para   No of sentences to summarize per paragraph
        
        @param Keyword:             Search keywords or sentence (Optional)
    '''
#     Summarizerr('tests/bbc1.txt', 10, 5, 2,"war pakistan terrorist")
# from tagger import Reader,Stemmer,Rater
# myreader = Reader()
# 
# with open ('tests/bbc1.txt', "r") as myfile:
#             data = myfile.read()
# 
# 
# print myreader(data)
# print "\n\n\n"


