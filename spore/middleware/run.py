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

__author__ = "elishowk@nonutc.fr"

from spore.middleware import SporeMiddleware
from spore import response

#import urllib
import re

class SporeRun(SporeMiddleware):
    """
    required and last middleware executing request
    """
    def __call__(self, *args, **kwargs):
        """
        execute and put the request into a SporeResponse instance
        """
        #self.request.connection.request(
        #    self.spec.get_httpmethod(self.request.methodname),
        #    self.construct_url(**kwargs),
        #    self.request.body,
        #    self.request.headers
        #)
        return response.SporeResponse(self.request)

    def construct_url(self, **request_kw_args):
        """
        forms the request url
        """
        url = self.request.spec.get_method_path(self.methodname)
        required = self.request.spec.get_method_required(self.methodname)
        for k in required:
            if k not in request_kw_args: raise Exception("missing required arg %s"%k)
        #allargs = list( set(required) & set(self.spec.get_method_optional(self.methodname)))
        for key, value in request_kw_args:
            #if strict is True and key not in allargs: continue
            url = re.sub(r":%s"%key, value, url)
        url = re.sub(r"(:\w+/?)*$", "", url)
        return url
