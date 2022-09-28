#
# This file is part of LCCS-WS.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
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
