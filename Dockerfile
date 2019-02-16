FROM ubuntu:xenial
LABEL maintainer="jonathan-lee@berkeley.edu"

RUN apt-get update -y
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y build-essential wget unzip python3.7 python3.7-dev python3-pip
RUN python3.7 -m pip install pipenv

WORKDIR /home/ubuntu
WORKDIR /home/ubuntu/protoc
RUN wget http://mirror.archlinuxarm.org/arm/extra/protobuf-3.6.1.3-1-arm.pkg.tar.xz
RUN tar -xf protobuf-3.6.1.3-1-arm.pkg.tar.xz
RUN rm protobuf-3.6.1.3-1-arm.pkg.tar.xz
RUN mv ./usr/bin/protoc /usr/bin/ 


WORKDIR /home/ubuntu/PieCentral
ADD ansible-protos ansible-protos
ADD runtime runtime
ADD hibike hibike

WORKDIR /home/ubuntu/PieCentral/runtime
ENV PATH="/home/ubuntu/bin:${PATH}" \
    PYTHONPATH="/home/ubuntu/PieCentral/runtime:/home/ubuntu/PieCentral/hibike:${PYTHONPATH}" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"
RUN pipenv install --dev --python=/usr/bin/python3.7
SHELL ["/bin/bash", "-c"]
RUN uname -a
RUN ls
COPY runtime/*_pb2.py .
RUN ls
EXPOSE 1234/tcp 1235/udp 1236/udp
CMD ["/usr/bin/env", "pipenv", "run", "python3", "/home/ubuntu/PieCentral/runtime/runtime.py"]
