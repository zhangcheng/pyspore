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
import sys
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
# supported deserialization
from xml.dom.minidom import parseString as sporexmlparser
from yaml import load as sporeyamlparser
from json import loads as sporejsonparser

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

class SporeAuth(object):
    pass

class SporeFinished(Warning):
    pass

class SporeFormat():
    def __init__(self, spec, bytes):
        """
        Data parser
        """
        self.spec = spec
        self.bytes = bytes

        if self.spec['declare']['api_format'] == "json":
            self.decode = sporejsonparser
        elif self.spec['declare']['api_format'] == "xml":
            self.decode = sporexmlparser
        elif self.spec['declare']['api_format'] == "yaml":
            self.decode = sporeyamlparser
        else:
            raise NotImplemented("api_format %s not recognized"%self.spec['declare']['api_format'])

    def decode(self, bytes):
        """
        default decode method
        """
        return bytes

    def __call__(self, *args, **kwargs):
        print self.decode(self.bytes)
        return self.decode(self.bytes)

class SporeResponse(Protocol):
    def __init__(self, spec, deferred):
        """
        Asynchrone data receiver and parser
        """
        self.deferred = deferred
        self.spec = spec
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
    def __init__(self,spec):
        Headers.__init__(self,
            {
                'User-Agent': ['Pyspore Client Example'],
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
        print self.url
        # twisted stuff
        agent = Agent(reactor)
        self.d = agent.request(
            str(self.spec['methods'][methodname]['method']),
            self.url,
            self.headers,
            self.body
        )
        self.d.addCallback(self.cbRequest)
        self.d.addBoth(self.cbShutdown)

    def __call__(self, *args, **kwargs):
        reactor.run()

    def cbRequest(self, response):
        """
        response is fired by Deferred()
        """
        print 'Response version:', response.version
        print 'Response code:', response.code
        print 'Response phrase:', response.phrase
        print 'Response headers:'
        print pformat(list(response.headers.getAllRawHeaders()))
        # response asynchrone handler
        deferred = Deferred()
        self.parser = SporeResponse(self.spec, deferred)
        response.deliverBody(self.parser)
        return deferred

    def cbShutdown(self, ignored):
        """
        Tells the reator request is finished
        """
        reactor.stop()
        #http://twistedmatrix.com/documents/current/core/howto/defer.html
        deserial = SporeFormat(self.spec, self.parser.content)
        deserial()

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

def usage():
    print "USAGE : python spore.py config_file_path"

if __name__ == "__main__":
    import getopt
    opts, args = getopt.getopt(sys.argv[1:],'')

    if len(args) < 1:
        usage()
        exit()

    configURL = args[0]

    try:
        spore = SporeCore(configURL)
    except Exception, exc:
        print exc
        usage()
        exit()

    print spore.spec
    # TODO : parse confFile for every method defined
    req = spore.public_timeline()
    print req
