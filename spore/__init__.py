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

from spore.middleware import *
from spore import *

import httplib
import urllib
import re

class SporeResponse(object):
    def __init__(self, spec, callbacks=None):
        self.spec = spec
        if callbacks is None:
            self.callbacks = []
        else:
            # loop and add_callbacks
            pass

    def add_callback(self):
        pass

    def __call__(self, httpresponse):
        return httpresponse.read()


class SporeRequest(object):
    def __init__(self, spec, methodname, **request_kw_args):
        """
        creates a request agent following spec
        """
        self.spec = spec
        self.methodname = methodname
        host = self.spec.get_api_base_url()
        self.connection = httplib.HTTPConnection(host)
        # add_middleware here

    def __call__(self, *args, **kwargs):
        """
        runs through all middlewares the request and returns the response
        """
        self.connection.request(
            self.spec.get_httpmethod(self.methodname),
            self.construct_url(),
            self.get_body(),
            self.get_headers()
        )
        resp = SporeResponse(self.spec)
        return resp(self.connection.getresponse())

    def get_body(self):
        return None

    def get_headers(self):
        return {}

    def add_middleware(self):
        pass

    def construct_url(self, **request_kw_args):
        """
        forms the request url
        """
        url = self.spec.get_method_path(self.methodname)
        regexp = ":([^/]*)"
        findall = re.split(regexp; url)
        while( $path =~ m!:([^/]*)!g ) {
            my $param = $1;
        }

        re =
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

