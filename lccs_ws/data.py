#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Data module of Land Cover Classification System Web Service."""
import json
import os

from flask import abort
from lccs_db.models import (ClassMapping, LucClass, LucClassificationSystem,
                            StyleFormats, Styles, db)
from lccs_db.utils import get_mimetype
from sqlalchemy.orm import aliased
from sqlalchemy import Float, and_, distinct, cast

from .config import Config
from .forms import ClassificationSystemSchema, ClassesSchema, StyleFormatsSchema, ClassesMappingSchema


def get_classification_systems():
    """Retrieve all classification systems available in service."""
    system = db.session.query(LucClassificationSystem).all()
    return ClassificationSystemSchema().dump(system, many=True)


def get_classification_system(system_id):
    """Retrieve information for a given classification system.

    :param system_id: identifier of a classification system
    :type system_id: integer
    """
    system = db.session.query(LucClassificationSystem) \
        .filter(LucClassificationSystem.id == system_id).first()
    return ClassificationSystemSchema().dump(system)


def get_classification_system_classes(system_id):
    """Retrieve a list of classes for a given classification system.

    :param system_id: identifier of a classification system
    :type system_id: integer
    """
    classes = db.session.query(LucClass) \
        .join(LucClassificationSystem, LucClass.class_system_id == LucClassificationSystem.id) \
        .filter(LucClassificationSystem.id == system_id) \
        .all()
    
    return ClassesSchema().dump(classes, many=True)


def get_classification_system_class(system_id, class_id):
    """Retrieve information for a given class.

    :param system_id: identifier of a classification system
    :type system_id: integer
    :param class_id: identifier of a class
    :type class_id: integer
    """
    columns = [LucClass.id, LucClass.name, LucClass.code, LucClass.description, LucClass.class_parent_id]
    
    where = [
        LucClassificationSystem.id == system_id,
        and_(LucClass.id == class_id)
    ]
    
    class_info = db.session.query(*columns) \
        .join(LucClassificationSystem, LucClass.class_system_id == LucClassificationSystem.id) \
        .filter(*where) \
        .first()
    
    return ClassesSchema().dump(class_info)


def get_style_formats():
    """Retrieve all styles formats available in service."""
    style_formats = db.session.query(StyleFormats.id).all()
    
    return StyleFormatsSchema().dump(style_formats, many=True)


def get_style_format(style_format_id):
    """Retrieve information for a style format.

    :param style_format_id: identifier of a style format
    :type style_format_id: integer
    """
    style_format = db.session.query(StyleFormats). \
        filter(StyleFormats.id == style_format_id).first()
    
    return StyleFormatsSchema().dump(style_format)


def get_system_style_format(system_id):
    """Return the styles formats available for a classification system.
    
    :param system_id: identifier of a classification system
    :type system_id: integer
    """
    if system_id:
        style_formats_id = db.session.query(Styles.style_format_id) \
            .filter(Styles.class_system_id == system_id) \
            .all()
        return style_formats_id


def get_classification_system_style(system_id, style_format_id):
    """Return the style of a classification system.

    :param system_id: Identification (name) of Classification System
    :type system_id: string
    :param style_format_id: Identification (name) of Style Format
    :type style_format_id: string
    """
    columns = [
        Styles.style,
        Styles.mime_type
    ]
    
    where = [
        Styles.class_system_id == system_id,
        and_(Styles.style_format_id == style_format_id),
    ]
    
    style_file = db.session.query(*columns) \
        .join(StyleFormats, StyleFormats.id == Styles.style_format_id) \
        .filter(*where) \
        .first()
    
    return style_file


def get_mappings(system_id_source):
    """Return available mapping for a classification system.

    :param system_id_source: identification of a classification system
    :type system_id_source: integer
    """
    classes_source = db.session.query(LucClass.id) \
        .filter(LucClass.class_system_id == system_id_source) \
        .all()
    
    targets_class_id = db.session.query(distinct(ClassMapping.target_class_id)) \
        .filter(ClassMapping.source_class_id.in_(classes_source)) \
        .all()
    
    systems = db.session.query(distinct(LucClassificationSystem.id)) \
        .join(LucClass, LucClass.class_system_id == LucClassificationSystem.id) \
        .filter(LucClass.id.in_(targets_class_id)) \
        .all()
    
    return [value[0] for value in systems]


def get_system_mapping(system_id_source, system_id_target):
    """Get Mapping."""
    classes_source = db.session.query(LucClass.id) \
        .filter(LucClass.class_system_id == system_id_source) \
        .all()
    
    classes_target = db.session.query(LucClass.id) \
        .filter(LucClass.class_system_id == system_id_target) \
        .all()
    
    columns = [
        ClassMapping.target_class_id,
        ClassMapping.source_class_id,
        ClassMapping.description,
        ClassMapping.degree_of_similarity
    ]
    
    mappings = db.session.query(*columns) \
        .filter(
        and_(ClassMapping.source_class_id.in_(classes_source), ClassMapping.target_class_id.in_(classes_target))) \
        .all()
    
    return mappings


