__author__ = 'Jasneet Sabharwal <jsabharw@sfu.ca>'

from django.conf.urls import patterns, url

from cluster import views

urlpatterns = patterns('',
                       url(r'^$', views.upload, name='upload'),
                       url(r'^cluster', views.cluster, name='cluster'),
                       url(r'^executeclustering', views.executeClustering, name='executeclustering'),
                       url(r'^getdata', views.getData, name='getdata'),
                       url(r'^upload-coordinates', views.uploadCoordinates, name='upload-coordinates'),
                       url(r'^get-concordance', views.getLangConcordance, name='get-concordance'))
