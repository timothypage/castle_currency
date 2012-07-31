# -*- coding: utf-8 -*
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'currency.views.home', name='home'),
    # url(r'^currency/', include('currency.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^staff/console/', include(admin.site.urls)),
)