def get_mapping(system_id_source, system_id_target):
    mappings = get_system_mapping(system_id_source, system_id_target)
    
    return ClassesMappingSchema().dump(mappings, many=True)


def classification_system(system_id):
    """Verify if classification system exist in server.

    :param system_id: identifier of classification system
    :type system_id: integer
    """
    return LucClassificationSystem.query.filter_by(id=system_id).first_or_404()


def create_classification_system(name, authority_name, version, description=None):
    """Create a full classification system.

    :param name: Classification system name
    :type name: string
    :param authority_name: Classification system authority name
    :type authority_name: string
    :param version: Classification system version
    :type version: string
    :param description: Classification system description
    :type description: string
    """
    system = db.session.query(LucClassificationSystem).filter(LucClassificationSystem.name == name,
                                                              LucClassificationSystem.version == version).first()
    if system:
        abort(409, 'Classification System already registered!')
    
    classification_system_info = dict(name=name, authority_name=authority_name, version=version,
                                      description=description)
    
    with db.session.begin_nested():
        system = LucClassificationSystem(**dict(classification_system_info))
        
        db.session.add(system)
    
    db.session.commit()
    
    return system


def delete_classification_system(system_id):
    """Delete an classification system by a identifier.

    :param system_id: identifier of a classification system to be deleted
    :type system_id: string
    """
    system = db.session.query(LucClassificationSystem).filter(LucClassificationSystem.id == system_id).first_or_404()
    
    db.session.delete(system)
    
    db.session.commit()


def update_classification_system(system_id, name=None, description=None, authority_name=None,
                                 version=None):
    """Update an classification system by a given name.

    :param system_id: Classification System identifier.
    :type system_id: string
    :param name: New Classification System name. Default None
    :type name: string
    :param description: New Classification System description. Default None
    :type description: string
    :param authority_name: New Classification System authority_name. Default None
    :type authority_name: string
    :param version: New Classification System version. Default None
    :type version: string
    """
    system = classification_system(system_id)
    
    with db.session.begin_nested():
        if name:
            system.name = name
        if description:
            system.description = description
        if authority_name:
            system.authority_name = authority_name
        if version:
            system.version = version
    
    db.session.commit()
    
    return system


def delete_classes(class_system):
    """Delete all class by a given classification system."""
    classes = LucClass.filter(class_system_id=class_system.id)
    
    with db.session.begin_nested():
        for c in classes:
            db.session.delete(c)
    db.session.commit()


def delete_class(system_id: int, class_id: int):
    """Delete an class by a given name and classification system."""
    class_to_delete = db.session.query(LucClass).filter(LucClass.id == class_id,
                                                        LucClass.class_system_id == system_id).first_or_404()
    
    with db.session.begin_nested():
        db.session.delete(class_to_delete)
    
    db.session.commit()


def update_class(system_id: int, class_id: int, name, code, description, class_parent_id):
    """Update an classification system by a given name."""
    system_class = LucClass.query.filter_by(id=class_id, classification_system_id=system_id).first_or_404()
    
    with db.session.begin_nested():
        if name:
            system_class.name = name
        if description:
            system_class.description = description
        if code:
            system_class.code = code
        if class_parent_id:
            system_class.class_parent_id = class_parent_id
    
    db.session.commit()


def insert_class(system_id: int, name, code, description, class_parent_id=None):
    """Create a new class.

    :param system_id: identifier of classification system.
    :type system_id: int
    :param name: name of a class.
    :type name: string
    :param code: class code.
    :type code: string
    :param description: class description.
    :type description: string
    :param class_parent_id: class class_parent_id.
    :type class_parent_id: integer
    """
    system_class = db.session.query(LucClass).filter_by(class_system_id=system_id, name=name).first()
    
    if system_class:
        abort(409, 'Class already registered in the system!')
    
    class_infos = dict(
        name=name,
        code=code,
        description=description,
        class_system_id=system_id,
        class_parent_id=class_parent_id
    )
    
    system_class = LucClass(**dict(class_infos))
    
    db.session.add(system_class)


def insert_classes(system_id: str, classes_files_json: dict):
    """Create classes for a given classification system.

    :param classes_files_json: classes file
    :type classes_files_json: dict
    :param system_id: classification system identifier
    :type system_id: string
    """
    system = classification_system(system_id)
    
    if system is None:
        abort(400, f'Error to add new class Classification System {system_id} not exist')
    
    for classes in classes_files_json:
        with db.session.begin_nested():
            insert_class(system_id, **classes)
    db.session.commit()
    
    classes = db.session.query(LucClass).filter(LucClass.class_system_id == system_id).all()
    
    return ClassesSchema().dump(classes, many=True)


