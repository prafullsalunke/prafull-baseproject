# imports #
from django.utils import simplejson
from django.conf import settings
from django.core.mail import send_mail
from django.db import models

#import solr
import logging
import re
import time
import datetime
import os
import hashlib
import csv, codecs, cStringIO

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

import urllib
import urllib2

import tempfile, zipfile
from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper

def group_by(lst, key, func=None):
    if not lst: return
    rdict = {}
    if not func:
        if type(lst[0]) == dict:
            for l in lst:
                if not rdict.get(l[key]): rdict[l[key]] = []
                rdict[l[key]].append(l)
        else:
            for l in lst:
                if not rdict.get(getattr(l,key)): rdict[getattr(l,key)] = []
                rdict[getattr(l,key)].append(l)
    else: #key is callable and so lst cannot be a dict #TODO: Handle class methods, static methods both
        for l in lst:
            v = getattr(getattr(l,key), func)()
            if not rdict.get(v): rdict[v] = []
            rdict[v].append(l)
            
    return rdict

def create_logger(name=None):
    if name is None:
        name = settings.SETTINGS_FILE_FOLDER.namebase
    logger = logging.getLogger(name)
    hdlr = logging.FileHandler(
        settings.SETTINGS_FILE_FOLDER.joinpath("%s.log" % name)
    )
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger

error_logger = create_logger("error")
response_logger = create_logger("response")

def errors_to_json(form_errors):
    content = dict((key, [unicode(v) for v in values]) for key, values in form_errors.items())
    response = ({ "success": False, "errors": content })
    return simplejson.dumps(response)

def get_image_path(instance, filename):
    now = datetime.datetime.now()
    monthdir = now.strftime("%Y-%m")
    newfilename = hashlib.md5(now.strftime("%I%M%S") + filename).hexdigest() + os.path.splitext(filename)[1]
    path_to_save = "uploads/%s/%s" % (monthdir, newfilename)
    return path_to_save

"""
import boto

def put_in_new_bucket(bucket_name, key_name, file_path):
    s3 = boto.connect_s3()
    bucket = s3.create_bucket(bucket_name)
    key = bucket.new_key(key_name)
    key.set_contents_from_filename(file_path)
    key.set_acl('public-read') 
    return "Ok"

def put_in_bucket(bucket_name, key_name, file_path):
    s3 = boto.connect_s3()
    bucket = s3.get_bucket(bucket_name)
    key = bucket.new_key(key_name)
    key.set_contents_from_filename(file_path)
    key.set_acl('public-read') 
    return "Ok"

def copy_file(bucket_name, key_name, file_path):
    s3 = boto.connect_s3()
    key = s3.get_bucket(bucket_name).get_key(key_name)
    key.get_contents_to_filename(file_path)
    return "Ok"

def move_file(from_bucket, from_key, to_bucket, to_key):
    s3 = boto.connect_s3()
    key = s3.get_bucket(from_bucket).get_key(from_key)
    new_key = key.copy(to_bucket, to_key)
    if new_key.exists:
        key.delete()
    return "Ok"

def delete_file(bucket_name, key_name):
    s3 = boto.connect_s3()
    key = s3.get_bucket(bucket_name).get_key(key_name)
    key.delete()
    return "Ok"
"""

