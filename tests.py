#!/usr/bin/env python
import unittest

from transmissionhq.client import TransmissionClient
from transmissionhq.helpers import TransmissionURL
from transmissionhq.rpc import (TransmissionRPCValue, TransmissionRPCError)

import time
import os
from subprocess import (Popen, call)
import signal
from shutil import rmtree

daemon_cmd = {
    'binary': '/usr/bin/transmission-daemon',
    'rpc_port': '65534',
    'peer_port': '65535',
    'rpc_ip': '127.0.0.1',
    'peer_ip': '127.0.0.1',
    'config_dir': '/tmp/transmissiontestconfig',
    'logfile': '/dev/null',
}

torrentlinks = ['magnet:?xt=urn:btih:%040d' % i for i in range(1, 100)]

rpctypes = [
    { 'type':'float',      'value':1.2345,    'pretty':u'1.2345' },
    { 'type':'ratio',      'value':1.2345,    'pretty':u'1.23' },
    { 'type':'int',        'value':1,         'pretty':u'1' },
    { 'type':'str',        'value':'Hello',   'pretty':u'Hello' },
    { 'type':'percent',    'value':0.55432,   'pretty':u'55 %' },
    { 'type':'boolean',    'value':True,      'pretty':u'true' },
    { 'type':'path_dir',   'value':os.environ['HOME']+'/test', 'pretty':u'~/test/' },
    { 'type':'path_file',  'value':os.environ['HOME']+'/test', 'pretty':u'~/test' },
    { 'type':'url',        'value':'http://some/link', 'pretty':u'http://some/link' },
    { 'type':'bytes_size', 'value':1073741824, 'pretty':u'1.00 GiB' },
    { 'type':'bytes_rate', 'value':1073741824, 'pretty':u'1.00 GiB/s' },
    { 'type':'date',       'value':1000000000, 'pretty':u'1000000000' },  # TODO
    { 'type':'timespan',   'value':300,        'pretty':u'300' },         # TODO
]


daemon_pid = None
def setUpModule():
    print 'Starting Transmission daemon: %s' % daemon_cmd
    global daemon_pid
    daemon_pid = Popen([
            daemon_cmd['binary'], '--foreground',
            '--logfile', daemon_cmd['logfile'], '--config-dir', daemon_cmd['config_dir'],
            '--rpc-bind-address', daemon_cmd['rpc_ip'], '--port', daemon_cmd['rpc_port'],
            '--bind-address-ipv4', daemon_cmd['peer_ip'], '--peerport', daemon_cmd['peer_port']
            ]).pid
    time.sleep(1)  # Wait for daemon to wake up

def tearDownModule():
    print 'Stopping Transmission daemon: %d' % daemon_pid
    os.kill(daemon_pid, signal.SIGTERM)
    os.waitpid(daemon_pid, 0)
    print 'Deleting temporary config dir: %s' % daemon_cmd['config_dir']
    rmtree(daemon_cmd['config_dir'])


class TransmissionURLTests(unittest.TestCase):
    def testURLDefaults(self):
        url = TransmissionURL()
        self.assertEqual(url['ssl'], False)
        self.assertEqual(url['username'], '')
        self.assertEqual(url['password'], '')
        self.assertEqual(url['host'], 'localhost')
        self.assertEqual(url['port'], 9091)
        self.assertEqual(url['path'], '/transmission/rpc')

    def testURLParser(self):
        url = TransmissionURL('https://kitty:hello@nondomain:1234/testpath')
        self.assertEqual(url['ssl'], True)
        self.assertEqual(url['username'], 'kitty')
        self.assertEqual(url['password'], 'hello')
        self.assertEqual(url['host'], 'nondomain')
        self.assertEqual(url['port'], 1234)
        self.assertEqual(url['path'], '/testpath')

    def testURL2String(self):
        url = TransmissionURL()
        self.assertEqual(str(url), 'http://localhost:9091/transmission/rpc')
        url = TransmissionURL('https://kitty:hello@nondomain:1234/testpath')
        self.assertEqual(str(url), 'https://kitty:***@nondomain:1234/testpath')


