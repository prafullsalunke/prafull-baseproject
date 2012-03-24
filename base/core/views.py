import datetime
import hashlib
import logging

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core import serializers
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from django.contrib.auth import authenticate, login
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from core.forms import *
from core.models import *
from customdb.customquery import sqltojson, sqltodict, executesql
from xl2python import Xl2Python

def show_html(request, filename):
    return render_to_response("core/%s.html" % (filename), { },
        context_instance=RequestContext(request)
    )

upload_field_map = [
    'agent_id',
    ('mobile','int'),
    ('trigger_date', 'datetime','%Y-%m-%d %H:%M:%S'),   # Datetime field
]
class Uploader(Xl2Python):
    pass

@login_required
def rate(request, eid=None):
    print eid
    if request.POST:
        sform = SampleForm(request.POST, request.FILES)
        if sform.is_valid():
        
            xlm = Uploader(upload_field_map, request.FILES['ufile'])
            if xlm.is_valid():
                print "CLEANED => ", xlm.cleaned_data
            else:
                print "ERRORS => ", xlm.errors
            
            eid = sform.cleaned_data['employee']
            return HttpResponseRedirect("/rate/%s/" % eid)
    else:
        sform = SampleForm()
    return render_to_response("core/sample_form.html",
        { 
            'form' : sform,
        },
        context_instance=RequestContext(request)
    )

def ajax_demo(request):
    form = SampleAjaxForm(request)
    return render_to_response("core/sample_form.html",
        {
            'form' : form,
        },
        context_instance=RequestContext(request)
    )
