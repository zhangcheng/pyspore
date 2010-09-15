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

# supported deserialization
import json
import yaml
#import xml

class SporeSpec(dict):
    def __init__(self,url):
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

class SporeParser(Protocol):
    def __init__(self, spec, deferred):
        """
        Asynchrone data receiver and parser
        """
        self.deferred = deferred
        self.spec = spec

        if self.spec['declare']['api_format'] == "json":
            self._getdecoder("json", "loads")

        elif self.spec['declare']['api_format'] == "xml":
            self._getdecoder("xml.dom.minidom", "parseString")

        elif self.spec['declare']['api_format'] == "yaml":
            self._getdecoder("yaml", "load")
        else:
            raise NotImplemented("api_format %s not recognized"%self.spec['declare']['api_format'])
        print self.decode

    def dataReceived(self, bytes):
        print "dataReceived"
        print bytes
        self.decode(bytes)

    def connectionLost(self, reason):
        print 'Finished receiving body: ', reason.getErrorMessage()
        self.deferred.callback(None)

    def decode(self, bytes):
        """
        default decode method
        """
        print bytes

    def _getdecoder(self, module, function):
        """
        module import and init the decode method
        """
        try:
            self.decode = __import__(module, globals(), locals(), [function], -1)
        except Exception, e:
            raise Exception("couldn't get spore parser : %s"%(e))

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

        agent = Agent(reactor)
        self.d = agent.request(
            str(self.spec['methods'][methodname]['method']),
            self.url,
            self.headers,
            self.body
        )
        self.d.addCallback(self.cbRequest)
        self.d.addBoth(self.cbShutdown)
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
        response.deliverBody(SporeParser(self.spec, deferred))
        return deferred

    def cbShutdown(self, ignored):
        """
        Tells the reator request is finished
        """
        reactor.stop()

    def _geturl(self):
        """
        forms the request url
        """
        if self.spec['declare']['api_format_mode'] == 'append':
            return str(self.spec['declare']['api_base_url'] +  self.spec['methods'][self.methodname]['path'] + "." + self.spec['declare']['api_format'])
        else:
            return str(self.spec['declare']['api_base_url'] +  self.spec['methods'][self.methodname]['path'])

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
        spec = SporeSpec(configURL)
    except Exception, exc:
        print exc
        usage()
        exit()

    print spec
    # TODO : parse confFile for every method defined
    SporeRequest(spec, "public_timeline")
