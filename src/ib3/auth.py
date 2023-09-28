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

import base64
import logging

import irc.events

from .mixins import JoinChannels

logger = logging.getLogger(__name__)


class AbstractAuth(JoinChannels):
    """Base class for authentication mixins."""

    def __init__(
        self,
        server_list,
        nickname,
        realname,
        ident_password,
        channels=None,
        username=None,
        **kwargs,
    ):
        """
        :param server_list: List of servers the bot will use.
        :param nickname: The bot's nickname
        :param realname: The bot's realname
        :param ident_password: The bot's password
        :param channels: List of channels to join after authenticating
        :param username: IRC username (default: nickname)
        """
        self._primary_nick = nickname
        self._username = username or nickname
        self._ident_password = ident_password
        self._channels = channels or []

        super().__init__(
            server_list=server_list,
            nickname=nickname,
            realname=realname,
            username=self._username,
            **kwargs,
        )


class NickServ(AbstractAuth):
    """Authenticate with NickServ before joining channels."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for event in ["welcome", "privnotice"]:
            self.connection.add_global_handler(
                event,
                getattr(self, f"_handle_{event}"),
            )

    def _handle_welcome(self, conn, event):  # noqa: U100 Unused argument
        """Handle WELCOME message.

        Starts authentication handshake by sending NickServ an ``identify``
        message.
        """
        logger.info("Connected to server %s", conn.get_server_name())
        self._identify_to_nickserv()

    def _handle_privnotice(self, conn, event):  # noqa: U100 Unused argument
        """Handle NOTICE sent directly to user.

        Check for messages from NickServ requesting auth, warning of password
        failures, and acknowledging successful auth.
        """
        msg = event.arguments[0]
        if event.source.nick == "NickServ":
            if "NickServ identify" in msg:
                logger.info("Authentication requested by Nickserv: %s", msg)
                self._identify_to_nickserv()
            elif "You are now identified" in msg:
                logger.debug("Authentication succeeded")
                self.join_channels(self._channels)
            elif "Invalid password" in msg:
                logger.error("Password invalid. Check your config!")
                self.die()

    def _identify_to_nickserv(self):
        """Send NickServ our username and password."""
        logger.info("Authenticating to NickServ")
        self.connection.privmsg(
            "NickServ",
            "identify {} {}".format(
                self._primary_nick,
                self._ident_password,
            ),
        )


class SASL(AbstractAuth):
    """Authenticate using SASL before joining channels."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        listen = {
            "cap": "cap",
            "authenticate": "authenticate",
            "saslsuccess": irc.events.numeric.get("903", "903"),
            "saslmechs": irc.events.numeric.get("908", "908"),
            "welcome": "welcome",
        }

        self.reactor._on_connect = self._handle_connect

        for handler, event in listen.items():
            logger.debug("Registering for %s", event)
            self.connection.add_global_handler(
                event,
                getattr(self, f"_handle_{handler}"),
            )

    def _handle_connect(self, sock):  # noqa: U100 Unused argument
        """Send CAP REQ :sasl on connect."""
        self.connection.cap("REQ", "sasl")

    def _handle_cap(self, conn, event):
        """Handle CAP responses."""
        if event.arguments and event.arguments[0] == "ACK":
            conn.send_raw("AUTHENTICATE PLAIN")
        else:
            logger.warning("Unexpected CAP response: %s", event)
            conn.disconnect()

    def _handle_authenticate(self, conn, event):
        """Handle AUTHENTICATE responses."""
        if event.target == "+":
            creds = "{username}\0{username}\0{password}".format(
                username=self._username,
                password=self._ident_password,
            )
            conn.send_raw(
                "AUTHENTICATE {}".format(
                    base64.b64encode(creds.encode("utf8")).decode("utf8"),
                ),
            )
        else:
            logger.warning("Unexpected AUTHENTICATE response: %s", event)
            conn.disconnect()

    def _handle_saslsuccess(self, conn, event):  # noqa: U100 Unused argument
        """Handle 903 RPL_SASLSUCCESS responses."""
        self.connection.cap("END")

    def _handle_saslmechs(self, conn, event):  # noqa: U100 Unused argument
        """Handle 908 RPL_SASLMECHS responses."""
        logger.warning("SASL PLAIN not supported: %s", event)
        self.die()

    def _handle_welcome(self, conn, event):  # noqa: U100 Unused argument
        """Handle WELCOME message."""
        logger.info("Connected to server %s", conn.get_server_name())
        self.join_channels(self._channels)
