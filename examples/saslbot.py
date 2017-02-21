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

import argparse
import logging

import irc.strings

import ib3
import ib3.auth
import ib3.connection
import ib3.nick


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
logging.captureWarnings(True)

logger = logging.getLogger('saslbot')


class SaslBot(ib3.auth.SASL, ib3.nick.Regain, ib3.connection.SSL, ib3.Bot):
    """Example bot showing use of SASL auth, REGAIN, and SSL encryption."""
    def on_privmsg(self, conn, event):
        self.do_command(conn, event, event.arguments[0])

    def on_pubmsg(self, conn, event):
        args = event.arguments[0].split(':', 1)
        if len(args) > 1:
            to = irc.strings.lower(args[0])
            if to == irc.strings.lower(conn.get_nickname()):
                self.do_command(conn, event, args[1].strip())

    def do_command(self, conn, event, cmd):
        to = event.target
        if to == conn.get_nickname():
            to = event.source.nick

        if cmd == 'disconnect':
            self.disconnect()
        elif cmd == 'die':
            self.die()
        else:
            conn.privmsg(to, 'What does "{}" mean?'.format(cmd))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example bot with SASL auth')
    parser.add_argument('nick')
    parser.add_argument('password')
    parser.add_argument('channel')
    args = parser.parse_args()

    bot = SaslBot(
        server_list=[('chat.freenode.net', 6697)],
        nickname=args.nick,
        realname=args.nick,
        ident_password=args.password,
        channels=[args.channel],
    )
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.disconnect('KeyboardInterrupt!')
    except Exception:
        logger.exception('Killed by unhandled exception')
        bot.disconnect('Exception!')
        raise SystemExit()
