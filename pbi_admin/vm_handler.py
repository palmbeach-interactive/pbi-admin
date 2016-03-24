# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import logging
import netifaces
from fabric.api import local
from logging.config import fileConfig


VZ_CONFIG_PATH = '/etc/vz/conf/'
CONFIG_PATH = '/Users/ohrstrom/Documents/Code/pbi/pbi-admin/dev/etc/'
DEFAULT_IMAGE = '/storage/nfs/shared/vm/images/debian-8-base.tar'
DEFAULT_STORAGE = 'nodes'
BASE_IP = '10.11.1.'
VZRESTORE_BINARY = '/usr/bin/vzrestore'
VZ_DEFAULT_IFACE = 'en4'

VM_MIN_ID = 101
VM_MAX_ID = 250

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

class VMHandlerException(Exception):
    pass

class VMHandler:

    def __init__(self, *args, **kwargs):
        pass

    def _exists(self, id):
        return os.path.isfile(os.path.join(VZ_CONFIG_PATH, '{}.conf'.format(id)))

    def _base_ip(self, iface=VZ_DEFAULT_IFACE):
        return netifaces.ifaddresses(iface)[netifaces.AF_INET][0].get('addr').split('.')


    def create(self, *args, **kwargs):

        id = kwargs.get('id')
        if self._exists(id):
            raise VMHandlerException('vm #{} exists'.format(id))

        if id < VM_MIN_ID or id > VM_MAX_ID:
            raise VMHandlerException('id out of accepted range [{}-{}]'.format(VM_MIN_ID, VM_MAX_ID))


        base_ip = self._base_ip()
        ip = '{}.{}.{}.{}'.format(
            base_ip[0],
            base_ip[1],
            base_ip[2],
            id
        )

        hostname = 'node{}'.format(id)

        print ip
        print hostname



        commands = [
            '{} {} {} -storage={}'.format(
                VZRESTORE_BINARY,
                DEFAULT_IMAGE,
                id,
                DEFAULT_STORAGE
            ),
        ]

        for command in commands:
            log.debug('running command: {}'.format(command))
            #local(command)

        pass