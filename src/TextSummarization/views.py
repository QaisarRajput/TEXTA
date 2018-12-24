from django.shortcuts import render_to_response,render
from django.http import HttpResponseRedirect,HttpResponse
# from django.contrib import auth
# from django.core.context_processors import csrf, request
from django import forms 
from django.db import models
# from django.core.urlresolvers import reverse
from django.template import RequestContext
import simplejson
from TextSummarization import stream_tweets
import multiprocessing as mp
from TextSummarization.lexicon_tech import get_simple_sentiment
import time
from TextSummarization.lexicon_tech import get_single_sentiment,get_non_stop_sentiment,get_best_sentiment,get_bigram_best_sentiment,\
    get_afinn_sentiment
from TextSummarization import Nltk_Word
from Summarizer_R import get_summary,get_top_tweets
from Summarizer import Summarizerr_int,RankTagger ,RankTagger_t
from TopicExtraction import Noun_Phrase,Noun_Phrase_t
from k_means_clustering import get_clusters_file,get_clusters_tweets
from TextSummarization.settings import Mongo_Client,Memcahce_Client
import datetime
from migrate.versioning.api import source


db = Mongo_Client["Text_Analysis"]
col = db["query"]

class UplaodFile(forms.Form):
    name = forms.CharField(max_length=100)
    docfile = forms.FileField(help_text='make sure format of file is (.txt)')
class TwitterSourceAdd(forms.Form):
    source = forms.CharField(max_length=100)
    hashtags = forms.CharField(max_length=300)

class Document(models.Model):
    docfile = models.FileField(upload_to='docs/%Y_%m_%d/')
    
class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='make sure format of file is (.txt)'
    )
    no_tags = forms.IntegerField(label='No of Tags')
    line_para = forms.IntegerField(label='Lines per Paragraph')
    line_whole = forms.IntegerField(label='Lines per File')
    Search_string = forms.CharField(label='Search String',max_length=100)
    textarea = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter the Text Here','class':'textbox','cols':'74','rows':'15'}))

class ClusterForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='make sure format of file is (.txt)'
    )
    no_cluster = forms.IntegerField(label='No of Clusters')
    textarea = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter the Text Here','class':'textbox','cols':'74','rows':'15'}))


def uploaded_file(f):
    return f.read()

def tagger_file(query_name,no_tags,algo):
    today = datetime.date.today()
    start_time= time.time()
    
    data = db['tweet_data'].find_one({'query_name':query_name},{'tweet':1})["tweet"]
#     print "keywords %s" %(keywords)

    tags_list = RankTagger(data, no_tags)

    print tags_list    
        
    tags_list['source'] = query_name
    tags_list['isFile'] = True
    tags_list['algo'] = algo
    tags_list['no_tags'] = no_tags
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    tags_list['date_time']=str(today)
    tags_list['time_elapsed']=endtime
    
    db['topic'].insert(tags_list)

def tagger_file_t(query_name,no_tags,algo):
    today = datetime.date.today()
    start_time= time.time()
    
    data = db['tweet_data'].find({'query_name':query_name},{'content_title':1})
    data = [d["content_title"] for d in data]
    no_tweet = data.__len__()
    data = ' '.join(data)
#     print "keywords %s" %(keywords)
    
    tags_list = RankTagger_t(data, no_tags)
    
        
        
    tags_list['source'] = query_name
    tags_list['isFile'] = False
    tags_list['algo'] = algo
    tags_list['no_tags'] = no_tags
    tags_list['no_tweet'] = no_tweet
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    tags_list['date_time']=str(today)
    tags_list['time_elapsed']=endtime
    
    db['topic'].insert(tags_list)


def Tf_Ranker(request):
    # Handle file upload
    print stream_tweets.get_full_sources()
    docs = db['topic'].find({'algo':"tf_ranker"},{'source':1,'topic_words':1,'date_time':1,'no_tags':1,'time_elapsed':1,'isFile':1})
    sum_sources = []
    sources_names = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        sources_names.append(doc['source'])
        
    return render_to_response(
        'ranker.html',
        {'sources':stream_tweets.get_full_sources(f_s=sources_names),
         'processed_sources':sum_sources},
        context_instance=RequestContext(request)
    )

def Add_Tf_Ranker(request):
    try:
        if request.method == 'POST':
            
            
            no_tags = int(request.POST.get('no_tag'))
            query_name = request.POST.get('source')
            print no_tags
            print query_name
            if db['query'].find_one({'query_name':query_name})['isFile'] == True:
                print "i am in file"
                
                mp.Process(target=tagger_file,args=(query_name,no_tags,"tf_ranker")).start()
            else:
                print "i am in not file"
                # for tweets
                mp.Process(target=tagger_file_t,args=(query_name,no_tags,"tf_ranker")).start()
                
            return HttpResponseRedirect('/Tf_Ranker')
                                
            
    except Exception,e:
        return HttpResponseRedirect('/Tf_Ranker')
        
    return render_to_response(
        'ranker.html',
        {'sources':stream_tweets.get_full_sources()},
        context_instance=RequestContext(request)
    )

def Tf_Ranker_source(request):
    source = request.POST['source_name']
    sum_source = db['topic'].find_one({'source':source,'algo':'tf_ranker'})
    sum_source['_id'] = str(sum_source['_id']) 
    return HttpResponse(simplejson.dumps(sum_source), content_type='application/javascript')
def Tf_Ranker_T_source(request):
    source = str(request.POST['source_name'])
    sum_source = db['topic'].find_one({'source':source,'algo':'tf_ranker'})
    sum_source['_id'] = str(sum_source['_id'])
    topic_source = sum_source 
    docs = db["tweet_data"].find({'query_name':source},{'content_title':1,'user_name':1})
    Memcahce_Client.flush_all()
    m_docs = []
    counter = 0
    pg_count = 0
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        if counter == 16:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
            counter = 0
            m_docs = []
        m_docs.append(doc)
        counter += 1
     
    if m_docs.__len__()>0:
        pg_count += 1
        Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
    Memcahce_Client.set(key="source",val=source)
    Memcahce_Client.set(key="current_page",val=1)
    Memcahce_Client.set(key="page_limit",val=pg_count)
    response_dict = {"tweets":Memcahce_Client.get(source+"_1"),'topic':topic_source}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')


def noun_phrase_file(query_name,no_tags,algo="noun_phrase"):
    today = datetime.date.today()
    start_time= time.time()
    
    data = db['tweet_data'].find_one({'query_name':query_name},{'tweet':1})["tweet"]
