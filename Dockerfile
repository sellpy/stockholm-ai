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

WORKDIR /app
ADD . /app