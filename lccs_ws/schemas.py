#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020-2021 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""This module WLTS Operations vocabularies."""
from json import loads as json_loads
from pathlib import Path

from lccs_ws.config import BASE_DIR

schemas_folder = Path(BASE_DIR) / 'jsonschemas/'


def load_schema(file_name):
    """Open file and parses as JSON file.

    :param file_name: File name of JSON Schema.
    """
    schema_file = schemas_folder / file_name

    with schema_file.open() as f:
        return json_loads(f.read())


root_response = load_schema('root.json')
classification_systems_response = load_schema('classification_systems.json')
classification_system_response = load_schema('classification_system.json')
classes_response = load_schema('classes.json')
class_response = load_schema('class.json')
classification_system_type = load_schema('classification_system_type.json')
exception_response = load_schema('exception.json')
