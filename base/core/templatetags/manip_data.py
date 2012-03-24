from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.utils.encoding import force_unicode, iri_to_uri
import simplejson
import datetime
import time
import os

from core.models import *
register = template.Library()

@register.filter
@stringfilter
def get_photo(value,arg):
    """TODO: Does Something """
    v = os.path.splitext(value)
    newname = "%s%s%s" % (v[0],arg,v[1])
    return newname

@register.filter
@stringfilter
def split_str(value,arg):
    """ Returns the first arg elements of the string """
    return value[:arg]

@register.filter
def maketable(element):
    """
    Makes Table given a list of lists of data. The data is html escaped.
    table data can be of any form other than [{}, abc]/({}, abc)

    Each tr can be given custom attributes by appending a dictionary of params before it.
    Each td can be given custom attributes by passing a list/tuple of the form [params, value] where params is a dict like {"colspan":2}
    egs.
    1. Without any styling
    li = [[1, "yo"], ["gracious", "priest"]]
    {{li|maketable}} -> <tr> <td> 1 </td> <td> yo </td> </tr> <tr> <td> gracious </td> <td> priest </td> </tr>

    2. With styling to a row
    li = [[{"class":"row"}, ["myname", 2], 23.5]]
    {{li|maketable}} -> <tr class="row"> <td> ['myname', 2] </td> <td> 23.5 </td> </tr>

    3. With styling to a td element and a row.
    li = [[{"style":"clear:both;"}, [{"colspan":2}, "Username"]]
    {{li|maketable}} -> <tr style="clear:both;"> <td colspan="2"> Username </td> </tr>
    
    """

    html = u""
    print element
    for row in element:
        html += u"""
<tr """
        if type(row[0]) == type({}):
            for k,v in row[0].items():
                html += u'%s="%s" ' %(k,v)
            html += u'>'
            row = row[1:]
        else:
            html += u'>'
        
        for ele in row:

            tdvalue = ele
            if type(ele) in [type([]), tuple]:
                try:
                    params, val = ele # If you error here, it means you have packed too many elements in the list / tuple
                    tdvalue = val
                except ValueError:
                    params = {}
                    
                html += """
    <td """
                try:
                    for k,v in params.items():
                        html += u'%s="%s" ' %(k,v)
                except AttributeError:
                    tdvalue = ele
                
                html += u'>'
                
            else:
                html += """
    <td> """
            html += escape(str(tdvalue))
            html += " </td>"

        html += """
</tr> """

    return mark_safe(html)

@register.filter
@stringfilter
def commator(value, price=""):
    """ adds commas to a number in indian 1234556.234|commator -> Rs. 12,34,556.234
    123456|commator:auto -> Rs. 1.23 lac.
    """
    li = value.split(".")
    value = li[0]
    try:
        rest = li[1]
    except IndexError:
        rest = "00"

    strval = value[::-1]
    
    if strval:
        strnew = strval[0]
        strval = strval[1:]

    for i in range(len(strval)):
            if i % 2 == 1:
                strnew += strval[i] + ","
            else:
                strnew += strval[i]
    strret = strnew[::-1]
    if rest:
        strret += ".%s" %rest

    pricedi = collections.OrderedDict([("none",""),("thousand","K."), ("lakh","lac."), ("crore","cr."), ("arab","ar."), ("kharab","khr."), ("neel","nl."), ("padma","pd."), ("shankh","shk.")])

    suffix = ""
    if price=="auto":
        li = strret.split(",")
        suffix = pricedi.values()[len(li)-1]
        strret = li[0]
        if len(li) > 1:
            strret+="."+li[1][:2]
    elif price in pricedi.keys():
        #TODO: Yet to implement
        li = strret.split(",")
        iter = -1
        for k,v in pricedi:
            iter+=1
            if k == price:
                val = v
                break
        if iter>0:
            strret = "".join(li[:0-iter]) +"." +li[0-iter][:2]
    else:
        pass
    strret = u"\u20B9. "+strret+" %s" %suffix
    return strret

@register.filter
@stringfilter
def jsondict(value):
    if not value:
        return ""
    else:
        return simplejson.loads(value).items()

@register.filter
@stringfilter
def jsonize(value):
    if not value:
        return ""
    else:
        return simplejson.loads(value)

@register.filter
def lookup(value, arg):
    return value.get(arg)

@register.filter
def make_dict(value):
    return value.split(",")

@register.filter
@stringfilter
def contains(value, arg):
    if value.find(arg) < 0:
        return False
    else:
        return True

@register.filter
def get_age(date):
    dt = datetime.datetime.now()
    delta = dt - date
    return str(delta.days)
