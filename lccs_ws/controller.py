#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Controllers of Land Cover Classification System Web Service."""
from json import dumps

from bdc_core.utils.flask import APIResource
from flask import Response, jsonify, request
from flask_restplus import Namespace
from lccs_db.models import (ApplicationsStyle, LucClass,
                            LucClassificationSystem, ParentClasses)
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest, NotFound

from lccs_ws.forms import LucClassificationSystemsSchema, LucClassSchema

from .config import Config
from .data import get_application_style, get_mappings

api = Namespace('lccs_ws', description='status')

BASE_URL = Config.SERVER_HOST + ":" + Config.PORT + "/lccs_ws"


@api.route('/')
class Index(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self):
        """Retrieve all routes of api."""
        links = [{"href": "{}".format(request.base_url), "rel": "self"},
                 {"href": "{}docs".format(request.base_url), "rel": "service"},
                 {"href": "{}classification_systems".format(request.base_url), "rel": "classification_systems"}, ]

        return jsonify(links)


@api.route('/classification_systems')
class ClassificationSystemsResource(APIResource):
    """URL Handler for Classification Systems through REST API."""

    def get(self):
        """Retrieve all classification systems."""
        retval = LucClassificationSystem.filter()

        result = LucClassificationSystemsSchema(only=['name']).dump(retval, many=True)

        links = [{"href": "{}/classification_systems".format(BASE_URL), "rel": "self"},
                 {"href": "{}/".format(BASE_URL), "rel": "root"}]

        for cls_system in result:
            links.append({"href": "{}/{}".format(request.base_url, cls_system["name"]), "rel": "child",
                          "title": cls_system["name"]})

        classification_systems = dict()

        classification_systems["links"] = links

        return jsonify(classification_systems)


@api.route('/classification_systems/getfile/<file_id>')
class StyleFileResource(APIResource):
    """URL Handler for Classification Systems through REST API."""

    def get(self, file_id):
        """Retrives json file of application style by name."""
        apl_style = ApplicationsStyle.get(name=file_id)

        return Response(dumps(apl_style.file),
                        mimetype="text/plain",
                        headers={"Content-Disposition": "attachment;filename=application_style.json"})


@api.route('/classification_systems/<system_id>')
class ClassificationSystemResource(APIResource):
    """URL Handler for Classification Systems through REST API."""

    def get(self, system_id):
        """Retrives metadata of classification system by name."""
        try:
            retval = LucClassificationSystem.get(name=system_id)
        except NoResultFound:
            raise NotFound('Classification system "{}" not found'.format(
                system_id))

        cls_systm = LucClassificationSystemsSchema().dump(retval, many=False)

        links = [{"href": "{}".format(request.base_url), "rel": "self"},
                 {"href": "{}/classification_systems/{}/classes".format(BASE_URL, system_id), "rel": "classes"},
                 {"href": "{}/classification_systems".format(BASE_URL), "rel": "parent"},
                 {"href": "{}/".format(BASE_URL), "rel": "root"}]

        cls_systm['links'] = links

        style = get_application_style(retval.id)
        all_style = list()

        for stl in style:
            all_style.append({"href": "{}/classification_systems/getfile/{}".format(BASE_URL, stl.name),
                              "rel": "child", "title": stl.name})

        cls_systm['style'] = all_style
        return cls_systm


@api.route('/classification_systems/<system_id>/classes')
class ClassesResource(APIResource):
    """URL Handler for Classification Systems through REST API."""

    def get(self, system_id):
        """Retrives metadata of classification system by nam."""
        try:
            class_sys = LucClassificationSystem.get(name=system_id)

        except NoResultFound:
            raise NotFound('Classification system "{}" not found'.format(system_id))

        retclasses = LucClassSchema(only=['name']).dump(LucClass.filter(class_system_id=class_sys.id), many=True)

        links = [{"href": "{}/classification_systems/{}/classes".format(BASE_URL, system_id), "rel": "self"},
                 {"href": "{}/classification_systems/{}".format(BASE_URL, system_id), "rel": "parent"},
                 {"href": "{}/classification_systems".format(BASE_URL), "rel": "classification_systems"},
                 {"href": "{}/".format(BASE_URL), "rel": "root"}]

        for class_id in retclasses:
            links.append({"href": "{}/{}".format(request.base_url, class_id["name"]), "rel": "child",
                          "title": class_id["name"]})

        classes = dict()

        classes["links"] = links

        return jsonify(classes)

        return classes


@api.route('/classification_systems/<system_id>/classes/<classe_id>')
class ClasseResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self, system_id, classe_id):
        """Retrieve all land user cover class."""
        classification_system = LucClassificationSystem.get(name=system_id)

        try:
            result_classe = LucClass.get(class_system_id=classification_system.id, name=classe_id)
        except NoResultFound:
            raise NotFound('Invalid Classification system Id "{}" for classe id{}'.format(system_id, classe_id))

        classe_info = LucClassSchema().dump(result_classe)

        parents = ParentClasses.filter(class_id=result_classe.id)

        parent = list()

        for parent_id in parents:
            data = LucClass.get(id=parent_id.class_parent_id)
            parent.append({"href": "{}/classification_systems/{}/classes/{}".format(BASE_URL, system_id, data.name),
                           "rel": "child", "title": data.name})

        links = [{"href": "{}/classification_systems/{}/classes/{}".format(BASE_URL, system_id, classe_id),
                  "rel": "self"},
                 {"href": "{}/classification_systems/{}/classes".format(BASE_URL, system_id), "rel": "parent"},
                 {"href": "{}/classification_systems/{}".format(BASE_URL, system_id), "rel": system_id},
                 {"href": "{}/classification_systems".format(BASE_URL), "rel": "classification_systems"},
                 {"href": "{}/".format(BASE_URL), "rel": "root"}]

        classe_info['link'] = links
        classe_info['parent'] = parent

        return classe_info


@api.route('/mappings/<system_id_source>/<system_id_target>')
class MappingResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self, system_id_source, system_id_target):
        """Retrieve all land user cover classes mappings."""
        try:
            system_source = LucClassificationSystem.get(name=system_id_source)
        except NoResultFound:
            raise NotFound('Classification system Source"{}" not found'.format(
                system_id_source))
        try:
            system_target = LucClassificationSystem.get(name=system_id_target)
        except NoResultFound:
            raise NotFound('Classification system Source"{}" not found'.format(
                system_id_target))

        result = list()

        classes_source = LucClass.filter(class_system_id=system_source.id)
        classes_target = LucClass.filter(class_system_id=system_target.id)

        mappings = get_mappings(classes_source, classes_target)

        for mapping in mappings:

            source_class_name = LucClass.get(id=mapping.source_class_id).name
            target_class_name = LucClass.get(id=mapping.target_class_id).name

            result.append({'description': mapping.description,
                           'degree_of_similarity': mapping.degree_of_similarity,
                           'links': [
                               {"href": "{}/classification_systems/{}/"
                                        "classes/{}".format(BASE_URL, system_id_source,
                                                            source_class_name),
                                "rel": "source_class",
                                "title": source_class_name},
                               {"href": "{}/classification_systems/{}/"
                                "classes/{}".format(BASE_URL,
                                                    system_id_target,
                                                    target_class_name),
                                "rel": "target_class",
                                "title": target_class_name},
                               {"href": "{}/".format(BASE_URL), "rel": "root"}]
                           })

        return result
