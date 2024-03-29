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
import ib3
import ib3.connection


class SSLBot(ib3.connection.SSL, ib3.Bot):
    pass


def test_ssl(mocker):
    mock_init = mocker.patch("irc.bot.SingleServerIRCBot.__init__")
    conn_factory = mocker.patch("irc.connection.Factory")
    bot = SSLBot(
        server_list=[("localhost", "9999")],
        realname="ib3test",
        nickname="ib3test",
    )
    assert isinstance(bot, ib3.connection.SSL)
    assert isinstance(bot, ib3.Bot)
    conn_factory.assert_called_once_with(wrapper=bot._ssl_context.wrap_socket)
    args, kwargs = mock_init.call_args
    assert kwargs["connect_factory"] is conn_factory.return_value
