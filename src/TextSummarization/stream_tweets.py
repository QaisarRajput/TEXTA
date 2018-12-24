from TwitterSearch import *
import csv,re
import nltk, pymongo, enchant
from bson.code import Code
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import brown
# import simplejson
from pymongo import MongoClient
from TextSummarization.settings import BASE_DIR
import datetime
client = MongoClient()
dictionary = enchant.Dict("en_US")
brown_tagged_sents = brown.tagged_sents(categories='news')
unigram_tagger = nltk.UnigramTagger(brown_tagged_sents)
stop_word_list = list(stopwords.words('english'))
my_stop_list = ['#','@',"'s",'http','https','i','the','pr','rt','.','..','...']
stop_word_list = stop_word_list+my_stop_list
pos_sent = open(BASE_DIR+"/data/positive-words.txt").read()
positive_words = pos_sent.split('\n')
neg_sent = open(BASE_DIR+"/data/negative-words.txt").read()
negative_words = neg_sent.split('\n')
db = client["Text_Analysis"]
col = db['tweet_data']


def get_sources():
    sources = db['query'].find({},{'query_name':1})
    sources = [dict['query_name'] for dict in sources]
    return sources

def get_full_sources(f_s=None):
    sources = db['query'].find({})
    sources_list = []
    if f_s == None:
        for dict in sources:
            dict["_id"] = str(dict["_id"])
            sources_list.append(dict)
    else:
        for dict in sources:
            if dict['query_name'] not in f_s:
                dict["_id"] = str(dict["_id"])
                sources_list.append(dict)
    return sources_list


def clean_word(dirty_word):
    clean_char_list = list()
    for char in dirty_word:
        if ord(char) <= 128:
            clean_char_list.append(char)
    return ''.join(clean_char_list)

def searchTwitterData(query_name,keywords):
    try:
        
        tso = TwitterSearchOrder() # create a TwitterSearchOrder object
        for word in keywords:
            tso.add_keyword(word)
#         tso.set_keywords(keywords) # let's define all words we would like to have a look for

        tso.set_language('en') # we want to see English tweets only
        tso.set_include_entities(False) # and don't give us all those entity information

        counter = 0
        # it's about time to create a TwitterSearch object with our secret tokens
        ts = TwitterSearch(
            consumer_key = 'NbolpgWCePaMWe3Zj6pfWG0Fx',
            consumer_secret = 'ux7nk22IHOrgFCPsGKtd5g7EQHszCC6ZM306H6OlSwkA88wO9J',
            access_token = '2936406578-i9wqVhLFdaNLG1byD9muMSGB73UymMdW97syQtz',
            access_token_secret = 'sPHZbLC5KDFdMFHEujpJrFPl5akB9P0451HaipkPy98Q3'
         )
#         csv_file = open(file_name, 'wb')
        
#         fieldnames = ['tweet_id','user_id','user_name','content_title','RT','publisher','rt_count',\
#                       'publish_timestamp','followers_count','friends_count','matched_terms','hash_tags',\
#                       'matched_categories','applied_labels','destination_url','location']
            # this is where the fun actually starts :)
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         writer.writeheader()
        for doc in ts.search_tweets_iterable(tso):
            #fieldnames = ['tweet']
#                 print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
                if counter>=1000:
                    break
                row = {}
                try:
                    if col.find({'query_name':query_name,'original_content':str(clean_word(doc['text']))}).count()==0:
                        row['query_name'] = query_name
                        row['matched_categories'] = ""
                        row['matched_terms'] = ""
                        row['applied_labels'] = ""
                        row['original_content'] = str(clean_word(doc['text']))
                        row['content_title'] = str(clean_word(doc['text']))
                        row['content_title']=row['content_title'].replace("\x80","")
                        row['content_title']=re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', row['content_title'], flags=re.MULTILINE)
                        row['content_title']= row['content_title'].replace(r"htt..+\s$", '')
                        row['content_title'] = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z\(\)',:;. \n\t])|(\w+:\/\/\S+)"," ",row['content_title']).split())
                        row['RT'] = doc['retweeted']
                        row['publisher'] = 'twitter'
                        row['rt_count'] = int(doc['retweet_count'])
                        row['publish_timestamp'] = doc['created_at']
                        row['user_name'] = clean_word(doc['user']['screen_name'])
                        row['user_id'] = str(doc['user']['id'])
                        row['tweet_id'] = str(doc['id'])
                        row['original_word_list_low'] = word_tokenize(row['content_title'].lower())
                        row['real_word_list_low'] = [word for word in row['original_word_list_low'] if dictionary.check(word)]
                        row['non_stop_word_list_low'] = [word for word in row['real_word_list_low'] if word not in stop_word_list]
                        row["pos_tags"] = [(w,t) for w,t in unigram_tagger.tag(row["real_word_list_low"]) if t is not None]
                        if 'location' in doc['user']:
                            row['location'] = str(doc['user']['location'])
                        else:
                            row['location'] = ''
                        row['followers_count'] = int(doc['user']['followers_count'])
                        row['friends_count'] = int(doc['user']['friends_count'])
                        row['hash_tags'] = "|".join(re.findall(r"#(\w+)", row['content_title']))
                        row['destination_url'] = "http://www.twitter.com"
                        
                        print row['content_title']
                        col.insert(row)
                        counter += 1