#     print "keywords %s" %(keywords)
    
    tags_list = Noun_Phrase(data, no_tags)
    
    print tags_list    
        
    tags_list['source'] = query_name
    tags_list['isFile'] = True
    tags_list['algo'] = algo
    tags_list['no_tags'] = no_tags
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    tags_list['date_time']=str(today)
    tags_list['time_elapsed']=endtime
    
    db['topic'].insert(tags_list)

def noun_phrase_file_t(query_name,no_tags,algo="noun_phrase"):
    try:
        today = datetime.date.today()
        start_time= time.time()
        
        data = db['tweet_data'].find({'query_name':query_name},{'content_title':1})
        data = [d["content_title"] for d in data]
        no_tweet = data.__len__()
        data = ' '.join(data)
    #     print "keywords %s" %(keywords)
        print data
        
        tags_list = Noun_Phrase_t(data, no_tags)
        
        print tags_list    
            
        tags_list['source'] = query_name
        tags_list['isFile'] = False
        tags_list['algo'] = algo
        tags_list['no_tags'] = no_tags
        tags_list['no_tweet'] = no_tweet
        seconds_elapsed = time.time() - start_time
        endtime = str(datetime.timedelta(seconds=seconds_elapsed))
        tags_list['date_time']=str(today)
        tags_list['time_elapsed']=endtime
        
        db['topic'].insert(tags_list)
    except Exception,e:
        print e
        

def Noun_phrase(request):
    # Handle file upload
    print stream_tweets.get_full_sources()
    docs = db['topic'].find({'algo':"noun_phrase"},{'source':1,'topic_words':1,'date_time':1,'no_tags':1,'time_elapsed':1,'isFile':1})
    sum_sources = []
    sources_names = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        sources_names.append(doc['source'])
        
    return render_to_response(
        'noun_phrase.html',
        {'sources':stream_tweets.get_full_sources(f_s=sources_names),
         'processed_sources':sum_sources},
        context_instance=RequestContext(request)
    )

def Add_Noun_phrase(request):
    try:
        if request.method == 'POST':
            
            
            no_tags = int(request.POST.get('no_tag'))
            query_name = request.POST.get('source')
            print no_tags
            print query_name
            if db['query'].find_one({'query_name':query_name})['isFile'] == True:
                print "i am in file"
                
                mp.Process(target=noun_phrase_file,args=(query_name,no_tags,)).start()
            else:
                print "i am in not file"
                # for tweets
                mp.Process(target=noun_phrase_file_t,args=(query_name,no_tags,)).start()
                
            return HttpResponseRedirect('/Noun_phrase')
                                
            
    except Exception,e:
        return HttpResponseRedirect('/Noun_phrase')
        
    return render_to_response(
        'noun_phrase.html',
        {'sources':stream_tweets.get_full_sources()},
        context_instance=RequestContext(request)
    )

def Noun_phrase_source(request):
    source = request.POST['source_name']
    sum_source = db['topic'].find_one({'source':source,'algo':'noun_phrase'})
    sum_source['_id'] = str(sum_source['_id']) 
    return HttpResponse(simplejson.dumps(sum_source), content_type='application/javascript')

def Noun_phrase_T_source(request):
    source = str(request.POST['source_name'])
    sum_source = db['topic'].find_one({'source':source,'algo':'noun_phrase'})
    sum_source['_id'] = str(sum_source['_id'])
    topic_source = sum_source 
    docs = db["tweet_data"].find({'query_name':source},{'content_title':1,'user_name':1})
    Memcahce_Client.flush_all()
    m_docs = []
    counter = 0
    pg_count = 0
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        if counter == 16:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
            counter = 0
            m_docs = []
        m_docs.append(doc)
        counter += 1
     
    if m_docs.__len__()>0:
        pg_count += 1
        Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
    Memcahce_Client.set(key="source",val=source)
    Memcahce_Client.set(key="current_page",val=1)
    Memcahce_Client.set(key="page_limit",val=pg_count)
    response_dict = {"tweets":Memcahce_Client.get(source+"_1"),'topic':topic_source}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')




def summary_intersection_file(query_name,line_whole,line_para,keywords):
    today = datetime.date.today()
    start_time= time.time()
    keys_u = []
    keys_n = []
    
    data = db['tweet_data'].find_one({'query_name':query_name},{'tweet':1})["tweet"]
#     print "keywords %s" %(keywords)
    if(keywords!=None):
        summary_dict = Summarizerr_int(data, no_line_whole=line_whole, no_line_para=line_para,keyword=keywords)
        keys_u = keywords.split()
        keys_n = Nltk_Word.similar_words(keywords)
        algo = "intersection_t"
    else:
        summary_dict = Summarizerr_int(data, no_line_whole=line_whole, no_line_para=line_para,keyword=None)
        algo = "intersection"
    summary_dict['source'] = query_name
    summary_dict['isFile'] = True
    summary_dict['algo'] = algo
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    summary_dict['date_time']=str(today)
    summary_dict['time_elapsed']=endtime
    summary_dict['keys_u']= keys_u
    summary_dict['keys_n']= keys_n
    print summary_dict
    db['summary'].insert(summary_dict)
    
def intersection(request):
    # Handle file upload
    print stream_tweets.get_full_sources()
    docs = db['summary'].find({'algo':"intersection"},{'source':1,'total_words':1,'summary_words':1,'summary_rate':1,'date_time':1})
    sum_sources = []
    sources_names = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        sources_names.append(doc['source'])
        
    return render_to_response(
        'intersection.html',
        {'sources':stream_tweets.get_full_sources(f_s=sources_names),
         'processed_sources':sum_sources},
        context_instance=RequestContext(request)
    )

def Add_Intersection(request):
    try:
        if request.method == 'POST':
            
            line_para = int(request.POST.get('no_par'))
            line_whole = int(request.POST.get('no_lines'))
            query_name = request.POST.get('source')
            print line_para
            print line_whole
            print query_name
            if db['query'].find_one({'query_name':query_name})['isFile'] == True:
                print "i am in file"
                mp.Process(target=summary_intersection_file,args=(query_name,line_whole,line_para,None)).start()
            else:
                print "i am in not file"
                # for tweets
                pass
            return HttpResponseRedirect('/Intersection')
                                
            
    except Exception,e:
        return HttpResponseRedirect('/Intersection')
   # Load documents for the list page
    

    # Render list page with the documents and the form
    
    return render_to_response(
        'intersection.html',
        {'sources':stream_tweets.get_full_sources()},
        context_instance=RequestContext(request)
    )

def intersection_source(request):
    source = request.POST['source_name']
    sum_source = db['summary'].find_one({'source':source,'algo':'intersection'})
    sum_source['_id'] = str(sum_source['_id'])
    sum_source['word_cloud'] = sum_source['word_cloud'][:100] 
    return HttpResponse(simplejson.dumps(sum_source), content_type='application/javascript')

