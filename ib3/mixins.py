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

import irc.client

logger = logging.getLogger(__name__)


class PingServer(object):
    """Add checks for connection liveness using PING commands."""
    def __init__(self, max_pings=2, ping_interval=300, *args, **kwargs):
        """
        :param max_pings: Maximum numer of missed pings to tolerate
        :param ping_interval: Seconds between ping attempts
        """
        super(PingServer, self).__init__(*args, **kwargs)
        self._unanswered_pings = 0
        self._unanswered_pings_limit = max_pings
        self.reactor.scheduler.execute_every(
            period=ping_interval,
            func=self._ping_server)
        self.connection.add_global_handler('pong', self._handle_pong)

    def _ping_server(self):
        """Send a ping or disconnect if too many pings are outstanding."""
        if self._unanswered_pings >= self._unanswered_pings_limit:
            logger.warning('Connection timed out. Disconnecting.')
            self.disconnect()
            self._unanswered_pings = 0
        else:
            try:
                self.connection.ping('keep-alive')
                self._unanswered_pings += 1
            except irc.client.ServerNotConnectedError:
                pass

    def _handle_pong(self, conn, event):
        """Clear ping count when a pong is received."""
        self._unanswered_pings = 0


class DisconnectOnError(object):
    """Handle ERROR message by logging and disconnecting."""
    def __init__(self, *args, **kwargs):
        super(DisconnectOnError, self).__init__(*args, **kwargs)
        self.connection.add_global_handler('error', self._handle_error)

    def _handle_error(self, conn, event):
        logger.warning(str(event))
        conn.disconnect()


class RejoinOnKick(object):
    """Handle KICK by attempting to rejoin channel."""
    def __init__(self, *args, **kwargs):
        super(RejoinOnKick, self).__init__(*args, **kwargs)
        self.connection.add_global_handler('kick', self._handle_kick)

    def _handle_kick(self, conn, event):
        nick = event.arguments[0]
        channel = event.target
        if nick == conn.get_nickname():
            logger.warn(
                'Kicked from %s by %s', channel, event.source.nick)
            self.reactor.scheduler.execute_after(
                30, functools.partial(conn.join, channel))


class RejoinOnBan(object):
    """Handle ERR_BANNEDFROMCHAN by attempting to rejoin channel."""
    def __init__(self, *args, **kwargs):
        super(RejoinOnKick, self).__init__(*args, **kwargs)
        self.connection.add_global_handler(
            'bannedfromchan', self._handle_bannedfromchan)

    def _handle_bannedfromchan(self, conn, event):
        logger.warning(str(event))
        self.reactor.scheduler.execute_after(
            60, functools.partial(conn.join, event.arguments[0]))


class JoinChannels(object):
    """Join channels one at a time to avoid flooding."""
    def join_channels(self, channels):
        """Join a list of channels, one at a time."""
        try:
            car, cdr = channels[0], channels[1:]
        except (IndexError, TypeError):
            logger.exception('Failed to find channel to join.')
        else:
            logger.info('Joining %s', car)
            self.connection.join(car)
            if cdr:
                self.reactor.scheduler.execute_after(
                    1, functools.partial(self.join_channels, cdr))
