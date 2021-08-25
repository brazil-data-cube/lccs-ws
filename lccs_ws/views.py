#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020-2021 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Views of Land Cover Classification System Web Service."""
from io import BytesIO
from werkzeug.urls import url_encode

from bdc_auth_client.decorators import oauth2
from flask import abort, current_app, jsonify, request, send_file
from lccs_db.utils import get_extension

from lccs_ws.forms import (ClassesMappingMetadataSchema, ClassesMappingSchema,
                           ClassesSchema, ClassificationSystemMetadataSchema,
                           ClassificationSystemSchema, ClassMetadataSchema, ClassMetadataForm,
                           StyleFormatsMetadataSchema, StyleFormatsSchema)

from . import data
from .config import Config
from .utils import language

BASE_URL = Config.LCCS_URL


@current_app.before_request
def before_request():
    """Handle for before request processing."""
    request.assets_kwargs = None

    if Config.BDC_LCCS_ASSETS_ARGS:
        assets_kwargs = {arg: request.args.get(arg) for arg in Config.BDC_LCCS_ASSETS_ARGS.split(",")}
        if "access_token" in request.args:
            assets_kwargs["access_token"] = request.args.get("access_token")
        assets_kwargs = "?" + url_encode(assets_kwargs) if url_encode(assets_kwargs) else ""
        request.assets_kwargs = assets_kwargs


@current_app.route("/", methods=["GET"])
@oauth2(required=False)
def root(**kwargs):
    """URL Handler for Land User Cover Classification System through REST API."""
    links = list()
    response = dict()

    links += [
        {"href": f"{BASE_URL}/", "rel": "self", "type": "application/json", "title": "Link to this document"},
        {
            "href": f"{BASE_URL}/classification_systems{request.assets_kwargs}",
            "rel": "classification_systems", "type": "application/json",
            "title": "Information about Classification Systems",
        },
        {
            "href": f"{BASE_URL}/style_formats{request.assets_kwargs}",
            "rel": "style_formats", "type": "application/json",
            "title": "Information about Style Formats"
        }
    ]

    response["links"] = links
    response["application_name"] = "Land Cover Classification System Service"
    response["version"] = Config.BDC_LCCS_API_VERSION

    return response, 200


@current_app.route("/classification_systems", methods=["GET"])
@oauth2(required=True)
def get_classification_systems(**kwargs):
    """Retrieve the list of available classification systems in the service."""
    classification_systems_list = data.get_classification_systems()

    for class_system in classification_systems_list:
        links = [
            {
                "href": f"{BASE_URL}/classification_systems/{class_system['id']}{request.assets_kwargs}",
                "rel": "classification_system",
                "type": "application/json",
                "title": "Link to Classification System",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{class_system['id']}/classes{request.assets_kwargs}",
                "rel": "classes",
                "type": "application/json",
                "title": "Link to Classification System Classes",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{class_system['id']}/style_formats{request.assets_kwargs}",
                "rel": "style_formats",
                "type": "application/json",
                "title": "Link to Available Style Formats",
            },
            {
                "href": f"{BASE_URL}/mappings/{class_system['id']}{request.assets_kwargs}",
                "rel": "mappings",
                "type": "application/json",
                "title": "Link to Classification Mappings",
            },
            {
                "href": f"{BASE_URL}/classification_systems{request.assets_kwargs}",
                "rel": "self",
                "type": "application/json",
                "title": "Link to this document",
            },
        ]

        class_system["links"] = links

    return jsonify(classification_systems_list), 200


@current_app.route("/classification_systems/<system_id_or_identifier>", methods=["GET"])
@language()
@oauth2(required=True)
def classification_systems(system_id_or_identifier, **kwargs):
    """Retrieve information about the classification system.

    :param system_id_or_identifier: The id or identifier of a classification system
    """
    classification_system = data.get_classification_system(system_id_or_identifier)

    if not classification_system:
        abort(404, "Classification System not found.")

    links = [
        {
            "href": f"{BASE_URL}/classification_systems",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to this document",
        },
        {
            "href": f"{BASE_URL}/classification_systems/{classification_system['id']}{request.assets_kwargs}",
            "rel": "self",
            "type": "application/json",
            "title": "The classification_system",
        },
        {
            "href": f"{BASE_URL}/classification_systems/{classification_system['id']}/classes{request.assets_kwargs}",
            "rel": "classes",
            "type": "application/json",
            "title": "The classes related to this item",
        },
        {
            "href": f"{BASE_URL}/classification_systems/{classification_system['id']}/style_formats{request.assets_kwargs}",
            "rel": "styles_formats",
            "type": "application/json",
            "title": "The styles formats related to this item",
        },
        {
            "href": f"{BASE_URL}/mappings/{classification_system['id']}{request.assets_kwargs}",
            "rel": "mappings",
            "type": "application/json",
            "title": "The classification system mappings",
        },
        {"href": f"{BASE_URL}/", "rel": "root", "type": "application/json", "title": "API landing page."},
    ]

    classification_system["links"] = links

    return classification_system, 200


