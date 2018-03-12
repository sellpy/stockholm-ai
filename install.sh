#!/bin/sh -e

export DEBIAN_FRONTEND=noninteractive

echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | tee /etc/apt/sources.list.d/tensorflow-serving.list
curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | apt-key add -

apt-get update
apt-get upgrade -y


PACKAGES=$(xargs <<EOF
build-essential
curl
git
nano
wget
python3-dev
python3-setuptools
python3-tk
python3-wheel
python-psycopg2
python3-pip
tensorflow-model-server
gfortran
swig
libagg-dev
libatlas-dev
libffi-dev
libfreetype6-dev
liblapack-dev
libncurses5-dev
libopenblas-dev
libpng12-dev
libpq-dev
libzmq3-dev
libxft-dev
libxml2-dev
libxslt-dev
zlib1g-dev
mlocate
pkg-config
ttf-bitstream-vera
software-properties-common
zip
libcurl3-dev
libsm6
EOF
)

apt-get install -y $PACKAGES
apt-get clean
