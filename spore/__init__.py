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

__all__ = ['middleware','sporespec']

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
from spore import *


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
        print "dataReceived..."
        print bytes
        self.content += bytes

    def connectionLost(self, reason):
        """
        End of the request
        """
        print 'Finished receiving body: ', reason.getErrorMessage()
        self.deferred.callback(None)


class SporeHeaders(Headers):
    """
    extends twisted.web.http_headers.Headers
    """
    def __init__(self, spec):
        Headers.__init__(self,
            {
                'User-Agent': ['pyspore'],
                'Content-Type': [spec.get_api_format()]
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
        self.url = self._get_url()
        self.callbacks = []
        # twisted agent stuff
        agent = Agent(reactor)
        self.request = agent.request(
            str(self.spec.get_httpmethod(self.methodname)),
            self.url,
            self.headers,
            self.body
        )
        self.request.addCallback(self.cb_request)
        self.request.addBoth(self.cb_shutdown)

    def __call__(self, *args, **kwargs):
        """
        runs the request
        """
        reactor.run()

    def _cb_request(self, response):
        """
        base callback with response object
        calls chained middlewares

        response is fired by Deferred()
        http://twistedmatrix.com/documents/current/core/howto/defer.html
        """
        #self.twistedresponse = response
        print 'Response version:', response.version
        print 'Response code:', response.code
        print 'Response phrase:', response.phrase
        #print 'Response headers:'
        #print pformat(list(response.headers.getAllRawHeaders()))
        # response asynchrone handler
        deferred = Deferred()
        self.response = SporeResponse(self, deferred)
        response.deliverBody(self.response)
        return deferred

    def _cb_shutdown(self, ignored):
        """
        Tells the reator request is finished
        """
        for cb in reverse(self.callbacks):
            cb(self.response)
        reactor.stop()

    def _get_url(self):
        """
        forms the request url
        """
        url = self.spec.get_api_base_url() + self.spec.get_method_path(self.methodname)
        if self.spec.api_format_mode() == 'append':
            return url + "." + self.spec.api_format_mode()
        else:
            return url

class SporeCore(object):
    def __init__(self, path, *args, **kwargs):
        """
        optional arguments to overwrite specification contents
        """
        self.new_from_spec(path, *args, **kwargs)

    def new_from_spec(self, path, *args, **kwargs):
        """
        attach to SporeCore callable SporeRequest read from the spec
        """
        self.spec = sporespec.SporeSpec(path, *args, **kwargs)
        for methodname, methodspec in self.spec['methods'].iteritems():
            setattr( self, methodname, SporeRequest(self.spec, methodname) )

