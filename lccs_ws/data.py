#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020 INPE.
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


def get_class_systems() -> list:
    """Retrieve available classification systems."""
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
        LucClassificationSystem.name.label("classification_system_name"),
        LucClassificationSystem.id.label("classification_system_id")

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
    class_system_class["classification_system_name"] = result[0].classification_system_name
    class_system_class["classification_system_id"] = result[0].classification_system_id

    return class_system_class


def get_styles(system_id, style_format_id: None):
    """Get Styles.

    :param system_id: Identification (name) of Classification System
    :type system_id: string
    :param style_format_id: Identification (name) of Style Format
    :type style_format_id: string
    """
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
    """Filter all mapping.

    :param classes_source: Identification (name) of class source
    :type classes_source: string
    :param classes_target: Identification (name) of class target
    :type classes_target: string
    """
    where = [ClassMapping.source_class_id.in_([value.id for value in classes_source])]

    if classes_target is not None:
        where += [ClassMapping.target_class_id.in_([value.id for value in classes_target])]

    result = db.session.query(ClassMapping). \
        filter(*where) \
        .group_by(ClassMapping.source_class_id,
                  ClassMapping.target_class_id).all()
    return result


def get_avaliable_mappings(system_id):
    """Retorn avaliable mapping for a givin classification system.

    :param system_id: Identification (name) of Classification System
    :type system_id: string
    """
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
    """Return mapping.

    :param system_id_source: Identification (name) of classification system source
    :type system_id_source: string
    :param system_id_target: Identification (name) of classification system target
    :type system_id_target: string
    """
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
            "source": i.source_class.name,
            "source_id": i.source_class.id,
            "target": i.target_class.name,
            "target_id": i.target_class.id,
            "description": i.description,
            "degree_of_similarity": float(i.degree_of_similarity)
        }]

    return result


def verify_style_format(style_name):
    """Filter style format.

    :param style_name: Identification (name) of style format
    :type style_name: string
    """
    try:
        style = StyleFormats.get(name=style_name)
        return style
    except:
        return None


def verify_class_system_exist(name):
    """Verify if classification system exist in server.

    :param name: Identification (name) of classification system
    :type name: string
    """
    try:
        class_system = LucClassificationSystem.get(name=name)
        return class_system
    except:
        return None


def insert_classification_systems(classification_system: dict):
    """Create a full classification system.

    :param classification_system: Informations about classification system
    :type classification_system: dict
    """
    class_system = LucClassificationSystem(name=classification_system['name'],
                                           description=classification_system['description'],
                                           authority_name=classification_system['authority_name'],
                                           version=classification_system['version'])

    class_system.save(commit=False)
    db.session.flush()

    return class_system


def delete_classification_system(classification_system_name):
    """Delete an classification system by a given name.

    Args:
        classification_system_name (string): classification_system_name name to be deleted
    """
    classification_system = LucClassificationSystem.get(name=classification_system_name)

    classes = LucClass.filter(class_system_id=classification_system.id)

    for i in classes:
        db.session.delete(i)

    db.session.delete(classification_system)

    db.session.commit()


def delete_classes(system_id, class_id):
    """Delete an class by a given name and classification system."""
    classification_system = LucClassificationSystem.get(name=system_id)

    class_to_delete = LucClass.get(class_system_id=classification_system.id, name=class_id)

    db.session.delete(class_to_delete)

    db.session.commit()


def update_class(classification_system: int, classe_name: str, class_info: dict):
    """Update an classification system by a given name."""
    class_system = LucClass.query.filter_by(name=classe_name,
                                            class_system_id=classification_system).first_or_404()

    if "name" in class_info:
        class_system.name = class_info["name"]
    if "description" in class_info:
        class_system.description = class_info["description"]
    if "code" in class_info:
        class_system.code = class_info["code"]
    if "parent" in class_info:
        parent_class = LucClass.query.filter_by(class_system_id=classification_system,
                                                name=class_info["parent"]).first_or_404()
        class_system.class_parent_id = parent_class.id


def update_classification_system(system_id, classes_file=None, name=None, description=None, authority_name=None,
                                 version=None):
    """Update an classification system by a given name.

    :param system_id: Classification System identifier.
    :type system_id: string
    :param classes_file: New Classes of an Classification System. Default None
    :type system_id: dict
    :param name: New Classification System name. Default None
    :type name: string
    :param description: New Classification System description. Default None
    :type description: string
    :param authority_name: New Classification System authority_name. Default None
    :type authority_name: string
    :param version: New Classification System version. Default None
    :type version: string
    """
    class_system = LucClassificationSystem.query.filter_by(name=system_id).first_or_404()

    with db.session.begin_nested():

        if classes_file:
            [update_class(class_system.id, c,v) for c,v in classes_file.items()]

            if name:
                class_system.name = name
            if description:
                class_system.description = description
            if authority_name:
                class_system.authority_name = authority_name
            if version:
                class_system.version = version

    db.session.commit()

    return class_system


def insert_class(classification_system: int, class_info: dict):
    """Create a new class.

    :param classification_system: Classification System id.
    :type classification_system: int
    :param class_info: Information of class.
    :type class_info: dict
    """
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
    """Return allowed files.

    :param style_file: Full Style file name.
    :type style_file: string
    """
    extensions = {'xml', 'json', 'qml', 'sdl'}

    if '.' in style_file and style_file.rsplit('.', 1)[1].lower() in extensions:
        return style_file.rsplit('.', 1)[1].lower()


def insert_file(style_format_name, class_system_name, style_file):
    """Insert File method.

    :param style_format_name: Identification (name) style format.
    :type style_format_name: string
    :param class_system_name: Identification (name) of classification system
    :type class_system_name: string
    :param style_file: Style File.
    :type style_file: json
    """
    system = verify_class_system_exist(class_system_name)

    style_format = StyleFormats.get(name=style_format_name)

    style = Styles(class_system_id=system.id,
                   style_format_id=style_format.id,
                   style=style_file)

    style.save()


def insert_mappings(system_id_source, system_id_target, classes_files_json: dict):
    """Create classes for a given classification system.

    :param system_id_source: Source Classification System
    :type system_id_source: string
    :param system_id_target: Target Classification System
    :type system_id_target: string
    :param classes_files_json: Json File with mappings
    :type classes_files_json: json
    """
    system_source = verify_class_system_exist(system_id_source)
    system_target = verify_class_system_exist(system_id_target)

    for classes in classes_files_json["mappings"]:
        mapping = None
        class_system_source = LucClass.get(name=classes["class_source"], class_system_id=system_source.id)
        class_system_class = LucClass.get(name=classes["class_target"], class_system_id=system_target.id)

        mapping = ClassMapping(source_class_id=class_system_source.id, target_class_id=class_system_class.id,
                               description=classes["description"], degree_of_similarity=classes["degree_of_similarity"])

        mapping.save(commit=False)
        db.session.flush()

    db.session.commit()
