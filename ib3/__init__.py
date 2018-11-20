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

import irc.bot
from jaraco.stream import buffer
import irc.client

logger = logging.getLogger(__name__)


class Bot(irc.bot.SingleServerIRCBot):
    """Basic IRC bot.

    Simple subclass of ``irc.bot.SingleServerIRCBot`` that sets up lenient
    UTF-8 encoding handling for inbound messages. This is a nice base to start
    from when adding other IB3 mixins.
    """
    def __init__(self, *args, **kwargs):
        # A UTF-8 only world is a nice dream but the real world is all yucky
        # and full of legacy encoding issues that should not crash our bot.
        buffer.LenientDecodingLineBuffer.errors = 'replace'
        irc.client.ServerConnection.buffer_class = \
            buffer.LenientDecodingLineBuffer

        super(Bot, self).__init__(*args, **kwargs)
