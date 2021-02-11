#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Views of Land Cover Classification System Web Service."""
from io import BytesIO

from bdc_auth_client.decorators import oauth2
from flask import abort, current_app, jsonify, request, send_file
from lccs_db.utils import get_extension

from lccs_ws.forms import (ClassesMappingMetadataSchema, ClassesMappingSchema,
                           ClassesSchema, ClassificationSystemMetadataSchema,
                           ClassificationSystemSchema, ClassMetadataSchema,
                           StyleFormatsMetadataSchema, StyleFormatsSchema)

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
    response["lccs_version"] = Config.BDC_LCCS_API_VERSION
    
    return response


@current_app.route("/classification_systems", methods=["GET"])
def get_classification_systems():
    """Retrieve the list of available classification systems in the service."""
    classification_systems_list = data.get_classification_systems()
    
    for class_system in classification_systems_list:
        links = [
            {
                "href": f"{BASE_URL}/classification_systems/{class_system['id']}",
                "rel": "classification_system",
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
                "rel": "styles",
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

    if not len(classes_list) > 0:
        return jsonify(links)
    
    for system_classes in classes_list:
        links.append(
            {
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
    
    return jsonify(class_system_mappings)


@current_app.route("/style_formats", methods=["GET"])
def get_styles_formats():
    """Retrieve available style formats in service."""
    styles_formats = data.get_style_formats()
    
    links = [
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
    
    for st_f in styles_formats:
        links.append({
            "href": f"{BASE_URL}/style_formats/{st_f['id']}",
            "rel": "items",
            "type": "application/json",
            "title": f"Link to style format {st_f['id']}"
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
    
    system = data.classification_system(system_id)
    style_format = data.get_style_format(style_format_id)
    
    file_name = f"{system.name}_version-{system.version}_{style_format['name']}" + extension
    
    return send_file(BytesIO(system_style_file.style), mimetype='application/octet-stream', as_attachment=True,
                     attachment_filename=file_name)


@current_app.route("/classification_systems/search/<system_name>/<system_version>", methods=["GET"])
def classification_system_search(system_name, system_version):
    """Return identifier of a classification system.
    
    :param system_name: name of a classification system
    :param system_version: version of a classification system
    """
    system = data.get_identifier_system(system_name, system_version)
    
    return ClassificationSystemSchema().dump(system), 200


@current_app.route("/style_formats/search/<style_format_name>", methods=["GET"])
def style_format_search(style_format_name):
    """Return identifier of a style format.
    
    :param style_format_name: name of a style format
    """
    style_format = data.get_identifier_style_format(style_format_name)
    
    return StyleFormatsSchema().dump(style_format), 200


@current_app.route('/classification_systems', defaults={'system_id': None}, methods=["POST"])
@current_app.route("/classification_systems/<system_id>", methods=["PUT", "DELETE"])
@oauth2(roles=["admin"])
def edit_classification_system(system_id, **kwargs):
    """Create or edit a specific classification system.

    :param system_id: identifier of a classification system
    """
    if request.method == "POST":
        args = request.get_json()
        
        errors = ClassificationSystemSchema().validate(args)
        
        if errors:
            return errors, 400
        
        classification_system = data.create_classification_system(**args)
        
        return ClassificationSystemSchema().dump(classification_system), 201
    
    if request.method == "DELETE":
        data.delete_classification_system(system_id)
        
        return {'message': f'{system_id} deleted'}, 204
    
    if request.method == "PUT":
        args = request.get_json()
        
        errors = ClassificationSystemMetadataSchema().validate(args)
        
        if errors:
            return errors, 400
        
        classification_system = data.update_classification_system(system_id, args)
        
        return ClassificationSystemSchema().dump(classification_system), 200


@current_app.route("/classification_systems/<system_id>/classes", methods=["POST"])
@oauth2(roles=["admin"])
def create_class_system_classes(system_id, **kwargs):
    """Create classes for a classification system.

    :param system_id: identifier of a classification system
    """
    args = request.get_json()
    
    errors = ClassesSchema(many=True).validate(args)
    
    if errors:
        return errors, 400
    
    classes = data.insert_classes(system_id, args)
    
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
            return errors, 400
        
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
            return errors, 400
        
        mappings = data.insert_mappings(system_id_source, system_id_target, args)
        
        return jsonify(ClassesMappingSchema().dump(mappings, many=True)), 201
    
    if request.method == "DELETE":
        data.delete_mappings(system_id_source, system_id_target)
        
        return {'message': 'Mapping delete!'}, 204
    
    if request.method == "PUT":
        args = request.get_json()
        
        errors = ClassesMappingMetadataSchema(many=True).validate(args)
        
        if errors:
            return errors, 400
        
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
            return errors, 400
        
        style_format = data.create_style_format(**args)
        
        return jsonify(StyleFormatsSchema().dump(style_format)), 201
    
    if request.method == "DELETE":
        data.delete_style_format(style_format_id)
        
        return {'message': 'deleted'}, 204
    
    if request.method == "PUT":
        args = request.get_json()
        
        errors = StyleFormatsMetadataSchema().validate(args)
        
        if errors:
            return errors, 400
        
        style_format = data.update_style_format(style_format_id, **args)
        
        return jsonify(StyleFormatsSchema().dump(style_format)), 200
