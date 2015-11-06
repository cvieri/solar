$rbd_pool = hiera('rbd_pool')
$rbd_user = hiera('rbd_user')
$rbd_ceph_conf = hiera('rbd_ceph_conf')
$rbd_flatten_volume_from_snapshot = hiera('rbd_flatten_volume_from_snapshot')
$rbd_secret_uuid = hiera('rbd_secret_uuid')
$volume_tmp_dir = hiera('volume_tmp_dir')
$rbd_max_clone_depth = hiera('rbd_max_clone_depth')
$glance_api_version = hiera('glance_api_version')

cinder::backend::rbd { 'DEFAULT':
  rbd_pool                         => $rbd_pool,
  rbd_user                         => $rbd_user,
  rbd_ceph_conf                    => $rbd_ceph_conf,
  rbd_flatten_volume_from_snapshot => $rbd_flatten_volume_from_snapshot,
  rbd_secret_uuid                  => $rbd_secret_uuid,
  volume_tmp_dir                   => $volume_tmp_dir,
  rbd_max_clone_depth              => $rbd_max_clone_depth,
  glance_api_version               => $glance_api_version,
} ~>

service {'cinder-volume':}