def intersection_t(request):
    # Handle file upload
    print stream_tweets.get_full_sources()
    docs = db['summary'].find({'algo':"intersection_t"},{'source':1,'total_words':1,'summary_words':1,'summary_rate':1,'date_time':1})
    sum_sources = []
    sources_names = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        sources_names.append(doc['source'])
        
    return render_to_response(
        'intersection_t.html',
        {'sources':stream_tweets.get_full_sources(f_s=sources_names),
         'processed_sources':sum_sources},
        context_instance=RequestContext(request)
    )

def Add_Intersection_t(request):
    try:
        if request.method == 'POST':
            
            line_para = int(request.POST.get('no_par'))
            line_whole = int(request.POST.get('no_lines'))
            query_name = request.POST.get('source')
            keywords = request.POST.get('keyword')
            print line_para
            print line_whole
            print query_name
            print keywords
            if db['query'].find_one({'query_name':query_name})['isFile'] == True:
                print "i am in file"
                mp.Process(target=summary_intersection_file,args=(query_name,line_whole,line_para,keywords)).start()
            else:
                print "i am in not file"
                # for tweets
                pass
            return HttpResponseRedirect('/Intersection_T')
                                
            
    except Exception,e:
        return HttpResponseRedirect('/Intersection_T')
   # Load documents for the list page
    

    # Render list page with the documents and the form
    
    return render_to_response(
        'intersection_t.html',
        {'sources':stream_tweets.get_full_sources()},
        context_instance=RequestContext(request)
    )

def intersection_source_t(request):
    source = request.POST['source_name']
    sum_source = db['summary'].find_one({'source':source,'algo':'intersection_t'})
    sum_source['_id'] = str(sum_source['_id'])
    sum_source['word_cloud'] = sum_source['word_cloud'][:100] 
    return HttpResponse(simplejson.dumps(sum_source), content_type='application/javascript')



def summary_cosine_file(query_name,line_whole):
    today = datetime.date.today()
    start_time= time.time()
    data = db['tweet_data'].find_one({'query_name':query_name},{'tweet':1})["tweet"]
    summary_dict = get_summary(data, line_whole)
    summary_dict['source'] = query_name
    summary_dict['isFile'] = True
    summary_dict['algo'] = "cosine_similarity"
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    summary_dict['date_time']=str(today)
    summary_dict['time_elapsed']=endtime
    print summary_dict
    db['summary'].insert(summary_dict)

def summary_cosine_tweets(query_name,line_whole):
    today = datetime.date.today()
    start_time= time.time()
    docs = db['tweet_data'].find({'query_name':query_name},{'content_title':1,'user_name':1})
    tweets = []
    users = []
    for doc in docs:
        tweets.append(doc['content_title'])
        users.append(doc['user_name'])
#     data = [doc['content_title'] for doc in docs]
    data = "\n".join(tweets)
    summary_dict = get_summary(data, line_whole)
    print 'top tweets start'
    top_tweets = get_top_tweets(tweets, 200)
    top_tweets_and_username = [{'user_name':users[tweets.index(tweet)],'tweet':tweet} for tweet in top_tweets]
    summary_dict['source'] = query_name
    summary_dict['isFile'] = True
    summary_dict['algo'] = "cosine_similarity"
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    summary_dict['date_time']=str(today)
    summary_dict['top_tweets'] = top_tweets_and_username
    summary_dict['time_elapsed']=endtime
    print summary_dict
    db['summary'].insert(summary_dict)


def cosine_similarity(request):
    # Handle file upload
    print stream_tweets.get_full_sources()
    docs = db['summary'].find({'algo':"cosine_similarity"},{'source':1,'total_words':1,'summary_words':1,'summary_rate':1,'date_time':1})
    sum_sources = []
    sources_names = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        sources_names.append(doc['source'])
        
    return render_to_response(
        'cosine_similarity.html',
        {'sources':stream_tweets.get_full_sources(f_s=sources_names),
         'processed_sources':sum_sources},
        context_instance=RequestContext(request)
    )

def Add_Cosine(request):
    try:
        if request.method == 'POST':
            
#             line_para = int(request.POST.get('no_par'))
            line_whole = int(request.POST.get('no_lines'))
            query_name = request.POST.get('source')
#             print line_para
            print line_whole
            print query_name
            if db['query'].find_one({'query_name':query_name})['isFile'] == True:
                print "i am in file"
                mp.Process(target=summary_cosine_file,args=(query_name,line_whole,)).start()
            else:
                print "i am in not file"
                mp.Process(target=summary_cosine_tweets,args=(query_name,line_whole,)).start()
                # for tweets
            return HttpResponseRedirect('/cosine_similarity')
                                
            
    except Exception,e:
        return HttpResponseRedirect('/cosine_similarity')
    # Load documents for the list page
    

    # Render list page with the documents and the form
    
    return render_to_response(
        'cosine_similarity.html',
        {'sources':stream_tweets.get_full_sources()},
        context_instance=RequestContext(request)
    )

def cosine_source(request):
    source = request.POST['source_name']
    sum_source = db['summary'].find_one({'source':source,'algo':'cosine_similarity'})
    sum_source['_id'] = str(sum_source['_id'])
    sum_source['word_cloud'] = sum_source['word_cloud'][:100] 
    return HttpResponse(simplejson.dumps(sum_source), content_type='application/javascript')

# def clustering(request):
#     # Handle file upload
#     db = Mongo_Client["clusters"]   
#     col = db['n_clusters']
#     clusters =''
#     text =''
#     try:
#         if request.method == 'POST':
#         
#             form = ClusterForm(request.POST, request.FILES)
#             
#             print "here"
#             print request.FILES['docfile']
#             newdoc = Document(docfile=request.FILES['docfile'])
#             text = uploaded_file(request.FILES['docfile'])
#     #         print text  
#             n_clusters = request.POST.get('no_cluster')
#             clusters = get_clusters(text.split('\n'), int(n_clusters))
#             docs = col.find({},{'name':1})
#             docs = [doc['name'] for doc in docs]
#             print clusters
#             
#             # Redirect to the document list after POST
#             return render_to_response('clustering.html',{'form': form, "clusters":docs,"file":text},context_instance=RequestContext(request))
#                                           
#         else:
#             form = ClusterForm() # A empty, unbound form
#     except Exception,e:
#             print e
#             return render_to_response('clustering.html',{'form': form, "clusters":clusters,"file":"Please fill all the input boxes"},context_instance=RequestContext(request))
#    # Load documents for the list page
#     
# 
#     # Render list page with the documents and the form
#     return render_to_response(
#         'clustering.html',
#         {'form': form,"clusters":clusters,"file":text},
#         context_instance=RequestContext(request)
#     )    
# 
# def cluster_docs(request,cluster_name):
#     print cluster_name
#     doc = col.find_one({"name":cluster_name})
#     
#     return render_to_response(
#         'cluster_panel.html',
#         {"documents":doc["documents"],"cluster_name":cluster_name},
#         context_instance=RequestContext(request)
#     )    

