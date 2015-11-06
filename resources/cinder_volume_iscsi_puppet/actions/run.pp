$iscsi_ip_address = hiera('iscsi_ip_address')
$volume_driver = hiera('volume_driver')
$volume_group = hiera('volume_group')
$volumes_dir = hiera('volumes_dir')
$iscsi_helper = hiera('iscsi_helper')
$iscsi_protocol = hiera('iscsi_protocol')

cinder::backend::iscsi { 'DEFAULT':
    iscsi_ip_address => $iscsi_ip_address,
    volume_driver    => $volume_driver,
    volume_group     => $volume_group,
    volumes_dir      => $volumes_dir,
    iscsi_helper     => $iscsi_helper,
    iscsi_protocol   => $iscsi_protocol,
    extra_options    => {},
} ~>

service {'cinder-volume':}
