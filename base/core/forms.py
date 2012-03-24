from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import authenticate

import random
import datetime,time
import uuid
import re
import hashlib

from core.models import *
from fhurl import RequestForm, RequestModelForm
from customforms.ajaxfield import AjaxField

class SampleForm(forms.Form):
    employee = forms.CharField(required=True)
    ufile = forms.FileField(required=True)
   
    def __init__(self, *args, **kwargs):
        super(SampleForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        d = self.cleaned_data.get
        return None

    def clean_employee(self):
        if self.cleaned_data.get('employee') not in ['devendra', 'rane']:
            raise forms.ValidationError("Please Enter Correct Employee-ID")
        else:
            return self.cleaned_data.get('employee').title()

class SampleFhurl(RequestForm):
    name = forms.CharField(required=True)
    designation = forms.CharField(required=True)

    def init(self, fid, gid):
        self.fid = fid
        self.gid = gid

    def save(self):
        print "cleaned :", self.cleaned_data
        print "vars :", self.fid, self.gid
        return "OK"

class SampleModelFhurl(RequestModelForm):
    pass
    class Meta:
        model = SampleModel

class SampleAjaxForm(RequestForm):
    name = forms.CharField(required=True)
    mfield = AjaxField(conditional_list = [
        ('state', lambda req, x : [(s.id,s.name) for s in State.objects.all()]),
        ('city', lambda req, x : [(c.id, c.name) for c in City.objects.filter(state__id=x)]),
        ('some', lambda req, x : [(1,1),(2,2),(3,3),(4,4)]),
    ])
    AjaxField.register('mfield', mfield)
