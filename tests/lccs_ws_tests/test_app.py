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
from unittest.mock import patch

import pytest
from jsonschema import validate
from pkg_resources import resource_filename

from lccs_ws import app as lccs_app
from lccs_ws.schemas import (classe_response, classes_response,
                             classification_system_response,
                             classification_system_type,
                             classification_systems_response,
                             exception_response, root_response)

url = os.environ.get('LCCS_SERVER_URL', 'http://localhost:5000')
match_url = re.compile(url)


@pytest.fixture
def requests_mock(requests_mock):
    requests_mock.get(re.compile('https://geojson.org/'), real_http=True)
    yield requests_mock


@pytest.fixture(scope="session")
def mocks():
    mocks_dir = resource_filename(__name__, 'json_schemas')
    mocks_files = os.listdir(os.path.dirname(mocks_dir))
    mocks = dict()
    for filename in mocks_files:
        if os.path.isfile(mocks_dir + filename):
            with open(mocks_dir + filename, 'r') as f:
                mocks[filename] = json.load(f)

    return mocks


@pytest.fixture(scope="class")
def client():
    with lccs_app.test_client() as app:
        yield app


@pytest.fixture(scope='class')
def mock_oauth2_cache():
    with patch('bdc_auth_client.decorators.token_cache') as mock:
        yield mock


class TestLCCSWS:
    def test_data_dir(self):
        return os.path.join(os.path.dirname(__file__), 'data')

    def _assert_json(self, response, expected_code: int = 200):
        assert response.status_code == expected_code
        assert response.content_type == 'application/json'

    def _configure_authentication_test(self, mock, roles):
        headers = {'x-api-key': 'SomeToken', 'Content-Type': 'application/json'}

        res = dict(sub=dict(roles=roles))

        mock.get.return_value(res)

        return headers

    def test_index(self, client, requests_mock, mocks):
        response = client.get('/')

        self._assert_json(response, expected_code=200)

        validate(instance=response.json, schema=root_response)

    def test_classification_systems(self, client, requests_mock, mocks):
        response = client.get('/classification_systems')

        self._assert_json(response, expected_code=200)

        validate(instance=response.json, schema=classification_systems_response)

    def test_classification_system(self, client, requests_mock, mocks):
        response = client.get('/classification_systems/1')

        self._assert_json(response, expected_code=200)

        validate(instance=response.json, schema=classification_system_response)

    def test_classification_system_404(self, client):
        response = client.get('/classification_systems/1000')

        self._assert_json(response, expected_code=404)

    def test_classes(self, client, requests_mock, mocks):
        response = client.get('/classification_systems/1/classes')

        self._assert_json(response, expected_code=200)
        validate(instance=response.json, schema=classes_response)

    def test_class(self, client, requests_mock, mocks):
        response = client.get('/classification_systems/1/classes/1')

        self._assert_json(response, expected_code=200)
        validate(instance=response.json, schema=classe_response)

    def test_class_404(self, client):
        response = client.get('/classification_systems/1/classes/10000')

        self._assert_json(response, expected_code=404)

    def test_classification_system_403(self, client):
        # Test Bad Request (Missing parameters)
        failed = client.post('/classification_systems', data=dict())
        self._assert_json(failed, expected_code=403)

    def test_classification_system_400(self, client, mock_oauth2_cache):
        # Test Bad Request (Missing parameters)
        headers = self._configure_authentication_test(mock_oauth2_cache, roles=['admin'])
        failed = client.post('/classification_systems', data=dict(), headers=headers)
        self._assert_json(failed, expected_code=400)

        validate(instance=failed.json, schema=exception_response)

    def test_create_classification_system(self, client, mock_oauth2_cache):
        creation_data = dict(
            authority_name='INPE-2',
            name='BDC-2',
            description='BDC Description',
            version='1.0'
        )

        headers = self._configure_authentication_test(mock_oauth2_cache, roles=['admin'])
        response = client.post('/classification_systems', json=creation_data, headers=headers)

        self._assert_json(response, expected_code=201)
        validate(instance=response.json, schema=classification_system_type)

    def test_delete_classification_system(self, client, mock_oauth2_cache):
        headers = self._configure_authentication_test(mock_oauth2_cache, roles=['admin'])

        response = client.delete('/classification_systems/3', headers=headers)

        self._assert_json(response, expected_code=204)