def index(request):
    return render_to_response(
        'base.html',
        {},
        context_instance=RequestContext(request)
    )
    
def Twitter(request):
    fileform = UplaodFile()
    twitterform = TwitterSourceAdd()
    all_sources = stream_tweets.get_full_sources()
    return render(request,
        'Twitter.html',
        {fileform:"fileform",twitterform:"twitterform","all_sources":all_sources}        
    )
def Load_File(request):
    source = str(request.POST['source_name'])
    docs = db["tweet_data"].find({'query_name':source,"isFile":True},{'tweet':1})
    docx = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        docx.append(doc)
    response_dict = {"files":docx}
    print docx
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')
def Load_Tweets(request):
    source = str(request.POST['source_name'])
    docs = db["tweet_data"].find({'query_name':source},{'content_title':1,'user_name':1})
    Memcahce_Client.flush_all()
    m_docs = []
    counter = 0
    pg_count = 0
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        if counter == 16:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
            counter = 0
            m_docs = []
        m_docs.append(doc)
        counter += 1
    
    if m_docs.__len__()>0:
        pg_count += 1
        Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
    Memcahce_Client.set(key="source",val=source)
    Memcahce_Client.set(key="current_page",val=1)
    Memcahce_Client.set(key="page_limit",val=pg_count)
    response_dict = {"tweets":Memcahce_Client.get(source+"_1")}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')

def Load_More(request):
    source = Memcahce_Client.get("source")
    Memcahce_Client.incr("current_page")
    pg_num = Memcahce_Client.get("current_page")
    
    print pg_num
    print Memcahce_Client.get("page_limit")
    if pg_num <= Memcahce_Client.get("page_limit"):
        response_dict = {"tweets":Memcahce_Client.get(source+"_"+str(pg_num)),'bool':True}
    else:
        response_dict = {'bool':False}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')    

def k_means(request):
    docs = db['cluster'].find({},{'source':1,'no_of_clusters':1,'time_elapsed':1,'date_time':1,'isFile':1})
    processed_sources = []
    p_s_names = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        processed_sources.append(doc)
        p_s_names.append(doc['source'])
    return render(request,
        'k-means.html',
        {'sources':stream_tweets.get_full_sources(f_s=p_s_names),'processed_sources':processed_sources}
        
    )
    
def Add_Kmeans(request):
    try:
        if request.method == 'POST':
            
            source = str(request.POST.get('source'))
            no_cluster = int(request.POST.get('no_cluster'))
            b_file = db['query'].find_one({'query_name':source})['isFile']
            print source
            print no_cluster
#             print text
            if b_file == True:
                docs = db['tweet_data'].find({'query_name':source,'isFile':True},{'tweet':1})
                docs = [doc['tweet'] for doc in docs]
                docs = "\n\n".join(docs)
                mp.Process(target=get_clusters_file,args=(source,docs,no_cluster,)).start()
                print 'i am in file cluster'
            else:
                docs = db['tweet_data'].find({'query_name':source},{'content_title':1})
                docs = [doc for doc in docs]
                mp.Process(target=get_clusters_tweets,args=(source,docs,no_cluster,)).start()
            return HttpResponseRedirect('/K-means')                             
            
    except Exception,e:
            print e
            return HttpResponseRedirect('/K-means')
    return HttpResponseRedirect('/K-means')

def k_means_load(request):
    source = str(request.POST['source'])
    docs = db["cluster"].find({'source':source},{"source":1,"cluster_names":1,'total_tweets':1,'total_words':1,'date_time':1,'time_elapsed':1,'no_of_clusters':1,'isFile':1})
    docx = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        docx.append(doc)
    response_dict = {"files":docx}
    print docx
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')

def k_means_load_f(request):
    source = str(request.POST['source'])
    cluster_id = str(request.POST['cluster_id'])
    print source
    print cluster_id
    cluster = db['cluster'].find_one({'source':source,'isFile':True},{'clusters':1})['clusters'][cluster_id]
#     sum_source['clusters'] = str(sum_source['clusters'])
#     topic_source = sum_source 
#     docs = db["tweet_data"].find({'query_name':source},{'content_title':1,'user_name':1})
#     Memcahce_Client.flush_all()
#     m_docs = []
#     counter = 0
#     pg_count = 0
#     for doc in docs:
#         doc["_id"] = str(doc["_id"])
#         if counter == 16:
#             pg_count += 1
#             Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
#             counter = 0
#             m_docs = []
#         m_docs.append(doc)
#         counter += 1
#      
#     if m_docs.__len__()>0:
#         pg_count += 1
#         Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
#     Memcahce_Client.set(key="source",val=source)
#     Memcahce_Client.set(key="current_page",val=1)
#     Memcahce_Client.set(key="page_limit",val=pg_count)
#     response_dict = {"tweets":Memcahce_Client.get(source+"_1"),'topic':topic_source}
    return HttpResponse(simplejson.dumps({'cluster':cluster}), content_type='application/javascript')

    
def k_means_load_t(request):
    source = str(request.POST['source'])
    cluster_id = str(request.POST['cluster_id'])
    print source
    print cluster_id
    t_ids = db['cluster'].find_one({'source':source,'isFile':False},{'clusters':1})['clusters'][cluster_id]
#     sum_source['_id'] = str(sum_source['_id'])
    
#     topic_source = sum_source 
    docs = db["tweet_data"].find({'_id':{'$in':t_ids}},{'content_title':1,'user_name':1})
    Memcahce_Client.flush_all()
    m_docs = []
    counter = 0
    pg_count = 0
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        if counter == 16:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
            counter = 0
            m_docs = []
        m_docs.append(doc)
        counter += 1
     
    if m_docs.__len__()>0:
        pg_count += 1
        Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
    Memcahce_Client.set(key="source",val=source)
    Memcahce_Client.set(key="current_page",val=1)
    Memcahce_Client.set(key="page_limit",val=pg_count)
    response_dict = {"tweets":Memcahce_Client.get(source+"_1")}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')




