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

class SporeResponse(SporeMiddleware):
    """
    calling it return the response string
    """
    def __init__(self, request):
        """
        overwrites default SporeMiddleware adding the response bytes
        """
        SporeMiddleware.__init__(self, request)
        #self.bytes = self.request.connection.getresponse().read()
        self.bytes = "hello world"


    def __call__(self, *args, **kwargs):
        return self.bytes