@current_app.route("/classification_systems/<system_id_or_identifier>/classes", methods=["GET"])
@oauth2(required=True)
def classification_systems_classes(system_id_or_identifier, **kwargs):
    """Retrieve the classes of a classification system.
    
    :param system_id_or_identifier: The id or identifier of a classification system
    """
    system_id, classes_list = data.get_classification_system_classes(system_id_or_identifier)

    links = [
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}/classes{request.assets_kwargs}",
            "rel": "self",
            "type": "application/json",
            "title": f"Classes of the classification system {system_id}{request.assets_kwargs}",
        },
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}{request.assets_kwargs}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to classification system",
        },
        {
            "href": f"{BASE_URL}/classification_systems{request.assets_kwargs}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to classification systems",
        },
        {
            "href": f"{BASE_URL}/",
            "rel": "root",
            "type": "application/json",
            "title": "API landing page",
        },
    ]

    if not len(classes_list) > 0:
        return jsonify(links)

    for system_classes in classes_list:
        system_classes["links"] = links
        system_classes["links"].append(
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}/classes/{system_classes['id']}{request.assets_kwargs}",
                "rel": "child",
                "type": "application/json",
                "title": "Classification System Class",
            }
        )

    return jsonify(classes_list), 200


@current_app.route("/classification_systems/<system_id_or_identifier>/classes/<class_id_or_name>", methods=["GET"])
@oauth2(required=True)
@language()
def classification_systems_class(system_id_or_identifier, class_id_or_name, **kwargs):
    """Retrieve class information from a classification system.

    :param system_id_or_identifier: The id or identifier of a classification system
    :param class_id_or_name: identifier of a class
    """
    system_id, class_info = data.get_classification_system_class(system_id_or_identifier, class_id_or_name)

    if not len(class_info) > 0:
        abort(404, f"Class not found.")

    links = [
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}/classes/{class_info['id']}{request.assets_kwargs}",
            "rel": "self",
            "type": "application/json",
            "title": "Link to this document",
        },
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}/classes{request.assets_kwargs}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to this document",
        },
        {
            "href": f"{BASE_URL}/classification_systems{request.assets_kwargs}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to classification systems",
        },
        {
            "href": f"{BASE_URL}/",
            "rel": "root",
            "type": "application/json",
            "title": "API landing page",
        },

    ]

    class_info["links"] = links

    return class_info, 200


@current_app.route("/mappings/<system_id_or_identifier>", methods=["GET"])
@oauth2(required=True)
@language()
def get_mappings(system_id_or_identifier, **kwargs):
    """Retrieve available mappings for a classification system.

    :param system_id_or_identifier: The id or identifier of a classification system
    """
    system_source, system_target = data.get_mappings(system_id_or_identifier)

    if not len(system_target) > 0:
        abort(404, f"Mappings not found.")

    links = list()

    links += [
        {
            "href": f"{BASE_URL}/classification_systems{request.assets_kwargs}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to classification systems",
        },
        {
            "href": f"{BASE_URL}/",
            "rel": "root",
            "type": "application/json",
            "title": "API landing page",
        },
    ]

    for sys in system_target:
        links.append(
            {
                "href": f"{BASE_URL}/mappings/{system_source.id}/{sys.id}{request.assets_kwargs}",
                "rel": "child",
                "type": "application/json",
                "title": "Mapping",
            }
        )

    return jsonify(links)


