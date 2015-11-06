from solar import events as evapi
from solar.core.resource import virtual_resource as vr
from solar.interfaces.db import get_db

import yaml

db = get_db()

STORAGE = {'objects_ceph': False,
           'osd_pool_size': 2,
           'pg_num': 128,
           'images_ceph': True,
           'images_vcenter': False,
           'volumes_lvm': False,
           'ephemeral_ceph': False,
           'iser': False,
           'volumes_ceph': True}

KEYSTONE = {'admin_token': 'abcde'}


NETWORK_SCHEMA = {
    'endpoints': {'eth1': {'IP': ['10.0.0.4/24']}},
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
        - compute
      name: solar-dev1

    """)


def deploy():
    db.clear()
    resources = vr.create('nodes', 'templates/nodes.yaml', {'count': 2})
    first_node, second_node = [x for x in resources if x.name.startswith('solar-dev')]

    library1 = vr.create('library1', 'resources/fuel_library',
        {'temp_directory': '/tmp/solar',
       'puppet_modules': '/etc/fuel/modules',
       'git':{'branch': 'master', 'repository': 'https://github.com/stackforge/fuel-library'},
       'librarian_puppet_simple': 'true'})[0]

    library2 = vr.create('library2', 'resources/fuel_library',
        {'temp_directory': '/tmp/solar',
       'puppet_modules': '/etc/fuel/modules',
       'git':{'branch': 'master', 'repository': 'https://github.com/stackforge/fuel-library'},
       'librarian_puppet_simple': 'true'})[0]

    ceph_pools1 = vr.create('ceph_pools1', 'resources/ceph_pools',
        {'storage': STORAGE,
         'keystone': KEYSTONE,
         'network_scheme': NETWORK_SCHEMA,
         'ceph_monitor_nodes': NETWORK_METADATA,
         'ceph_primary_monitor_node': NETWORK_METADATA,
         'use_neutron': True,
         'role': 'primary-controller',
         })[0]
    
    ceph_compute2 = vr.create('ceph_compute2', 'resources/ceph_compute',
        {'storage': STORAGE,
         'keystone': KEYSTONE,
         'network_scheme': NETWORK_SCHEMA,
         'ceph_monitor_nodes': NETWORK_METADATA,
         'ceph_primary_monitor_node': NETWORK_METADATA,
         'use_neutron': True,
         'role': 'compute',
         })[0]

    glance_backend_rbd_puppet1 = vr.create('glance_backend_rbd_puppet1', 'resources/glance_backend_rbd_puppet', {})[0]
    first_node.connect(glance_backend_rbd_puppet1, {})

    cinder_volume_rbd_puppet1 = vr.create('cinder_volume_rbd_puppet1', 'resources/cinder_volume_rbd_puppet', {})[0]
    first_node.connect(cinder_volume_rbd_puppet1, {})

    first_node.connect(ceph_pools1,
        {'ip': ['ip', 'public_vip', 'management_vip']})
    first_node.connect(library1, {})
    library1.connect(ceph_pools1, {'puppet_modules': 'puppet_modules'})

    second_node.connect(ceph_compute2,
        {'ip': ['ip', 'public_vip', 'management_vip']})
    second_node.connect(library2, {})
    library2.connect(ceph_compute2, {'puppet_modules': 'puppet_modules'})

    evapi.add_dep(second_node.name, ceph_compute2.name, actions=('run',))
    evapi.add_dep(first_node.name, ceph_pools1.name, actions=('run',))

if __name__ == '__main__':
    deploy()
