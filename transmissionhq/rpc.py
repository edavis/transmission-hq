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
A txt2python translation of Transmission's rpc-spec.txt.

Exceptions:
    TransmissionRPCError

Classes:
    TransmissionRPCValue: An extension to any value like str/int/float/etc.
    TransmissionRPC: Basically a dict of TransmissionRPCValues.
"""

import os
import re
from rpcspec import RPC
from constants import (ENCODING,
                       BYTE_SYMBOLS, BYTE_SIZES,
                       RE_HOMEDIR, RE_ONE)

class TransmissionRPCError(Exception): pass

class TransmissionRPCValue(object):

    """Maintain one value according to its specifications in rpcspec.py."""

    def __init__(self, key, value=None, **spec):
        """Initialize new TransmissionRPCValue.

        Arguments:
            key: A description. Simply use the key of the specs.
            value: An optional normal str/int/float/etc value.
            spec: A dictionary with the following keys:
                type: One of float, ratio, int, str, percent, boolean,
                      path_dir, path_file, url, bytes_size, bytes_rate, date,
                      timespan, dict or list.
                mutable: True if value can be changed, False otherwise.
                onupdate: See onupdate method.
                onwrite: See onwrite method.
                prettify: See prettify method.
                version: TODO
        """

        self._key = key
        self._type = spec['type']
        self.mutable = spec['mutable']
        self.needs_push = False

        self._hooks = {
            'onupdate': lambda v: v,
            'onwrite': lambda v: v,
            'prettify': self._std_prettify
        }
        for name in ('onupdate','onwrite','prettify'):
            if name in spec:
                self._hooks[name] = spec[name]

        self._value = self.onupdate(value)
        self._value_pretty = self.prettify(self._value)
#        print "Created new TransmissionRPCValue: %s" % repr(self)

    def update(self, value):
        """This is supposed to be called whenever the DAEMON changes our value
        so we can assimilate it properly."""
        new_value = self.onupdate(value)
        if new_value != self._value:
            self._value = new_value
            self._value_pretty = self.prettify(self._value)
#            print 'daemon says: %s=%s' % (self._key, self._value)

    def set(self, new_value):
        """This is supposed to be called whenever the USER changes our value
        so we know it differs from the daemon's value."""
        if not self.mutable:
            raise TransmissionRPCError("Can't alter %s" % self._key)
        if new_value != self._value:
            self._value = new_value
            self._value_pretty = self.prettify(self._value)
#            print 'setting %s=%s' % (self._key, self._value)
            self.needs_push = True

    def _hook(self, name, arg):
        if callable(arg):
            self._hooks[name] = arg  # Set new hook
        else:
            return self._hooks[name](arg)  # Execute hook
    def onupdate(self, func):
        """Set callback function for value updates from daemon.

        func will get the raw value from the daemon. func's return value will
        be used as our new value.
        """
        return self._hook('onupdate', func)
    def onwrite(self, func):
        """TODO
        """
        return self._hook('onwrite', func)
    def prettify(self, func):
        """Set callback function for any value update.

        func will get the raw value. func's return value will
        be used as the pretty/human-readable version.
        """
        return self._hook('prettify', func)

    def _std_prettify(self, value):
        if self._type == 'float':         pass
        elif self._type == 'ratio':       value = hr_ratio(value)
        elif self._type == 'int':         pass
        elif self._type == 'str':         pass
        elif self._type == 'percent':     value = hr_percent(value)
        elif self._type == 'boolean':     value = unicode(value).lower()
        elif self._type == 'path_dir':    value = hr_path(value) + '/'
        elif self._type == 'path_file':   value = hr_path(value)
        elif self._type == 'url':         pass
        elif self._type == 'bytes_size':  value = hr_bytes(value)
        elif self._type == 'bytes_rate':  value = hr_bytes(value) + '/s'
        elif self._type == 'date':        pass
        elif self._type == 'timespan':    pass
        return unicode(value)

    # Offer easy access to human-readable and machine-readable values
    hr = property(fget=lambda self: self._value_pretty)
    mr = property(fget=lambda self: self._value)

    def __unicode__(self): return self._value_pretty
    def __str__(self): return self._value_pretty.encode(ENCODING)
    def __repr__(self): return repr(self._value)
    def __trunc__(self): return int(self._value)
    def __float__(self): return float(self._value)
    def __len__(self): return len(self._value_pretty)
    def __eq__(self, other): return self._value == other
    def __ne__(self, other): return self._value != other
    def __lt__(self, other): return self._value < other
    def __le__(self, other): return self._value <= other
    def __gt__(self, other): return self._value > other
    def __ge__(self, other): return self._value >= other
    def lower(self): return self._value_pretty.lower()
    def upper(self): return self._value_pretty.upper()


class TransmissionRPC(object):

    """A dict or list of TransmissionRPCs and TransmissionRPCValues
    according to rpcspec.py."""

    def __init__(self, section, data=None, setter=None):
        """Create a new TransmissionRPC instance.

        Arguments:
            section: Path to locate spec in rpcspec.py.  Can be str for
                     top-level sections ('session' or 'torrent') or list.
            data: Optional list or dict. Can be set later via update method.
            setter: Optional callable that will get called with changed items
                    via push method.
        """
        self._setter = setter
        if type(section) is list:
            self._section = section
        else:
            self._section = [section]
        if type(data) is list:
            self._data = []
        else:
            self._data = {}
        if data is not None:
            self.update(data)
