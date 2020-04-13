#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Controllers of Land Cover Classification System Web Service."""

from bdc_core.utils.flask import APIResource
from flask import Response, abort, jsonify, request
from flask_restplus import Namespace
from lccs_db.models import LucClass, LucClassificationSystem, db
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest, NotFound

from lccs_ws.forms import ClassesSchema, ClassificationSystemSchema

from .config import Config
from .data import get_mappings

api = Namespace('lccs_ws', description='status')

BASE_URL = Config.BASE_URL + "/lccs_ws"

@api.route('/')
class Index(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self):
        """Retrieve all routes of api."""
        links = [{"href": "{}".format(request.base_url), "rel": "self"},
                 {"href": "{}classification_systems".format(request.base_url), "rel": "classification_systems"}, ]

        return jsonify(links)

@api.route('/classification_systems')
class ClassificationSystemResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self):
        """Retrieve all land user cover classification system."""
        retval = LucClassificationSystem.filter()

        systems_result = ClassificationSystemSchema(only=['name']).dump(retval, many=True)

        links = [{"href": "{}/classification_systems".format(BASE_URL), "rel": "self"},
                 {"href": "{}/".format(BASE_URL), "rel": "root"}]

        for systems in systems_result:
            links.append({"href": "{}/{}".format(request.base_url, systems["name"]), "rel": "child",
                          "title": systems["name"]})

        classification_systems = dict()

        classification_systems["links"] = links

        return jsonify(classification_systems)

    def post(self):
        """Create new Classification system."""
        if request.is_json:

            request_json = request.get_json()

            name = request_json.get('name')
            description = request_json.get('description')
            authority_name = request_json.get('authority_name')
            version = request_json.get('version')

            class_system = LucClassificationSystem(name=name,
                                                   description=description,
                                                   authority_name=authority_name,
                                                   version=version)

            class_system.save()

            return ClassificationSystemSchema().dump(class_system), 201
        else:
            abort(400, "POST Request must be an current_application/json")

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

        systems = ClassificationSystemSchema().dump(retval, many=False)

        links = [{"href": "{}".format(request.base_url), "rel": "self"},
                 {"href": "{}/classification_systems/{}/classes".format(BASE_URL, system_id), "rel": "classes"},
                 {"href": "{}/classification_systems".format(BASE_URL), "rel": "parent"},
                 {"href": "{}/".format(BASE_URL), "rel": "root"}]

        systems['links'] = links

        all_style = list()

        all_style.append({"href": "{}/classification_systems/{}/styles/".format(BASE_URL, system_id),
                              "rel": "child", "title": "Styles"})

        systems['styles'] = all_style

        return systems

@api.route('/classification_systems/<system_id>/classes')
class ClassesResource(APIResource):
    """URL Handler for Classification Systems through REST API."""

    def get(self, system_id):
        """Retrives metadata of classification system by nam."""
        try:
            class_sys = LucClassificationSystem.get(name=system_id)

        except NoResultFound:
            raise NotFound('Classification system "{}" not found'.format(system_id))

        retval = ClassesSchema(only=['name']).dump(LucClass.filter(class_system_id=class_sys.id), many=True)

        links = [{"href": "{}/classification_systems/{}/classes".format(BASE_URL, system_id), "rel": "self"},
                 {"href": "{}/classification_systems/{}".format(BASE_URL, system_id), "rel": "parent"},
                 {"href": "{}/classification_systems".format(BASE_URL), "rel": "classification_systems"},
                 {"href": "{}/".format(BASE_URL), "rel": "root"}]

        for class_result in retval:
            links.append({"href": "{}/{}".format(request.base_url, class_result["name"]), "rel": "child",
                          "title": class_result["name"]})

        classes = dict()

        classes["links"] = links

        return jsonify(classes)

    def post(self, system_id):
        """Create new Class."""
        if request.is_json:
            try:
                luc_class_system = LucClassificationSystem.get(name=system_id)

            except NoResultFound:
                raise NotFound('Classification system "{}" not found'.format(system_id))

            request_json = request.get_json()

            name = request_json.get('name')
            code = request_json.get('code')
            description = request_json.get('description')
            parent = request_json.get('parent', None)

            if parent is not None:
                try:
                    parent_class = LucClass.get(class_system_id=luc_class_system.id, name=parent)

                    classes = LucClass(name=name,
                                         description=description,
                                         code=code,
                                         class_system_id=luc_class_system.id,
                                         class_parent_id=parent_class.id)
                    classes.save()

                    return ClassesSchema().dump(classes), 201

                except NoResultFound:
                    abort(404 , "Class Parent Not Found")

            else:
                classes = LucClass(name=name, description=description,
                                   code=code, class_system_id=luc_class_system.id)
                classes.save()

                return ClassesSchema().dump(classes), 201


        else:
           abort(400, "POST Request must be an current_application/json")

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

        classe_info = ClassesSchema().dump(result_classe)

        parent = LucClass.get(id=result_classe.id)

        if (parent):
            classe_info['parent'] = {"href": "{}/classification_systems/{}/classes/{}".format(BASE_URL, system_id,
                                                                                              parent.name),
                                     "rel": "child", "title": "Parent Class"}

        links = [{"href": "{}/classification_systems/{}/classes/{}".format(BASE_URL, system_id, classe_id),
                  "rel": "self"},
                 {"href": "{}/classification_systems/{}/classes".format(BASE_URL, system_id), "rel": "parent"},
                 {"href": "{}/classification_systems/{}".format(BASE_URL, system_id), "rel": system_id},
                 {"href": "{}/classification_systems".format(BASE_URL), "rel": "classification_systems"},
                 {"href": "{}/".format(BASE_URL), "rel": "root"}]

        classe_info['links'] = links

        return classe_info

@api.route('/mappings/<system_id_source>/<system_id_target>')
class MappingResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self, system_id_source, system_id_target):
        """Retrieve all land user cover classes mappings."""
        try:
            system_source = LucClassificationSystem.get(name=system_id_source)
        except NoResultFound:
            return abort(500, "Classification system Source {} not found".format(system_id_source))
        try:
            system_target = LucClassificationSystem.get(name=system_id_target)
        except NoResultFound:
            return abort(500, "Classification system Target {} not found".format(system_id_target))

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
