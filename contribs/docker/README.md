Dockerfile for XiVO confgend

## Install Docker

To install docker on Linux :

    curl -sL https://get.docker.io/ | sh
 
 or
 
     wget -qO- https://get.docker.io/ | sh

## Build

To build the image, simply invoke

    docker build -t xivo-confgend github.com/wazo-pbx/xivo-confgen

Or directly in the sources in contribs/docker

    docker build -t xivo-confgend .
  
## Usage

To run the container, do the following:

    docker run -v /conf/confgend:/etc/xivo/ -p 8669:8669 -t xivo-confgend

On interactive mode :

    docker run -v /conf/confgend:/etc/xivo/ -p 8669:8669 -it xivo-confgend bash

After launch xivo-confgend-service in /root directory.

    twistd -no -y /usr/local/bin/xivo-confgend

## Infos

- Using docker version 1.4.0 (from get.docker.io) on ubuntu 14.04.
- If you want to using a simple webi to administrate docker use : https://github.com/crosbymichael/dockerui

To get the IP of your container use :

    docker ps -a
    docker inspect <container_id> | grep IPAddress | awk -F\" '{print $4}'
