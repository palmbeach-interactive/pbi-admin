pbi.io - CLI admin tools
========================



Prerequisites
-------------

Usually our systems have these packages installed by default. On a bare machine you will have to install:

    apt-get install python-setuptools git autoconf build-essential python-dev
    easy_install pip


Installation
------------

    pip install -e git+https://github.com/palmbeach-interactive/pbi-admin.git#egg=pbi-admin

Configuration
-------------

Create a config file at '~/.pbi-admin.cfg' (this is the default path. can alternatively be provided using the '--config' option)

    nano ~/.pbi-admin.cfg

should look like;

    vz_iface=eth1
    base_image=/storage/nfs/shared/vm/images/debian-8-base.tar
    node_storage=nodes



Usage
-----

VM
::

    pbi_vm create -i 153

    pbi_vm bulk_create -i 111 -n 50
