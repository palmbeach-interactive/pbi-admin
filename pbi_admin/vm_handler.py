# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import logging
import netifaces
from fabric.api import local
from fabric.operations import prompt
from logging.config import fileConfig


VZ_CONFIG_PATH = '/etc/pve/openvz/'
#VZ_CONFIG_PATH = '/Users/ohrstrom/Documents/Code/pbi/pbi-admin/dev/etc/'
LXC_CONFIG_PATH = '/etc/pve/lxc/'
DEFAULT_IMAGE = '/storage/nfs/shared/vm/images/debian-8-base.tar'
DEFAULT_STORAGE = 'nodes'
DEFAULT_VIRTUALIZATION_TYPE = 'openvz'
DEFAULT_NETWORK_TYPE = 'ip'
DEFAULT_HOSTNAME_SUFFIX = 'auto'
DEFAULT_HOSTNAME_PREFIX = 'node'
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
        self.virtualization_type = conf.get('virtualization_type', DEFAULT_VIRTUALIZATION_TYPE)
        self.network_type = conf.get('network_type', DEFAULT_NETWORK_TYPE)
        self.hostname_suffix = conf.get('hostname_suffix', DEFAULT_HOSTNAME_SUFFIX)
        self.hostname_prefix = conf.get('hostname_prefix', DEFAULT_HOSTNAME_PREFIX)
        self.quiet = kwargs.get('quiet', False)
        self.fake = kwargs.get('fake', False)

    def _exists(self, id):

        if self.virtualization_type == 'openvz':
            return os.path.isfile(os.path.join(VZ_CONFIG_PATH, '{}.conf'.format(id)))

        if self.virtualization_type == 'lxc':
            return os.path.isfile(os.path.join(LXC_CONFIG_PATH, '{}.conf'.format(id)))

    def _base_ip(self):
        return netifaces.ifaddresses(self.vz_iface)[netifaces.AF_INET][0].get('addr').split('.')

    def _base_mac(self, id):

        base_ip = self._base_ip()
        host_bits = str(base_ip[-1]).zfill(4)
        node_bits = str(id).zfill(4)

        return '00:00:{}:{}:{}:{}'.format(
            host_bits[0:2],
            host_bits[2:4],
            node_bits[0:2],
            node_bits[2:4]
        )


    def create(self, override_id=None, *args, **kwargs):

        if override_id:
            id = override_id
        else:
            id = kwargs.get('id')

        if self._exists(id):

            if prompt('vm #{} exists. DO YOU WANT TO DESTROY IT???'.format(id), default='n').lower() == 'y':

                if self.virtualization_type == 'openvz':
                    commands = [
                        'vzctl stop {id}'.format(id=id),
                        'vzctl destroy {id}'.format(id=id),
                    ]

                if self.virtualization_type == 'lxc':
                    commands = [
                        'pct stop {id}'.format(id=id),
                        'pct destroy {id}'.format(id=id),
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


        if not self.hostname_suffix:
            hostname = '{}{}'.format(self.hostname_prefix, id)
        elif self.hostname_suffix == 'auto':
            import socket
            hostname_suffix = socket.gethostname()
            hostname = '{}{}.{}'.format(self.hostname_prefix, id, hostname_suffix)
        else:
            hostname = '{}{}.{}'.format(self.hostname_prefix, id, self.hostname_suffix)


        """
        vzrestore /tmp/slow_query.log 126 -storage=nodes
        vzctl set 126 --hostname "node126" --save
        vzctl set 126 --ipdel all --save
        vzctl set 126 --ipadd 10.40.10.126 --save
        vzctl set 126 --onboot yes --save
        vzctl enter 126
        """

        commands = []

        if self.virtualization_type == 'openvz':
            commands = [
                'vzrestore {} {} -storage={}'.format(self.base_image, id, self.node_storage),
                'vzctl set {id} --hostname "{hostname}" --save'.format(id=id, hostname=hostname),
                'vzctl set {id} --ipadd {ip} --save'.format(id=id, ip=ip),
            ]

        if self.virtualization_type == 'lxc':
            commands = [
                'pct restore {} {} -storage={}'.format(id, self.base_image, self.node_storage),
                'pct set {id} -hostname "{hostname}"'.format(id=id, hostname=hostname),
                'pct set {id} -swap 0'.format(id=id),
            ]
            if self.network_type == 'ip':
                # TODO: no hardcoded subnet
                commands.append(
                    'pct set {id} -net0 name=eth0,bridge=vmbr0,ip={ip}/24,type=veth'.format(id=id, ip=ip)
                )
            if self.network_type == 'mac':
                """
                pct set 203 -net0 name=eth0,bridge=vmbr0,hwaddr=00:00:00:33:02:03,ip=dhcp,type=veth
                """
                mac = self._base_mac(id)
                commands.append(
                    'pct set {id} -net0 name=eth0,bridge=vmbr0,hwaddr={hwaddr},ip=dhcp,type=veth'.format(id=id, hwaddr=mac)
                )

        if not self.quiet:

            if prompt('enable on-boot?', default='n').lower() == 'y':
                if self.virtualization_type == 'openvz':
                    commands.append(
                        'vzctl set {id} --onboot yes --save'.format(id=id)
                    )
                if self.virtualization_type == 'lxc':
                    commands.append(
                        'pct set {id} -onboot 1'.format(id=id)
                    )

            if prompt('start container?', default='n').lower() == 'y':
                if self.virtualization_type == 'openvz':
                    commands.append(
                        'vzctl start {id}'.format(id=id)
                    )
                if self.virtualization_type == 'lxc':
                    commands.append(
                        'pct start {id}'.format(id=id)
                    )

            if prompt('open console?', default='n').lower() == 'y':
                if self.virtualization_type == 'openvz':
                    commands.append(
                        'vzctl enter {id}'.format(id=id)
                    )
                if self.virtualization_type == 'lxc':
                    commands.append(
                        'pct enter {id}'.format(id=id)
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



