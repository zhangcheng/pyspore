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
        elif format in ["xml"]:
            raise NotImplemented()
        else:
            raise Exception("format %s not recognized"%format)
            
        for x in config:
            self[x]=config[x]
                   

class SporeBody(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class SporeParser(Protocol):
    def __init__(self, finished, format):
        """
        """
        self.finished = finished
        self.format = format

    def dataReceived(self, bytes):
        print bytes

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        self.finished.callback(None)

    def _getFormat(name):
        """
        module import and return
        """
        pass

class SporeHeaders(Headers):
    def __init__(self,spec):
        Headers.__init__(self,
            {
                'User-Agent': ['Pynet-hhtp-api Client Example'],
                'Content-Type': ['application/json']
            }
        )

class SporeRequest(object):
    def __init__(self, spec, headers, parserclass, body=None):
        """
        creates a request agent following spec
        """
        self.format = json
        self.parserclass = parserclass
        agent = Agent(reactor)
        self.d = agent.request(
            'GET',
            'http://api.twitter.com/1/statuses/public_timeline',
            headers,
            body)
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
        # asynch handler
        finished = Deferred()
        response.deliverBody(self.parserclass(finished, self.format))
        return finished

    def cbShutdown(self, ignored):
        reactor.stop()


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
        config = SporeSpec(configURL)
    except Exception, exc:
        print exc
        usage()
        exit()
        
    print config
    # TODO : parse confFile and init every request
    head = SporeHeaders(config)
    SporeRequest(config, head, SporeParser)
