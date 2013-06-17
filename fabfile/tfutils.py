#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# tfutils - installs tools and does some initial settings.
#

import os
import sys
from fabric.api import *
from fabric.contrib import *
from cuisine import *

@task
def install_pdsh():
    ''':opsys=XXXXX | Installs Parallel Distributed Shell'''
    if not env.user == 'root':
        print 'You need to login as root'
        exit(1)
    if dir_exists('/opt/pdsh-2.26'):
        print 'pdsh-2.26 is already installed.'
        exit(1)
    #package_update()
    distro = run('python -c "import platform; print platform.dist()[0].lower()"')
    if distro == 'centos' or \
            distro == 'redhat':
        select_package('yum')
        package_ensure('make gcc wget bzip2 openssl')
    elif distro == 'ubuntu' or \
            distro == 'debian':
        select_package('apt')
        package_update()
        package_ensure('build-essential')
    else:
        print 'currently supported: centos, redhat, ubuntu, debian'
    dir_ensure('/root/source')
    with cd('/root/source'):
        run('wget http://pdsh.googlecode.com/files/pdsh-2.26.tar.bz2')
        run('tar jxvf pdsh-2.26.tar.bz2')
    with cd('/root/source/pdsh-2.26'):
        run('./configure --prefix=/opt/pdsh-2.26 \
                         --without-rsh --with-ssh \
                         --with-dshgroups=/opt/pdsh-2.26/dshgroups')
        run('make')
        run('make install')
    with cd('/root'):
        files.append('.bashrc', 'export PATH=/opt/pdsh-2.26/bin:$PATH')

@task
def enable_root_login(authorized_keys='root/.ssh/authorized_keys'):
    '''| Enable root login'''
    if env.user == 'root':
        print 'You are trying to enable_root_login as root. A bit off sense.'
        exit(1)

    keyfile = 'private/tfutils/%s' % authorized_keys
    put(keyfile, '/root/.ssh/authorized_keys', mode=0640, use_sudo=True)
    sudo('chown root:root /root/.ssh/authorized_keys')

def ensure_users():
    '''| Ensure Users and ssh keys'''
    