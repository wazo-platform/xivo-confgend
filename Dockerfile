## Image to build from sources

FROM debian:latest
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add dependencies
RUN apt-get -qq update
RUN apt-get -qq -y install \
    git \
    apt-utils \
    python-pip \
    python-dev \
    libpq-dev \
    python-twisted

# Install xivo-confgend
WORKDIR /root
ADD . /root/confgend
WORKDIR confgend
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-confgend.log
RUN mkdir -p /etc/xivo/
RUN mkdir /var/lib/xivo-confgend
RUN cp -a etc/* /etc/xivo/
WORKDIR /root

# Clean
RUN apt-get clean
RUN rm -rf /root/confgend

EXPOSE 8669

CMD twistd -no -y /usr/local/bin/xivo-confgend
