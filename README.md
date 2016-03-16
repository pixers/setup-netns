setup-netns
==========

`setup-netns` creates a network namespace, adds some veth interfaces and optionally adds them to bridges, then `exec()`s to another command.

Installation
---------------

    cd setup-netns
    pip install -U .

Usage
---------

`setup-netns [OPTIONS] COMMAND`

Options:

  * `--veth outer:inner[:mac]` - creates a veth interface pair. The `outer` interface will be moved outside the namespace, while the `inner` one will remain inside. Optionally, sets a mac address for the `inner` interface.
  * `--bridge br:outer:inner[:mac]` - same as above, but adds the `outer` interface to a bridge named `br`

All options can be given multiple times. The first thing that isn't an option is assumed to be the start of the commandline for the next command.

The `COMMAND` will replace the `setup-netns` process after setting up the namespace.
