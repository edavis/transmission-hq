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

def kilo2bytes(kb):
    return kb*1000
def bytes2kilo(b):
    return int(round(b/1000.0))

def status(s):
    if s == 0: return 'paused'
    if s == 1: return 'will verify'
    if s == 2: return 'verifying'
    if s == 3: return 'will download'
    if s == 4: return 'downloading'
    if s == 5: return 'will seed'
    if s == 6: return 'seeding'


RPC = {
    'session' : {
        'alt-speed-down': { 'onupdate':kilo2bytes, 'onwrite':bytes2kilo,
                            'type':'bytes_rate', 'mutable':True },
        'alt-speed-enabled': { 'type':'boolean', 'mutable':True },
        'alt-speed-time-begin': { 'type':'date', 'mutable':True },
        'alt-speed-time-enabled': { 'type':'boolean', 'mutable':True },
        'alt-speed-time-end': { 'type':'date', 'mutable':True },
        'alt-speed-time-day': { 'type':'int', 'mutable':True },
        'alt-speed-up': { 'onupdate':kilo2bytes, 'onwrite':bytes2kilo,
                          'type':'bytes_rate', 'mutable':True },
        'blocklist-url': { 'type':'url', 'mutable':True },
        'blocklist-enabled': { 'type':'boolean', 'mutable':True },
        'blocklist-size': { 'type':'int', 'mutable':False },
        'cache-size-mb': { 'type':'bytes_size', 'mutable':True },
        'config-dir': { 'type':'path_dir', 'mutable':False },
        'download-dir': { 'type':'path_dir', 'mutable':True },
        'download-dir-free-space': { 'type':'bytes_size', 'mutable':False },
        'download-queue-size': { 'type':'int', 'mutable':True },
        'download-queue-enabled': { 'type':'boolean', 'mutable':True },
        'dht-enabled': { 'type':'boolean', 'mutable':True },
        'encryption': { 'type':'str', 'mutable':True },
        'idle-seeding-limit': { 'type':'timespan', 'mutable':True },
        'idle-seeding-limit-enabled': { 'type':'boolean', 'mutable':True },
        'incomplete-dir': { 'type':'path_dir', 'mutable':True },
        'incomplete-dir-enabled': { 'type':'boolean', 'mutable':True },
        'lpd-enabled': { 'type':'boolean', 'mutable':True },
        'peer-limit-global': { 'type':'int', 'mutable':True },
        'peer-limit-per-torrent': { 'type':'int', 'mutable':True },
        'pex-enabled': { 'type':'boolean', 'mutable':True },
        'peer-port': { 'type':'int', 'mutable':True },
        'peer-port-random-on-start': { 'type':'boolean', 'mutable':True },
        'port-forwarding-enabled': { 'type':'boolean', 'mutable':True },
        'queue-stalled-enabled': { 'type':'boolean', 'mutable':True },
        'queue-stalled-minutes': { 'type':'timespan', 'mutable':True },
        'rename-partial-files': { 'type':'boolean', 'mutable':True },
        'rpc-version': { 'type':'int', 'mutable':False },
        'rpc-version-minimum': { 'type':'int', 'mutable':False },
        'script-torrent-done-filename': { 'type':'path_file', 'mutable':True },
        'script-torrent-done-enabled': { 'type':'boolean', 'mutable':True },
        'seedRatioLimit': { 'type':'ratio', 'mutable':True },
        'seedRatioLimited': { 'type':'boolean', 'mutable':True },
        'seed-queue-size': { 'type':'int', 'mutable':True },
        'seed-queue-enabled': { 'type':'boolean', 'mutable':True },
        'speed-limit-down': { 'onupdate':kilo2bytes, 'onwrite':bytes2kilo,
                              'type':'bytes_rate', 'mutable':True },
        'speed-limit-down-enabled': { 'type':'boolean', 'mutable':True },
        'speed-limit-up': { 'onupdate':kilo2bytes, 'onwrite':bytes2kilo,
                            'type':'bytes_rate', 'mutable':True },
        'speed-limit-up-enabled': { 'type':'boolean', 'mutable':True },
        'start-added-torrents': { 'type':'boolean', 'mutable':True },
        'trash-original-torrent-files': { 'type':'boolean', 'mutable':True },
        'utp-enabled': { 'type':'boolean', 'mutable':True },
        'version': { 'type':'str', 'mutable':False },

        'units': { 'type':'dict', 'mutable':True,
                   'subspec': { 'speed-bytes': { 'type':'int', 'mutable':True },
                                'speed-units': { 'type':'list', 'mutable':True,
                                                 'subspec': { 'type':'str', 'mutable':False } },
                                'memory-bytes': { 'type':'int', 'mutable':True },
                                'memory-units': { 'type':'list', 'mutable':True,
                                                  'subspec': { 'type':'str', 'mutable':False } },
                                'size-bytes': { 'type':'int', 'mutable':True },
                                'size-units': { 'type':'list', 'mutable':True,
                                                'subspec': { 'type':'str', 'mutable':False } },
                              }
                 }
    },

    'torrent' : {
        'activityDate': { 'type':'date', 'mutable':False },
        'addedDate': { 'type':'date', 'mutable':False },
        'bandwidthPriority': { 'type':'int', 'mutable':True },
        'comment': { 'type':'str', 'mutable':False },
        'corruptEver': { 'type':'bytes_size', 'mutable':False },
        'creator': { 'type':'str', 'mutable':False },
        'dateCreated': { 'type':'date', 'mutable':False },
        'desiredAvailable': { 'type':'bytes_size', 'mutable':False },
        'doneDate': { 'type':'date', 'mutable':False },
        'downloadDir': { 'type':'path_dir', 'mutable':False },
        'downloadedEver': { 'type':'bytes_size', 'mutable':False },
        'downloadLimit': { 'onupdate':kilo2bytes, 'onwrite':bytes2kilo,
                           'type':'bytes_rate', 'mutable':True },
        'downloadLimited': { 'type':'boolean', 'mutable':True },
        'error': { 'type':'int', 'mutable':False },
        'errorString': { 'type':'str', 'mutable':False },
        'eta': { 'type':'timespan', 'mutable':False },
        'files': { 'type':'list', 'mutable':False,
                   'subspec': { 'bytesCompleted': { 'type':'bytes_size', 'mutable':False },
                                'length': { 'type':'bytes_size', 'mutable':False },
                                'name': { 'type':'str', 'mutable':False }
                              }
                 },
        'fileStats': { 'type':'list', 'mutable':False,
                       'subspec': { 'bytesCompleted': { 'type':'bytes_size', 'mutable':False },
                                    'wanted': { 'type':'boolean', 'mutable':False },
                                    'priority': { 'type':'int', 'mutable':False }
                                  }
                     },
        'hashString': { 'type':'str', 'mutable':False },
        'haveUnchecked': { 'type':'bytes_size', 'mutable':False },
        'haveValid': { 'type':'bytes_size', 'mutable':False },
        'honorsSessionLimits': { 'type':'boolean', 'mutable':True },
        'id': { 'type':'int', 'mutable':False },
        'isFinished': { 'type':'boolean', 'mutable':False },
        'isPrivate': { 'type':'boolean', 'mutable':False },
        'isStalled': { 'type':'boolean', 'mutable':False },
        'leftUntilDone': { 'type':'bytes_size', 'mutable':False },
        'magnetLink': { 'type':'number', 'mutable':False },  # TODO What is this?
        'manualAnnounceTime': { 'type':'timespan', 'mutable':False },
        'maxConnectedPeers': { 'type':'int', 'mutable':False },
        'metadataPercentComplete': { 'type':'percent', 'mutable':False },
        'name': { 'type':'str', 'mutable':False },
        'peer-limit': { 'type':'int', 'mutable':True },
        'peers': { 'type':'list', 'mutable':False,
                   'subspec': { 'address': { 'type':'str', 'mutable':False },
                                'clientName': { 'type':'str', 'mutable':False },
                                'clientIsChoked': { 'type':'boolean', 'mutable':False },
                                'clientIsInterested': { 'type':'boolean', 'mutable':False },
                                'flagStr': { 'type':'str', 'mutable':False },
                                'isDownloadingFrom': { 'type':'boolean', 'mutable':False },
                                'isEncrypted': { 'type':'boolean', 'mutable':False },
                                'isIncoming': { 'type':'boolean', 'mutable':False },
                                'isUploadingTo': { 'type':'boolean', 'mutable':False },
                                'isUTP': { 'type':'boolean', 'mutable':False },
                                'peerIsChoked': { 'type':'boolean', 'mutable':False },
                                'peerIsInterested': { 'type':'boolean', 'mutable':False },
                                'port': { 'type':'int', 'mutable':False },
                                'progress': { 'type':'percent', 'mutable':False },
                                'rateToClient': { 'type':'bytes_rate', 'mutable':False },
                                'rateToPeer': { 'type':'bytes_rate', 'mutable':False  }
                              }
                 },
        'peersConnected': { 'type':'int', 'mutable':False },
        'peersFrom': { 'type':'dict', 'mutable':False,
                       'subspec': { 'fromCache': { 'type':'number', 'mutable':False },
                                    'fromDht': { 'type':'number', 'mutable':False },
                                    'fromIncoming': { 'type':'number', 'mutable':False },
                                    'fromLpd': { 'type':'number', 'mutable':False },
                                    'fromLtep': { 'type':'number', 'mutable':False },
                                    'fromPex': { 'type':'number', 'mutable':False },
                                    'fromTracker': { 'type':'number', 'mutable':False }
                                  }
                     },
        'peersGettingFromUs': { 'type':'int', 'mutable':False },
        'peersSendingToUs': { 'type':'int', 'mutable':False },
        'percentDone': { 'type':'percent', 'mutable':False },
        'pieces': { 'type':'str', 'mutable':False },  # TODO Can this be translated into Python?
        'pieceCount': { 'type':'int', 'mutable':False },
        'pieceSize': { 'type':'bytes_size', 'mutable':False },
        'priorities': { 'type':'list', 'mutable':False,
                        'subspec': { 'type':'int', 'mutable':False }
                      },
        'queuePosition': { 'type':'int', 'mutable':True },
        'rateDownload': { 'type':'bytes_rate', 'mutable':False },
        'rateUpload': { 'type':'bytes_rate', 'mutable':False },
        'recheckProgress': { 'type':'percent', 'mutable':False },
        'secondsDownloading': { 'type':'timespan', 'mutable':False },
        'secondsSeeding': { 'type':'timespan', 'mutable':False },
        'seedIdleLimit': { 'type':'timespan', 'mutable':True },
        'seedIdleMode': { 'type':'int', 'mutable':True },  # TODO 'type':dict(tr_idlelimit)
        'seedRatioLimit': { 'type':'ratio', 'mutable':True },
        'seedRatioMode': { 'type':'int', 'mutable':True }, # TODO 'type':dict(tr_ratiolimit)
        'sizeWhenDone': { 'type':'bytes_size', 'mutable':False },
        'startDate': { 'type':'date', 'mutable':False },
        'status': { 'onupdate':status, 'type':'int', 'mutable':False },
        'trackers': { 'type':'list', 'mutable':False,
                      'subspec': { 'announce': { 'type':'str', 'mutable':False },
                                   'id': { 'type':'int', 'mutable':False },
                                   'scrape': { 'type':'str', 'mutable':False },
                                   'tier': { 'type':'int', 'mutable':False },
                                 }
                    },
        'trackerStats': { 'type':'list', 'mutable':False,
                          'subspec': { 'announce': { 'type':'str', 'mutable':False },
                                       'announceState': { 'type':'int', 'mutable':False },
                                       'downloadCount': { 'type':'int', 'mutable':False },
                                       'hasAnnounced': { 'type':'boolean', 'mutable':False },
                                       'hasScraped': { 'type':'boolean', 'mutable':False },
                                       'host': { 'type':'str', 'mutable':False },
                                       'id': { 'type':'int', 'mutable':False },
                                       'isBackup': { 'type':'boolean', 'mutable':False },
                                       'lastAnnouncePeerCount': { 'type':'int', 'mutable':False },
                                       'lastAnnounceResult': { 'type':'str', 'mutable':False },
                                       'lastAnnounceStartTime': { 'type':'int', 'mutable':False },
                                       'lastAnnounceSucceeded': { 'type':'boolean', 'mutable':False },
                                       'lastAnnounceTime': { 'type':'int', 'mutable':False },
                                       'lastAnnounceTimedOut': { 'type':'boolean', 'mutable':False },
                                       'lastScrapeResult': { 'type':'str', 'mutable':False },
                                       'lastScrapeStartTime': { 'type':'int', 'mutable':False },
                                       'lastScrapeSucceeded': { 'type':'boolean', 'mutable':False },
                                       'lastScrapeTime': { 'type':'int', 'mutable':False },
                                       'lastScrapeTimedOut': { 'type':'boolean', 'mutable':False },
                                       'leecherCount': { 'type':'int', 'mutable':False },
                                       'nextAnnounceTime': { 'type':'int', 'mutable':False },
                                       'nextScrapeTime': { 'type':'int', 'mutable':False },
                                       'scrape': { 'type':'str', 'mutable':False },
                                       'scrapeState': { 'type':'int', 'mutable':False },
                                       'seederCount': { 'type':'int', 'mutable':False },
                                       'tier': { 'type':'int', 'mutable':False },
                                     }
                        },
        'totalSize': { 'type':'bytes_size', 'mutable':False },
        'torrentFile': { 'type':'str', 'mutable':False },
        'uploadedEver': { 'type':'bytes_size', 'mutable':False },
        'uploadLimit': { 'onupdate':kilo2bytes, 'onwrite':bytes2kilo,
                         'type':'bytes_rate', 'mutable':True },
        'uploadLimited': { 'type':'boolean', 'mutable':True },
        'uploadRatio': { 'type':'ratio', 'mutable':False },
        'wanted': { 'type':'list', 'mutable':False,
                    'subspec': { 'type':'boolean', 'mutable':False } }
        # TODO or deprecated?
        # 'webseeds': { 'type':'list', 'mutable':False },
        # 'webseedsSendingToUs': { 'type':'number', 'mutable':False }
    }
}
