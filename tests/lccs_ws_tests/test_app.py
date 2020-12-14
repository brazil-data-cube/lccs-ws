#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020 INPE.
#
# Land Cover Classification System Web Service. is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import json
import os
import re
from json import loads as json_loads

import pytest
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from pkg_resources import resource_filename

from lccs_ws import create_app
from lccs_ws.schemas import (classe_response, classes_response,
                             classification_system_response, root_response)

url = os.environ.get('LCCS_SERVER_URL', 'http://localhost:5000')
match_url = re.compile(url)


@pytest.fixture
def requests_mock(requests_mock):
    requests_mock.get(re.compile('https://geojson.org/'), real_http=True)
    yield requests_mock


@pytest.fixture(scope="session")
def mocks():
    mocks_dir = resource_filename(__name__, '../json_schemas/')
    mocks_files = os.listdir(mocks_dir)
    mocks = dict()
    for filename in mocks_files:
        if os.path.isfile(mocks_dir + filename):
            with open(mocks_dir + filename, 'r') as f:
                mocks[filename] = json.load(f)

    return mocks


@pytest.fixture(scope="class")
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


class TestLCCSWS:
    def test_data_dir(self):
        return os.path.join(os.path.dirname(__file__), 'data')

    def test_index(self, client, requests_mock, mocks):
        response = client.get('/')

        assert response.status_code == 200
        assert response.content_type == 'application/json'
        validate(instance=response.json, schema=root_response)