from stream_tweets import word_tokenize,dictionary,unigram_tagger,stop_word_list,clean_word   
def upload_file(request):
    try:
        if request.method == 'POST':
            
            form = UplaodFile(request.POST, request.FILES)
            db = Mongo_Client["Text_Analysis"]
            col = db["query"]
            print "here"
            print request.FILES['docfile']
            newdoc = Document(docfile=request.FILES['docfile'])
            text = str(uploaded_file(request.FILES['docfile']))
            print text
            name = str(request.POST.get('name'))
            today = datetime.date.today()
            print name
#             print text
            if col.find({"query_name":name,"isFile":True}).count()==0:
                print "i am here"
                print today
                try:
                    col.insert({"query_name":name,"isFile":True,"tweet_count":1,"date_time":str(today),'processed':True})
                except Exception,ex:
                    print Exception
                    print ex
            else:
                col.update({"query_name":name,"isFile":True},{"$inc":{"tweet_count":1}})
            text1 = clean_word(text).replace("\x80","")
            row = {"query_name":name,"isFile":True,"tweet":str(text)}
            row['original_word_list_low'] = word_tokenize(text1.lower())
            row['total_words'] = len(row['original_word_list_low'])
            row['real_word_list_low'] = [word for word in row['original_word_list_low'] if dictionary.check(word)]
            row['non_stop_word_list_low'] = [word for word in row['real_word_list_low'] if word not in stop_word_list]
            row["pos_tags"] = [(w,t) for w,t in unigram_tagger.tag(row["real_word_list_low"]) if t is not None]
            db["tweet_data"].insert(row)
            # Redirect to the document list after POST
#             return render_to_response('Twitter.html',{'form': form,},context_instance=RequestContext(request))
            return HttpResponseRedirect('/Twitter')                             
        else:
            form = UplaodFile() # A empty, unbound form
    except Exception,e:
            print e
            return HttpResponseRedirect('/Twitter')
    return HttpResponseRedirect('/Twitter')
#     return render_to_response(
#         'Twitter.html',
#         {'form': form},
#         context_instance=RequestContext(request)
#     )    

def stream_twitter(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('source')
            print name
            hashtags = request.POST.get('hashtags')
            print hashtags
            stream_thread = mp.Process(target=stream_tweets.stream_all_tweets,args=(hashtags, name,))
            stream_thread.start()
            
            # Redirect to the document list after POST
#             return render_to_response('Twitter.html',{'form': form,},context_instance=RequestContext(request))
            return HttpResponseRedirect('/Twitter')                             
        else:
            form = UplaodFile() # A empty, unbound form
    except Exception,e:
            print e
            return HttpResponseRedirect('/Twitter')
    return HttpResponseRedirect('/Twitter')
        
def process_freq(source):
    today = datetime.date.today()
    start_time= time.time()
    tweets_cur = db["tweet_data"].find({'query_name':source},{'content_title':1})
    tweets = [tweet for tweet in tweets_cur]
    for tweet in tweets:
        sentiment = get_simple_sentiment(tweet["content_title"])
#         print sentiment
        db["tweet_data"].update({"_id":tweet["_id"]},{"$set":sentiment})
    total_tweets = tweets.__len__()
    pos_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'positive'}).count()
    neg_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'frequency','isFile':False,'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source,'total_tweets':total_tweets,'pos_tweets':pos_tweets,'neg_tweets':neg_tweets})

def process_freq_f(source):
    today = datetime.date.today()
    start_time= time.time()
    content = db["tweet_data"].find_one({'query_name':source},{'tweet':1,'total_words':1})
#     tweets = [tweet for tweet in tweets_cur]
#     for tweet in tweets:
#         sentiment = get_simple_sentiment(tweet["content_title"])
#         print sentiment
    sentiment = get_simple_sentiment(content['tweet'])
    db["tweet_data"].update({"_id":content["_id"]},{"$set":sentiment})
#     total_tweets = tweets.__len__()
#     pos_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'positive'}).count()
#     neg_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'frequency','total_words':content['total_words'],'isFile':True,'sentiment':sentiment['frequency_sentiment'],'content_title':content['tweet'],'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source})


def process_afinn(source):
    today = datetime.date.today()
    start_time= time.time()
    tweets_cur = db["tweet_data"].find({'query_name':source},{'content_title':1})
    tweets = [tweet for tweet in tweets_cur]
    for tweet in tweets:
        sentiment = get_afinn_sentiment(tweet["content_title"])
#         print sentiment
        db["tweet_data"].update({"_id":tweet["_id"]},{"$set":sentiment})
    total_tweets = tweets.__len__()
    pos_tweets = db["tweet_data"].find({'query_name':source,'afinn_sentiment.sentiment':'positive'}).count()
    neg_tweets = db["tweet_data"].find({'query_name':source,'afinn_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'afinn','isFile':False,'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source,'total_tweets':total_tweets,'pos_tweets':pos_tweets,'neg_tweets':neg_tweets})    

def process_afinn_f(source):
    today = datetime.date.today()
    start_time= time.time()
    content = db["tweet_data"].find_one({'query_name':source},{'tweet':1,'total_words':1})
#     tweets = [tweet for tweet in tweets_cur]
#     for tweet in tweets:
#         sentiment = get_simple_sentiment(tweet["content_title"])
#         print sentiment
    sentiment = get_afinn_sentiment(content['tweet'])
    db["tweet_data"].update({"_id":content["_id"]},{"$set":sentiment})
#     total_tweets = tweets.__len__()
#     pos_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'positive'}).count()
#     neg_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'afinn','total_words':content['total_words'],'isFile':True,'sentiment':sentiment['afinn_sentiment'],'content_title':content['tweet'],'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source})
    
def process_nb_single(source):
    today = datetime.date.today()
    start_time= time.time()
    tweets_cur = db["tweet_data"].find({'query_name':source},{'content_title':1})
    tweets = [tweet for tweet in tweets_cur]
    for tweet in tweets:
        sentiment = get_single_sentiment(tweet["content_title"])
        print sentiment
        db["tweet_data"].update({"_id":tweet["_id"]},{"$set":sentiment})
    total_tweets = tweets.__len__()
    pos_tweets = db["tweet_data"].find({'query_name':source,'nb_single_sentiment.sentiment':'positive'}).count()
    neg_tweets = db["tweet_data"].find({'query_name':source,'nb_single_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'nb_single','isFile':False,'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source,'total_tweets':total_tweets,'pos_tweets':pos_tweets,'neg_tweets':neg_tweets})
    
def process_nb_single_f(source):
    today = datetime.date.today()
    start_time= time.time()
    content = db["tweet_data"].find_one({'query_name':source},{'tweet':1,'total_words':1})
