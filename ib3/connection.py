# -*- coding: utf-8 -*-
#
# This file is part of IRC Bot Behavior Bundle (IB3)
# Copyright (C) 2017 Bryan Davis and contributors
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import ssl

import irc.connection

logger = logging.getLogger(__name__)


class SSL(object):
    """Use SSL connections."""
    def __init__(self, *args, **kwargs):
        kwargs['connect_factory'] = irc.connection.Factory(
            wrapper=ssl.wrap_socket)
        super(SSL, self).__init__(*args, **kwargs)