#                     writer.writerow(row)
                except Exception,ex:
                    print ex
        db['query'].update({'query_name':query_name},{"$inc":{'tweets_count':counter}})    
#         csv_file.close()
    except TwitterSearchException as e: # take care of all those ugly errors if there are some
        print(e)



def stream_all_tweets(query,name):
    today = datetime.date.today()
    queries = query.split(',')
    if db['query'].find({'query_name':name}).count()<1:
            db['query'].insert({'query_name':name,'query':query,'tweets_count':0,"isFile":False,"date_time":str(today),'processed':False})
    for q in queries:
        searchTwitterData(name,keywords=q.split())
    db['query'].update({'query_name':name},{"$set":{'processed':True}})       
        
def get_real_word_key_count(search_key):
    mapperfunc = Code("""
               function() {
                   if(this.hasOwnProperty('non_stop_word_list_low')){
                        var key = this._id;
                        this.non_stop_word_list_low.forEach(function(item){ emit(item, {'o_id':key ,'record':1,'count':1}); });
                    }
                }
               """)

    reducefunc = Code("""
                function (key, values) {
                  var reduce_value = {'count':0,'record':0};
                  var poc_list = [];
                  for (var i = 0; i < values.length; i++) {
                    reduce_value.count += values[i].count;
                    
                    if(poc_list.indexOf(values[i].o_id) == -1){
                        poc_list.push(values[i].o_id);
                        reduce_value.record += 1;
                    }
                  }
                  return reduce_value;
                }
                """)
    result = col.map_reduce(mapperfunc, reducefunc,"real_word_count",query=search_key, sort={"_id":1})
    stop_word_list = list(stopwords.words('english'))
    my_stop_list = ['i','the','pr','rt','.','..','...']
    stop_word_list = stop_word_list+my_stop_list
#     print stop_word_list
    real_word_count_list = [[doc["_id"],doc["value"]["count"],doc["value"]["record"]] for doc in result.find().sort("value.count",pymongo.DESCENDING) if doc['_id'] not in stop_word_list]
    return real_word_count_list

def get_pos_count(search_key):
    mapperfunc = Code("""
               function() {
                   if(this.hasOwnProperty('pos_tags')){
                        var l_tag = "";
                        var l_word = "";
                        this.pos_tags.forEach(
                        function(w_t){ 
                        if(w_t[1] != null){
                        if(w_t[1].toString().indexOf("NN")>-1 && l_tag.indexOf("JJ")>-1){
                        emit(l_word.concat("_",w_t[0].toString()), 1);
                        l_tag = "";
                        l_word = "";
                        }else if(w_t[1].toString().indexOf("JJ")>-1){
                        l_tag = w_t[1].toString();
                        l_word = w_t[0].toString();
                        }else{
                        l_tag = "";
                        l_word = "";
                        }
                        }
                         });
                    }
                }
               """)
 
    reducefunc = Code("""
                function (key, values) {
                  var total = 0;
                  for (var i = 0; i < values.length; i++) {
                    total += values[i];
                  }
                  return total;
                }
                """)
    result = col.map_reduce(mapperfunc, reducefunc, "pos_count",query=search_key,sort={"_id":1})
    positive_children = {'name':'positive','size':0,'children':[]}
    pos_list = []
    neg_list = []
    negative_children = {'name':'negative','size':0,'children':[]}
    for word in result.find().sort("value",pymongo.DESCENDING):
#         print word["_id"]
#         print word["value"]
        value = int(word["value"])
        adj = str(word["_id"].split('_')[0])
        nn = str(word["_id"].split('_')[1])
        try:
            if adj in positive_words:
                if adj not in pos_list:
                    positive_children['children'].append({'name':adj,'size':value,'children':[{'name':nn,'size':value}]})
                    pos_list.append(adj)
                else:
#                     print 'else'
                    for child in positive_children['children']:
#                         print child
                        if child['name'] == adj:
                            child['size'] += value
                            child['children'].append({'name':nn,'size':value})
                positive_children['size'] += 1
            if adj in negative_words:
                if adj not in neg_list:
                    negative_children['children'].append({'name':adj,'size':value,'children':[{'name':nn,'size':value}]})
                    neg_list.append(adj)
                else:
                    for child in negative_children['children']:
                        if child['name'] == adj:
                            child['size'] += value
                            child['children'].append({'name':nn,'size':value})
                negative_children['size'] += 1
        except Exception,ex:
            print ex
            print Exception
    
    pos_count_list = {'name':'colocations','size':2,'children':[positive_children,negative_children]}                           
#     pos_count_list = [{'adjective':doc["_id"].split('_')[0],'noun':doc["_id"].split('_')[1],'count':doc["value"]} for doc in result.find().sort("value",pymongo.DESCENDING)]
    return pos_count_list
