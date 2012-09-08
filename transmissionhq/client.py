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
"""
A high-level abstraction of Transmission's RPC interfaces.

Exceptions:
    ConnectionError: The daemon can't be reached.
    TransmissionError: The daemon reports abuse.

Classes:
    TransmissionClient:
        >>> from transmissionhq.client import TransmissionClient
        >>> client = TransmissionClient()
        >>> list = client.torrents(ids=range(1,11), keys=['id','name','totalSize'])
        >>> list
        [ {u'totalSize': 123456789, u'id': 1, u'name': u'This is not a torrent'},
          # ...
          {u'totalSize': 987654321, u'id': 10, u'name': u"And this is surely not a pipe"}
        ]
        >>> list[3]['totalSize'].mr  # machine-readable
        1048576
        >>> list[3]['totalSize'].hr  # human-readable
        u'1.00 MiB'
        >>> s = client.session()
        >>> s['speed-limit-down'] = 50*1024
        >>> s['speed-limit-down-enabled'] = True
        >>> s.push()
"""

import os
from transmission import (Transmission, BadRequest)  # transmission-fluid
from helpers import TransmissionURL
from rpc import TransmissionRPC
import requests.exceptions
from operator import itemgetter


class ConnectionError(Exception): pass
class TransmissionError(Exception): pass

class TransmissionClient(Transmission):

    """Handle communication between user interface and daemon."""

    def __init__(self, url=None):
        """Create a new client instance.

        The url argument can be a TransmissionURL object or dict with any
        combination of the following keys:
            host, port, path, username, password, ssl
        """
        if url is None:
            url = TransmissionURL()
        Transmission.__init__(self, **url)
        self._cache = {}
        self._cache['session'] = TransmissionRPC('session', setter=self.session)
        self._cache['torrents'] = {}

    def _request(self, method, **kwargs):
        try:
            response = self.__call__(method, **kwargs)
        except (requests.ConnectionError, requests.Timeout) as err:
            raise ConnectionError("Can't connect to %s: %s" % (self.url, err))
        except BadRequest as err:
            raise TransmissionError(err)
        else:
            return response

    def session(self, **settings):
        """Get or set session settings.

        If keyword arguments are given, forward them to the daemon in a
        'session-set' request.  Otherwise, return all 'session-get' values in
        a TransmissionRPC instance.
        """
        if settings:
            self._request('session-set', **settings)
        else:
            self._cache['session'].update(self._request('session-get'))
            return self._cache['session']

    def _torrentsetter(self, **items):
        """ A callback provided to TransmissionRPC 'torrent' instances to send
        value changes back to the daemon."""
        return self._request('torrent-set', **items)

    def torrents(self, ids=None, keys=[]):
        """Get a list of torrents.

        Arguments:
            ids:  A list of torrent IDs.  Invalid IDs are ignored.
            keys: A list of 'torrent-get' keys.  (See rpc-spec.txt in the
                  Transmission docs.)  Invalid keys will be ignored.
        """

        if ids is None:
            param = { 'fields':keys }
        else:
            param = { 'ids':ids, 'fields':keys }

        # We need 'id' internally
        if 'id' not in param['fields']:
            param['fields'].append('id')

        tlist = self._request('torrent-get', **param)['torrents']
        # Update/Add requested torrents in our cache
        for t in tlist:
            try:
                self._cache['torrents'][t['id']].update(t)
            except KeyError:
                self._cache['torrents'][t['id']] = \
                    TransmissionRPC('torrent', t,
                                    setter=self._torrentsetter)
        # Return only requested torrents
        return [t for t in self._cache['torrents'].values() if ids is None or t['id'] in ids]

    def add_torrent(self, torrent):
        """Submit torrent via filepath, weblink or magnetlink.

        Return ID of the added torrent.  Raise TransmissionError on failure.
        """
        if os.path.exists(torrent):
            # torrent is a file; convert to absolute path or Transmission may not find it
            torrent = os.path.abspath(torrent)
        try:
            response = self._request('torrent-add', filename=torrent)
        except TransmissionError as err:
            raise TransmissionError('Could not add torrent %s: %s' % (torrent, err))
        return response['torrent-added']['id']

    def move_torrents(self, ids, location):
        """Move torrents to another directory.

        Arguments:
            ids: List of torrent IDs.
            location: Path to directory.
        """
        self._request('torrent-set-location', ids=ids, location=location, move=True)

    def delete_torrents(self, ids, delete_files=False):
        """Delete torrents.

        Arguments:
            ids: List of torrent IDs.
            delete_files: Delete torrents' files if True.
        """
        tlist = self.torrents(ids=ids, keys=['id'])
        if not tlist:
            raise TransmissionError('No torrents found')
        self._request('torrent-remove', ids=ids, delete_local_data=delete_files)
        for id in ids:  # Delete from internal cache
            del self._cache['torrents'][id]

    def upload_limit(self, limit=None, id=None):
        """Get or set global or torrent specific upload limit.

        Arguments:
            limit: Bytes per second.  Return current value if omitted.
            id:    A torrent ID.  Get or set global limit if omitted.
        """
        return self._rate_limit('up', limit, id)
    def download_limit(self, limit=None, id=None):
        """Get or set global or torrent specific download limit.

        Arguments:
            limit: Bytes per second.  Return current value if omitted.
            id:    A torrent ID.  Get or set global limit if omitted.
        """
        return self._rate_limit('down', limit, id)
    def _rate_limit(self, dir, limit, id):
        if id is None:  # Global limit
            session = self.session()
            if limit is True or limit is False:
                session['speed-limit-'+dir+'-enabled'].set(limit)
            elif type(limit) is int:
                session['speed-limit-'+dir].set(limit)
                session['speed-limit-'+dir+'-enabled'].set(True)
            session.push()
            session = self.session()
            if session['speed-limit-'+dir+'-enabled'].mr:
                return session['speed-limit-'+dir]
            else:
                return session['speed-limit-'+dir+'-enabled']

        elif type(id) is int:
            t = self.torrents(ids=[id], keys=[dir+'loadLimit', dir+'loadLimited'])[0]
            if limit is True or limit is False:
                t[dir+'loadLimited'].set(limit)
            elif type(limit) is int:
                t[dir+'loadLimit'].set(limit)
                t[dir+'loadLimited'].set(True)
            t.push()
            if t[dir+'loadLimited'].mr:
                return t[dir+'loadLimit']
            else:
                return t[dir+'loadLimited']

        elif type(id) is list:
            retvals = []
            for i in id:
                retvals.append(self._rate_limit(dir, limit, i))
            return retvals

        else:
            raise ValueError('Invalid ID: %s' % id)


