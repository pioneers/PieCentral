FROM python:3.8-alpine AS base
ENV SHELL /bin/sh
ENV ZMQ_VERSION 4.3.2
LABEL maintainer="devops@pioneers.berkeley.edu"
# Reduce size of the package
RUN apk add binutils build-base python3-dev libuv
WORKDIR /tmp
RUN wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz
RUN tar -xzf libzmq.tar.gz
WORKDIR /tmp/zeromq-${ZMQ_VERSION}
RUN ./configure --prefix=/usr/local --enable-drafts
RUN make -j && make install
WORKDIR /tmp
RUN rm libzmq.tar.gz && rm -rf zeromq-${ZMQ_VERSION}
RUN strip --strip-all /usr/local/lib/*.so*
RUN strip --strip-all /usr/local/lib/python3.8/lib-dynload/*.so*
RUN rm -f /usr/local/lib/python3.8/config-*/libpython3.8.a
RUN pip3 install pipenv
WORKDIR /root/runtime
ADD Pipfile Pipfile
RUN pipenv install
EXPOSE 6000-6010
RUN pipenv run pip3 install -v --pre pyzmq --install-option=--enable-drafts --install-option=--zmq=${ZMQ_VERSION}
CMD ["/usr/bin/env", "pipenv", "run", "python3", "-m", "runtime", "run", "-l", "DEBUG", "-p"]
# --deploy, --dev

FROM base AS development
ADD runtime runtime

FROM base AS production
ADD runtime runtime
RUN apk del binutils build-base python3-dev
