=============================
IRC Bot Behavior Bundle (IB3)
=============================

IRC bot framework using mixins to provide commonly desired functionality.

Overview
========
The `irc`_ python library's ``irc.bot.SingleServerIRCBot`` provides a nice
base for making a new bot, but there are many common tasks needed by a robust
bot that it does not handle out of the box. IB3 collects some commonly desired
behaviors for a bot as `mixin`_ classes that can be used via `multiple
inheritance`_::

    from ib3 import Bot
    from ib3.auth import SASL
    from ib3.connection import SSL
    from ib3.mixins import DisconnectOnError

    class TestBot(SASL, SSL, DisconnectOnError, Bot):
        pass

Installation
============
* ``python3 -m pip install --upgrade ib3`` (recommended)
* ``python3 -m pip install .`` (from source distribution)

License
=======
IB3 is licensed under the `GPL-3.0-or-later`_ license.

Credits
=======
Some code and much inspiration taken from Wikimedia irc bots `Adminbot`_,
`Jouncebot`_, and `Stashbot`_.

.. _irc: https://pypi.org/project/irc/
.. _mixin: https://en.wikipedia.org/wiki/Mixin
.. _multiple inheritance: https://docs.python.org/3/tutorial/classes.html#multiple-inheritance
.. _GPL-3.0-or-later: https://www.gnu.org/copyleft/gpl.html
.. _Adminbot: https://phabricator.wikimedia.org/diffusion/ODAC/
.. _Jouncebot: https://phabricator.wikimedia.org/diffusion/GJOU/
.. _Stashbot: https://phabricator.wikimedia.org/diffusion/LTST/
