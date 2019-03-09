FROM python:3.7-alpine
LABEL maintainer="runtime@pioneers.berkeley.edu"

RUN apk update && apk upgrade
RUN pip3 install pipenv

WORKDIR /root
ADD ansible-protos ansible-protos
ADD runtime runtime
ADD hibike hibike

WORKDIR /root/runtime
RUN mkdir -p store
RUN pipenv install

ENV PYTHONPATH="/root/runtime:/root/hibike:${PYTHONPATH}" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"

EXPOSE 1234/tcp 1235/udp 1236/udp
CMD ["/usr/bin/env", "pipenv", "run", "python3", "runtime.py"]
