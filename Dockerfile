FROM gliderlabs/alpine:latest

LABEL maintainer="elastest-users@googlegroups.com"
LABEL description="Provides the sentinel syslog agent"
ARG GIT_COMMIT=unspecified
LABEL git_commit=$GIT_COMMIT
ARG COMMIT_DATE=unspecified
LABEL commit_date=$COMMIT_DATE
ARG VERSION=unspecified
LABEL version=$VERSION

WORKDIR /app
COPY src/syslog_agent.py /app
COPY src/config.py /app
COPY src/requirements.txt /app

RUN apk --update add --virtual build-deps python3-dev build-base linux-headers libffi-dev openssl-dev
RUN apk --update add python3 py3-pip openssl ca-certificates git \
    && pip3 install --upgrade setuptools pip \
    && pip3 install -r /app/requirements.txt && rm /app/requirements.txt \
    && apk del build-deps

CMD /usr/bin/python3 /app/syslog_agent.py
