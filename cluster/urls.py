__author__ = 'Jasneet Sabharwal <jsabharw@sfu.ca>'

from django.conf.urls import patterns, url

from cluster import views

urlpatterns = patterns('',
                       url(r'^$', views.upload, name='upload'),
                       url(r'^cluster/(?P<sessionKey>.*)/', views.cluster, name='cluster'))