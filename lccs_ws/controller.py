#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Controllers of Land Cover Classification System Web Service."""

from bdc_core.utils.flask import APIResource
from flask_restplus import Namespace
from lccs_db.models import LucClassificationSystem

from lccs_ws.forms import ClassesSchema, ClassificationSystemSchema

api = Namespace('lccs_ws', description='status')

@api.route('/classification_system')
class ClassificationSystemResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self):
        """Retrieve all land user cover classification system."""
        retval = LucClassificationSystem.filter()

        return ClassificationSystemSchema().dump(retval, many=True)
