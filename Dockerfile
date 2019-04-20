FROM alpine:edge
LABEL maintainer="runtime@pioneers.berkeley.edu"

RUN apk update && apk upgrade
RUN apk add python3 bash vim git
RUN pip3 install --upgrade pip
RUN pip3 install pipenv

ENV PYTHONPATH="/root/runtime:/root/hibike:${PYTHONPATH}" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"

WORKDIR /root
ADD runtime runtime
ADD hibike hibike

WORKDIR /root/runtime
RUN pipenv install

EXPOSE 1234:1234/tcp 1235:1235/udp 1236:1236/udp 6020:6020/tcp
CMD ["/usr/bin/env", "pipenv", "run", "python3", "runtime.py"]