@current_app.route("/mappings/<system_id_or_identifier_source>/<system_id_or_identifier_target>", methods=["GET"])
@oauth2(required=True)
@language()
def get_mapping(system_id_or_identifier_source, system_id_or_identifier_target, **kwargs):
    """Retrieve mapping.

    :param system_id_or_identifier_source: The id or identifier of source classification system
    :param system_id_or_identifier_target: The id or identifier of target classification system
    """
    system_id_source, system_id_target, mappings = data.get_mapping(system_id_or_identifier_source,
                                                                    system_id_or_identifier_target)

    for mp in mappings:
        links = [
            {
                "href": f"{BASE_URL}/classification_systems/{system_id_source}/classes/{mp['source_class_id']}{request.assets_kwargs}",
                "rel": "item",
                "type": "application/json",
                "title": "Link to source class",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{system_id_target}/classes/{mp['target_class_id']}{request.assets_kwargs}",
                "rel": "item",
                "type": "application/json",
                "title": "Link to target class",
            },
        ]
        if mp["degree_of_similarity"] is not None:
            mp["degree_of_similarity"] = float(mp["degree_of_similarity"])
        mp["links"] = links

    return jsonify(mappings)


@current_app.route("/style_formats", methods=["GET"])
@oauth2(required=True)
def get_styles_formats(**kwargs):
    """Retrieve available style formats in service."""
    styles_formats = data.get_style_formats()

    for st_f in styles_formats:
        links = [
            {
                "href": f"{BASE_URL}/classification_systems{request.assets_kwargs}",
                "rel": "parent",
                "type": "application/json",
                "title": "Link to classification systems",
            },
            {
                "href": f"{BASE_URL}/",
                "rel": "root",
                "type": "application/json",
                "title": "API landing page",
            },
            {
                "href": f"{BASE_URL}/style_formats/{st_f['id']}{request.assets_kwargs}",
                "rel": "items",
                "type": "application/json",
                "title": f"Link to style format {st_f['id']}"
            }
        ]

        st_f["links"] = links

    return jsonify(styles_formats)


@current_app.route("/style_formats/<style_format_id_or_name>", methods=["GET"])
@oauth2(required=True)
def get_style_format(style_format_id_or_name, **kwargs):
    """Retrieve information of a style formats.

    :param style_format_id_or_name: The id or name of a style format
    """
    styles_format = data.get_style_format(style_format_id_or_name)

    if not len(styles_format) > 0:
        abort(404, f"Style Format not found.")

    links = [
        {
            "href": f"{BASE_URL}/classification_systems{request.assets_kwargs}",
            "rel": "classification_systems",
            "type": "application/json",
            "title": "Link to classification systems",
        },
        {
            "href": f"{BASE_URL}/",
            "rel": "root",
            "type": "application/json",
            "title": "API landing page",
        },
        {
            "href": f"{BASE_URL}/style_formats/{styles_format['id']}{request.assets_kwargs}",
            "rel": "style_format",
            "type": "application/json",
            "title": "Link to classification systems",
        },
        {
            "href": f"{BASE_URL}/style_formats/{request.assets_kwargs}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to classification systems",
        },
    ]

    styles_format["links"] = links

    return styles_format

#TODO: review
@current_app.route("/classification_systems/<system_id_or_identifier>/style_formats", methods=["GET"])
@oauth2(required=True)
def get_style_formats_classification_system(system_id_or_identifier, **kwargs):
    """Retrieve available style formats for a classification system.

    :param system_id_or_identifier: The id or identifier of a source classification system
    """
    system_id, style_formats_id = data.get_system_style_format(system_id_or_identifier)

    if not len(style_formats_id) > 0:
        abort(404, f"Style Formats not found.")

    links = list()

    links += [
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}/style_formats{request.assets_kwargs}",
            "rel": "self",
            "type": "application/json",
            "title": f"Available style formats for {system_id}{request.assets_kwargs}",
        },
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}{request.assets_kwargs}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to classification system",
        },
        {
            "href": f"{BASE_URL}/classification_systems{request.assets_kwargs}",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to classification systems",
        },
        {
            "href": f"{BASE_URL}/",
            "rel": "root",
            "type": "application/json",
            "title": "API landing page",
        },
    ]

    for style_id in style_formats_id:
        links.append(
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}/styles/{style_id[0]}",
                "rel": "style",
                "type": "application/json",
                "title": "Link to style",
            }
        )

    return jsonify(links)

