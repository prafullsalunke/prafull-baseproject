from django.conf.urls.defaults import patterns, url, include
from django.views.generic.simple import direct_to_template

from fhurl import fhurl
from core.forms import *

urlpatterns = patterns('core.views',
    #url for testing flat pages
    url(r'^html/(?P<filename>[\w-]+).html$', 'show_html'),
    
    url(r'^rate/(?P<eid>\w+)/$', 'rate'),
    url(r'^upload/$', 'upload'),
    url(r'^ajax-demo/$', 'ajax_demo'),

    fhurl(r'^fhurl/(?P<fid>\w+)/(?P<gid>\w+)/$', SampleFhurl, template="core/sample_form.html"), 
    fhurl(r'^mfhurl/(?P<fid>\w+)/(?P<gid>\w+)/$', SampleModelFhurl, template="core/sample_form.html"),
)
