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

from flask import (Response, abort, current_app, jsonify, request,
                   send_from_directory)
from werkzeug.utils import secure_filename

from lccs_ws.forms import ClassificationSystemSchema

from .config import Config
from .data import (allowed_file, get_avaliable_mappings, get_class,
                   get_class_system, get_class_systems,
                   get_classification_system_classes, get_mapping, get_styles,
                   insert_classes, insert_classification_systems, insert_file,
                   verify_class_system_exist)

BASE_URL = Config.LCCS_URL


@current_app.route("/", methods=["GET"])
def index():
    """URL Handler for Land User Cover Classification System through REST API."""
    links = list()
    links += [
        {"href": f"{BASE_URL}/", "rel": "self", "type": "application/json", "title": "Link to this document"},
        {"href": f"{BASE_URL}/classification_systems", "rel": "classification_systems", "type": "application/json",
         "title": "List classification_systems", }
    ]

    return jsonify(links)


@current_app.route("/classification_systems", methods=["GET", "POST"])
def classification_systems():
    """Retrieve classification systems avaliable."""
    if request.method == "GET":

        class_systems = get_class_systems()

        response = dict()

        for class_system in class_systems:
            links = [
                {
                    "href": f"{BASE_URL}/classification_system/{class_system['name']}",
                    "rel": "self",
                    "type": "application/json",
                    "title": "Link to Classification System",
                },
                {
                    "href": f"{BASE_URL}/classification_system/{class_system['name']}/classes",
                    "rel": "classes",
                    "type": "application/json",
                    "title": "Link to Classification System Classes",
                },
                {
                    "href": f"{BASE_URL}/mappings/{class_system['name']}",
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

        response["classification_systems"] = class_systems

        return response

    if request.method == "POST":

        classes_files = request.files['classes']

        classification_system = {
            "name": request.form.get('name'),
            "description": request.form.get('description'),
            "authority_name": request.form.get('authority_name'),
            "version": request.form.get('version')
        }

        if verify_class_system_exist(classification_system['name']) is not None:
            abort(409, 'Classification System Already Exists')

        if classes_files.content_type != 'application/json':
            abort(400, 'Classes is not a JSON file')

        class_system = None

        try:
            class_system = insert_classification_systems(classification_system)
        except Exception as e:
            abort(400, 'Error creating Classification System')

        classes_file = str(classes_files.read(), 'utf-8')

        post_file = json.loads(classes_file)

        insert_classes(post_file, class_system.id)

        return ClassificationSystemSchema(exclude=['id']).dump(class_system), 201


@current_app.route("/classification_system/<system_id>", methods=["GET"])
def classification_system(system_id):
    """Retrieve metadata of classification system.

    :param system_id: identifier (name) of a classification system
    """
    classification_system = get_class_system(system_id)

    links = [
        {
            "href": f"{BASE_URL}/classification_system",
            "rel": "parent",
            "type": "application/json",
            "title": "Link to this document",
        },
        {
            "href": f"{BASE_URL}/classification_system/{system_id}",
            "rel": "self",
            "type": "application/json",
            "title": "The classification_system",
        },
        {
            "href": f"{BASE_URL}/classification_system/{system_id}/classes",
            "rel": "classes",
            "type": "application/json",
            "title": "The classes related to this item",
        },
        {
            "href": f"{BASE_URL}/classification_system/{system_id}/styles",
            "rel": "styles",
            "type": "application/json",
            "title": "The styles related to this item",
        },
        {"href": f"{BASE_URL}/", "rel": "root", "type": "application/json", "title": "API landing page."},
    ]

    classification_system["links"] = links

    return classification_system


@current_app.route("/classification_system/<system_id>/classes", methods=["GET"])
def class_system_classes(system_id):
    """Retrieve classes of classification system.

    :param system_id: identifier (name) of a classification system
    """
    classes = get_classification_system_classes(system_id)

    links = list()

    links += [
        {
            "href": f"{BASE_URL}/classification_system/{system_id}/classes",
            "rel": "self",
            "type": "application/json",
            "title": f"Classes of the classification system {system_id}",
        },
        {
            "href": f"{BASE_URL}/classification_system/{system_id}",
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

    for system_class in classes:
        links.append({
            "href": f"{BASE_URL}/classification_system/{system_id}/classes/{system_class['name']}",
            "rel": "child",
            "type": "application/json",
            "title": "Classification System Classes",
        }
        )

    result = dict()

    result["links"] = links

    return result


@current_app.route("/classification_system/<system_id>/classes/<class_id>", methods=["GET"])
def class_system_class(system_id, class_id):
    """Retrieve metadata of classe.

    :param system_id: identifier (name) of a classification system
    :param class_id: identifier (name) of a class
    """
    classes = get_class(system_id, class_id)

    links = [
        {
            "href": f"{BASE_URL}/classification_system/{system_id}/classes/{classes['name']}",
            "rel": "self",
            "type": "application/json",
            "title": "Link to this document",
        },
        {
            "href": f"{BASE_URL}/classification_system{system_id}/classes",
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
def mappings(system_id):
    """Retrieve avaliable mappings of classification system.

    :param system_id: identifier (name) of a classification system
    """
    mappings = get_avaliable_mappings(system_id)

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


@current_app.route("/mappings/<system_id_source>/<system_id_target>", methods=["GET", "POST"])
def mapping(system_id_source, system_id_target):
    """Retrieve mapping.

    :param system_id_source: identifier (name) of a source classification system
    :param system_id_target: identifier (name) of a target classification system
    """
    if request.method == "GET":

        class_system_mappings = get_mapping(system_id_source, system_id_target)

        for mp in class_system_mappings:
            links = [
                {
                    "href": f"{BASE_URL}/classification_system/{system_id_source}/classes/{mp['source']}",
                    "rel": "item",
                    "type": "application/json",
                    "title": "Link to the source class",
                },
                {
                    "href": f"{BASE_URL}/classification_system/{system_id_source}/classes/{mp['target']}",
                    "rel": "item",
                    "type": "application/json",
                    "title": "Link to target class",
                },
            ]

            mp["links"] = links

        result = dict()

        result["mappings"] = class_system_mappings

        return result


@current_app.route("/classification_system/<system_id>/styles", methods=["GET", "POST"])
def styles(system_id):
    """Retrieve available styles.

    :param system_id: identifier (name) of a source classification system
    """
    if request.method == "GET":
        styles = get_styles(system_id, None)

        links = list()

        links += [
            {
                "href": f"{BASE_URL}/classification_system/{system_id}/styles",
                "rel": "self",
                "type": "application/json",
                "title": f"Styles of the classification system {system_id}",
            },
            {
                "href": f"{BASE_URL}/classification_system/{system_id}",
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

        for style in styles:
            links.append(
                {
                    "href": f"{BASE_URL}/classification_system/{style[0]}/styles/{style[1]}",
                    "rel": "child",
                    "type": "application/json",
                    "title": f"{style[1]}",
                }
            )

        result = dict()

        result["links"] = links

        return result

    if request.method == "POST":

        style_format = request.form.get('style_format')

        if 'style' not in request.files:
            return abort(500, "Style File not found!")

        file = request.files['style']

        file_format = allowed_file(file.filename)

        if file_format:

            filename = secure_filename(file.filename)

            file_directory = os.path.join(Config.LCCS_UPLOAD_FOLDER, filename)

            file.save(file_directory)

            json_file = json.dumps({"format": file_format,
                                    "filename": filename})

            insert_file(style_format_name=style_format,
                        class_system_name=system_id,
                        style_file=json_file)

            return {'message': 'Classification Sytem Style Insert'}, 201


@current_app.route("/classification_system/<system_id>/styles/<style_id>", methods=["GET"])
def style(system_id, style_id):
    """Retrieve available styles.

    :param system_id: identifier (name) of a classification system
    :param style_id: identifier (name) of a style format
    """
    styles = get_styles(system_id, style_id)

    file = json.loads(styles[0].style_file)

    return send_from_directory(Config.LCCS_UPLOAD_FOLDER, file['filename'], as_attachment=True)