#TODO: review
@current_app.route("/classification_systems/<system_id>/styles/<style_format_id>", methods=["GET"])
@oauth2(required=True)
def style_file(system_id, style_format_id, **kwargs):
    """Retrieve available styles.

    :param system_id: identifier of a classification system
    :param style_format_id: identifier of a style format
    """
    system_style_file = data.get_classification_system_style(system_id, style_format_id)

    if not system_style_file:
        abort(404, f"Style File not found.")

    extension = get_extension(system_style_file.mime_type)

    system = data.classification_system(system_id)
    style_format = data.get_style_format(style_format_id)

    file_name = f"{system.name}_version-{system.version}_{style_format['name']}" + extension

    return send_file(BytesIO(system_style_file.style), mimetype='application/octet-stream', as_attachment=True,
                     attachment_filename=file_name)


@current_app.route("/classification_systems/search/<system_name>/<system_version>", methods=["GET"])
@oauth2(required=True)
def classification_system_search(system_name, system_version, **kwargs):
    """Return identifier of a classification system.
    
    :param system_name: name of a classification system
    :param system_version: version of a classification system
    """
    system = data.get_identifier_system(system_name, system_version)

    return ClassificationSystemSchema().dump(system), 200


@current_app.route("/style_formats/search/<style_format_name>", methods=["GET"])
@oauth2(required=True)
def style_format_search(style_format_name, **kwargs):
    """Return identifier of a style format.
    
    :param style_format_name: name of a style format
    """
    style_format = data.get_identifier_style_format(style_format_name)

    return StyleFormatsSchema().dump(style_format), 200


@current_app.route('/classification_systems', defaults={'system_id_or_identifier': None}, methods=["POST"])
@current_app.route("/classification_systems/<system_id_or_identifier>", methods=["PUT", "DELETE"])
@oauth2(roles=[['admin', 'editor']])
def edit_classification_system(system_id_or_identifier, **kwargs):
    """Create or edit a specific classification system.

    :param system_id_or_identifier: The id or identifier of a classification system
    """
    if request.method == "POST":
        args = request.get_json()

        errors = ClassificationSystemMetadataSchema().validate(args)

        if errors:
            return abort(400, str(errors))

        classification_system = data.create_classification_system(**args)

        return classification_system, 201

    if request.method == "DELETE":
        data.delete_classification_system(system_id_or_identifier)

        return {'message': f'{system_id_or_identifier} deleted'}, 204

    if request.method == "PUT":
        args = request.get_json()

        errors = ClassificationSystemMetadataSchema().validate(args, partial=True)

        if errors:
            return abort(400, str(errors))

        classification_system = data.update_classification_system(system_id_or_identifier, args)

        return classification_system, 200


@current_app.route("/classification_systems/<system_id>/classes", methods=["POST"])
@oauth2(roles=["admin"])
def create_class_system_classes(system_id, **kwargs):
    """Create classes for a classification system.

    :param system_id: identifier of a classification system
    """
    args = request.get_json()

    errors = ClassMetadataForm().validate(args)

    if errors:
        return abort(400, str(errors))

    classes = data.insert_classes(system_id_or_identifier=system_id, classes_files_json=args['classes'])

    result = ClassesSchema().dump(classes, many=True)

    return jsonify(result), 201


@current_app.route("/classification_systems/<system_id>/classes/<class_id>", methods=["PUT", "DELETE"])
@oauth2(roles=["admin"])
def edit_class_system_class(system_id, class_id, **kwargs):
    """Delete class of a specific classification system.
    
    :param system_id: identifier of a classification system
    :param class_id: identifier of a class
    """
    if request.method == "DELETE":
        data.delete_class(system_id, class_id)

        return {'message': f'{class_id} deleted'}, 204

    if request.method == "PUT":

        args = request.get_json()

        errors = ClassMetadataSchema().validate(args)

        if errors:
            return abort(400, str(errors))

        system_class = data.update_class(system_id, class_id, args)

        return ClassesSchema().dump(system_class), 200


