FROM python:3.7-slim-buster AS compile-image
LABEL maintainer="Wazo Maintainers <dev@wazo.community>"

RUN apt-get -qq update && apt-get -qq -y install gcc
RUN python3 -m venv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /usr/local/src/wazo-confgend/requirements.txt
WORKDIR /usr/local/src/wazo-confgend
# incremental is needed by twisted setup
RUN pip install -r requirements.txt

COPY setup.py /usr/local/src/wazo-confgend/
COPY bin /usr/local/src/wazo-confgend/bin
COPY wazo_confgend /usr/local/src/wazo-confgend/wazo_confgend
RUN python setup.py install

FROM python:3.7-slim-buster AS build-image
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
