#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Controllers of Land Cover Classification System Web Service."""

from bdc_core.decorators.validators import require_model
from bdc_core.utils.flask import APIResource
from flask_restplus import Namespace
from lccs_db.models import LucClass, LucClassificationSystem, ParentClasses
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest, NotFound

from lccs_ws.forms import LucClassificationSystemsSchema, LucClassSchema

api = Namespace('lccs_ws', description='status')

@api.route('/classification_systems')
class ClassificationSystemsResource(APIResource):
    """URL Handler for Classification Systems through REST API."""

    def get(self):
        """Retrieve all classification systems."""
        retval = LucClassificationSystem.filter()

        result = LucClassificationSystemsSchema(only=['name']).dump(retval, many=True)

        return {"classification_systems": [item["name"] for item in result]}

@api.route('/<name>')
class ClassificationSystemResource(APIResource):
    """URL Handler for Classification Systems through REST API."""

    def get(self, name):
        """Retrives metadata of classification system by nam."""
        try:
            retval = LucClassificationSystem.get(name=name)

        except NoResultFound:
            raise NotFound('Classification system "{}" not found'.format(
                name))

        result_class = LucClassSchema().dump(LucClass.filter(class_system_id = retval.id), many=True)

        cls_systm = LucClassificationSystemsSchema().dump(retval, many=False)

        if result_class is None:
            cls_systm.update({"classes": []})

        else:
            cls_systm.update({"classes": result_class})

        return cls_systm



@api.route('/<name>/<class_name>')
class CSClass(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self, name, class_name):
        """Retrieve all land user cover class."""
        classification_system = LucClassificationSystem.get(name=name)

        result_classes = LucClass.filter(class_system_id=classification_system.id, name=class_name)

        parents = ParentClasses.filter(class_id=result_classes[0].id)

        parents_id = list()

        for cls_id in parents:
            parents_id.append(LucClassSchema().dump(LucClass.filter(id=cls_id.class_parent_id), many=True)[0])

        classe_metainfo = LucClassSchema().dump(result_classes, many=True)[0]

        if parents_id :
            classe_metainfo.update({"parent": parents_id})

        return classe_metainfo

        # return LucClassSchema().dump(result_classes, many=True)[0]
