FROM python:3.8-alpine AS base
LABEL maintainer="devops@pioneers.berkeley.edu"
# Reduce size of the package
RUN apk add binutils build-base python3-dev zeromq-dev
RUN strip --strip-all /usr/local/lib/*.so*
RUN strip --strip-all /usr/local/lib/python3.8/lib-dynload/*.so*
RUN rm -f /usr/local/lib/python3.8/config-*/libpython3.8.a
RUN pip3 install pipenv
WORKDIR /root/runtime
ADD Pipfile Pipfile
RUN pipenv install
EXPOSE 6000-6010
CMD ["/usr/bin/env", "pipenv", "run", "python3", "-m", "runtime", "run", "-l", "DEBUG", "-p"]
# --deploy, --dev

FROM base AS development
ADD runtime runtime

FROM base AS production
ADD runtime runtime
RUN apk del binutils build-base python3-dev
