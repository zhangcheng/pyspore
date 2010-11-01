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

__all__ = ['middleware','callback','sporespec','response']

from spore.middleware import *
from spore.callback import *
from spore import *

import httplib


class SporeRequest(object):
    def __init__(self, spec, methodname, **request_kw_args):
        """
        creates a request and prepares the middleware sta
        """
        self.spec = spec
        self.methodname = methodname
        self.host = self.spec.get_api_base_url()
        self.body = {}
        self.headers = {}
        self.connection = httplib.HTTPConnection(self.host)
        self.before = [run.SporeRun, body.SporeRequestBody, headers.SporeHeaders]
        self.callbacks = []

    def __call__(self, *args, **kwargs):
        """
        runs all middlewares
        kwargs are client argument of the request
        """
        # middleware, callbacks
        # dernier middleware == request()
        # si un middleware renvoit :
        ## un objet SporeResponse: stop execution middleware, passe aux callbacks
        ## un objet Callback : empile la CB dans la file.
        self.before.reverse()
        returnValue = None
        for middleware in self.before:
            returnValue = middleware(self)(*args, **kwargs)
            if isinstance(returnValue, response.SporeResponse): break
            if isinstance(returnValue, SporeCallback):
                self.callback += [returnValue]

        self.callbacks.reverse()
        for callback in self.callbacks:
            returnValue = callback(returnValue)
        return returnValue()

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