#     tweets = [tweet for tweet in tweets_cur]
#     for tweet in tweets:
#         sentiment = get_simple_sentiment(tweet["content_title"])
#         print sentiment
    sentiment = get_single_sentiment(content['tweet'])
    db["tweet_data"].update({"_id":content["_id"]},{"$set":sentiment})
#     total_tweets = tweets.__len__()
#     pos_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'positive'}).count()
#     neg_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'nb_single','total_words':content['total_words'],'isFile':True,'sentiment':sentiment['nb_single_sentiment'],'content_title':content['tweet'],'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source})
    
def process_nb_non_stop(source):
    today = datetime.date.today()
    start_time= time.time()
    tweets_cur = db["tweet_data"].find({'query_name':source},{'content_title':1})
    tweets = [tweet for tweet in tweets_cur]
    for tweet in tweets:
        sentiment = get_non_stop_sentiment(tweet["content_title"])
        db["tweet_data"].update({"_id":tweet["_id"]},{"$set":sentiment})
    total_tweets = tweets.__len__()
    pos_tweets = db["tweet_data"].find({'query_name':source,'nb_non_stop_sentiment.sentiment':'positive'}).count()
    neg_tweets = db["tweet_data"].find({'query_name':source,'nb_non_stop_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'nb_non_stop','isFile':False,'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source,'total_tweets':total_tweets,'pos_tweets':pos_tweets,'neg_tweets':neg_tweets})

def process_nb_non_stop_f(source):
    today = datetime.date.today()
    start_time= time.time()
    content = db["tweet_data"].find_one({'query_name':source},{'tweet':1,'total_words':1})
#     tweets = [tweet for tweet in tweets_cur]
#     for tweet in tweets:
#         sentiment = get_simple_sentiment(tweet["content_title"])
#         print sentiment
    sentiment = get_non_stop_sentiment(content['tweet'])
    db["tweet_data"].update({"_id":content["_id"]},{"$set":sentiment})
#     total_tweets = tweets.__len__()
#     pos_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'positive'}).count()
#     neg_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'nb_non_stop','total_words':content['total_words'],'isFile':True,'sentiment':sentiment['nb_non_stop_sentiment'],'content_title':content['tweet'],'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source})
     
def process_nb_best(source):
    today = datetime.date.today()
    start_time= time.time()
    tweets_cur = db["tweet_data"].find({'query_name':source},{'content_title':1})
    tweets = [tweet for tweet in tweets_cur]
    for tweet in tweets:
        sentiment = get_best_sentiment(tweet["content_title"])
        db["tweet_data"].update({"_id":tweet["_id"]},{"$set":sentiment})
    total_tweets = tweets.__len__()
    pos_tweets = db["tweet_data"].find({'query_name':source,'nb_best_sentiment.sentiment':'positive'}).count()
    neg_tweets = db["tweet_data"].find({'query_name':source,'nb_best_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'nb_best','isFile':False,'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source,'total_tweets':total_tweets,'pos_tweets':pos_tweets,'neg_tweets':neg_tweets})
  
def process_nb_best_f(source):
    today = datetime.date.today()
    start_time= time.time()
    content = db["tweet_data"].find_one({'query_name':source},{'tweet':1,'total_words':1})
#     tweets = [tweet for tweet in tweets_cur]
#     for tweet in tweets:
#         sentiment = get_simple_sentiment(tweet["content_title"])
#         print sentiment
    sentiment = get_best_sentiment(content['tweet'])
    db["tweet_data"].update({"_id":content["_id"]},{"$set":sentiment})
#     total_tweets = tweets.__len__()
#     pos_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'positive'}).count()
#     neg_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'nb_best','total_words':content['total_words'],'isFile':True,'sentiment':sentiment['nb_best_sentiment'],'content_title':content['tweet'],'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source})
    
def process_nb_bigram_best(source):
    today = datetime.date.today()
    start_time= time.time()
    tweets_cur = db["tweet_data"].find({'query_name':source},{'content_title':1})
    tweets = [tweet for tweet in tweets_cur]
    for tweet in tweets:
        sentiment = get_bigram_best_sentiment(tweet["content_title"])
        db["tweet_data"].update({"_id":tweet["_id"]},{"$set":sentiment})
    total_tweets = tweets.__len__()
    pos_tweets = db["tweet_data"].find({'query_name':source,'nb_bigram_best_sentiment.sentiment':'positive'}).count()
    neg_tweets = db["tweet_data"].find({'query_name':source,'nb_bigram_best_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'nb_bigram_best','isFile':False,'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source,'total_tweets':total_tweets,'pos_tweets':pos_tweets,'neg_tweets':neg_tweets})        

def process_nb_bigram_best_f(source):
    today = datetime.date.today()
    start_time= time.time()
    content = db["tweet_data"].find_one({'query_name':source},{'tweet':1,'total_words':1})
#     tweets = [tweet for tweet in tweets_cur]
#     for tweet in tweets:
#         sentiment = get_simple_sentiment(tweet["content_title"])
#         print sentiment
    sentiment = get_bigram_best_sentiment(content['tweet'])
    db["tweet_data"].update({"_id":content["_id"]},{"$set":sentiment})
#     total_tweets = tweets.__len__()
#     pos_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'positive'}).count()
#     neg_tweets = db["tweet_data"].find({'query_name':source,'frequency_sentiment.sentiment':'negative'}).count()
    Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
    seconds_elapsed = time.time() - start_time
    endtime = str(datetime.timedelta(seconds=seconds_elapsed))
    db["sentiment"].insert({'algo':'nb_bigram_best','total_words':content['total_words'],'isFile':True,'sentiment':sentiment['nb_bigram_best_sentiment'],'content_title':content['tweet'],'histograms':Histograms_bubbles,'pos_bubbles':POS_bubbles,'date_time':str(today),'time_elapsed':endtime,'source':source})
    
def frequency(request):
    # just use another function for full sources information
    # stream_tweets.get_full_sources()
    docs = db["sentiment"].find({'algo':'frequency'})
    sum_sources = []
    sources_names = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        sources_names.append(doc['source'])
    
    return render(request,
        'Frequency.html',
        {'sources':stream_tweets.get_full_sources(f_s=sources_names),'processed_sources':sum_sources}
    )    

def Add_frequency(request):
    try:
        if request.method == 'POST':
            
            source = request.POST.get('source')
            print source
            if db['query'].find_one({'query_name':source})['isFile']:
                mp.Process(target=process_freq_f,args=(source,)).start()
            else:
                mp.Process(target=process_freq,args=(source,)).start()
            return HttpResponseRedirect('/Frequency')                             
    except Exception,e:
            print e
            return HttpResponseRedirect('/Frequency')
    return HttpResponseRedirect('/Frequency')
        
