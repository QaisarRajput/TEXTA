from django.conf.urls import patterns, include, url
from django.conf.urls import handler404, handler500
from django.contrib import admin
# from TextSummarization.views import error404
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TextSummarization.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'TextSummarization.views.index', name='index'),
#     url(r'^submit$', 'TextSummarization.views.submit', name='submit'),
    url(r'^Intersection/$', 'TextSummarization.views.intersection', name='intersection'),
    url(r'^Intersection/Add_Intersection$', 'TextSummarization.views.Add_Intersection', name='Add_Intersection'),
    url(r'^Intersection/Load$', 'TextSummarization.views.intersection_source', name='intersection_source'),
    
    url(r'^Intersection_T/$', 'TextSummarization.views.intersection_t', name='intersection_t'),
    url(r'^Intersection_T/Add_Intersection$', 'TextSummarization.views.Add_Intersection_t', name='Add_Intersection_t'),
    url(r'^Intersection_T/Load$', 'TextSummarization.views.intersection_source_t', name='intersection_source_t'),
    
    url(r'^cosine_similarity/$', 'TextSummarization.views.cosine_similarity', name='cosine_similarity'),
    url(r'^cosine_similarity/Add_cosine_similarity$', 'TextSummarization.views.Add_Cosine', name='Add_Cosine'),
    url(r'^cosine_similarity/Load$', 'TextSummarization.views.cosine_source', name='cosine_source'),
    
    url(r'^Tf_Ranker/$', 'TextSummarization.views.Tf_Ranker', name='Tf_Ranker'),
    url(r'^Tf_Ranker/Add_Tf_Ranker$', 'TextSummarization.views.Add_Tf_Ranker', name='Add_Tf_Ranker'),
    url(r'^Tf_Ranker/Load$', 'TextSummarization.views.Tf_Ranker_source', name='Tf_Ranker_source'),
    url(r'^Tf_Ranker/Load_T$', 'TextSummarization.views.Tf_Ranker_T_source', name='Tf_Ranker_T_source'),
    url(r'^Tf_Ranker/Load_More$', 'TextSummarization.views.Load_More', name='Load_More'),
    
    url(r'^Noun_phrase/$', 'TextSummarization.views.Noun_phrase', name='Noun_phrase'),
    url(r'^Noun_phrase/Add_Noun_phrase$', 'TextSummarization.views.Add_Noun_phrase', name='Add_Noun_phrase'),
    url(r'^Noun_phrase/Load$', 'TextSummarization.views.Noun_phrase_source', name='Noun_phrase_source'),
    url(r'^Noun_phrase/Load_T$', 'TextSummarization.views.Noun_phrase_T_source', name='Noun_phrase_T_source'),
    url(r'^Noun_phrase/Load_More$', 'TextSummarization.views.Load_More', name='Load_More'),
    
    url(r'^Frequency/$', 'TextSummarization.views.frequency', name='frequency'),
    url(r'^Frequency/Load$', 'TextSummarization.views.frequency_source', name='frequency_source'),
    url(r'^Frequency/Add_frequency$', 'TextSummarization.views.Add_frequency', name='Add_frequency'),
    
    url(r'^Afinn/$', 'TextSummarization.views.afinn', name='afinn'),
    url(r'^Afinn/Load$', 'TextSummarization.views.afinn_source', name='afinn_source'),
    url(r'^Afinn/Add_afinn$', 'TextSummarization.views.Add_afinn', name='Add_afinn'),
    
    url(r'^Nb_single/$', 'TextSummarization.views.nb_single', name='nb_single'),
    url(r'^Nb_single/Load$', 'TextSummarization.views.nb_single_source', name='nb_single_source'),
    url(r'^Nb_single/Add_nb_single$', 'TextSummarization.views.Add_nb_single', name='Add_nb_single'),
    
    url(r'^Nb_non_stop/$', 'TextSummarization.views.nb_non_stop', name='nb_non_stop'),
    url(r'^Nb_non_stop/Load$', 'TextSummarization.views.nb_non_stop_source', name='nb_non_stop_source'),
    url(r'^Nb_non_stop/Add_nb_non_stop$', 'TextSummarization.views.Add_nb_non_stop', name='Add_nb_non_stop'),
    
    url(r'^Nb_best/$', 'TextSummarization.views.nb_best', name='nb_best'),
    url(r'^Nb_best/Load$', 'TextSummarization.views.nb_best_source', name='nb_best_source'),
    url(r'^Nb_best/Add_nb_best$', 'TextSummarization.views.Add_nb_best', name='Add_nb_best'),
    
    url(r'^Nb_bigram_best/$', 'TextSummarization.views.nb_bigram_best', name='nb_bigram_best'),
    url(r'^Nb_bigram_best/Load$', 'TextSummarization.views.nb_bigram_best_source', name='nb_bigram_best_source'),
    url(r'^Nb_bigram_best/Add_nb_bigram_best$', 'TextSummarization.views.Add_nb_bigram_best', name='Add_nb_bigram_best'),
    
    url(r'^K-means/$', 'TextSummarization.views.k_means', name='k_means'),
    url(r'^K-means/Add_Kmeans$', 'TextSummarization.views.Add_Kmeans', name='Add_Kmeans'),
    url(r'^K-means/Load$', 'TextSummarization.views.k_means_load', name='k_means_load'),
    url(r'^K-means/Load_F$', 'TextSummarization.views.k_means_load_f', name='k_means_load_f'),
    url(r'^K-means/Load_T$', 'TextSummarization.views.k_means_load_t', name='k_means_load_t'),
    
    url(r'^Twitter/$', 'TextSummarization.views.Twitter', name='twitter'),
    url(r'^Twitter/Upload$', 'TextSummarization.views.upload_file', name='upload_file'),
    url(r'^Twitter/Stream$', 'TextSummarization.views.stream_twitter', name='stream_twitter'),
    url(r'^Twitter/Load_Tweet$', 'TextSummarization.views.Load_Tweets', name='Load_Tweets'),
    url(r'^Twitter/Load_File$', 'TextSummarization.views.Load_File', name='Load_File'),
    url(r'^Twitter/Load_More$', 'TextSummarization.views.Load_More', name='Load_More'),
#     url(r'^Clustering/(?P<cluster_name>[ .a-zA-Z_0-9]+)/$', 'TextSummarization.views.cluster_docs', name='cluster_docs'),
    url(r'^admin/', include(admin.site.urls)),
)

# handler404 = error404