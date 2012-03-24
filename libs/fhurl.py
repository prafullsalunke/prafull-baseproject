from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils.translation import force_unicode
from django.core.urlresolvers import get_mod_func
from django.utils.functional import Promise
from django.template import RequestContext
from django.conf.urls.defaults import url
from datetime import datetime, date
from django.conf import settings
from django import forms
from django.forms.models import model_to_dict
import urllib2
try:
    import json
except ImportError:
    from django.utils import simplejson as json

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_unicode(o)
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%S')
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return super(JSONEncoder, self).default(o)

class JSONResponse(HttpResponse):
    def __init__(self, data):
        HttpResponse.__init__(
            self, content=json.dumps(data, cls=JSONEncoder),
            #mimetype="text/html",
        ) 

#might remove this method completely, no use case in mind
def get_form_representation(form):
    d = {}
    for field in form.fields:
        value = form.fields[field]
        dd = {}
        if value.label:
            dd["label"] = value.label.title()
        dd["help_text"] = value.help_text
        dd["required"] = value.required
        if field in form.initial:
            dd["initial"] = form.initial[field]
        if value.initial: dd["initial"] = value.initial
        d[field] = dd
    return d

class RequestModelForm(forms.ModelForm):
    def __init__(self, request, *args, **kw):
        super(RequestModelForm, self).__init__(*args, **kw)
        for form_name, f in self.base_fields.items():
            if f.__class__.__name__ == "AjaxField":
                for c in f.conditional_list:
                    fname = c[0]
                    self.fields[fname] = forms.ChoiceField(choices=(), required=False)
                f.request = request
                f.parent_form = self
        self.request = request

class RequestForm(forms.Form):
    def __init__(self, request, *args, **kw):
        super(RequestForm, self).__init__(*args, **kw)
        for form_name, f in self.base_fields.items():
            if f.__class__.__name__ == "AjaxField":
                for c in f.conditional_list:
                    fname = c[0]
                    self.fields[fname] = forms.ChoiceField(choices=(), required=False)
                f.request = request
                f.parent_form = self
        self.request = request

    # To initialize form either using a single field at
    # a time of using a dictionary
    def initialize(self, field=None, value=None, **kw):
        if field: self.fields[field].initial = value
        for k, v in kw.items():
            self.fields[k].initial = v
        return self

    # To initialize form either using a object or a dict
    def initialize_with_object(self, obj, *fields, **kw):
        for field in fields:
            self.fields[field].initial = getattr(obj, field)
        for ffield,ofield in kw.items():
            self.fields[ffield].initial = getattr(obj, ofield)
        return self

    def update_object(self, obj, *args, **kw):
        d = self.cleaned_data.get
        for arg in args:
            setattr(obj, arg, d(arg))
        for k, v in kw.items():
            setattr(obj, k, d(v))
        return obj

def form_handler(
    request, form_cls, require_login=False, block_get=False, json=False,
    next=None, template=None, login_url=None, success_template=None,
    validate_only=False, form_renderer=None, **kwargs
):
    next = next or (request.REQUEST.get("next"))
    json = json or (request.REQUEST.get("json") == "true")
    validate_only = validate_only or (request.REQUEST.get("validate_only") == "true")
    login_url = login_url or request.REQUEST.get("login_url") or getattr(settings, "LOGIN_URL", "/accounts/login/")
    
    if isinstance(form_cls, basestring):
        # can take form_cls of the form: "project.app.forms.FormName"
        mod_name, form_name = get_mod_func(form_cls)
        form_cls = getattr(__import__(mod_name, {}, {}, ['']), form_name)

    # Check Logged in status
    if require_login:
        logged_in = False
        if callable(require_login): 
            logged_in = require_login(request)
        else:
            logged_in = request.user.is_authenticated()
        if not logged_in:
            redirect_url = "%s?next=%s" % (login_url, urllib2.quote(request.get_full_path()))
            if json:
                return JSONResponse({ 'success': False, 'redirect': redirect_url })
            else:
                return HttpResponseRedirect(redirect_url)

    #Check block get
    if block_get and request.method != "POST":
        raise Http404("Only Post Allowed")

    # render for a GET request
    if request.method == "GET":
        form = get_form(form_cls, request, with_data=False, **kwargs)
        if template:
            if json:
                rendered_form = render_to_string(
                    template, {'form':form}, context_instance=RequestContext(request)
                )
                return JSONResponse({'form':rendered_form}) #show we send back the kwargs also?
            else:
                return render_to_response(
                    template, {"form": form}, context_instance=RequestContext(request)
                )
        #if template is not present, it has to be a json call
        else:
            if form_renderer:
                rendered_form = getattr(form, form_renderer)() # form.as_table, form.as_ul etc.
                return JSONResponse({'form':rendered_form}) #show we send back the kwargs also?
            else:
                return JSONResponse(get_form_representation(form))
   

    #with request method as POST
    form = get_form(form_cls, request, with_data=True, **kwargs)
    
    #Form validation
    if form.is_valid():
        if validate_only: # return if its only for validation, validate only assumes json=True
            return JSONResponse({"valid": True, "errors": {}})
        resp = form.save()
        if json: 
            #The form must return a json serializable dictionary
            return JSONResponse({
                'success': True,
                'response': resp
            })
        else:
            if next: return HttpResponseRedirect(next)
            if isinstance(resp, HttpResponse): return resp
            if success_template or template:
                #get success_template to render after successfull save or use the request GET template
                template_to_render = success_template or template
                return render_to_response(
                    template_to_render, {"form": form, 'saved' : resp}, context_instance=RequestContext(request)
                )
   
    else:
        errors = form.errors
        if validate_only:
            return JSONResponse({ "errors": errors, "valid": False})
        else:
            if json:
                return JSONResponse({ 'success': False, 'errors': form.errors })
            if template:
                return render_to_response(
                    template, {"form": form}, context_instance=RequestContext(request)
                )
    
def get_form(form_cls, request, with_data=False, **kwargs):
    form = form_cls(request)
    form.next = next
    if with_data:
        form.data = request.REQUEST
        form.files = request.FILES
        form.is_bound = True
    if hasattr(form, "init"):
        form.init(**kwargs)
    return form

def fhurl(reg, form_cls, decorator=lambda x: x, **kw):
    name = kw.pop("name", None)
    kw["form_cls"] = form_cls
    return url(reg, decorator(form_handler), kw, name=name)
