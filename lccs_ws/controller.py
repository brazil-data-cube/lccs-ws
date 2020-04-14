#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Controllers of Land Cover Classification System Web Service."""

from bdc_core.utils.flask import APIResource
from flask import abort, jsonify, request, render_template, make_response, Response
from flask_restplus import Namespace
from lccs_db.models import (LucClass, LucClassificationSystem, StyleFormats,
                            Styles)
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import NotFound
from json import dumps

from lccs_ws.forms import ClassesSchema, ClassificationSystemSchema

from .config import Config
from .data import get_mappings

api = Namespace('lccs', description='status')


@api.route('/')
class Index(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self):
        """Retrieve all routes of api."""
        links = [{"href": "{}".format(request.base_url), "rel": "self"},
                 {"href": "{}classification_systems".format(request.base_url), "rel": "classification_systems"}, ]

        return jsonify(links)

@api.route('/classification_systems')
class ClassificationSystemsResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self):
        """Retrieve all land user cover classification system."""
        try:

            retval = LucClassificationSystem.filter()

            systems_result = ClassificationSystemSchema(only=['name']).dump(retval, many=True)

            links = [{"href": "{}/lccs/classification_systems".format(Config.LCCS_URL), "rel": "self"},
                     {"href": "{}/lccs/".format(Config.LCCS_URL), "rel": "root"}]

            for systems in systems_result:
                links.append({"href": "{}/{}".format(request.base_url, systems["name"]), "rel": "child",
                              "title": systems["name"]})

            classification_systems = dict()

            classification_systems["links"] = links

            return jsonify(classification_systems)
        except:
            abort(500, "Classification Systems Error")


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

            return ClassificationSystemSchema(exclude=['id']).dump(class_system), 201
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
            abort(500, 'Classification system "{}" not found'.format(system_id))

        systems = ClassificationSystemSchema().dump(retval, many=False)

        links = [{"href": "{}".format(request.base_url), "rel": "self"},
                 {"href": "{}/lccs/classification_systems/{}/classes".format(Config.LCCS_URL, system_id), "rel": "classes"},
                 {"href": "{}/lccs/classification_systems".format(Config.LCCS_URL), "rel": "parent"},
                 {"href": "{}/lccs/".format(Config.LCCS_URL), "rel": "root"}]

        systems['links'] = links

        all_style = list()

        all_style.append({"href": "{}/lccs/classification_systems/{}/styles/".format(Config.LCCS_URL, system_id),
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
            abort(500, 'Classification system "{}" not found'.format(system_id))

        retval = ClassesSchema(only=['name']).dump(LucClass.filter(class_system_id=class_sys.id), many=True)

        links = [{"href": "{}/lccs/classification_systems/{}/classes".format(Config.LCCS_URL, system_id), "rel": "self"},
                 {"href": "{}/lccs/classification_systems/{}".format(Config.LCCS_URL, system_id), "rel": "parent"},
                 {"href": "{}/lccs/classification_systems".format(Config.LCCS_URL), "rel": "classification_systems"},
                 {"href": "{}/lccs/".format(Config.LCCS_URL), "rel": "root"}]

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
            parent = request_json.get('parent_name', None)

            if parent is not None:
                try:
                    parent_class = LucClass.get(class_system_id=luc_class_system.id, name=parent)

                    classes = LucClass(name=name,
                                         description=description,
                                         code=code,
                                         class_system_id=luc_class_system.id,
                                         class_parent_id=parent_class.id)
                    classes.save()

                    schema = ClassesSchema(exclude=['id', 'class_system_id', 'class_parent_id']).dump(classes)

                    schema['parent_name'] = parent_class.name

                    return schema, 201

                except NoResultFound:
                    abort(404 , "Class Parent Not Found")

            else:
                classes = LucClass(name=name, description=description,
                                   code=code, class_system_id=luc_class_system.id)
                classes.save()

                schema = ClassesSchema(exclude=['id', 'class_system_id', 'class_parent_id']).dump(classes)

                schema['parent_name'] = None

                return schema, 201


        else:
           abort(400, "POST Request must be an current_application/json")

@api.route('/classification_systems/<system_id>/classes/<classe_id>')
class ClassResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self, system_id, classe_id):
        """Retrieve land user cover class."""
        classification_system = LucClassificationSystem.get(name=system_id)

        try:
            result_classe = LucClass.get(class_system_id=classification_system.id, name=classe_id)
        except NoResultFound:
            abort(500, 'Invalid Classification system Id "{}" for classe id {}'.format(system_id, classe_id))

        classe_info = ClassesSchema(exclude=['class_system_id', 'class_parent_id']).dump(result_classe)

        parent = LucClass.get(id=result_classe.id)

        if (parent):
            classe_info['parent'] = ClassesSchema(exclude=['class_system_id', 'class_parent_id']).dump(parent)
        else:
            classe_info['parent'] = None


        links = [{"href": "{}/lccs/classification_systems/{}/classes/{}".format(Config.LCCS_URL, system_id, classe_id),
                  "rel": "self"},
                 {"href": "{}/lccs/classification_systems/{}/classes".format(Config.LCCS_URL, system_id), "rel": "parent"},
                 {"href": "{}/lccs/classification_systems/{}".format(Config.LCCS_URL, system_id), "rel": system_id},
                 {"href": "{}/lccs/classification_systems".format(Config.LCCS_URL), "rel": "classification_systems"},
                 {"href": "{}/lccs/".format(Config.LCCS_URL), "rel": "root"}]

        classe_info['links'] = links

        return classe_info

@api.route('/mappings/<system_id_source>/')
class AllMappingResource(APIResource):
    """URL Handler for Land User Cover Classification System through REST API."""

    def get(self, system_id_source):
        """Retrieve all mappings."""
        try:
            system_source = LucClassificationSystem.get(name=system_id_source)
        except NoResultFound:
            return abort(500, "Classification system Source {} not found".format(system_id_source))

        result = list()

        classes_source = LucClass.filter(class_system_id=system_source.id)

        mappings = get_mappings(classes_source, None)

        for mapping in mappings:
            target_class_name = LucClass.get(id=mapping.target_class_id)
            system = LucClassificationSystem.get(id=target_class_name.class_system_id)

            result.append({"href": "{}/lccs/classification_systems/{}".format(Config.LCCS_URL, system.name),
                      "rel": system.name})
        return result

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
                               {"href": "{}/lccs/classification_systems/{}/"
                                        "classes/{}".format(Config.LCCS_URL, system_id_source,
                                                            source_class_name),
                                "rel": "source_class",
                                "title": source_class_name},
                               {"href": "{}/lccs/classification_systems/{}/"
                                "classes/{}".format(Config.LCCS_URL,
                                                    system_id_target,
                                                    target_class_name),
                                "rel": "target_class",
                                "title": target_class_name},
                               {"href": "{}/lccs/".format(Config.LCCS_URL), "rel": "root"}]
                           })

        return result

