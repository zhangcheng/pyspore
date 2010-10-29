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


class SporeHeaders(SporeMiddleware):
    """
    middleware that sets the request's headers
    """

    def _set_header(self, request, key, value):
        self.request.header.append(key, value)

    def __call__(self, *args, **kwargs):
        self._set_header( request, 'Content-Type', spec.get_api_format() )
        for key, value in kwargs.iteritems():
            self._set_request(request, key, value)
        return self.request

