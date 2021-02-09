#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Views of Land Cover Classification System Web Service."""
import json
from io import BytesIO

from bdc_auth_client.decorators import oauth2
from flask import abort, current_app, jsonify, request, send_file
from lccs_db.utils import get_extension

from lccs_ws.forms import ClassificationSystemSchema

from . import data
from .config import Config

BASE_URL = Config.LCCS_URL


@current_app.route("/", methods=["GET"])
def root():
    """URL Handler for Land User Cover Classification System through REST API."""
    links = list()
    response = dict()

    links += [
        {"href": f"{BASE_URL}/", "rel": "self", "type": "application/json", "title": "Link to this document"},
        {"href": f"{BASE_URL}/classification_systems", "rel": "classification_systems", "type": "application/json",
         "title": "List classification_systems", }
    ]

    response["links"] = links

    return response


@current_app.route("/classification_systems", methods=["GET"])
def get_classification_systems():
    """Retrieve the list of available classification systems in the service."""
    classification_systems_list = data.get_classification_systems()

    for class_system in classification_systems_list:
        links = [
            {
                "href": f"{BASE_URL}/classification_systems/{class_system['id']}",
                "rel": "classification system",
                "type": "application/json",
                "title": "Link to Classification System",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{class_system['id']}/classes",
                "rel": "classes",
                "type": "application/json",
                "title": "Link to Classification System Classes",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{class_system['id']}/styles",
                "rel": "classes",
                "type": "application/json",
                "title": "Link to Available Styles",
            },
            {
                "href": f"{BASE_URL}/mappings/{class_system['id']}",
                "rel": "mappings",
                "type": "application/json",
                "title": "Link to Classification Mappings",
            },
            {
                "href": f"{BASE_URL}/classification_systems",
                "rel": "self",
                "type": "application/json",
                "title": "Link to this document",
            },
        ]

        class_system["links"] = links

    return jsonify(classification_systems_list)


@current_app.route("/classification_systems/<system_id>", methods=["GET"])
def classification_systems(system_id):
    """Retrieve information about the classification system.

    :param system_id: identifier of a classification system
    """
    classification_system = data.get_classification_system(system_id)

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
            "href": f"{BASE_URL}/classification_systems/{system_id}",
            "rel": "self",
            "type": "application/json",
            "title": "The classification_system",
        },
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}/classes",
            "rel": "classes",
            "type": "application/json",
            "title": "The classes related to this item",
        },
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}/styles",
            "rel": "styles",
            "type": "application/json",
            "title": "The styles related to this item",
        },
        {
            "href": f"{BASE_URL}/mappings/{system_id}",
            "rel": "mappings",
            "type": "application/json",
            "title": "The classification system mappings",
        },
        {"href": f"{BASE_URL}/", "rel": "root", "type": "application/json", "title": "API landing page."},
    ]

    classification_system["links"] = links

    return classification_system


@current_app.route("/classification_systems/<system_id>/classes", methods=["GET"])
def classification_systems_classes(system_id):
    """Retrieve the classes of a classification system.
    
    :param system_id: identifier of a classification system
    """
    classes_list = data.get_classification_system_classes(system_id)

    if not len(classes_list) > 0:
        abort(404, f"Classes not found.")

    links = list()

    links += [
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}/classes",
            "rel": "self",
            "type": "application/json",
            "title": f"Classes of the classification system {system_id}",
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

    for system_classes in classes_list:
        links.append({
            "href": f"{BASE_URL}/classification_systems/{system_id}/classes/{system_classes['id']}",
            "rel": "child",
            "type": "application/json",
            "title": "Classification System Classes",
        }
        )

    return jsonify(links)


