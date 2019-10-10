FROM python:2.7-buster
MAINTAINER Wazo Maintainers <dev@wazo.community>

ENV DEBIAN_FRONTEND noninteractive

ADD . /usr/src/wazo-confgend
WORKDIR /usr/src/wazo-confgend
RUN apt-get -qq update \
    && apt-get -qq -y install apt-utils libpq-dev python-twisted \
    && pip install -r requirements.txt \
    && python setup.py install \
    && adduser --quiet --system --group --no-create-home wazo-confgend \
    && install -o wazo-confgend -g wazo-confgend /dev/null /var/log/wazo-confgend.log \
    && install -d -o wazo-confgend -g wazo-confgend /run/wazo-confgend \
    && mkdir -p /var/cache/wazo-confgend \
    && cp -a etc/* /etc \
    && apt-get clean

EXPOSE 8669

CMD ["/usr/local/bin/wazo-confgend"]