@api.route('/classification_systems/<system_id>/styles')
class StyleFileResource(APIResource):
    """URL Handler for Classification Systems through REST API."""

    def get(self, system_id):
        """Retrives json file of application style by name."""
        try:
            system = LucClassificationSystem.get(name=system_id)
        except NoResultFound:
            return abort(500, "Classification system Source {} not found".format(system_id))

        styles = Styles.filter(class_system_id=system.id)

        links = list()
        result = dict()

        for style in styles:

            style_name =   StyleFormats.get(id=style.style_format_id).name
            links.append({"href": "{}/lccs/classification_systems/{}/styles/{}".format(Config.LCCS_URL, system_id,
                                                                                style_name),
                  "rel": "self", "title":style_name})

        result['links'] = links

        return result

@api.route('/classification_systems/<system_id>/styles/<style_format>')
class FileResource(APIResource):
    """URL Handler for Classification Systems Style through REST API."""

    def get(self, system_id, style_format):
        """Retrives json file of application style by name."""
        system = LucClassificationSystem.get(name=system_id)
        style_format = StyleFormats.get(name=style_format)
        styles = Styles.get(class_system_id=system.id, style_format_id=style_format.id)


        if styles.style:
            return Response(dumps(styles.style),
                        mimetype="text/plain",
                        headers={"Content-Disposition": "attachment;filename={}_style_{}.json".format(system.name,
                                                                                                      style_format.name)})

        else:
            return abort(500, "File Format {} not found".format(style_format.name))