@current_app.route("/classification_systems/<system_id>/classes/<class_id>", methods=["GET"])
def classification_systems_class(system_id, class_id):
    """Retrieve class information from a classification system.

    :param system_id: identifier of a classification system
    :param class_id: identifier of a class
    """
    classes = data.get_classification_system_class(system_id, class_id)
    
    if not len(classes) > 0:
        abort(404, f"Class not found.")

    links = [
        {
            "href": f"{BASE_URL}/classification_systems/{system_id}/classes/{classes['id']}",
            "rel": "self",
            "type": "application/json",
            "title": "Link to this document",
        },
        {
            "href": f"{BASE_URL}/classification_systems{system_id}/classes",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to this document",
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

    classes["links"] = links

    return classes


@current_app.route("/mappings/<system_id>", methods=["GET"])
def get_mappings(system_id):
    """Retrieve available mappings for a classification system.

    :param system_id: identifier of a classification system
    """
    mappings = data.get_mappings(system_id)

    if not len(mappings) > 0:
        abort(404, f"Mappings not found.")

    links = list()

    links += [
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

    for mapping_system in mappings:
        links.append({
            "href": f"{BASE_URL}/mappings/{system_id}/{mapping_system}",
            "rel": "child",
            "type": "application/json",
            "title": "Mapping",
        })

    return jsonify(links)


@current_app.route("/mappings/<system_id_source>/<system_id_target>", methods=["GET"])
def get_mapping(system_id_source, system_id_target):
    """Retrieve mapping.

    :param system_id_source: identifier of source classification system
    :param system_id_target: identifier of target classification system
    """
    class_system_mappings = data.get_mapping(system_id_source, system_id_target)

    for mp in class_system_mappings:
        links = [
            {
                "href": f"{BASE_URL}/classification_systems/{system_id_source}/classes/{mp['source_class_id']}",
                "rel": "item",
                "type": "application/json",
                "title": "Link to the source class",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{system_id_source}/classes/{mp['target_class_id']}",
                "rel": "item",
                "type": "application/json",
                "title": "Link to target class",
            },
        ]
        mp["degree_of_similarity"] = float(mp["degree_of_similarity"])
        mp["links"] = links

    result = dict()

    result["mappings"] = class_system_mappings

    return jsonify(class_system_mappings)


@current_app.route("/style_formats", methods=["GET"])
def get_styles_formats():
    """Retrieve available style formats in service."""
    styles_formats = data.get_style_formats()

    links = [
        {
            "href": f"{BASE_URL}/classification_systems",
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
    ]

    for st_f in styles_formats:
        links.append({
            "href": f"{BASE_URL}/style_formats/{st_f['id']}",
            "rel": "style_format",
            "type": "application/json",
            "title": "Link to style format",
        })
    
    return jsonify(links)


@current_app.route("/style_formats/<style_format_id>", methods=["GET"])
def get_style_format(style_format_id):
    """Retrieve information of a style formats.

    :param style_format_id: identifier of a style format
    """
    styles_format = data.get_style_format(style_format_id=style_format_id)

    if not len(styles_format) > 0:
        abort(404, f"Style Format not found.")
    
    links = [
        {
            "href": f"{BASE_URL}/classification_systems",
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
            "href": f"{BASE_URL}/style_formats/{styles_format['id']}",
            "rel": "style_format",
            "type": "application/json",
            "title": "Link to classification systems",
        },
        {
            "href": f"{BASE_URL}/style_formats/",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to classification systems",
        },
    ]

    styles_format["links"] = links

    return styles_format


@current_app.route("/classification_systems/<system_id>/style_formats", methods=["GET"])
def get_style_formats_classification_system(system_id):
    """Retrieve available style formats for a classification system.

    :param system_id: identifier of a source classification system
    """
    style_formats_id = data.get_system_style_format(system_id=system_id)

    if not len(style_formats_id) > 0:
        abort(404, f"Style Formats not found.")

    links = list()

    links += [
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

    for style_id in style_formats_id:
        links.append(
            {
                "href": f"{BASE_URL}/classification_systems/{system_id}/styles/{style_id[0]}",
                "rel": "style",
                "type": "application/json",
                "title": "style_format",
            }
        )

    return jsonify(links)


@current_app.route("/classification_systems/<system_id>/styles/<style_format_id>", methods=["GET"])
def style_file(system_id, style_format_id):
    """Retrieve available styles.

    :param system_id: identifier of a classification system
    :param style_format_id: identifier of a style format
    """
    system_style_file = data.get_classification_system_style(system_id, style_format_id)

    if not system_style_file:
        abort(404, f"Style File not found.")

    extension = get_extension(system_style_file.mime_type)
    
    file_name = f"{system_id}_{style_format_id}_style" + extension

    return send_file(BytesIO(system_style_file.style), mimetype='application/octet-stream', as_attachment=True,
                     attachment_filename=file_name)


@current_app.route('/classification_systems', defaults={'system_id': None}, methods=["POST"])
@current_app.route("/classification_systems/<system_id>", methods=["PUT", "DELETE"])
@oauth2(roles=["admin"])
def edit_classification_system(system_id, **kwargs):
    """Create or edit a specific classification system.

    :param system_id: identifier of a classification system
    """
    if request.method == "POST":
        try:
            classification_system = data.create_classification_system(**request.json)
        except Exception as e:
            abort(400, 'Error creating classification system')

        return ClassificationSystemSchema().dump(classification_system), 201

    if request.method == "DELETE":
        try:
            data.delete_classification_system(system_id)
        except Exception as e:
            raise e
        return {'message': 'deleted'}, 200

    if request.method == "PUT":
        try:
            classification_system = data.update_classification_system(system_id, **request.json)
        except Exception as e:
            abort(400, 'Error to update Classification System')
        return ClassificationSystemSchema().dump(classification_system), 200


@current_app.route("/classification_systems/<system_id>/classes", methods=["POST"])
@oauth2(roles=["admin"])
def create_class_system_classes(system_id, **kwargs):
    """Create classes for a classification system.

    :param system_id: identifier of a classification system
    """
    if request.content_type != 'application/json':
        abort(400, 'Classes is not a JSON file')

    file = request.json
    classes_files = json.loads(json.dumps(file))

    try:
        data.insert_classes(system_id, classes_files)
    except Exception as e:
        abort(400, 'Error add new class!')

    return {'message': 'created'}, 201


@current_app.route("/classification_systems/<system_id>/classes/<class_id>", methods=["PUT", "DELETE"])
@oauth2(roles=["admin"])
def edit_class_system_class(system_id, class_id, **kwargs):
    """Delete class of a specific classification system.
    
    :param system_id: identifier of a classification system
    :param class_id: identifier of a class
    """
    if request.method == "DELETE":
        try:
            data.delete_class(system_id, class_id)
        except Exception as e:
            abort(400, f'Error while delete {class_id} class!')
    
        return {'message': 'deleted'}, 200

    if request.method == "PUT":
        if request.content_type != 'application/json':
            abort(400, 'Classes is not a JSON file')

        classes_files = json.loads(request.json)

        try:
            data.update_class(system_id, class_id, **classes_files)
        except Exception as e:
            abort(400, f'Error while update classes!')

        return {'message': 'updated'}, 200


@current_app.route("/mappings/<system_id_source>/<system_id_target>", methods=["POST", "PUT", "DELETE"])
@oauth2(roles=['admin'])
def edit_mapping(system_id_source, system_id_target, **kwargs):
    """Create or edit mappings in service.
    
    :param system_id_source: identifier of a source classification system
    :param system_id_target: identifier of a target classification system
    """
    if request.method == "POST":
        if request.content_type != 'application/json':
            abort(400, 'Classes is not a JSON file')
    
        file = request.json
        mapping_files = json.loads(json.dumps(file))

        try:
            data.insert_mappings(system_id_source, system_id_target, mapping_files)
        except RuntimeError:
            abort(400, 'Error while insert mappings')

        return {'message': 'created'}, 200

    if request.method == "DELETE":

        try:
            data.delete_mappings(system_id_source, system_id_target)
        except Exception as e:
            abort(400, f'Error while delete {system_id_source} {system_id_target} mapping!')

        return {'message': 'Mapping delete!'}, 200

    if request.method == "PUT":
    
        if request.content_type != 'application/json':
            abort(400, 'Classes is not a JSON file')
    
        file = request.json
        
        mapping_files = json.loads(json.dumps(file))

        try:
            data.update_mappings(system_id_source, system_id_target, mapping_files)
        except Exception as e:
            abort(400, f'Error while updating {system_id_source} {system_id_target} mapping!')

        return {'message': 'Mapping updating!'}, 200


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
            return abort(500, "Style Format not found!")

        style_format_id = request.form.get('style_format_id')

        if 'style' not in request.files:
            return abort(500, "Style File not found!")

        file = request.files['style']

        try:
            data.insert_file(style_format_id=style_format_id,
                             system_id=system_id,
                             style_file=file)
        except Exception as e:
            abort(400, f'Error while insert style!')

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
        if 'style_format_id' not in request.form:
            return abort(500, "Style Format not found!")
    
        style_format_id = request.form.get('style_format_id')
    
        if 'style' not in request.files:
            return abort(500, "Style File not found!")
    
        file = request.files['style']

        try:
            data.update_file(style_format_id=style_format_id,
                             system_id=system_id,
                             style_file=file)
        except Exception as e:
            abort(400, f'Error while insert style!')

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
        try:
            data.delete_file(style_format_id, system_id)
        except Exception as e:
            abort(400, f'Error while delete {style_format_id} of {system_id} mapping!')

        return {'message': 'deleted!'}, 201


@current_app.route("/style_formats", defaults={'style_format_id': None}, methods=["POST"])
@current_app.route("/style_formats/<style_format_id>", methods=["PUT", "DELETE"])
@oauth2(roles=['admin'])
def edit_style_formats(style_format_id, **kwargs):
    """Create or edit styles formats.
    
    :param style_format_id: identifier of a specific style format
    """
    if request.method == "POST":
        try:
            style_format = data.create_style_format(**request.json)
        except Exception as e:
            abort(400, 'Error creating classification system')
        
        return style_format, 201

    if request.method == "DELETE":
        try:
            data.delete_style_format(style_format_id)
        except Exception as e:
            raise e
        return {'message': 'deleted'}, 200

    if request.method == "PUT":
        try:
            style_format = data.update_style_format(style_format_id, **request.json)
        except Exception as e:
            abort(400, 'Error to update Classification System')
        return style_format, 200
