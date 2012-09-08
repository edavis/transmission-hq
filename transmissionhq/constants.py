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

import locale
import re
import os

ENCODING = locale.getpreferredencoding()

BYTE_SYMBOLS = {
    1000 : { 'short' : ('k', 'M', 'G', 'T', 'P'),
             'long'  : ('kilo', 'mega', 'giga', 'tera', 'peta') },
    1024 : { 'short' : ('Ki', 'Mi', 'Gi', 'Ti', 'Pi'),
             'long'  : ('kibi', 'mebi', 'gibi', 'tebi', 'pebi') }
}

BYTE_SIZES = {
    1000: (1000, 1000000, 1000000000, 1000000000000, 1000000000000000),
    1024: (1024, 1048576, 1073741824, 1099511627776, 1125899906842624)
}

RE_HOMEDIR = re.compile('^(' + os.environ['HOME'] + ')')
RE_ONE = re.compile('^1[\.0]+\D+')  # Match any number that is exactly 1
