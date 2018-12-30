FROM python:3.7-alpine
LABEL maintainer="runtime@pioneers.berkeley.edu"

RUN apk update && apk upgrade
RUN pip3 install pipenv

WORKDIR /root
ADD runtime runtime
ADD hibike hibike

WORKDIR /root/runtime
ENV PYTHONPATH="/root/runtime:/root/hibike:${PYTHONPATH}" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"
RUN pipenv install
EXPOSE 1234/tcp 1235/udp 1236/udp
CMD ["/bin/ash"]
# CMD ["/usr/bin/env", "pipenv", "run", "python3", "runtime.py"]

# RUN apt update -y && apt upgrade -y
# RUN apt install -y build-essential wget unzip python3 python3-dev python3-pip
# RUN pip3 install pipenv

# WORKDIR /home/ubuntu
# WORKDIR /home/ubuntu/protoc
# RUN wget https://github.com/google/protobuf/releases/download/v3.2.0/protoc-3.2.0-linux-x86_64.zip
# RUN unzip protoc-3.2.0-linux-x86_64.zip
# RUN rm protoc-3.2.0-linux-x86_64.zip
# RUN mv bin /home/ubuntu

# WORKDIR /home/ubuntu/PieCentral
# ADD ansible-protos ansible-protos
# ADD runtime runtime
# ADD hibike hibike

# WORKDIR /home/ubuntu/PieCentral/runtime
# ENV PATH="/home/ubuntu/bin:${PATH}" \
#     PYTHONPATH="/home/ubuntu/PieCentral/runtime:/home/ubuntu/PieCentral/hibike:${PYTHONPATH}" \
#     LC_ALL="C.UTF-8" \
#     LANG="C.UTF-8"
# RUN pipenv install --dev
# RUN protoc -I ../ansible-protos --python_out=. ../ansible-protos/*.proto
# EXPOSE 1234/tcp 1235/udp 1236/udp
# CMD ["/usr/bin/env", "pipenv", "run", "python3", "runtime.py"]
