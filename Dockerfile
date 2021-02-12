#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020-2021 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

FROM python:3.7-slim-buster

RUN apt-get update \
    && apt-get install -y libpq-dev build-essential git vim \
    && rm -rf /var/lib/apt/lists/*

ADD . /lccs-ws

WORKDIR /lccs-ws

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN pip3 install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade wheel

RUN pip install -e .[all]
RUN pip install gunicorn

EXPOSE 5000

CMD ["gunicorn", "-w4", "--bind=0.0.0.0:5000", "lccs_ws:app"]