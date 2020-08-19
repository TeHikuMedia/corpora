#!/usr/bin/env python

import sys
import os
import argparse
import re
from time import time


try:
    import json
except ImportError:
    import simplejson as json


class VagrantInventory(object):
    def _empty_inventory(self):
        return {"_meta" : {"hostvars" : {}}}

    def __init__(self):
        ''' Main execution path '''

        # Inventory grouped by instance IDs, tags, security groups, regions,
        # and availability zones
        self.inventory = self._empty_inventory()


        cmd = 'ssh vagrant@localhost -p 2226 -i .vagrant/machines/default/virtualbox/private_key ip -f inet address show eth1 | grep "inet " | cut -d "/" -f 1 | cut -d "t" -f 2 > tmp'

        os.system(cmd)

        f = open('tmp','r')
        host = f.read().strip()
        group = 'vagrant'
        f.close()
        os.system('rm tmp')

        vagrant_dictionary = {
            host: {
                'ansible_ip': host,
                'ansible_ssh_port':22,
                'ansible_ssh_private_key':'.vagrant/machines/default/virtualbox/private_key',
                'ansible_ssh_user':'vagrant'
            }
        }

        self.inventory['all'] = {
            "children": [group]
        }

        self.inventory[group] = {
            "hosts": [host]
        }

        self.inventory['_meta']['hostvars'] = vagrant_dictionary
        data_to_print = self.json_format_dict(self.inventory, True)
        print(data_to_print)

    def json_format_dict(self, data, pretty=False):
        ''' Converts a dict to a JSON object and dumps it as a formatted
        string '''

        if pretty:
            return json.dumps(data, sort_keys=True, indent=2)
        else:
            return json.dumps(data)


# Run the script
VagrantInventory()
