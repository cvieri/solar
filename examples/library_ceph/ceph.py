from solar import events as evapi
from solar.core.resource import virtual_resource as vr
from solar.interfaces.db import get_db

import yaml

db = get_db()

STORAGE = {'objects_ceph': True,
           'osd_pool_size': 2,
           'pg_num': 128}

KEYSTONE = {'admin_token': 'abcde'}


NETWORK_SCHEMA = {
    'endpoints': {'eth1': {'IP': ['10.0.0.3/24']}},
    'roles': {'ceph/replication': 'eth1',
              'ceph/public': 'eth1'}
    }

NETWORK_METADATA = yaml.load("""
    solar-dev1:
      uid: '1'
      fqdn: solar-dev1
      network_roles:
        ceph/public: 10.0.0.3
        ceph/replication: 10.0.0.3
      node_roles:
        - ceph-mon
      name: solar-dev1

    """)


def deploy():
    db.clear()
    resources = vr.create('nodes', 'templates/nodes.yaml', {'count': 2})
    first_node, second_node = [x for x in resources if x.name.startswith('solar-dev')]
    first_transp = next(x for x in resources if x.name.startswith('transport'))
    
    host1,  host2 = [x for x in resources if x.name.startswith('hosts_file')]

    library1 = vr.create('library1', 'resources/fuel_library', {})[0]
    library2 = vr.create('library2', 'resources/fuel_library',
      {'temp_directory': '/tmp/solar',
      'puppet_modules': '/etc/fuel/modules',
      'git':{'branch': 'master', 'repository': 'https://github.com/stackforge/fuel-library'},
      'librarian_puppet_simple': 'true'})[0] 

    keys = vr.create('ceph_key', 'resources/ceph_keys', {})[0]
    first_node.connect(keys)

    remote_file = vr.create('ceph_key2', 'resources/remote_file',
    {'dest': '/var/lib/astute/'})[0]
    second_node.connect(remote_file)
    keys.connect(remote_file, {'ip': 'remote_ip', 'path': 'remote_path'})
    first_transp.connect(remote_file, {'transports': 'remote'})

    remote_file = vr.create('ceph_key2', 'resources/remote_file',
      {'dest': '/var/lib/astute/'})[0]
    second_node.connect(remote_file)
    keys.connect(remote_file, {'ip': 'remote_ip', 'path': 'remote_path'})
    first_transp.connect(remote_file, {'transports': 'remote'})

    ceph_disk = vr.create('ceph_disk1', 'resources/ceph_disk',
        {'disk_name': '/dev/vdb'})[0]

    second_node.connect(ceph_disk, {})

    ceph_mon = vr.create('ceph_mon1', 'resources/ceph_mon',
        {'storage': STORAGE,
         'keystone': KEYSTONE,
         'network_scheme': NETWORK_SCHEMA,
         'ceph_monitor_nodes': NETWORK_METADATA,
         'ceph_primary_monitor_node': NETWORK_METADATA,
         'role': 'primary-controller',
         })[0]

    ceph_osd = vr.create('ceph_osd2', 'resources/ceph_osd',
        {'storage': STORAGE,
         'keystone': KEYSTONE,
         'network_scheme': NETWORK_SCHEMA,
         'ceph_monitor_nodes': NETWORK_METADATA,
         'ceph_primary_monitor_node': NETWORK_METADATA,
         'role': 'ceph-osd',
         })[0]

    managed_apt1 = vr.create(
      'managed_apt1', 'templates/mos_repos.yaml',
      {'node': first_node.name, 'index': 0})[-1]

    managed_apt2 = vr.create(
      'managed_apt2', 'templates/mos_repos.yaml',
      {'node': second_node.name, 'index': 1})[-1]

    first_node.connect(library1, {})
    second_node.connect(library2, {})

    first_node.connect(ceph_mon,
        {'ip': ['ip', 'public_vip', 'management_vip']})
    second_node.connect(ceph_osd,
        {'ip': ['ip', 'public_vip', 'management_vip']})
    library1.connect(ceph_mon, {'puppet_modules': 'puppet_modules'})
    library2.connect(ceph_osd, {'puppet_modules': 'puppet_modules'})

    evapi.add_dep(second_node.name, ceph_osd.name, actions=('run',))
    evapi.add_dep(first_node.name, ceph_mon.name, actions=('run',))
    evapi.add_dep(keys.name, ceph_mon.name, actions=('run',))
    evapi.add_dep(remote_file.name, ceph_osd.name, actions=('run',))
    evapi.add_dep(managed_apt1.name, ceph_mon.name, actions=('run',))
    evapi.add_dep(managed_apt2.name, ceph_osd.name, actions=('run',))
    evapi.add_dep(ceph_mon.name, ceph_osd.name, actions=('run',))
    evapi.add_dep(ceph_disk.name, ceph_osd.name, actions=('run',))


if __name__ == '__main__':
    deploy()
