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


class SSL:
    """Use SSL connections."""

    def __init__(self, *args, **kwargs):
        self._ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
        self._ssl_context.load_default_certs()
        # Unfortunately the upstream library doesn't give us a simple way to
        # pass the IRC server hostname to the socket factory for SNI and cert
        # verification. See https://github.com/jaraco/irc/issues/216
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE

        kwargs["connect_factory"] = irc.connection.Factory(
            wrapper=self._ssl_context.wrap_socket,
        )
        super().__init__(*args, **kwargs)
