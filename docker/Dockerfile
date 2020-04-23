# FROM brazildatacube/base:0.1

FROM python:3.7-slim-buster

RUN apt-get update && apt-get install -y libpq-dev build-essential git

ADD . /lccs-ws

WORKDIR /lccs-ws

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN pip3 install pip --upgrade && \
    pip install wheel && \
    pip install setuptools && \
    pip install -e .[all]

EXPOSE 5000

CMD [ "lccs_ws", "run", "--host", "0.0.0.0" ]