def frequency_source(request):
#     response_dict = {}
    source = str(request.POST['source_name'])
    f_sentiment = db["sentiment"].find_one({'algo':'frequency','source':source})
    f_sentiment['_id'] = str(f_sentiment['_id'])
    print f_sentiment
    if db['query'].find_one({'query_name':source})['isFile']:
        response_dict = {'source_info':f_sentiment}
    else:
        docs = db["tweet_data"].find({'query_name':source},{"frequency_sentiment":1,'content_title':1,'user_name':1})
        Memcahce_Client.flush_all()
        m_docs = []
        all_tweets = []
        counter = 0
        pg_count = 0
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if doc['frequency_sentiment']["sentiment"] != 'neutral':
                if counter == 16:
                    pg_count += 1
                    Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
                    counter = 0
                    m_docs = []
                m_docs.append(doc)
            
                all_tweets.append(doc)
                counter += 1
        
        if m_docs.__len__()>0:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
        Memcahce_Client.set(key="source",val=source)
        Memcahce_Client.set(key="current_page",val=1)
        Memcahce_Client.set(key="page_limit",val=pg_count)
#     Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
#     POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
        response_dict = {'source_info':f_sentiment,'all_tweets':all_tweets,'tweets_page_1':Memcahce_Client.get(str(source+"_1"))}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')

def afinn(request):
    # just use another function for full sources information
    # stream_tweets.get_full_sources()
    sources = db["sentiment"].find({'algo':'afinn'})
    sum_sources = []
    sources_names = []
    for doc in sources:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        sources_names.append(doc['source'])
    
    return render(request,
        'Afinn.html',
        {'sources':stream_tweets.get_full_sources(f_s=sources_names),'processed_sources':sum_sources}
    )    

def Add_afinn(request):
    try:
        if request.method == 'POST':
            
            source = request.POST.get('source')
            print source
            if db['query'].find_one({'query_name':source})['isFile']:
                mp.Process(target=process_afinn_f,args=(source,)).start()
            else:
                mp.Process(target=process_afinn,args=(source,)).start()
            return HttpResponseRedirect('/Afinn')                             
    except Exception,e:
            print e
            return HttpResponseRedirect('/Afinn')
    return HttpResponseRedirect('/Afinn')
        
def afinn_source(request):
    response_dict = {}
    source = str(request.POST['source_name'])
    f_sentiment = db["sentiment"].find_one({'algo':'afinn','source':source})
    f_sentiment['_id'] = str(f_sentiment['_id'])
    print f_sentiment
    if db['query'].find_one({'query_name':source})['isFile']:
        response_dict = {'source_info':f_sentiment}
    else:
        docs = db["tweet_data"].find({'query_name':source},{"afinn_sentiment":1,'content_title':1,'user_name':1})
        Memcahce_Client.flush_all()
        m_docs = []
        all_tweets = []
        counter = 0
        pg_count = 0
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if doc['afinn_sentiment']["sentiment"] != 'neutral':
                if counter == 16:
                    pg_count += 1
                    Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
                    counter = 0
                    m_docs = []
                m_docs.append(doc)
            
            
                all_tweets.append(doc)
                counter += 1
        
        if m_docs.__len__()>0:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
        Memcahce_Client.set(key="source",val=source)
        Memcahce_Client.set(key="current_page",val=1)
        Memcahce_Client.set(key="page_limit",val=pg_count)
    #     Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    #     POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
        response_dict = {'source_info':f_sentiment,'all_tweets':all_tweets,'tweets_page_1':Memcahce_Client.get(str(source+"_1"))}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')



def nb_single(request):
    # just use another function for full sources information
    # stream_tweets.get_full_sources()
    sources = db["sentiment"].find({'algo':'nb_single'})
    sum_sources = []
    sources_names = []
    for doc in sources:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        sources_names.append(doc['source'])
    
    return render(request,
        'Nb_single.html',
        {'sources':stream_tweets.get_full_sources(f_s=sources_names),'processed_sources':sum_sources}
    )    

def Add_nb_single(request):
    try:
        if request.method == 'POST':
            
            source = request.POST.get('source')
            print source
            if db['query'].find_one({'query_name':source})['isFile']:
                mp.Process(target=process_nb_single_f,args=(source,)).start()
            else:
                mp.Process(target=process_nb_single,args=(source,)).start()
            return HttpResponseRedirect('/Nb_single')                             
    except Exception,e:
            print e
            return HttpResponseRedirect('/Nb_single')
    return HttpResponseRedirect('/Nb_single')
        
def nb_single_source(request):
    response_dict = {}
    source = str(request.POST['source_name'])
    f_sentiment = db["sentiment"].find_one({'algo':'nb_single','source':source})
    f_sentiment['_id'] = str(f_sentiment['_id'])
    print f_sentiment
    if db['query'].find_one({'query_name':source})['isFile']:
        response_dict = {'source_info':f_sentiment}
    else:
        docs = db["tweet_data"].find({'query_name':source},{"nb_single_sentiment":1,'content_title':1,'user_name':1})
        Memcahce_Client.flush_all()
        m_docs = []
        all_tweets = []
        counter = 0
        pg_count = 0
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if doc['nb_single_sentiment']["sentiment"] != 'neutral':
                if counter == 16:
                    pg_count += 1
                    Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
                    counter = 0
                    m_docs = []
                m_docs.append(doc)
                
                
                all_tweets.append(doc)
                counter += 1
        
        if m_docs.__len__()>0:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
        Memcahce_Client.set(key="source",val=source)
        Memcahce_Client.set(key="current_page",val=1)
        Memcahce_Client.set(key="page_limit",val=pg_count)
    #     Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    #     POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
        response_dict = {'source_info':f_sentiment,'all_tweets':all_tweets,'tweets_page_1':Memcahce_Client.get(str(source+"_1"))}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')


def nb_non_stop(request):
    # just use another function for full sources information
    # stream_tweets.get_full_sources()
    sources = db["sentiment"].find({'algo':'nb_non_stop'})
    sum_sources = []
    s_names = []
    for doc in sources:
        doc["_id"] = str(doc["_id"])
        sum_sources.append(doc)
        s_names.append(doc['source'])
    
    return render(request,
        'Nb_non_stop.html',
        {'sources':stream_tweets.get_full_sources(f_s=s_names),'processed_sources':sum_sources}
    )    