@current_app.route("/mappings/<system_id_source>/<system_id_target>", methods=["POST", "PUT", "DELETE"])
@oauth2(roles=['admin'])
def edit_mapping(system_id_source, system_id_target, **kwargs):
    """Create or edit mappings in service.
    
    :param system_id_source: identifier of a source classification system
    :param system_id_target: identifier of a target classification system
    """
    if request.method == "POST":
        args = request.get_json()

        errors = ClassesMappingSchema(many=True).validate(args)

        if errors:
            return abort(400, str(errors))

        mappings = data.insert_mappings(system_id_source, system_id_target, args)

        return jsonify(ClassesMappingSchema().dump(mappings, many=True)), 201

    if request.method == "DELETE":
        data.delete_mappings(system_id_source, system_id_target)

        return {'message': 'Mapping delete!'}, 204

    if request.method == "PUT":
        args = request.get_json()

        errors = ClassesMappingMetadataSchema(many=True).validate(args)

        if errors:
            return abort(400, str(errors))

        mappings = data.update_mappings(system_id_source, system_id_target, args)

        return jsonify(ClassesMappingSchema().dump(mappings, many=True)), 200


@current_app.route("/classification_systems/<system_id>/styles", defaults={'style_format_id': None}, methods=["POST"])
@current_app.route("/classification_systems/<system_id>/styles/<style_format_id>", methods=["PUT", "DELETE"])
@oauth2(roles=['admin'])
def edit_styles(system_id, style_format_id, **kwargs):
    """Create or edit styles.

    :param system_id: identifier of a specific classification system
    :param style_format_id: identifier of a specific style format.
    """
    if request.method == "POST":

        if 'style_format_id' not in request.form:
            return abort(404, "Invalid parameter.")

        style_format_id = request.form.get('style_format_id')

        if 'style' not in request.files:
            return abort(404, "Invalid parameter.")

        file = request.files['style']

        data.insert_file(style_format_id=style_format_id,
                         system_id=system_id,
                         file=file)

        links = list()
        links += [
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}/styles/{style_format_id}",
                "rel": "style",
                "type": "application/json",
                "title": "style",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}/style_formats",
                "rel": "self",
                "type": "application/json",
                "title": f"Styles of the classification system {system_id}",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}",
                "rel": "parent",
                "type": "application/json",
                "title": "Link to classification system",
            },
            {
                "href": f"{BASE_URL}/classification_systems",
                "rel": "parent",
                "type": "application/json",
                "title": "Link to classification systems",
            },
            {
                "href": f"{BASE_URL}/",
                "rel": "root",
                "type": "application/json",
                "title": "API landing page",
            },
        ]
        return jsonify(links)

    if request.method == "PUT":
        if 'style' not in request.files:
            return abort(500, "Style File not found!")

        file = request.files['style']

        data.update_file(style_format_id=style_format_id,
                         system_id=system_id,
                         file=file)

        links = list()
        links += [
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}/styles/{style_format_id}",
                "rel": "style",
                "type": "application/json",
                "title": "style",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}/style_formats",
                "rel": "self",
                "type": "application/json",
                "title": f"Styles of the classification system {system_id}",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}",
                "rel": "parent",
                "type": "application/json",
                "title": "Link to classification system",
            },
            {
                "href": f"{BASE_URL}/classification_systems",
                "rel": "parent",
                "type": "application/json",
                "title": "Link to classification systems",
            },
            {
                "href": f"{BASE_URL}/",
                "rel": "root",
                "type": "application/json",
                "title": "API landing page",
            },
        ]
        return jsonify(links)

    if request.method == "DELETE":
        data.delete_file(style_format_id, system_id)

        return {'message': 'deleted!'}, 204


@current_app.route("/style_formats", defaults={'style_format_id': None}, methods=["POST"])
@current_app.route("/style_formats/<style_format_id>", methods=["PUT", "DELETE"])
@oauth2(roles=['admin'])
def edit_style_formats(style_format_id, **kwargs):
    """Create or edit styles formats.
    
    :param style_format_id: identifier of a specific style format
    """
    if request.method == "POST":
        args = request.get_json()

        errors = StyleFormatsSchema().validate(args)

        if errors:
            return abort(400, str(errors))

        style_format = data.create_style_format(**args)

        return jsonify(StyleFormatsSchema().dump(style_format)), 201

    if request.method == "DELETE":
        data.delete_style_format(style_format_id)

        return {'message': 'deleted'}, 204

    if request.method == "PUT":
        args = request.get_json()

        errors = StyleFormatsMetadataSchema().validate(args)

        if errors:
            return abort(400, str(errors))

        style_format = data.update_style_format(style_format_id, **args)

        return jsonify(StyleFormatsSchema().dump(style_format)), 200