def insert_file(style_format_id, system_id, file):
    """Insert File method.

    :param style_format_id: identification of style format.
    :type style_format_id: int
    :param system_id: identification of classification system
    :type system_id: int
    :param file: Style File.
    :type file: binary
    """
    system = classification_system(system_id)
    
    style_format = db.session.query(StyleFormats) \
        .filter(StyleFormats.id == style_format_id) \
        .first_or_404()
    
    style_file = file.read()
    
    mime_type = get_mimetype(file.name)
    
    style = Styles(class_system_id=system_id,
                   style_format_id=style_format_id,
                   mime_type=mime_type,
                   style=style_file)
    
    db.session.add(style)
    db.session.commit()
    
    return


def update_file(style_format_id, system_id, file):
    """Update File style.

    :param style_format_id: identification of style format.
    :type style_format_id: int
    :param system_id: identification of classification system
    :type system_id: int
    :param file: Style File.
    :type file: binary
    """
    
    style = Styles.query(Styles) \
        .filter(Styles.class_system_id == system_id, Styles.style_format_id == style_format_id) \
        .first_or_404()
    
    with db.session.begin_nested():
        style.style = file
    
    db.session.commit()
    
    return


def delete_file(style_format_id, system_id):
    """Delete a style from a classification system."""
    style_to_delete = db.session.query(Styles).filter(Styles.style_format_id == style_format_id,
                                                      Styles.class_system_id == system_id).first_or_404()
    with db.session.begin_nested():
        db.session.delete(style_to_delete)
    
    db.session.commit()


def insert_mapping(system_id_source, system_id_target, target_id, source_id, description, degree_of_similarity):
    """Insert mapping."""
    source_class = db.session.query(LucClass). \
        filter_by(id=source_id, class_system_id=system_id_source) \
        .first_or_404()
    
    target_class = db.session.query(LucClass) \
        .filter_by(id=target_id, class_system_id=system_id_target) \
        .first_or_404()
    
    mapping_infos = dict(
        source_class_id=source_id,
        target_class_id=target_id,
        description=description,
        degree_of_similarity=degree_of_similarity
    )
    
    mapping = ClassMapping(**dict(mapping_infos))
    
    db.session.add(mapping)


def insert_mappings(system_id_source, system_id_target, mapping_file: dict):
    """Create classes for a given classification system.

    :param system_id_source: Source Classification System
    :type system_id_source: string
    :param system_id_target: Target Classification System
    :type system_id_target: string
    :param mapping_file: Json File with mappings
    :type mapping_file: json
    """
    
    for mapping in mapping_file:
        with db.session.begin_nested():
            insert_mapping(system_id_source, system_id_target, **mapping)
        db.session.commit()
    
    mappings = get_mapping(system_id_source, system_id_target)
    
    return ClassesMappingSchema().dump(mappings, many=True)


def update_mapping(system_id_source, system_id_target, target_id, source_id, description, degree_of_similarity):
    source_class = db.session.query(LucClass). \
        filter_by(id=source_id, class_system_id=system_id_source) \
        .first_or_404()
    
    target_class = db.session.query(LucClass) \
        .filter_by(id=target_id, class_system_id=system_id_target) \
        .first_or_404()
    
    mapping = db.session.query(ClassMapping) \
        .filter(ClassMapping.source_class_id == source_id, ClassMapping.target_class_id == target_id) \
        .first_or_404()
    
    #TODO ver se o novo target deve ser passado
    with db.session.begin_nested():
        if description:
            mapping.description = description
        if degree_of_similarity:
            mapping.degree_of_similarity = degree_of_similarity

    db.session.commit()


def update_mappings(system_id_source, system_id_target, classes_files_json: dict):
    """Update mappings.

    :param system_id_source: Source Classification System
    :type system_id_source: string
    :param system_id_target: Target Classification System
    :type system_id_target: string
    :param classes_files_json: Json File with mappings
    :type classes_files_json: json
    """
    system_source = verify_class_system_exist(system_id_source)
    system_target = verify_class_system_exist(system_id_target)
    
    with db.session.begin_nested():
        
        for classes in classes_files_json:
            class_source = None
            class_target = None
            
            class_source = LucClass.get(name=classes["class_source"], class_system_id=system_source.id)
            class_target = LucClass.get(name=classes["class_target"]["old"], class_system_id=system_target.id)
            
            mapping = ClassMapping.query.filter_by(source_class_id=class_source.id, target_class_id=class_target.id)
            
            if "new" in classes["class_target"]:
                class_target = LucClass.get(name=classes["class_target"]["new"], class_system_id=system_target.id)
                
                mapping.target_class_id = class_target.id
            
            if "degree_of_similarity" in classes:
                mapping.description = classes["description"]
            
            if "degree_of_similarity" in classes:
                mapping.description = classes["description"]
    
    db.session.commit()


def delete_mappings(system_id_source, system_id_target):
    """Delete classification system mappings."""
    mappings = get_system_mapping(system_id_source, system_id_target)
    
    with db.session.begin_nested():
        for m in mappings:
            db.session.delete(m)
    
    db.session.commit()
    
    return