class TransmissionRPCValueTests(unittest.TestCase):
    def testTransmissionRPCValueTypes(self):
        for rpctype in rpctypes:
            rpcval = TransmissionRPCValue('TEST', value=rpctype['value'], type=rpctype['type'], mutable=True)
            self.assertEqual(rpcval.mr, rpctype['value'])
            self.assertEqual(rpcval.hr, rpctype['pretty'])

    # User induced changes
    def testTransmissionRPCValueChange(self):
        for rpctype in rpctypes:
            rpcval = TransmissionRPCValue('TEST', value=None, type=rpctype['type'], mutable=True)
            rpcval.set(rpctype['value'])
            self.assertEqual(rpcval.mr, rpctype['value'])
            self.assertEqual(rpcval.hr, rpctype['pretty'])

    # Daemon induced changes
    def testTransmissionRPCValueUpdate(self):
        for rpctype in rpctypes:
            rpcval = TransmissionRPCValue('TEST', value=None, type=rpctype['type'], mutable=True)
            rpcval.update(rpctype['value'])
            self.assertEqual(rpcval.mr, rpctype['value'])
            self.assertEqual(rpcval.hr, rpctype['pretty'])

    def testTransmissionRPCValueMutable(self):
        for rpctype in rpctypes:
            rpcval = TransmissionRPCValue('TEST', value=None, type=rpctype['type'], mutable=False)
            self.assertRaises(TransmissionRPCError, rpcval.set, rpctype['value'])

    def testTransmissionRPCValueHooks(self):
        # TODO Test onwrite() / rename to onpush() / ...? -- Investigate!
        for rpctype in rpctypes:
            rpcval = TransmissionRPCValue('TEST', value=0, type=rpctype['type'], mutable=True)
            rpcval.onupdate(lambda val: None)
            rpcval.prettify(lambda val: u'Snow White')
            rpcval.update(rpctype['value'])
            self.assertEqual(rpcval.mr, None)
            self.assertEqual(rpcval.hr, u'Snow White')


class TransmissionClientTests(unittest.TestCase):
    def setUp(self):
        self.client = TransmissionClient( TransmissionURL(port=65534) )
        self.session = self.client.session()

    def testSessionGetValue(self):
        utp_mr = self.session['utp-enabled'].mr
        utp_hr = self.session['utp-enabled'].hr
        self.assertTrue(type(self.session['utp-enabled'].mr) is bool)
        self.assertTrue(type(self.session['utp-enabled'].hr) is unicode)

    def testSessionChangeValue(self):
        # Store original setting
        store = self.session['peer-limit-global'].mr

        # Change value
        self.session['peer-limit-global'] = 10000
        self.session.push()
        del self.session
        self.session = self.client.session()
        self.assertEqual(self.session['peer-limit-global'].mr, 10000)

        # Change value, but 'forget' to push() it
        self.session['peer-limit-global'] = 10
        del self.session
        self.session = self.client.session()
        self.assertEqual(self.session['peer-limit-global'].mr, 10000)

        # Restore original setting
        self.session['peer-limit-global'] = store
        self.session.push()

    def testAddListDelTorrent(self):
        tid = self.client.add_torrent(torrentlinks.pop(0))
        self.assertTrue(type(tid) is int)

        tlist = self.client.torrents(ids=[tid], keys=['id', 'name'])
        self.assertEqual(tlist[0]['id'].mr, tid)
        self.assertTrue(type(tlist[0]['name'].hr) is unicode)

        self.client.delete_torrents([tid], delete_files=True)
        tlist = self.client.torrents(keys=['id'])
        self.assertNotIn(tid, [t['id'] for t in tlist])

    def testMoveTorrent(self):
        tid = self.client.add_torrent(torrentlinks.pop(0))
        self.client.move_torrents([tid], os.environ['HOME'])
        tlist = self.client.torrents(ids=[tid], keys=['downloadDir'])
        self.assertEqual(tlist[0]['downloadDir'].hr, '~/')
        self.client.delete_torrents([tid], delete_files=True)

    def testChangeTorrentValues(self):
        tid = self.client.add_torrent(torrentlinks.pop(0))
        torrent = self.client.torrents(ids=[tid],
                                       keys=['uploadLimit', 'eta'])[0]
        torrent['uploadLimit'] = 123
        torrent.push()
        self.assertEqual(torrent['uploadLimit'].hr, '123 B/s')
        self.assertRaises(TransmissionRPCError, torrent.__setitem__, 'eta', 10)
        self.client.delete_torrents([tid], delete_files=True)

if __name__ == '__main__':
    unittest.main()

