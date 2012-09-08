########################################################################
# This file is part of transmission-hq.                                #
#                                                                      #
# This program is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details:                         #
# http://www.gnu.org/licenses/gpl-3.0.txt                              #
########################################################################

class TransmissionURL(dict):

    """Parse Transmission daemon URL.

    If argument is a string or dict it is expected to be an URL that points to
    the RPC interface of a Transmission daemon.  Valid dict keys are: host,
    port, path, username, password and ssl.  If parts are missing, their
    defaults will be filled in.  If argument is None, the default URL will be
    used.
    """

    def __init__(self, url_str=None, **url_dict):
        super(TransmissionURL, self)
        defaults = { 'host':'localhost', 'port':9091, 'path':'/transmission/rpc',
                     'ssl':False, 'username':'', 'password':'' }
        self.update(defaults)
        if url_str is not None:
            self.update(url_str)
        if url_dict:
            self.update(url_dict)

    def update(self, other):
        try:
            self._parse(other)
        except AttributeError:
            try:
                dict.update(self, other)
            except TypeError:
                pass
        self['port'] = int(self['port'])

    def _parse(self, urltxt):
        if urltxt.count('://'):
            protocol, urltxt = urltxt.split('://')
            self['ssl'] = protocol == 'https'
        if urltxt.count('@') == 1:
            auth, urltxt = urltxt.split('@')
            if auth.count(':'):
                self['username'], self['password']= auth.split(':', 1)
            else:
                self['username'] = auth
        if urltxt.count('/') >= 1:
            urltxt, self['path'] = urltxt.split('/', 1)
            self['path'] = '/' + self['path']
        if urltxt.count(':') == 1:
            self['host'], self['port'] = urltxt.split(':')
        else:
            self['host'] = urltxt

    def __str__(self):
        auth = ''
        if self['username'] and self['password']:
            auth = '%s:%s@' % (self['username'], '***')
        elif self['username']:
            auth = '%s@' % self['username']
        string = 'http%s://%s%s:%s%s' % (('','s')[self['ssl']], auth,
                                         self['host'], self['port'],
                                         self['path'])
        return string

