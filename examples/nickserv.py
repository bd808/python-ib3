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

from ib3 import Bot
from ib3.auth import NickServ


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
logging.captureWarnings(True)


class TestBot(NickServ, Bot):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Example bot with NickServ auth')
    parser.add_argument('nick')
    parser.add_argument('password')
    parser.add_argument('channel')
    args = parser.parse_args()

    bot = TestBot(
        server_list=[('chat.freenode.net', 6667)],
        nickname=args.nick,
        realname=args.nick,
        ident_password=args.password,
        channels=[args.channel]
    )
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.disconnect('KeyboardInterrupt!')
    except Exception:
        logging.getLogger('root').exception('Killed by unhandled exception')
        bot.disconnect('Exception!')
        raise SystemExit()
