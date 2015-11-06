$stores                = hiera('stores')
$default_store         = hiera('default_store')
$rbd_store_ceph_conf   = hiera('rbd_store_ceph_conf')
$rbd_store_user        = hiera('rbd_store_user')
$rbd_store_pool        = hiera('rbd_store_pool')
$rbd_store_chunk_size  = hiera('rbd_store_chunk_size')
$rados_connect_timeout = hiera('rados_connect_timeout')

package { 'python-ceph':
  ensure => latest,
} ->

glance_api_config {
  'glance_store/stores':                 value => $stores;
  'glance_store/default_store':          value => $default_store;
  'glance_store/rbd_store_ceph_conf':    value => $rbd_store_ceph_conf;
  'glance_store/rbd_store_user':         value => $rbd_store_user;
  'glance_store/rbd_store_pool':         value => $rbd_store_pool;
  'glance_store/rbd_store_chunk_size':   value => $rbd_store_chunk_size;
  'glance_store/rados_connect_timeout':  value => $rados_connect_timeout;
} ~>

service {'glance-api': }
