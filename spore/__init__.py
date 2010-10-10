#!/usr/bin/python

# -*- coding: utf-8 -*-
#  Copyright (C) 2010 Elias Showk
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__="elishowk@nonutc.fr"

__all__ = ['middleware']

from pprint import pformat

# SporeBody
from zope.interface import implements
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer

# SporeRequest and SporeParser
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
# SporeHeaders
from twisted.web.http_headers import Headers

# supported spec file formats
import json
import yaml

from spore.middleware import *

class SporeSpec(dict):
    def __init__(self,url):
        """
        Spore reader
        handle files adressed by path and optionally by protocol
        """
        dict.__init__(self)
        format = url.split(".")[1]
        config = {}
        raw = ""
        try:
            if url[:7] == "file://":
                url = url[7:]
            raw = open(url)
        except:
            try:
                import urllib2
                raw = urllib2.urlopen(url).read()
            except  Exception, e:
                raise Exception("couldn't open %s: %s"%(url,e))

        if format in ["yaml","yml","json"]:
            try:
                config = __import__(format).load(raw)
            except Exception, e:
                raise Exception("couldn't parse config file: %s"%(e))
        else:
            raise NotImplemented("format %s not recognized"%format)

        for x in config:
            self[x]=config[x]


class SporeRequestBody(object):
    implements(IBodyProducer)

    def __init__(self, spec, body):
        self.spec = spec
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass



class SporeResponse(Protocol):
    def __init__(self, request, deferred):
        """
        Asynchrone data receiver and parser
        """
        self.deferred = deferred
        self.request = request
        self.content = ""


    def dataReceived(self, bytes):
        """
        Callback on the data received event
        """
        self.content += bytes

    def connectionLost(self, reason):
        """
        End of the request attached to the parser
        """
        #print 'Finished receiving body: ', reason.getErrorMessage()
        self.deferred.callback(None)


class SporeHeaders(Headers):
    """
    extends twisted.web.http_headers.Headers
    """
    def __init__(self, spec):
        Headers.__init__(self,
            {
                'User-Agent': ['pyspore'],
                'Content-Type': [str(spec['declare']['api_format'])]
            }
        )

class SporeRequest(object):
    def __init__(self, spec, methodname):
        """
        creates a request agent following spec
        """
        self.spec = spec
        self.methodname = methodname
        self.headers = SporeHeaders(self.spec)
        # TODO body and authentication
        self.body = None
        self.url = self._geturl()
        # twisted agent stuff
        agent = Agent(reactor)
        self.request = agent.request(
            str(self.spec['methods'][methodname]['method']),
            self.url,
            self.headers,
            self.body
        )
        self.request.addCallback(self.cbRequest)
        self.request.addBoth(self.cbShutdown)

    def __call__(self, *args, **kwargs):
        """
        before request middlewares
        then run !
        """
        reactor.run()

    def cbRequest(self, response):
        """
        base callback with response object
        calls chained middlewares

        response is fired by Deferred()
        http://twistedmatrix.com/documents/current/core/howto/defer.html
        """
        self.twistedresponse = response
        print 'Response version:', response.version
        print 'Response code:', response.code
        print 'Response phrase:', response.phrase
        #print 'Response headers:'
        #print pformat(list(response.headers.getAllRawHeaders()))
        # response asynchrone handler
        deferred = Deferred()
        self.sporeresponse = SporeResponse(self, deferred)
        response.deliverBody(self.sporeresponse)
        return deferred

    def cbShutdown(self, ignored):
        """
        Tells the reator request is finished
        """
        reactor.stop()
        self.sporeresponse()

    def _geturl(self):
        """
        forms the request url
        """
        url = self.spec['declare']['api_base_url'] + self.spec['methods'][self.methodname]['path']
        if self.spec['declare']['api_format_mode'] == 'append':
            return str( url + "." + self.spec['declare']['api_format'])
        else:
            return str(url)

class SporeCore(object):
    def __init__(self, path):
        self.new_from_spec(path)

    def new_from_spec(self, path):
        self.spec = SporeSpec(path)
        for methodname, methodspec in self.spec['methods'].iteritems():
            setattr( self, methodname, SporeRequest(self.spec, methodname) )

