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

        print kwargs
        conf = kwargs.get('conf')
        self.vz_iface = conf.get('vz_iface', VZ_DEFAULT_IFACE)
        self.base_image = conf.get('base_image', DEFAULT_IMAGE)

    def _exists(self, id):
        return os.path.isfile(os.path.join(VZ_CONFIG_PATH, '{}.conf'.format(id)))

    def _base_ip(self):
        return netifaces.ifaddresses(self.vz_iface)[netifaces.AF_INET][0].get('addr').split('.')


    def create(self, *args, **kwargs):

        id = kwargs.get('id')
        if self._exists(id):
            raise VMHandlerException('vm #{} exists'.format(id))
        if not os.path.exists(self.base_image):
            raise VMHandlerException('image does not exist: {}'.format(self.base_image))

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

        """
        vzrestore /vm/base/debian_7.8.tar 109 -storage nodes
        vzctl set 109 --hostname "node09.chumba" --save
        vzctl set 109 --ipadd {} --save
        vzctl set 109 --onboot yes --save
        """

        commands = [
            '{} {} {} -storage={}'.format(
                VZRESTORE_BINARY,
                self.base_image,
                id,
                DEFAULT_STORAGE
            ),
            'vzctl set {id} --hostname "{hostname}" --save'.format(id=id, hostname=hostname),
            'vzctl set {id} --ipdel all --save'.format(id=id),
            'vzctl set {id} --ipadd {ip} --save'.format(id=id, ip=ip),
        ]

        for command in commands:
            log.debug('running command: {}'.format(command))
            #local(command)

        pass