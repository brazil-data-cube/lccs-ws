#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Controllers of Land Cover Classification System Web Service."""
import json

from flask import abort, current_app, jsonify, request

from lccs_ws.forms import ClassesSchema, ClassificationSystemSchema

from .config import Config
from .data import (get_class, get_class_system, get_class_systems,
                   get_classification_system_classes, get_mappings,
                   insert_classes, insert_classification_systems,
                   verify_class_system_exist)

BASE_URL = Config.LCCS_URL

@current_app.route("/", methods=["GET"])
def index():
    """URL Handler for Land User Cover Classification System through REST API."""
    links = list()
    links += [
        {"href": f"{BASE_URL}/", "rel": "self", "type": "application/json", "title": "Link to this document"},
        {"href": f"{BASE_URL}/classification_systems","rel": "classification_systems", "type": "application/json",
        "title": "List classification_systems",}
    ]

    return jsonify(links)

@current_app.route("/classification_systems", methods=["GET", "POST"])
def classification_systems():
    """URL Handler for Land User Cover Classification System through REST API."""
    if request.method == "GET":

        class_systems = get_class_systems()

        response = dict()

        for class_system in class_systems:
            links = [
                {
                    "href": f"{BASE_URL}/classification_system/{class_system['name']}",
                    "rel": "self",
                    "type": "application/json",
                    "title": "Link to this document",
                },
                {
                    "href": f"{BASE_URL}/classification_system/{class_system['name']}/classes",
                    "rel": "self",
                    "type": "application/json",
                    "title": "Link to this document",
                },
                {
                    "href": f"{BASE_URL}/classification_systems",
                    "rel": "parent",
                    "type": "application/json",
                    "title": "Link to classification systems",
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

        if (classes_files.content_type != 'application/json'):
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

        links.append( {
            "href": f"{BASE_URL}/classification_system/{system_id}/classes/{system_class['name']}",
            "rel": "child",
            "type": "application/json",
            "title": "Classification System Classes",
        }
        )

    result = dict()

    result["links"] = links

    return result

@current_app.route("/classification_system/<system_id>/classes/<class_id>", methods=["GET", "POST", "PUT", "DELETE"])
def class_system_class(system_id, class_id):
    """URL Handler for Land User Cover Class through REST API."""
    if request.method == "GET":

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