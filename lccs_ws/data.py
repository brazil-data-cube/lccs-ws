#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Data module of Land Cover Classification System Web Service."""
from flask import abort
from lccs_db.models import (ClassMapping, LucClass, LucClassificationSystem,
                            StyleFormats, Styles, db)
from sqlalchemy.orm import aliased

from .forms import ClassificationSystemSchema


def get_class_systems():
    """Retrieve avaliable classification systems."""
    retval = LucClassificationSystem.filter()
    class_systems = ClassificationSystemSchema().dump(retval, many=True)

    return class_systems


def get_class_system(system_id):
    """Retrieve information for a given classification system.

    :param system_id: classification system identifier
    :type system_id: str
    :return: list of classification system
    :rtype: list
    """
    try:
        retval = LucClassificationSystem.get(name=system_id)
        class_system = ClassificationSystemSchema().dump(retval)
    except:
        return abort(500, 'Classification system "{}" not found'.format(system_id))

    return class_system


def get_classification_system_classes(system_id):
    """Retrieve a list of classes for a given classification system.

    :param system_id: classification system identifier
    :type system_id: str
    :return: list of classes
    :rtype: list
    """
    retval = db.session.query(LucClass) \
        .join(LucClassificationSystem, LucClass.class_system_id == LucClassificationSystem.id) \
        .filter(LucClassificationSystem.name == system_id) \
        .all()

    class_systems = ClassificationSystemSchema().dump(retval, many=True)

    return class_systems


def get_class(system_id, class_id):
    """Retrieve information about a class for a given classification system.

    :param system_id: classification system identifier
    :type system_id: str
    :param class_id: classs identifier
    :type class_id: str
    :return: list of classes
    :rtype: list
    """
    parent_classes = aliased(LucClass)

    columns = [
        LucClass.id,
        LucClass.name,
        LucClass.code,
        LucClass.description,
        parent_classes.name.label("class_parent"),
        LucClassificationSystem.name.label("class_system")

    ]

    where = [
        LucClassificationSystem.name == system_id,
        LucClass.name == class_id
    ]

    result = db.session.query(*columns) \
        .join(LucClassificationSystem, LucClass.class_system_id == LucClassificationSystem.id) \
        .join(parent_classes, LucClass.class_parent_id == parent_classes.id, isouter=True) \
        .filter(*where) \
        .all()

    class_system_class = dict()

    class_system_class["id"] = result[0].id
    class_system_class["name"] = result[0].name
    class_system_class["code"] = result[0].code
    class_system_class["description"] = result[0].description
    class_system_class["class_parent"] = result[0].class_parent
    class_system_class["class_system"] = result[0].class_system

    return class_system_class


def get_styles(system_id, style_format_id: None):
    """Get Styles."""
    columns = [
        LucClassificationSystem.name.label("class_system_name"),
        StyleFormats.name.label("style_format"),
        Styles.style.label("style_file")
    ]

    where = [LucClassificationSystem.name == system_id]

    if style_format_id:
        where += [StyleFormats.name == style_format_id]

    styles_formats = db.session.query(*columns) \
        .join(Styles, LucClassificationSystem.id == Styles.class_system_id) \
        .join(StyleFormats, Styles.style_format_id == StyleFormats.id) \
        .filter(*where) \
        .all()

    return styles_formats


def get_mappings(classes_source, classes_target):
    """Filter all mapping."""
    where = [ClassMapping.source_class_id.in_([value.id for value in classes_source])]

    if classes_target is not None:
        where += [ClassMapping.target_class_id.in_([value.id for value in classes_target])]

    result = db.session.query(ClassMapping). \
        filter(*where) \
        .group_by(ClassMapping.source_class_id,
                  ClassMapping.target_class_id).all()
    return result


def get_avaliable_mappings(system_id):
    """Retorn avaliable mapping for a givin classification system."""
    system_source = LucClassificationSystem.get(name=system_id)

    classes_source = LucClass.filter(class_system_id=system_source.id)

    mappings = get_mappings(classes_source, None)

    result = list()

    for mapping in mappings:
        target_class_name = LucClass.get(id=mapping.target_class_id)
        system = LucClassificationSystem.get(id=target_class_name.class_system_id)

        result.append(system.name) if system.name not in result else None

    return result


def get_mapping(system_id_source, system_id_target):
    """Return mapping."""
    try:
        system_source = LucClassificationSystem.get(name=system_id_source)
    except:
        return abort(500, "Classification system Source {} not found".format(system_id_source))
    try:
        system_target = LucClassificationSystem.get(name=system_id_target)
    except:
        return abort(500, "Classification system Target {} not found".format(system_id_target))

    classes_source = LucClass.filter(class_system_id=system_source.id)

    classes_target = LucClass.filter(class_system_id=system_target.id)

    mappings = get_mappings(classes_source, classes_target)

    result = list()

    for i in mappings:
        result += [{
            "source": LucClass.get(id=i.source_class_id).name,
            "target": LucClass.get(id=i.target_class_id).name,
            "description": i.description,
            "degree_of_similarity": float(i.degree_of_similarity)
        }]

    return result


def verify_style_format(style_name):
    """Filter style format."""
    try:
        style = StyleFormats.get(name=style_name)
        return style
    except:
        return None


def verify_class_system_exist(name):
    """Verify if classification system exist in server."""
    try:
        class_system = LucClassificationSystem.get(name=name)
        return class_system
    except:
        return None


def insert_classification_systems(classification_system: dict):
    """Create a full classification system."""
    class_system = LucClassificationSystem(name=classification_system['name'],
                                           description=classification_system['description'],
                                           authority_name=classification_system['authority_name'],
                                           version=classification_system['version'])

    class_system.save(commit=False)
    db.session.flush()

    return class_system


def insert_class(classification_system: int, class_info: dict):
    """Create a new class."""
    name = class_info['name']
    code = class_info['code']
    description = None
    parent = None
    classes = None

    if 'description' in class_info:
        description = class_info['description']

    if 'parent' in class_info:
        parent = class_info['parent']

    if parent is not None:
        try:
            parent_class = LucClass.get(class_system_id=classification_system, name=parent)

            classes = LucClass(name=name,
                               description=description,
                               code=code,
                               class_system_id=classification_system,
                               class_parent_id=parent_class.id)
            classes.save(commit=False)
            db.session.flush()
        except:
            abort(409, 'Error while crating Class')

    else:
        classes = LucClass(name=name, description=description,
                           code=code, class_system_id=classification_system)

        classes.save(commit=False)
        db.session.flush()

    return classes


def insert_classes(classes_files_json: dict, class_system: int):
    """Create classes for a given classification system.

    :param classes_files_json: classes file
    :type classes_files_json: dict
    :param class_system: classification system identifier
    :type class_system: int
    """
    for classes in classes_files_json["classes"]:
        insert_class(class_system, classes)

    db.session.commit()


def allowed_file(style_file):
    extensions = {'xml', 'json', 'qml', 'sdl'}

    if '.' in style_file and style_file.rsplit('.', 1)[1].lower() in extensions:
        return style_file.rsplit('.', 1)[1].lower()

    # return '.' in style_file and \
    #        style_file.rsplit('.', 1)[1].lower() in extensions


def insert_file(style_format_name, class_system_name, style_file):

    system = verify_class_system_exist(class_system_name)

    style_format = StyleFormats.get(name=style_format_name)

    style = Styles(class_system_id=system.id,
                   style_format_id=style_format.id,
                   style=style_file)

    style.save()
