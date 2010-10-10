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
__all__ = ['format', 'auth']

class SporeMiddleware(object):
    """
    Wrapper of a request
    Interface before and after method
    """
    def __init__(self, request, spec, *args, **kwargs):
        self.request = request
        self.spec = spec
        for name in set(dir(request)) - set(dir(self)):
            setattr(self, name, getattr(request, name))

    def __call__(self, *args, **kwargs):
        """
        A do-nothing wrapper
        """
        return self.request(*args, **kwargs)

    #def response_cb(self, callback):
        """
        a do-nothing callback
        """
    #    return callback(*arg, **kwargs)
