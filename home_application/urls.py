# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'home'),
    (r'^dev-guide/$', 'dev_guide'),
    (r'^contactus/$', 'contactus'),
    (r'^api/test/$', 'test'),
    (r'^history/$', 'history'),
    (r'^performance/$', 'performance'),
    (r'^get_set/$', 'get_set'),
    (r'^get_biz/$', 'get_biz'),
    (r'^search_host/$', 'get_host')
)
