FROM wazoplatform/wazo-confgend:local
ARG WAZO_CONFGEND_CLIENT_REV=master

# install useful utilities
RUN apt-get -y update && apt-get install -y inetutils-ping
# get wazo-confgen client binary from repo.
ADD --chmod=700 https://raw.githubusercontent.com/wazo-platform/wazo-confgend-client/$WAZO_CONFGEND_CLIENT_REV/bin/wazo-confgen /usr/local/bin/wazo-confgen

# add back source code and install over version "compiled" in base image.
COPY . /usr/local/src/wazo-confgend
WORKDIR /usr/local/src/wazo-confgend
RUN python setup.py develop
ENV PATH="/opt/venv/bin:$PATH"

# volume for test data
VOLUME /data

CMD ["/opt/venv/bin/wazo-confgend"]
