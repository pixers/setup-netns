#! /usr/bin/env python3

from pyroute2 import IPRoute
import ctypes
import errno
import os
import sys

# linux/sched.h
CLONE_NEWNET = 0x40000000

libc = ctypes.CDLL("libc.so.6")
def unshare(flags):
    return_value = libc.unshare(flags)
    if return_value != 0:
        errno_val = ctypes.get_errno()
        raise OSError("unshare() called failed (errno={0} ({1}))".format(
            errno_val, errno.errorcode.get(errno_val, "?")))

outer_netns = os.open('/proc/self/ns/net', os.O_RDONLY)
outer_ip = IPRoute()

unshare(CLONE_NEWNET)
inner_ip = IPRoute()
def create_veth(outer_name, inner_name, mac=None):
    # Create the interface
    peer_name = inner_name
    if mac:
        mac = '{}:{}:{}:{}:{}:{}'.format(mac[0:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:12])
        peer_name = {'address': mac, 'name': inner_name}
    inner_ip.link_create(ifname=outer_name, kind='veth', peer=peer_name)
    host_if = inner_ip.link_lookup(ifname=outer_name)[0]
    # And move the outer half to the parent namespace
    inner_ip.link('set', index=host_if, net_ns_fd=outer_netns)

    # Then set the interface's state to up,
    # otherwise the container couldn't use it's inteface
    # to communicate with the host.
    host_if = outer_ip.link_lookup(ifname=outer_name)[0]
    outer_ip.link_up(host_if)

def add_to_bridge(bridge, interface):
    interface = outer_ip.link_lookup(ifname=interface)[0]
    bridge = outer_ip.link_lookup(ifname=bridge)[0]
    outer_ip.link('set', index=interface, master=bridge)

def run():
    name = sys.argv.pop(0)
    while len(sys.argv) > 0:
        if sys.argv[0] == '--veth':
            sys.argv.pop(0)
            args = sys.argv.pop(0).split(':')
            if len(args) != 2 and len(args) != 3:
                print("setup-ns: Wrong format for --veth: '{}'."
                      "Use host_ifname:container_ifname[:mac]."
                      .format(':'.join(args)))
            create_veth(*args)
        elif sys.argv[0] == '--bridge':
            sys.argv.pop(0)
            args = sys.argv.pop(0).split(':')
            if len(args) != 3 and len(args) != 4:
                print("setup-ns: Wrong format for --veth: '{}'."
                      "Use bridge:host_ifname:container_ifname[:mac]."
                      .format(':'.join(args)))
            create_veth(*args[1:])
            add_to_bridge(args[0], args[1])
        else:
            os.execvp(sys.argv[0], sys.argv) 

    print("Usage: {} [--veth outer:inner...] [--bridge br:outer:inner...] command")
    sys.exit(1)

if __name__ == '__main__':
    run()
