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

import os.path
# supported spec file formats
import json
import yaml


class SporeSpec(dict):
    def __init__(self, url, *args, **kwargs):
        """
        Spore specification reader
        handle files adressed by path and optionally by protocol
        """
        dict.__init__(self)
        raw = self._get_raw(url )
        config = self._get_config(raw, url)
        # default & parameters configuration
        for default in config:
            self[default]=config[default]
        for overwrite in kwargs:
            self[overwrite]=config[overwrite]
        self._check_required()

    def _get_config(self, raw, url):
        config = {}
        format = os.path.split( url )[1].split(".")[1]
        if format in ["yaml","yml","json"]:
            try:
                config = __import__(format).load(raw)
            except Exception, e:
                raise Exception("couldn't parse config file: %s"%(e))
        else:
            raise Exception("format %s not recognized"%format)
        return config

    def _get_raw(self, url):
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
        return raw

    def _check_required(self):
        """
        checks required SPORE spec parameters
        """
        for param in ['api_format','api_base_url','methods']:
            if param not in self:
                raise Exception("missing required spore parameter : %s"%param)
        for method in self['methods'].itervalues():
            for methodparam in ['path','method']:
                if methodparam not in method:
                    raise Exception("missing required spore parameter : %s"%methodparam)

    def get_httpmethod(self, methodname):
        return str(self['methods'][methodname]['method'])

    def get_api_base_url(self):
        return str(self['api_base_url'])

    def get_method_path(self, methodname):
        return str(self['methods'][methodname]['path'])

    def get_api_format(self):
        """
        returns the list of authorized formats
        """
        return self['api_format']
