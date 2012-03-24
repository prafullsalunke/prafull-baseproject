import hashlib
import logging
import struct
import time

from django.utils.encoding import smart_str, smart_unicode


import drlog

def get_request_id(request):
    """
    Create a unique tag for the request, to make it easier to follow its log 
    entries.
    """

    s = hashlib.sha1()
    s.update(str(time.time()))
    s.update(request.META['REMOTE_ADDR'])
    s.update(request.META['SERVER_NAME'])
    s.update(request.get_full_path())
    h = s.hexdigest()
    l = long(h, 16)

    # shortening courtesy of Ian Bicking by way of ASPN
    tag = struct.pack('d', l).encode('base64').replace('\n', '').strip('=')
    return tag


def configure(request):
    # store the request, of course
    drlog.REQUEST_CONTEXT.request = request
    
    # To track the request's log entries, they need a unique identifier.
    # If Apache's mod_unique_id is in use, use that. Otherwise create one
    # using information about the request.
    if request.META.has_key('UNIQUE_ID'):
        drlog.REQUEST_CONTEXT.request_id = request.META['UNIQUE_ID']
    else:
        drlog.REQUEST_CONTEXT.request_id = get_request_id(request)

include_keys = [
    'HTTP_REFERER',
    'PATH_INFO',
    'SERVER_PROTOCOL',
    'SERVER_SOFTWARE',
    'SCRIPT_NAME',
    'REQUEST_METHOD',
    'QUERY_STRING',
    'SERVER_NAME',
    'CONTENT_TYPE',
    'HTTP_KEEP_ALIVE',
    'wsgi.url_scheme',
    'CONTENT_LENGTH',
    'HTTP_USER_AGENT',
    'HTTP_HOST',
    'REMOTE_HOST',
    'HTTP_ACCEPT_ENCODING',
    'LESSOPEN',
    'source',
    'HTTP_X_FORWARDED_FOR',
]

def log_query_object(obj,prefix):
    l_str = ''
    for o in obj.keys():
        if o == 'password': continue
        for k in obj.getlist(o):
            #print prefix + "__"  + o + "=" + k
            if type(k) == type(u''):
                l_str += prefix + "__"  + str(o) + "=" + k.encode('utf-8') + " || "
            else:
                l_str += prefix + "__"  + str(o) + "=" + k + " || "
    return l_str

import threading
store = threading.local()
store.l_str = ""
def log_object(obj,prefix, include_keys=[]):
    if not hasattr(store, 'l_str'):
        store.l_str = ""
    
    obj_str = '' 
    if type(obj) == type({}):
        for k,v in obj.items():
            #print str(k)
            if str(k) in include_keys or not include_keys:
                if type(v) != type({}) and type(v) != type([]) and type(v) != type(()):
                    if type(v) == type(u''):
                        store.l_str += prefix + "__" + k + " = " + v.encode('utf-8') + " || "
                    else:
                        store.l_str += prefix + "__" + k + " = " + str(v) + " || "
                else:
                    log_object(v, prefix + "__" +  k, include_keys)
            else:
                pass
    if type(obj) == type([]):
        j = 0
        for i in obj:
            if type(i) != type({}) and type(i) != type([]) and type(i) != type(()):
                if type(i) == type(u''):
                    store.l_str += prefix + "__" + str(j) + " = " + i.encode('utf-8') + " || "
                else:
                    store.l_str += prefix + "__" + str(j) + " = " + str(i) + " || "
            else:
                log_object(i, prefix + "__" + str(j), include_keys)
            j = j + 1
    return store.l_str


class RequestLoggingMiddleware(object):
    """
    RequestLoggingMiddleware configures a logging context for each request. It
    should be installed first in your MIDDLEWARE_CLASSES setting, so that the
    request information is available to logging statements as early as 
    possible.
    """
    def __init__(self):
        super(RequestLoggingMiddleware, self).__init__()
    
    def process_request(self, request):
        if (request.META.get('HTTP_REFERER','').find('/static/') >= 0) or (request.META['PATH_INFO'].find('/static/') >= 0):
            return None
        configure(request)
        log_data = "sessionid = " + request.COOKIES.get('sessionid','')
        if hasattr(request, 'user'):
            if request.user:
                log_data += " || userid = " + request.user['id']
        try:
            if request.POST:
                log_data = log_data.encode('utf-8')
                log_data += " || " + log_query_object(request.POST, 'requestpost')
            if request.GET: 
                log_data = log_data.encode('utf-8')
                log_data += " || " + log_query_object(request.GET, 'requestget')
            
            if request.COOKIES.get('sessionid'):
                log_data = log_data.encode('utf-8')
                log_data += " || " + log_object(request.COOKIES['sessionid'], 'requestsession')
            
            log_data += " || " + log_object(request.META, 'requestmeta', include_keys)
        except Exception,e:
            log_data += "|| LOGGING_ERROR=" + str(e)
            pass

        log_data += ""
        drlog.logging.info(log_data)
        log_data = ""
        store.l_str = ""
        return None

    def process_response(self, request, response):
        return response

    def process_exception(self, request, exception):
        return None