def Add_nb_non_stop(request):
    try:
        if request.method == 'POST':
            
            source = request.POST.get('source')
            print source
            if db['query'].find_one({'query_name':source})['isFile']:
                mp.Process(target=process_nb_non_stop_f,args=(source,)).start()
            else:
                mp.Process(target=process_nb_non_stop,args=(source,)).start()
            return HttpResponseRedirect('/Nb_non_stop')                             
    except Exception,e:
            print e
            return HttpResponseRedirect('/Nb_non_stop')
    return HttpResponseRedirect('/Nb_non_stop')
        
def nb_non_stop_source(request):
    response_dict = {}
    source = str(request.POST['source_name'])
    f_sentiment = db["sentiment"].find_one({'algo':'nb_non_stop','source':source})
    f_sentiment['_id'] = str(f_sentiment['_id'])
    print f_sentiment
    if db['query'].find_one({'query_name':source})['isFile']:
        response_dict = {'source_info':f_sentiment}
    else:
        docs = db["tweet_data"].find({'query_name':source},{"nb_non_stop_sentiment":1,'content_title':1,'user_name':1})
        Memcahce_Client.flush_all()
        m_docs = []
        all_tweets = []
        counter = 0
        pg_count = 0
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if doc['nb_non_stop_sentiment']["sentiment"] != 'neutral':
                if counter == 16:
                    pg_count += 1
                    Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
                    counter = 0
                    m_docs = []
                m_docs.append(doc)
            
            
                all_tweets.append(doc)
                counter += 1
        
        if m_docs.__len__()>0:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
        Memcahce_Client.set(key="source",val=source)
        Memcahce_Client.set(key="current_page",val=1)
        Memcahce_Client.set(key="page_limit",val=pg_count)
    #     Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    #     POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
        response_dict = {'source_info':f_sentiment,'all_tweets':all_tweets,'tweets_page_1':Memcahce_Client.get(str(source+"_1"))}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')


def nb_best(request):
    # just use another function for full sources information
    # stream_tweets.get_full_sources()
    sources = db["sentiment"].find({'algo':'nb_best'})
    sources = [s for s in sources]
    s_names = [s['source'] for s in sources]
    return render(request,
        'Nb_best.html',
        {'sources':stream_tweets.get_full_sources(f_s=s_names),'processed_sources':sources}
    )    

def Add_nb_best(request):
    try:
        if request.method == 'POST':
            
            source = request.POST.get('source')
            print source
            if db['query'].find_one({'query_name':source})['isFile']:
                mp.Process(target=process_nb_best_f,args=(source,)).start()
            else:
                mp.Process(target=process_nb_best,args=(source,)).start()
            return HttpResponseRedirect('/Nb_best')                             
    except Exception,e:
            print e
            return HttpResponseRedirect('/Nb_best')
    return HttpResponseRedirect('/Nb_best')
        
def nb_best_source(request):
    response_dict = {}
    source = str(request.POST['source_name'])
    f_sentiment = db["sentiment"].find_one({'algo':'nb_best','source':source})
    f_sentiment['_id'] = str(f_sentiment['_id'])
    print f_sentiment
    if db['query'].find_one({'query_name':source})['isFile']:
        response_dict = {'source_info':f_sentiment}
    else:
        docs = db["tweet_data"].find({'query_name':source},{"nb_best_sentiment":1,'content_title':1,'user_name':1})
        Memcahce_Client.flush_all()
        m_docs = []
        all_tweets = []
        counter = 0
        pg_count = 0
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if doc['nb_best_sentiment']["sentiment"] != 'neutral':
                
                if counter == 16:
                    pg_count += 1
                    Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
                    counter = 0
                    m_docs = []
                m_docs.append(doc)
                
                all_tweets.append(doc)
                counter += 1
        
        if m_docs.__len__()>0:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
        Memcahce_Client.set(key="source",val=source)
        Memcahce_Client.set(key="current_page",val=1)
        Memcahce_Client.set(key="page_limit",val=pg_count)
    #     Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    #     POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
        response_dict = {'source_info':f_sentiment,'all_tweets':all_tweets,'tweets_page_1':Memcahce_Client.get(str(source+"_1"))}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')


def nb_bigram_best(request):
    # just use another function for full sources information
    # stream_tweets.get_full_sources()
    sources = db["sentiment"].find({'algo':'nb_bigram_best'})
    sources = [s for s in sources]
    s_names = [s['source'] for s in sources]
    return render(request,
        'Nb_bigram_best.html',
        {'sources':stream_tweets.get_full_sources(f_s=s_names),'processed_sources':sources}
    )    

def Add_nb_bigram_best(request):
    try:
        if request.method == 'POST':
            
            source = request.POST.get('source')
            print source
            if db['query'].find_one({'query_name':source})['isFile']:
                mp.Process(target=process_nb_bigram_best_f,args=(source,)).start()
            else:
                mp.Process(target=process_nb_bigram_best,args=(source,)).start()
            return HttpResponseRedirect('/Nb_bigram_best')                             
    except Exception,e:
            print e
            return HttpResponseRedirect('/Nb_bigram_best')
    return HttpResponseRedirect('/Nb_bigram_best')
        
def nb_bigram_best_source(request):
    response_dict = {}
    source = str(request.POST['source_name'])
    f_sentiment = db["sentiment"].find_one({'algo':'nb_bigram_best','source':source})
    f_sentiment['_id'] = str(f_sentiment['_id'])
    print f_sentiment
    if db['query'].find_one({'query_name':source})['isFile']:
        response_dict = {'source_info':f_sentiment}
    else:
        docs = db["tweet_data"].find({'query_name':source},{"nb_bigram_best_sentiment":1,'content_title':1,'user_name':1})
        Memcahce_Client.flush_all()
        m_docs = []
        all_tweets = []
        counter = 0
        pg_count = 0
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if doc['nb_bigram_best_sentiment']["sentiment"] != 'neutral':
                if counter == 16:
                    pg_count += 1
                    Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
                    counter = 0
                    m_docs = []
                m_docs.append(doc)
            
            
                all_tweets.append(doc)
                counter += 1
        
        if m_docs.__len__()>0:
            pg_count += 1
            Memcahce_Client.set(key=source+"_"+str(pg_count),val=m_docs)
        Memcahce_Client.set(key="source",val=source)
        Memcahce_Client.set(key="current_page",val=1)
        Memcahce_Client.set(key="page_limit",val=pg_count)
    #     Histograms_bubbles = stream_tweets.get_real_word_key_count({'query_name':source})
    #     POS_bubbles = stream_tweets.get_pos_count({'query_name':source})
        response_dict = {'source_info':f_sentiment,'all_tweets':all_tweets,'tweets_page_1':Memcahce_Client.get(str(source+"_1"))}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/javascript')

def error404(request):
    response = render_to_response('404.html',{},context_instance=RequestContext(request))
    response.status_code = 404
    return response
    