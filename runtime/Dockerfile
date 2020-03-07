FROM python:3.8-alpine AS base
LABEL maintainer="devops@pioneers.berkeley.edu"
ENV SHELL /bin/sh
# Reduce size of the package
RUN apk add binutils build-base python3-dev libuv udev
RUN strip --strip-all /usr/local/lib/*.so*
RUN strip --strip-all /usr/local/lib/python3.8/lib-dynload/*.so*
RUN rm -f /usr/local/lib/python3.8/config-*/libpython3.8.a
# Build libzmq with DRAFT socket support
WORKDIR /tmp
ENV ZMQ_VERSION 4.3.2
RUN wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz
RUN tar -xzf libzmq.tar.gz
WORKDIR /tmp/zeromq-${ZMQ_VERSION}
RUN ./configure --prefix=/usr/local --enable-drafts
RUN make -j 4 && make install
WORKDIR /tmp
RUN rm libzmq.tar.gz && rm -rf zeromq-${ZMQ_VERSION}
# Install pip packages
WORKDIR /root/runtime
RUN pip3 install pipenv
ADD Pipfile Pipfile
ADD setup.py setup.py
ADD runtime runtime
RUN pipenv install --pre
RUN pipenv run build
RUN pipenv run pip3 install --pre pyzmq --install-option=--enable-drafts --install-option=--zmq=${ZMQ_VERSION}
RUN rm -rf ~/.cache
EXPOSE 6000-6010

FROM base AS development
RUN pipenv install --pre --dev
ADD runtime runtime
CMD ["/usr/bin/env", "pipenv", "run", "dev"]

FROM base AS production
ADD runtime runtime
RUN apk del build-base python3-dev linux-headers
CMD ["/usr/bin/env", "pipenv", "run", "prod"]
