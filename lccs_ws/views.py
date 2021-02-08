#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Views of Land Cover Classification System Web Service."""
import json
import os

from io import BytesIO
from bdc_auth_client.decorators import oauth2
from flask import abort, current_app, jsonify, request, send_file
from werkzeug.utils import secure_filename

from lccs_ws.forms import ClassificationSystemSchema
from lccs_db.utils import get_extension

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
    """Retrieves the list of available classification systems in the service."""
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
    """Retrieves information about the classification system.

    :param system_id: identifier of a classification system
    """
    classification_system = data.get_classification_systems(system_id)

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
    """Retrieves the classes of a classification system.
    
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
    classes = data.get_classification_system_classes(system_id, class_id)
    
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
    """Retrieve available mappings of classification system.

    :param system_id: identifier of a classification system
    """
    mappings = data.get_available_mappings(system_id)

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

    for mapping_name in mappings:
        links.append({
            "href": f"{BASE_URL}/mappings/{system_id}/{mapping_name}",
            "rel": "child",
            "type": "application/json",
            "title": mapping_name,
        })

    result = dict()

    result["links"] = links

    return result


@current_app.route("/mappings/<system_id_source>/<system_id_target>", methods=["GET"])
def get_mapping(system_id_source, system_id_target):
    """Retrieve mapping.

    :param system_id_source: identifier (name) of a source classification system
    :param system_id_target: identifier (name) of a target classification system
    """
    class_system_mappings = data.get_mapping(system_id_source, system_id_target)

    for mp in class_system_mappings:
        links = [
            {
                "href": f"{BASE_URL}/classification_systems/{system_id_source}/classes/{mp['source']}",
                "rel": "item",
                "type": "application/json",
                "title": "Link to the source class",
            },
            {
                "href": f"{BASE_URL}/classification_systems/{system_id_source}/classes/{mp['target']}",
                "rel": "item",
                "type": "application/json",
                "title": "Link to target class",
            },
        ]

        mp["links"] = links

    result = dict()

    result["mappings"] = class_system_mappings

    return result


@current_app.route("/style_formats", methods=["GET"])
def get_styles_formats():
    """Retrieve available style formats."""
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
    """Retrieve available style formats."""
    styles_format = data.get_style_formats(style_format_id=style_format_id)

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
    """Retrieve available styles.

    :param system_id: identifier (name) of a source classification system
    """
    style_formats_id = data.get_style_formats(system_id=system_id)

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

    :param system_id: identifier (name) of a classification system
    :param style_id: identifier (name) of a style format
    """
    system_style_file = data.get_classification_system_style(system_id, style_format_id)

    if not system_style_file:
        abort(404, f"Style File not found.")

    extension = get_extension(system_style_file.mime_type)
    
    file_name = f"{system_id}_{style_format_id}_style" + extension

    return send_file(BytesIO(system_style_file.style), mimetype='application/octet-stream', as_attachment=True,
                     attachment_filename=file_name)

# ----

@current_app.route('/classification_systems', defaults={'system_id': None}, methods=["POST"])
@current_app.route("/classification_systems/<system_id>", methods=["PUT", "DELETE"])
@oauth2(roles=["admin"])
def edit_classification_system(system_id, **kwargs):
    """Add, update or delete a single a classification system."""
    if request.method == "POST":
        try:
            classification_system = data.create_classification_system(**request.json)
        except Exception as e:
            abort(400, 'Error creating classification system')

        return ClassificationSystemSchema(exclude=['id']).dump(classification_system), 201

    if request.method == "DELETE":
        try:
            data.delete_classification_system(system_id)
        except Exception as e:
            abort(400, 'Error when deleting the Classification Systems')
        return {'message': 'deleted'}, 200

    if request.method == "PUT":
        try:
            classification_system = data.update_classification_system(system_id, **request.json)
        except Exception as e:
            abort(400, 'Error to update Classification System')
        return ClassificationSystemSchema(exclude=['id']).dump(classification_system), 200


