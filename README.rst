=============================
IRC Bot Behavior Bundle (IB3)
=============================

IRC bot framework using mixins to provide commonly desired functionality.

Mixins
======
* DisconnectOnError: Handle ERROR message by logging and disconnecting
* FreenodePasswdAuth: Authenticate with NickServ before joining channels
* Ping: Add checks for connection liveness using PING commands
* RejoinOnBan: Handle ERR_BANNEDFROMCHAN by attempting to rejoin channel
* RejoinOnKick: Handle KICK by attempting to rejoin channel

License
=======
`GNU GPLv3+`_

Some code and much inspiration taken from:

* `Adminbot`_
* `Jouncebot`_
* `Stashbot`_

.. _GNU GPLv3+: https://www.gnu.org/copyleft/gpl.html
.. _Adminbot: https://phabricator.wikimedia.org/diffusion/ODAC/
.. _Jouncebot: https://phabricator.wikimedia.org/diffusion/GJOU/
.. _Stashbot: https://phabricator.wikimedia.org/diffusion/LTST/
