FROM python:2.7-slim-buster AS compile-image
LABEL maintainer="Wazo Maintainers <dev@wazo.community>"

RUN apt-get -qq update && apt-get -qq -y install python-virtualenv
RUN virtualenv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get install -y gcc

COPY requirements.txt /usr/local/src/wazo-confgend/requirements.txt
WORKDIR /usr/local/src/wazo-confgend
RUN pip install -r requirements.txt

COPY setup.py /usr/local/src/wazo-confgend/
COPY bin /usr/local/src/wazo-confgend/bin
COPY wazo_confgend /usr/local/src/wazo-confgend/wazo_confgend
RUN python setup.py install

FROM python:2.7-slim-buster AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY ./etc/wazo-confgend /etc/wazo-confgend
RUN true\
    && adduser --quiet --system --group --home /var/lib/wazo-confgend wazo-confgend \
    && mkdir -p /etc/wazo-confgend/conf.d \
    && install -D -o wazo-confgend -g wazo-confgend /dev/null /var/log/wazo-confgend.log \
    && install -d -o wazo-confgend -g wazo-confgend /var/cache/wazo-confgend

EXPOSE 8668

# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"
CMD ["wazo-confgend"]
