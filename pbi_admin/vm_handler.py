# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import logging
import netifaces
from fabric.api import local
from fabric.operations import prompt
from logging.config import fileConfig


VZ_CONFIG_PATH = '/etc/vz/conf/'
VZ_CONFIG_PATH = '/Users/ohrstrom/Documents/Code/pbi/pbi-admin/dev/etc/'
DEFAULT_IMAGE = '/storage/nfs/shared/vm/images/debian-8-base.tar'
DEFAULT_STORAGE = 'nodes'
VZ_DEFAULT_IFACE = 'en4'

VM_MIN_ID = 101
VM_MAX_ID = 250

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

class VMHandlerException(Exception):
    pass

class VMHandler:

    def __init__(self, *args, **kwargs):

        #print kwargs
        conf = kwargs.get('conf')
        self.vz_iface = conf.get('vz_iface', VZ_DEFAULT_IFACE)
        self.base_image = conf.get('base_image', DEFAULT_IMAGE)
        self.node_storage = conf.get('node_storage', DEFAULT_STORAGE)
        self.quiet = kwargs.get('quiet', False)
        self.fake = kwargs.get('fake', False)

    def _exists(self, id):

        return os.path.isfile(os.path.join(VZ_CONFIG_PATH, '{}.conf'.format(id)))

    def _base_ip(self):
        return netifaces.ifaddresses(self.vz_iface)[netifaces.AF_INET][0].get('addr').split('.')


    def create(self, override_id=None, *args, **kwargs):

        if override_id:
            id = override_id
        else:
            id = kwargs.get('id')

        if self._exists(id):

            if prompt('vm #{} exists. DO YOU WANT TO DESTROY IT???'.format(id), default='n').lower() == 'y':

                commands = [
                    'vzctl stop {id}'.format(id=id),
                    'vzctl destroy {id}'.format(id=id),
                ]

                for command in commands:
                    log.debug('running command: {}'.format(command))
                    if not self.fake:
                        local(command)
            else:
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

        """
        vzrestore /tmp/slow_query.log 126 -storage=nodes
        vzctl set 126 --hostname "node126" --save
        vzctl set 126 --ipdel all --save
        vzctl set 126 --ipadd 10.40.10.126 --save
        vzctl set 126 --onboot yes --save
        vzctl enter 126
        """

        commands = [
            'vzrestore {} {} -storage={}'.format(self.base_image, id, self.node_storage),
            'vzctl set {id} --hostname "{hostname}" --save'.format(id=id, hostname=hostname),
            'vzctl set {id} --ipdel all --save'.format(id=id),
            'vzctl set {id} --ipadd {ip} --save'.format(id=id, ip=ip),
        ]

        if not self.quiet:

            if prompt('enable on-boot?', default='n').lower() == 'y':
                commands.append(
                    'vzctl set {id} --onboot yes --save'.format(id=id),
                )

            if prompt('start container?', default='n').lower() == 'y':
                commands.append(
                    'vzctl start {id}'.format(id=id),
                )

            if prompt('open console?', default='n').lower() == 'y':
                commands.append(
                    'vzctl enter {id}'.format(id=id),
                )


        for command in commands:
            log.debug('running command: {}'.format(command))
            if not self.fake:
                local(command)



    def bulk_create(self, *args, **kwargs):

        starting_id = kwargs.get('id')
        num_instances = kwargs.get('num_instances')
        self.quiet = True

        for id in range(starting_id, starting_id + num_instances):
            log.debug('check for existing containers: #{}'.format(id))
            if self._exists(id):
                raise VMHandlerException('vm #{} exists'.format(id))

        for id in range(starting_id, starting_id + num_instances):
            log.debug('create container: #{}'.format(id))
            self.create(override_id=id, *args, **kwargs)