#        print "Created new TransmissionRPC: %s" % repr(self)

    def update(self, new):
        """Update or create TransmissionRPC(Value) instances from new
        according to specs."""
        for key,value in get_items(new):
            try:
                # TransmissionRPC and TransmissionRPCValue conveniently have
                # update() methods
                self._data[key].update(value)
            except (KeyError, IndexError):
                if type(value) is dict or type(value) is list:
                    add_key(self._data, key, TransmissionRPC(self._section+[key], value))
                else:
                    spec = get_spec(self._section, key)
                    add_key(self._data, key, TransmissionRPCValue(key, value, **spec))

    def push(self):
        """Find altered values and update the daemon."""
        if not callable(self._setter):
            return
        def get_changed_items(data):
            keyvalpairs = get_items(data)
            if type(data) is list:
                filtered = []
            else:
                filtered = {}
            for key,value in keyvalpairs:
                try:
                    if value.needs_push:
                        print 'writing', value.onwrite(value.mr)
                        add_key(filtered, key, value.onwrite(value.mr))
                        value.needs_push = False
                except AttributeError:
                    item = get_changed_items(data[key])
                    if len(item):
                        add_key(filtered, key, item)
            return filtered
        changed_items = get_changed_items(self._data)
        if changed_items:
            if self._section[0] == 'torrent':
                changed_items['id'] = self._data['id'].mr
            self._setter(**changed_items)

    def __getitem__(self, key):
        return self._data[key]
    def __setitem__(self, key, value):
        self._data[key].set(value)
    def __iter__(self):
        return iter(self._data)
    def __repr__(self): return repr(self._data)
    def items(self): return self._data.items()
    def keys(self): return self._data.keys()


### Helper functions

def get_items(listordict):
    try:
        return listordict.items()
    except AttributeError:
        return list(enumerate(listordict))

def add_key(dictorlist, key, value):
    try:
        dictorlist[key] = value
    except (IndexError, TypeError):
        dictorlist.append(value)

def get_spec(sections, key):
    """ Find specifications for RPC value. """
    category = RPC
    try:
        for section in sections:
            if type(section) is not int:
                category = category[section]
            if 'subspec' in category:
                category = category['subspec']
    except KeyError:
        raise TransmissionRPCError('Missing RPC specifications: %s' % \
                                       (':'.join(str(s) for s in sections+[key])))
    if type(key) is int:
        return category
    else:
        return category[key]


### Converters (machine-readable -> human-readable)

def hr_ratio(v):
    if v == -1: return 'n/a'
    if v == -2: return 'inf'
    try:
        return u'%.2f' % v
    except TypeError:
        return u'0.00'

def hr_percent(v):
    try:
        return u'%d %%' % (v*100)
    except TypeError:
        return u'0 %'

def hr_path(path):
    try:
        if RE_HOMEDIR.match(path):
            path = '~' + RE_HOMEDIR.sub('', path, 1)
        return path.rstrip('/')
    except TypeError:
        return u''

def hr_bytes(bytes, base=1000, lengthy=False, format=None):
    """
    Adapted from:
        Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
        License: MIT
        Link: http://code.activestate.com/recipes/578019-bytes-to-human-human-to-bytes-converter/
    """
    try:
        bytes = int(bytes)
    except TypeError:
        return u'0 B'
    if bytes < 0:
        raise ValueError('bytes < 0: %d' % bytes)

    # Associate BYTE_SYMBOLS with BYTE_SIZES (e.g. 'k' -> 1000)
    try:
        byte_symbols = BYTE_SYMBOLS[base][('short','long')[lengthy]]
        byte_sizes = dict(zip(byte_symbols, BYTE_SIZES[base]))
    except KeyError:
        raise ValueError('Unknown base for byte conversion: %s' % base)

    # '5000' --> 'value=5 symbol=kilo'
    value = bytes
    symbol = ''
    for s in reversed(byte_symbols):
        if bytes >= byte_sizes[s]:
            value = float(bytes) / byte_sizes[s]
            symbol = s
            break

    # Cut everything after two decimal points
    value = float('%.2f' % value)

    if format is None:
        # Use reasonable format depending on magnitude
        if value < 10:      # 'n.nn' between 0 and 10
            format = '%(value).2f %(symbol)s'
        elif value < 100:   # 'n.n' between 10 and 100
            format = '%(value).1f %(symbol)s'
        else:               # 'n' between 100 and 1000/1024
            format = '%(value)d %(symbol)s'

    text = (format % dict(symbol=symbol, value=value)).replace('.0 ', ' ')

    # Consider plural-s for lengthy notation
    if lengthy:
        unit_name = 'byte%s' % ('','s')[RE_ONE.match(text) is None]
    else:
        unit_name = 'B'

    return text + unit_name

