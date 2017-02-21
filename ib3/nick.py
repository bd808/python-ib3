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

import functools
import logging

logger = logging.getLogger(__name__)


class NicknameInUse(object):
    """Handle ERR_NICKNAMEINUSE messages by changing to an alternate nick."""
    def __init__(
            self, server_list, nickname, realname,
            altnick=None, *args, **kwargs):
        """
        :param server_list: List of servers the bot will use.
        :param nickname: The bot's nickname
        :param realname: The bot's realname
        :param altnick: Alternate nickname if primary nick is taken
        """
        self._primary_nick = nickname
        self._altnick = altnick or nickname + '_'

        super(NicknameInUse, self).__init__(
                server_list=server_list,
                nickname=nickname,
                realname=realname,
                **kwargs)
        self.connection.add_global_handler(
            'nicknameinuse', self._handle_nicknameinuse)

    def _handle_nicknameinuse(self, conn, event):
        """Handle ERR_NICKNAMEINUSE message.

        If failed nick matches our desired nick, switch to secondary nick, and
        schedule an attempt to reclaim our primary nick.

        If failed nick matches our secondary nick, die.
        """
        nick = conn.get_nickname()
        logger.warning('Requested nick "%s" in use', nick)
        if nick == self._altnick:
            self.die(
                'Cowardly refusing to fill the channel with copies of myself')
        conn.nick(self._altnick)
        self.reactor.scheduler.execute_after(30, self._recover_nick)

    def _recover_nick(self):
        """Do nothing.

        Subclasses can override this method to perform some special action to
        recover the bot's primary nickname.
        """
        pass

    def has_primary_nick(self):
        """Do we currently have our primary nick?

        :rtype: bool
        """
        return self.connection.get_nickname() == self._primary_nick


class Ghost(NicknameInUse):
    """GHOST disconnects an old user session, or somebody attempting to use
    your nickname without authorization.

    This mixin assumes that you are also using a mixin from ``ib3.auth`` or
    another means to authenticate your IRC account.
    """
    def _recover_nick(self):
        """Recover nick by sending GHOST command to NickServ."""
        if not self.has_primary_nick():
            self.connection.privmsg(
                'NickServ', 'GHOST {}'.format(self._primary_nick))
            self.reactor.scheduler.execute_after(
                1, functools.partial(
                    self.connection.nick, self._primary_nick))


class Regain(NicknameInUse):
    """REGAIN disconnects an old user session, or somebody attempting to use
    your nickname without authorization, then changes your nickname to the
    given nickname. This may not work, disconnecting you, if the target client
    reconnects automatically.

    This mixin assumes that you are also using a mixin from ``ib3.auth`` or
    another means to authenticate your IRC account.
    """
    def _recover_nick(self):
        """Recover nick by sending REGAIN command to NickServ."""
        if not self.has_primary_nick():
            self.connection.privmsg(
                'NickServ', 'REGAIN {}'.format(self._primary_nick))
