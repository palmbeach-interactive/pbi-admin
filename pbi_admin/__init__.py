#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.0.1'

import argparse
import os
from vm_handler import VMHandler
from configobj import ConfigObj

DEFAULT_SOURCE = 'ssh://git@lab.hazelfire.com/palmbeach/example-com.git'


usage="""
----------------------------------------------------------------
PBI.IO - CLI admin tools
----------------------------------------------------------------
    ...
----------------------------------------------------------------
"""

epilog="""
- pbi.io -------------------------------------------------------
"""

def vm():

    parser = argparse.ArgumentParser(usage=usage, epilog=epilog)

    parser.add_argument(
        'action',
        metavar='<action>',
        help='Action',
    )
    parser.add_argument(
        '--config',
        dest='config_file',
        metavar='PATH',
        help='Config file path',
        default=os.path.expanduser('~/.pbi-admin.cfg'),
        required=False
    )
    parser.add_argument(
        '-i', '--id',
        dest='id',
        type=int,
        help='Node id',
        required=True
    )
    parser.add_argument(
        '-n', '--num',
        dest='num_instances',
        type=int,
        default=1,
        help='How many instances to create. Starting with "id" and incrementing. Only for "bulk_create" action.'
    )
    parser.add_argument(
        '-q', '--quiet',
        dest='quiet',
        help='No prompts',
        action='store_true',
        default=False
    )
    parser.add_argument(
        '--fake',
        dest='fake',
        help='Dry run. Just pretend...',
        action='store_true',
        default=False
    )

    args = parser.parse_args()
    args_dict = args.__dict__

    config_file = args_dict['config_file']
    if not os.path.isfile(config_file):
        raise IOError('Unable to read config file: {}'.format(config_file))

    conf = ConfigObj(os.path.expanduser('~/.pbi-admin.cfg'))
    args_dict['conf'] = conf

    action = args_dict['action']

    handler = VMHandler(**args_dict)
    getattr(handler, action)(**args_dict)
