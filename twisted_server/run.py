# -*- coding: utf-8 -*-
#    Copyright 2005 Spike^ekipS <spikeekips@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import re, os.path, os, sys

from twisted.web2 import log, wsgi, resource, iweb
from twisted.internet import reactor

from django.core.handlers.wsgi import  WSGIHandler
from django.core.servers.basehttp import AdminMediaHandler

# default settings.
SSL_PRIVATE_KEY_PATH = None
LOG_STYLE = "apache"

for k, v in os.environ.items() :
    if k.startswith("DOT_") :
        locals()[k.replace("DOT_", "")] = v

if not os.path.isdir("../log") :
    os.mkdir("../log")

def write_pid (file_pid) :
    fd = file(file_pid, "w")
    fd.write(str(os.getpid()))
    fd.close()

def make_wsgi (req) :
    # twisted.web2 can not insert 'PATH_INFO' into environment.
    os.environ["PATH_INFO"] = req.path
    os.environ["SCRIPT_URL"] = req.path

    return wsgi.WSGIResource(AdminMediaHandler(WSGIHandler()))

class ArbitrarySettingsDecide (resource.Resource) :
    addSlash = True

    def locateChild (self, request, segments) :
        return self, ()

    def renderHTTP (self, request) :
        return make_wsgi(request)

LOG_FORMAT = "Call Type: %s | User From: %s | Header: %s | Status: %s | Byte Sent: %d | User-Agent: %s | Referer: %s"
LOG_FORMAT_APACHE = "%s - %s [%s] \"%s\" %s %d \"%s\" \"%s\""
RE_NOT_LOG = re.compile("\.(css|js|png|gif|jpg)$")

class AccessLoggingObserver (log.DefaultCommonAccessLoggingObserver) :

    def start (self, log_type="") :
        self.log_type = log_type
        log.DefaultCommonAccessLoggingObserver.start(self)

    def emit (self, eventDict) :
        if eventDict.get("interface") is not iweb.IRequest:
            return

        request = eventDict["request"]
        if RE_NOT_LOG.search(request.uri) :
            return
        response = eventDict["response"]
        loginfo = eventDict["loginfo"]
        firstLine = "%s %s HTTP/%s" %(
            request.method,
            request.uri,
            ".".join([str(x) for x in request.clientproto]))

        if self.log_type == "apache" :
            self.logMessage( \
                 LOG_FORMAT_APACHE %( \
                    request.remoteAddr.host, \
                    # XXX: Where to get user from? \
                    "-", \
                    self.logDateString( \
                         response.headers.getHeader("date", 0)), \
                    firstLine, \
                    response.code, \
                    loginfo.bytesSent, \
                    request.headers.getHeader("referer", "-"), \
                    request.headers.getHeader("user-agent", "-") \
                    ) \
                )
        else :
            self.logMessage( \
                LOG_FORMAT % (
                        request.headers.getRawHeaders("x-requested-with") or "",
                        request.remoteAddr.host,
                        # XXX: Where to get user from?
                        #self.logDateString(response.headers.getHeader("date", 0)),
                        firstLine,
                        response.code,
                        loginfo.bytesSent,
                        request.headers.getHeader("user-agent", "-"),
                        request.headers.getHeader("referer", "-"),
                    )
                )

# This part gets run when you run this file via: "twistd -noy demo.py"
if __name__ == "__builtin__":
    from twisted.application import service, strports
    from twisted.web2 import server, vhost
    from twisted.web2 import channel

    __port = os.getenv("ENV_WWW_PORT", "8000")

    choose_site = ArbitrarySettingsDecide()
    res = log.LogWrapperResource(choose_site)
    AccessLoggingObserver().start(LOG_STYLE)

    # Create the site and application objects
    site = server.Site(res)
    application = service.Application("test:%s" % __port)

    ##################################################
    # HTTP FastCGI, Serve it via standard HTTP on port 1026
    #s = strports.service("tcp:%s" % __port, channel.FastCGIFactory(site))
    #s.setServiceParent(application)

    # HTTPs, Serve it via standard HTTP on port 8081
    if not SSL_PRIVATE_KEY_PATH :
        # HTTP, Serve it via standard HTTP on port 8000
        s = strports.service("tcp:%s" % __port, channel.HTTPFactory(site))
        s.setServiceParent(application)
    else :
        from twisted.internet.ssl import DefaultOpenSSLContextFactory
        s = strports.service( \
            "ssl:%s:privateKey=%s" % (__port, SSL_PRIVATE_KEY_PATH), \
            channel.HTTPFactory(site) \
        )
        s.setServiceParent(application)


"""
Description
-----------


ChangeLog
---------


Usage
-----


"""

__author__ =  "Spike^ekipS <spikeekips@gmail.com>"

