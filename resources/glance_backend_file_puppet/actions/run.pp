$iscsi_ip_address = hiera('filesystem_store_datadir')

glance_api_config {
  'glance_store/default_store':            value => 'file';
  'glance_store/filesystem_store_datadir': value => $filesystem_store_datadir;
} ~>

service {'glance-api':}

glance_cache_config {
  'glance_store/filesystem_store_datadir': value => $filesystem_store_datadir;
}
