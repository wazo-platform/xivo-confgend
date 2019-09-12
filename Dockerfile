## Image to build from sources

FROM debian:buster
MAINTAINER Wazo Maintainers <dev@wazo.community>

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
RUN mkdir /var/lib/xivo-confgend
RUN cp -a etc/* /etc
WORKDIR /root

# Clean
RUN apt-get clean
RUN rm -rf /root/confgend

EXPOSE 8669

CMD /usr/local/bin/xivo-confgend