"""
def solr_tags(fields, q='*:*'):
    s = solr.SolrConnection(settings.SOLR_ROOT)
    res = s.raw_query(q=q, wt='json', facet='true', facet_field=fields)
    result = simplejson.loads(res)['facet_counts']['facet_fields']
    r = []
    for k,v in result.items():
        r.extend(v)
    response = dict([(r[i],r[i+1]) for i in range(len(r)-1)[::2]])
    return response

def solr_paginator(q, start,rows):
    response = {}
    conn = solr.SolrConnection(settings.SOLR_ROOT)
    try:
        res = conn.query(q)
        numFound = int(res.results.numFound)
        results = res.next_batch(start=start,rows=rows).results
    except:
        numFound = 0
        results = []
    response['results'] = [dict(element) for element in results]
    response['count'] = numFound
    response['num_found'] = len(response['results'])
    response['has_prev'] = True
    response['has_next'] = True
    if start <= 0:
        response['has_prev'] = False
    if (start + rows) >= numFound:
        response['has_next'] = False
    return response

def add_data(data, include_fields=[]):
    if include_fields:
        for k,v in data.items():
            if k not in include_fields:
               data.pop(k) 
    solr_add(**data)

def solr_add(**data_dict):
    s = solr.SolrConnection(settings.SOLR_ROOT)
    print data_dict
    s.add(**data_dict)
    s.commit()
    s.close()

def solr_delete(id):
    s = solr.SolrConnection(settings.SOLR_ROOT)
    s.delete(id)
    s.commit()
    s.close()

def solr_search(q, fields=None, highlight=None,
                  score=True, sort=None, sort_order="asc", **params):
    s = solr.SolrConnection(settings.SOLR_ROOT)
    response = s.query(q, fields, highlight, score, sort, sort_order, **params)
    return response

def solr_tags(fields, q='*:*'):
    s = solr.SolrConnection(settings.SOLR_ROOT)
    res = s.raw_query(q=q, wt='json', facet='true', facet_field=fields)
    result = simplejson.loads(res)['facet_counts']['facet_fields']
    r = []
    for k,v in result.items():
        r.extend(v)
    response = dict([(r[i],r[i+1]) for i in range(len(r)-1)[::2]])
    return response

def solr_time(t):
    dt = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    tt = time.mktime(dt.timetuple())+1e-6*dt.microsecond
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(tt))
"""
#########   CSV Writer and Reader for any encoding ##################
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

############################################

def send_sms(to, msg, mask="ICICIPRU"):
    p = "http://enterprise.smsgupshup.com/GatewayAPI/rest"

    if len(to) > 10 and type(to) == type([]):
        register_openers()
        at_one_time = 100000

        if type(msg) != type([]):
            msg = [msg for i in range(len(to))]
        
        zipped = zip(to, msg)
        for bucket in [zipped[i:i+at_one_time] for i in range(0, len(zipped)) if i%at_one_time == 0]:
            csv.register_dialect('gupshup', delimiter=',', quoting=csv.QUOTE_ALL)
            filename = os.path.join("/tmp/", "%s.csv" % hashlib.md5(str(time.time())).hexdigest())
            file_stream = open(filename,'wb')
            writer = UnicodeWriter(file_stream, dialect=csv.get_dialect('gupshup'))
            writer.writerow(["PHONE","MESSAGE"])
            if type(msg) == type([]):
                for i_to, i_msg in bucket:
                    writer.writerow([i_to, "%s" % i_msg])
            
            file_stream.close()
            wfile_stream = open(filename,'rb')

            datagen, headers = multipart_encode({
                "file": wfile_stream, 
                'method' : 'xlsUpload',
                'filetype' : 'csv',
                'msg_type' : 'text',
                'mask' : mask,
                'v' : '1.1',
                'userid' : '2000058874',
                'password' : 'glitterfuck',
            })
            request = urllib2.Request(url=p, data=datagen, headers=headers)    
            res = urllib2.urlopen(request).read()
            response_logger.info("Response %s" % (res))

    else:
        if type(to) == type([]):
            to = ",".join(to)
        
        data = {
            'msg' : msg,
            'send_to' : to,
            'v' : '1.1',
            'userid' : '2000058874',
            'password' : 'glitterfuck',
            'msg_type' : 'text',
            'method' : 'sendMessage',
            'mask' : mask,
        }
        querystring = urllib.urlencode(data)
        request = urllib2.Request(url=p, data=querystring)    
        res = urllib2.urlopen(request).read()
        response_logger.info("Response %s" % (res))
    
    return res

def profile_type_only(*user_type):
    def _inner(fn):
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated():
                try:
                    up = request.user.userprofile
                except UserProfile.DoesNotExist:
                    raise PermissionDenied
                for ut in user_type:
                    if up.user_type == ut:
                        return fn(request, *args, **kwargs)
                raise PermissionDenied
            else:
                raise PermissionDenied
        return wraps(fn)(wrapped)
    return _inner

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&amp;", "&")
    s = s.replace("&quot;", "\"")
    return s

def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner

def send_file(request):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                                 
    """
    filename = __file__ # Select your file here.                                
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(filename)
    return response

def send_zipfile(request):
    """                                                                         
    Create a ZIP file on disk and transmit it in chunks of 8KB,                 
    without loading the whole file into memory. A similar approach can          
    be used for large dynamic PDF files.                                        
    """
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for index in range(10):
        filename = __file__ # Select your files here.                           
        archive.write(filename, 'file%d.txt' % index)
    archive.close()
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=test.zip'
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response
