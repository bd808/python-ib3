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

# Dummy test file that really tests nothing other than that imports succeed

import irc.client
import jaraco.stream

import ib3


def test_construct_sets_lenient_decoding():
    bot = ib3.Bot(
        server_list=[('localhost', '9999')],
        realname='ib3test',
        nickname='ib3test',
    )
    assert len(bot.server_list) == 1
    assert jaraco.stream.buffer.LenientDecodingLineBuffer.errors == 'replace'
    assert irc.client.ServerConnection.buffer_class == \
        jaraco.stream.buffer.LenientDecodingLineBuffer