@current_app.route("/classification_systems/<system_id>/classes", methods=["POST", "PUT", "DELETE"])
@oauth2(roles=["admin"])
def edit_class_system_classes(system_id, **kwargs):
    """Add or update or delete a single class.

    :param system_id: identifier (name) of a classification system
    """
    if request.method == "POST":

        classes_files = request.files['classes']

        if classes_files.content_type != 'application/json':
            abort(400, 'Classes is not a JSON file')

        classes_file = str(classes_files.read(), 'utf-8')

        post_file = json.loads(classes_file)

        try:
            data.insert_classes(post_file, system_id)
        except Exception as e:
            abort(400, 'Error add new class!')

        return {'message': 'created'}, 201

    if request.method == "PUT":

        class_system = data.verify_class_system_exist(system_id)

        if class_system is None:
            abort(400, f'Error to add new class Classification System {system_id} not exist')

        classes_files = request.files['classes']

        if classes_files.content_type != 'application/json':
            abort(400, 'Classes is not a JSON file')

        classes_file = str(classes_files.read(), 'utf-8')

        post_file = json.loads(classes_file)

        try:
            data.update_class(class_system.id, post_file)
        except Exception as e:
            abort(400, f'Error while update classes!')

        return {'message': 'updated'}, 200

    if request.method == "DELETE":

        class_system = data.verify_class_system_exist(system_id)

        if class_system is None:
            abort(400, f'Error to add new class Classification System {system_id} not exist')

        try:
            data.delete_classes(class_system)
        except Exception as e:
            abort(400, f'Error while delete {system_id} classes!')

        return {'message': 'deleted'}, 200


@current_app.route("/classification_systems/<system_id>/classes/<class_id>", methods=["DELETE"])
@oauth2(roles=["admin"])
def edit_class_system_class(system_id, class_id, **kwargs):
    """Delete a single class."""
    class_system = data.verify_class_system_exist(system_id)

    if class_system is None:
        abort(400, f'Error to add new class Classification System {system_id} not exist')

    try:
        data.delete_one_classe(class_system, class_id)
    except Exception as e:
        abort(400, f'Error while delete {class_id} class!')

    return {'message': 'deleted'}, 200


@current_app.route("/mappings/<system_id_source>/<system_id_target>", methods=["POST", "PUT", "DELETE"])
@oauth2(roles=['admin'])
def edit_mapping(system_id_source, system_id_target, **kwargs):
    """Edit classification system mapping."""
    if request.method == "POST":

        mappings = request.files['mappings']

        if mappings.content_type != 'application/json':
            abort(415, 'Mappings is not a JSON file')

        mappings_file = str(mappings.read(), 'utf-8')

        post_file = json.loads(mappings_file)

        try:
            data.insert_mappings(system_id_source, system_id_target, post_file)
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

        mappings = request.files['mappings']

        if mappings.content_type != 'application/json':
            abort(415, 'Mappings is not a JSON file')

        mappings_file = str(mappings.read(), 'utf-8')

        post_file = json.loads(mappings_file)

        try:
            data.update_mappings(system_id_source, system_id_target, post_file)
        except Exception as e:
            abort(400, f'Error while updating {system_id_source} {system_id_target} mapping!')

        return {'message': 'Mapping updating!'}, 200


@current_app.route("/classification_systems/<system_id>/styles", defaults={'style_format_id': None}, methods=["POST"])
@current_app.route("/classification_systems/<system_id>/styles/<style_format_id>", methods=["DELETE"])
@oauth2(roles=['admin'])
def edit_styles(system_id, style_format_id, **kwargs):
    """Retrieve available styles.

    :param system_id: identifier (name) of a source classification system
    :param style_format_id: identifier (name) of a style format.
    """
    if request.method == "POST":

        if 'style_format' not in request.form:
            return abort(500, "Style Format not found!")

        style_format = request.form.get('style_format')

        if 'style' not in request.files:
            return abort(500, "Style File not found!")

        file = request.files['style']

        file_format = data.allowed_file(file.filename)

        if file_format:

            filename = secure_filename(file.filename)

            file_directory = os.path.join(Config.LCCS_UPLOAD_FOLDER, filename)

            file.save(file_directory)

            json_file = json.dumps({"format": file_format,
                                    "filename": filename})

            try:
                data.insert_file(style_format_name=style_format,
                                 class_system_name=system_id,
                                 style_file=json_file)
            except Exception as e:
                os.remove(file_directory)
                abort(400, f'Error while insert style!')

            return {'message': 'style insert!'}, 201

    if request.method == "DELETE":
        try:
            data.delete_file(style_format_id, system_id)
        except Exception as e:
            abort(400, f'Error while delete {style_format_id} of {system_id} mapping!')

        return {'message': 'deleted!'}, 201
