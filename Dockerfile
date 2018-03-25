FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        git \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ADD install.sh /tmp/install.sh
RUN sh -e /tmp/install.sh

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt


# Seems TFserving turned ugly for ubuntu16.04
# https://github.com/tensorflow/serving/issues/819
RUN add-apt-repository ppa:ubuntu-toolchain-r/test -y
RUN apt-get update -y && apt-get upgrade -y && apt-get dist-upgrade -y

WORKDIR /app
ADD . /app