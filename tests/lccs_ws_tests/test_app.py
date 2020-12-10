#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020 INPE.
#
# Land Cover Classification System Web Service. is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
import os
from json import loads as json_loads

import pytest
from jsonschema import validate

from lccs_ws import create_app
from lccs_ws.schemas import (classe_response, classes_response,
                             classification_system_response)


@pytest.fixture(scope="class")
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


class TestLCCSWS:
    def test_index(self, client):
        response = client.get('/')

        data = response.get_json()

        assert response.status_code == 200
        assert "links" in data
        assert "href" in data["links"][0]
        assert "rel" in data["links"][0]
        assert "title" in data["links"][0]

    def test_classification_systems(self, client):
        response = client.get('/classification_systems')

        data = json_loads(response.data.decode('utf-8'))

        validate(instance=data, schema=classification_system_response)

        assert response.status_code == 200

    def test_classification_system(self, client):
        response = client.get('/classification_system/PRODES')

        data = json_loads(response.data.decode('utf-8'))

        validate(instance=data, schema=classification_system_response)

        assert response.status_code == 200

    def test_classes(self, client):
        response = client.get('/classification_system/PRODES/classes')

        data = json_loads(response.data.decode('utf-8'))

        validate(instance=data, schema=classes_response)

        assert response.status_code == 200

    def test_class(self, client):
        response = client.get('/classification_system/PRODES/classes/Desflorestamento')

        data = json_loads(response.data.decode('utf-8'))

        validate(instance=data, schema=classe_response)

        assert response.status_code == 200
