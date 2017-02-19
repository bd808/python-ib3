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
"""Base IRC bot and mixins for commonly desired functionality."""

import functools
import logging

import irc.bot
import irc.buffer
import irc.client

logger = logging.getLogger(__name__)


class Bot(irc.bot.SingleServerIRCBot):
    """Basic IRC bot"""
    def __init__(self, *args, **kwargs):
        # A UTF-8 only world is a nice dream but the real world is all yucky
        # and full of legacy encoding issues that should not crash our bot.
        irc.buffer.LenientDecodingLineBuffer.errors = 'replace'
        irc.client.ServerConnection.buffer_class = \
            irc.buffer.LenientDecodingLineBuffer

        super(Bot, self).__init__(*args, **kwargs)


class Ping(object):
    """Add checks for connection liveness using PING commands."""
    def __init__(self, max_pings=2, ping_interval=300, *args, **kwargs):
        """
        :param max_pings: Maximum numer of missed pings to tolerate
        :param ping_interval: Seconds between ping attempts
        """
        super(Ping, self).__init__(*args, **kwargs)
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


class FreenodePasswdAuth(object):
    """Authenticate with NickServ before joining channels."""
    def __init__(
            self, server_list, nickname, realname,
            ident_password, channels, **kwargs):
        """
        :param server_list: List of servers the bot will use.
        :param nickname: The bot's nickname
        :param realname: The bot's realname
        :param ident_password: The bot's password
        :param channels: List of channels to join after authenticating
        """
        self._primary_nick = nickname
        self._ident_password = ident_password
        self._channels = channels

        super(FreenodePasswdAuth, self).__init__(
                server_list=server_list,
                nickname=nickname,
                realname=realname,
                **kwargs)
        for event in ['welcome', 'nicknameinuse', 'privnotice']:
            self.connection.add_global_handler(
                event, getattr(self, "_handle_%s" % event))

    def _handle_welcome(self, conn, event):
        """Handle WELCOME message.

        Starts authentication handshake by sending NickServ an `identify`
        message.
        """
        logger.info('Connected to server %s', conn.get_server_name())
        self._identify_to_nickserv()

    def _handle_nicknameinuse(self, conn, event):
        """Handle ERR_NICKNAMEINUSE message.

        If failed nick matches our desired nick, switch to secondary nick by
        appending `_` to the desired nick and schedule an attempt to reclaim
        our primary nick.

        If failed nick matches our secondary nick, die.
        """
        nick = conn.get_nickname()
        logger.warning('Requested nick "%s" in use', nick)
        alt_nick = self._primary_nick + '_'
        if nick == alt_nick:
            # Primary and secondary nicks taken, abort connection
            self.die(
                'Cowardly refusing to fill the channel with copies of myself')
        conn.nick(alt_nick)
        self.reactor.scheduler.execute_after(30, self._nickserv_regain)

    def _handle_privnotice(self, conn, event):
        """Handle NOTICE sent directly to user.

        Check for messages from NickServ requesting auth, warning of password
        failures, and acknowledging successful auth.
        """
        msg = event.arguments[0]
        if event.source.nick == 'NickServ':
            if 'NickServ identify' in msg:
                logger.info('Authentication requested by Nickserv: %s', msg)
                self._identify_to_nickserv()
            elif 'You are now identified' in msg:
                logger.debug('Authentication succeeded')
                self.reactor.scheduler.execute_after(
                    1, self._join_next_channel)
            elif 'Invalid password' in msg:
                logger.error('Password invalid. Check your config!')
                self.die()

    def _identify_to_nickserv(self):
        """Send NickServ our username and password."""
        logger.info('Authenticating to NickServ')
        self.connection.privmsg('NickServ', 'identify %s %s' % (
            self._primary_nick, self._ident_password))

    def _join_next_channel(self, channels=None):
        """Join the next channel in our join list."""
        if channels is None:
            channels = self._channels
        try:
            car, cdr = channels[0], channels[1:]
        except (IndexError, TypeError):
            logger.exception('Failed to find channel to join.')
        else:
            logger.info('Joining %s', car)
            self.connection.join(car)
            if cdr:
                self.reactor.scheduler.execute_after(
                    1, functools.partial(self._join_next_channel, cdr))

    def _nickserv_regain(self):
        if not self.has_primary_nick():
            # REGAIN disconnects an old user session, or somebody
            # attempting to use your nickname without authorization,
            # then changes your nickname to the given nickname.
            # This may not work, disconnecting you, if the target
            # client reconnects automatically.
            self.connection.privmsg('NickServ', 'regain %s %s' % (
                self._primary_nick, self._ident_password))

    def has_primary_nick(self):
        """Do we currently have our primary nick?"""
        return self.connection.get_nickname() == self._primary_nick
