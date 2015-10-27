#!/bin/bash

mkdir -p {{temp_directory}}
use_librarin_simple={{librarian_puppet_simple}}


pushd {{temp_directory}}
if [ ! -d fuel-library ]
then
    git clone -b {{ git['branch'] }} {{ git['repository'] }}
else
    pushd ./fuel-library
    git pull
    popd
fi

[ -n $use_librarian_puppet_simple ] && gem install librarian-puppet-simple --no-ri --no-rdoc

pushd ./fuel-library/deployment
./update_modules.sh
popd

[ -n $use_librarian_puppet_simple ] && gem uninstall -x librarian-puppet-simple

mkdir -p {{puppet_modules}}
cp -r ./fuel-library/deployment/puppet/* {{puppet_modules}}
popd
