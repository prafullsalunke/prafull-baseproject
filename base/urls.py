from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Static serving for css images and stuff, for media (pics/videos), make different static serve
	(r'^nimda/doc/', include('django.contrib.admindocs.urls')),
	(r'^nimda/', admin.site.urls),
	(r'^static/(?P<path>.*)$', 'django.views.static.serve',
		{	
			'document_root': settings.SETTINGS_FILE_FOLDER.joinpath('../static'),
			'show_indexes': False
		}
	),
    url(r'^ajax/AjaxField/(?P<form_name>[\w-]+)/(?P<form_meta>[\w-]+)/$', 'customforms.ajaxfield.widget_url'),
	(r'', include('core.urls')),
    
    (r'^accounts/login/$',  login),
    (r'^accounts/logout/$', logout),

	# Example:

	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# (r'^admin/(.*)', admin.site.root),
)
