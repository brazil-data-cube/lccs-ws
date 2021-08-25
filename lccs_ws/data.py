#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020-2021 INPE.
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
from sqlalchemy import and_, distinct

from .forms import (ClassesMappingSchema, ClassesSchema,
                    ClassificationSystemSchema, StyleFormatsSchema)

from sqlalchemy.util._collections import _LW
from sqlalchemy.orm.util import aliased
from typing import Callable, Iterator, Union, Optional, List, Dict, Tuple


def _get_classification_system(system_id_or_identifier: str):
    """Return the classification system matching search criteria."""
    # columns = [
    #     LucClassificationSystem.id,
    #     LucClassificationSystem.name,
    #     LucClassificationSystem.title.label("title"),
    #     LucClassificationSystem.version,
    #     LucClassificationSystem.identifier,
    #     LucClassificationSystem.authority_name,
    #     LucClassificationSystem.description.label("description"),
    #     LucClassificationSystem.version_successor,
    #     LucClassificationSystem.version_predecessor
    # ]
    #
    # search_criteria = dict()
    #
    # try:
    #     system_id = int(system_id_or_identifier)
    #     search_criteria["id"] = system_id
    # except ValueError:
    #     search_criteria["identifier"] = system_id_or_identifier
    #
    # query = db.session.query(*columns).filter_by(**search_criteria).first_or_404()

    try:
        system_id = int(system_id_or_identifier)
        where = [LucClassificationSystem.id == system_id]
    except ValueError:
        where = [LucClassificationSystem.identifier == system_id_or_identifier]

    system = db.session.query(LucClassificationSystem).filter(*where).first_or_404()

    return system


def get_classification_systems() -> List[dict]:
    """Retrieve all classification systems available in service."""
    system = db.session.query(LucClassificationSystem.id, LucClassificationSystem.identifier).all()
    return ClassificationSystemSchema().dump(system, many=True)


def get_classification_system(system_id_or_identifier: str) -> Dict:
    """Retrieve information for a given classification system.

    :param system_id_or_identifier: The id or identifier of a classification system
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)
    return ClassificationSystemSchema(only=("id", "name", "version", "title", "authority_name", "description",
                                            "version_predecessor", "version_successor")).dump(system)


def get_classification_system_classes(system_id_or_identifier: str) -> Tuple[int, list]:
    """Retrieve a list of classes for a given classification system.

    :param system_id_or_identifier: The id or identifier of a classification system
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)

    columns = [
        LucClass.id,
        LucClass.name,
        LucClass.title.label("title"),
        LucClass.code,
        LucClass.description.label("description"),
        LucClass.class_parent_id,
        # LucClassificationSystem.classification_system_id,
    ]

    classes = db.session.query(*columns) \
        .join(LucClassificationSystem, LucClass.classification_system_id == LucClassificationSystem.id) \
        .filter(LucClassificationSystem.id == system.id) \
        .all()
    
    return system.id, ClassesSchema().dump(classes, many=True)


def get_classification_system_class(system_id_or_identifier: str, class_id_or_name: str) -> Tuple[int, dict]:
    """Retrieve information for a given class.

    :param system_id_or_identifier: The id or identifier of a classification system
    :type system_id_or_identifier: string
    :param class_id_or_name: The id or name of a class
    :type class_id_or_name: string
    """
    system = _get_classification_system(system_id_or_identifier)

    columns = [
        LucClass.id,
        LucClass.name,
        LucClass.title.label("title"),
        LucClass.code,
        LucClass.description.label("description"),
        LucClass.class_parent_id
    ]

    where = [
        LucClassificationSystem.id == system.id,
    ]

    try:
        class_id = int(class_id_or_name)
        where.append(LucClass.id == class_id)
    except ValueError:
        where.append(LucClass.name == class_id_or_name)
    
    class_info = db.session.query(*columns) \
        .join(LucClassificationSystem, LucClass.classification_system_id == LucClassificationSystem.id) \
        .filter(*where) \
        .first_or_404()
    
    return system.id, ClassesSchema().dump(class_info)


def get_style_formats() -> List[dict]:
    """Retrieve all styles formats available in service."""
    style_formats = db.session.query(StyleFormats).all()
    
    return StyleFormatsSchema().dump(style_formats, many=True)


def get_style_format(style_format_id_or_name) -> dict:
    """Retrieve information for a style format.

    :param style_format_id_or_name: The id or name of a style format
    :type style_format_id_or_name: string
    """
    try:
        style_f_id = int(style_format_id_or_name)
        where = [StyleFormats.id == style_f_id]
    except ValueError:
        where = [StyleFormats.name == style_format_id_or_name]

    style_format = db.session.query(StyleFormats).filter(*where).first_or_404()
    
    return StyleFormatsSchema().dump(style_format)


def get_system_style_format(system_id_or_identifier) -> Tuple[int, List[int]]:
    """Return the styles formats available for a classification system.
    
    :param system_id_or_identifier: The id or identifier of a classification system
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)
    style_formats_id = db.session.query(Styles.style_format_id) \
        .filter(Styles.classification_system_id == system.id) \
        .all()
    return system.id, style_formats_id


def get_classification_system_style(system_id, style_format_id):
    """Return the style of a classification system.

    :param system_id: identifier of a specific classification system
    :type system_id: int
    :param style_format_id: identifier of a specific of Style Format
    :type style_format_id: int
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


def get_mappings(system_id_or_identifier: str) -> [LucClassificationSystem, list]:
    """Return available mapping for a classification system.

    :param system_id_or_identifier: identification of a source classification system
    :type system_id_or_identifier: int
    """
    system = _get_classification_system(system_id_or_identifier)

    classes_source = db.session.query(LucClass.id) \
        .filter(LucClass.classification_system_id == system.id) \
        .all()
    
    targets_class_id = db.session.query(distinct(ClassMapping.target_class_id)) \
        .filter(ClassMapping.source_class_id.in_(classes_source)) \
        .all()

    systems = db.session.query(LucClassificationSystem) \
        .join(LucClass, LucClass.classification_system_id == LucClassificationSystem.id) \
        .filter(LucClass.id.in_(targets_class_id)) \
        .all()

    return system, systems


def get_system_mapping(system_id_source: int, system_id_target: int):
    """Return a Mapping.

    :param system_id_source: identification of a source classification system
    :type system_id_source: int
    :param system_id_target: identification of a target classification system
    :type system_id_target: int
    """
    classes_source = db.session.query(LucClass.id) \
        .filter(LucClass.classification_system_id == system_id_source) \
        .all()
    
    classes_target = db.session.query(LucClass.id) \
        .filter(LucClass.classification_system_id == system_id_target) \
        .all()

    source_alias = aliased(LucClass)

    mappings = db.session.query(
        ClassMapping.source_class_id,
        ClassMapping.target_class_id,
        ClassMapping.description,
        ClassMapping.degree_of_similarity,
        source_alias.name.label('source_class_name'),
        source_alias.title.label('source_class_title'),
        LucClass.name.label('target_class_name'),
        LucClass.title.label('target_class_title'),
    ).filter(
            and_(ClassMapping.source_class_id.in_(classes_source), ClassMapping.target_class_id.in_(classes_target)),
            ClassMapping.source_class_id == source_alias.id,
            ClassMapping.target_class_id == LucClass.id
    ).all()
    
    return mappings


def get_mapping(system_id_or_identifier_source: str, system_id_or_identifier_target: str) -> [int, int, list]:
    """Return the classes mapping between the classification system.
    
    :param system_id_or_identifier_source: id or identifier of a source classification system
    :type system_id_or_identifier_source: str
    :param system_id_or_identifier_target: id or identifier of a target classification system
    :type system_id_or_identifier_target: str
    """
    system_source = _get_classification_system(system_id_or_identifier_source)
    system_target = _get_classification_system(system_id_or_identifier_target)

    mappings = get_system_mapping(system_source.id, system_target.id)

    return system_source.id, system_target.id, ClassesMappingSchema().dump(mappings, many=True)


def classification_system(system_id):
    """Verify if classification system exist in server.

    :param system_id: identifier of classification system
    :type system_id: integer
    """
    return LucClassificationSystem.query.filter_by(id=system_id).first_or_404()


def create_classification_system(name, authority_name, version, title, description=None) -> dict:
    """Create a full classification system.

    :param name: Classification system name
    :type name: string
    :param authority_name: Classification system authority name
    :type authority_name: string
    :param version: Classification system version
    :type version: string
    :param description: Classification system description
    :type description: string
    :title the classification system title
    :type title: string
    """
    system = db.session.query(LucClassificationSystem)\
        .filter(LucClassificationSystem.identifier == f'{name}-{version}')\
        .first()

    if system:
        abort(400, 'Classification System already registered!')

    classification_system_info = dict(name=name,
                                      authority_name=authority_name,
                                      version=version,
                                      title_translations=title,
                                      description_translations=description)

    with db.session.begin_nested():
        system = LucClassificationSystem(**dict(classification_system_info))
        
        db.session.add(system)
    
    db.session.commit()

    return ClassificationSystemSchema(only=("id", "name", "version", "title", "authority_name", "description",
                                            "version_predecessor", "version_successor")).dump(system)


def delete_classification_system(system_id_or_identifier):
    """Delete an classification system by a identifier.

    :param system_id_or_identifier: The id or identifier of a classification system to be deleted
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)

    db.session.delete(system)

    db.session.commit()


def update_classification_system(system_id_or_identifier, obj: dict) -> dict:
    """Update an classification system by a given name.

    :param system_id_or_identifier: Classification System identifier.
    :type system_id_or_identifier: string
    :param obj: Object with classification system information to update
    :type obj: dict
    """
    system = _get_classification_system(system_id_or_identifier)

    if 'title' in obj:
        obj['title_translations'] = obj.pop('title')

    if 'description' in obj:
        obj['description_translations'] = obj.pop('description')

    with db.session.begin_nested():
        for attr in obj.keys():
            setattr(system, attr, obj.get(attr))

    db.session.commit()

    return ClassificationSystemSchema(only=("id", "name", "version", "title", "authority_name", "description",
                                            "version_predecessor", "version_successor")).dump(system)


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


def update_class(system_id: int, class_id: int, obj: dict):
    """Update an classification system by a given name."""
    system_class = LucClass.query.filter_by(id=class_id, class_system_id=system_id).first_or_404()
    
    with db.session.begin_nested():
        for attr in obj.keys():
            setattr(system_class, attr, obj.get(attr))
    
    db.session.commit()
    
    return system_class


def insert_class(system_id: int, name, code, title, description, class_parent_id=None) -> int:
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
    system_class = db.session.query(LucClass).filter_by(classification_system_id=system_id, name=name).first()
    
    if system_class:
        abort(409, f'Class already {name} registered in the system!')
    
    class_infos = dict(
        name=name,
        code=code,
        title_translations=title,
        description_translations=description,
        classification_system_id=system_id,
        class_parent_id=class_parent_id
    )

    system_class = LucClass(**dict(class_infos))
    
    db.session.add(system_class)

    return system_class.id


def insert_classes(system_id_or_identifier: str, classes_files_json: dict):
    """Create classes for a given classification system.

    :param classes_files_json: classes file
    :type classes_files_json: dict
    :param system_id_or_identifier: The id or identifier of classification system
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)
    
    if system is None:
        abort(400, f'Error to add new class Classification System {system_id_or_identifier} not exist')

    for system_class in classes_files_json:
        _add_classes(system.id, system_class)

    classes = db.session.query(LucClass).filter(LucClass.class_system_id == system.id).all()
    
    return classes


def _add_classes(system_id, classes, class_parent_id=None):
    """Add class to a classification system."""
    if class_parent_id:
        classes['class_parent_id'] = class_parent_id

    with db.session.begin_nested():
        class_id = insert_class(system_id, **classes)

    db.session.commit()

    if classes.get('children') is not None:
        for child in classes['children']:
            _add_classes(system_id, child, class_parent_id=class_id)
    return


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
    
    mime_type = get_mimetype(file.filename)
    
    style = Styles(class_system_id=system_id,
                   style_format_id=style_format_id,
                   mime_type=mime_type,
                   style=style_file)
    
    db.session.add(style)
    db.session.commit()
    
    return style


def update_file(style_format_id, system_id, file):
    """Update File style.
    
    :param style_format_id: identification of style format
    :type style_format_id: int
    :param system_id: identification of classification system
    :type system_id: int
    :param file: Style File
    :type file: binary
    """
    style = db.session.query(Styles) \
        .filter(Styles.class_system_id == system_id,
                Styles.style_format_id == style_format_id) \
        .first_or_404()
    
    style_file = file.read()
    
    mime_type = get_mimetype(file.filename)
    
    with db.session.begin_nested():
        style.style = style_file
        style.mime_type = mime_type
    
    db.session.commit()
    
    return


def delete_file(style_format_id, system_id):
    """Delete a style from a classification system."""
    style_to_delete = db.session.query(Styles).filter(Styles.style_format_id == style_format_id,
                                                      Styles.class_system_id == system_id).first_or_404()
    with db.session.begin_nested():
        db.session.delete(style_to_delete)
    
    db.session.commit()


def insert_mapping(system_id_source, system_id_target, target_class_id, source_class_id, description,
                   degree_of_similarity):
    """Insert mapping."""
    source_class = db.session.query(LucClass). \
        filter_by(id=source_class_id, class_system_id=system_id_source) \
        .first_or_404()
    
    target_class = db.session.query(LucClass) \
        .filter_by(id=target_class_id, class_system_id=system_id_target) \
        .first_or_404()
    
    mapping_infos = dict(
        source_class_id=source_class_id,
        target_class_id=target_class_id,
        description=description,
        degree_of_similarity=degree_of_similarity
    )
    
    mapping = ClassMapping(**dict(mapping_infos))
    
    db.session.add(mapping)


def insert_mappings(system_id_source, system_id_target, mapping_file: dict):
    """Create classes for a given classification system.

    :param system_id_source: identifier of a source classification system
    :type system_id_source: integer
    :param system_id_target: identifier of a target classification system
    :type system_id_target: string
    :param mapping_file: json file with mappings
    :type mapping_file: json
    """
    for mapping in mapping_file:
        with db.session.begin_nested():
            insert_mapping(system_id_source, system_id_target, **mapping)
        db.session.commit()
    
    mappings = get_mapping(system_id_source, system_id_target)
    
    return mappings


def update_mapping(system_id_source, system_id_target, target_class_id, source_class_id, description=None,
                   degree_of_similarity=None):
    """Update a exist mapping.
    
    :param system_id_source: identifier of a source classification system
    :type system_id_source: integer
    :param system_id_target: identifier of a target classification system
    :type system_id_target: string
    :param target_class_id: identifier of a target class
    :type target_class_id: integer
    :param source_class_id: identifier of a source class
    :type source_class_id: integer
    :param description: the mapping description
    :type description: string
    :param degree_of_similarity: the degree_of_similarity of a mapping
    :type degree_of_similarity: float
    """
    source_class = db.session.query(LucClass) \
        .filter_by(id=source_class_id, class_system_id=system_id_source) \
        .first_or_404()
    
    target_class = db.session.query(LucClass) \
        .filter_by(id=target_class_id, class_system_id=system_id_target) \
        .first_or_404()
    
    mapping = db.session.query(ClassMapping) \
        .filter(ClassMapping.source_class_id == source_class_id, ClassMapping.target_class_id == target_class_id) \
        .first_or_404()
    
    with db.session.begin_nested():
        if description:
            mapping.description = description
        if degree_of_similarity:
            mapping.degree_of_similarity = degree_of_similarity
    
    db.session.commit()


def update_mappings(system_id_source, system_id_target, mappings):
    """Update mappings.

    :param system_id_source: Source Classification System
    :type system_id_source: string
    :param system_id_target: Target Classification System
    :type system_id_target: string
    :param mappings: mappings to update
    :type mappings: json
    """
    for mapping in mappings:
        update_mapping(system_id_source, system_id_target, **mapping)
    
    mappings = get_mapping(system_id_source, system_id_target)
    
    return mappings


def delete_mappings(system_id_source, system_id_target):
    """Delete classification system mappings."""
    mappings = get_system_mapping(system_id_source, system_id_target)
    
    if mappings is None:
        abort(400, f'Error to delete mapping')
    
    with db.session.begin_nested():
        for m in mappings:
            db.session.delete(m)
    
    db.session.commit()
    
    return


def create_style_format(name: str):
    """Create style format.

    :param name: name for a new style format
    :type name: string
    """
    style_format = db.session.query(StyleFormats). \
        filter_by(name=name) \
        .first()
    
    if style_format is not None:
        abort(400, f'Error to add new class style format {name} already exist')
    
    with db.session.begin_nested():
        style_format = StyleFormats(name=name)
        
        db.session.add(style_format)
    
    db.session.commit()
    
    return style_format


def delete_style_format(style_format_id):
    """Delete an style format a identifier.

    :param style_format_id: identifier of a style format to be deleted
    :type style_format_id: integer
    """
    style_format = db.session.query(StyleFormats) \
        .filter_by(id=style_format_id) \
        .first_or_404()
    
    db.session.delete(style_format)
    db.session.commit()


def update_style_format(style_format_id, name):
    """Update an style format.

    :param style_format_id: identifier of style format.
    :type style_format_id: integer
    :param name: name of style format for update.
    :type name: string
    """
    style_format = db.session.query(StyleFormats) \
        .filter_by(id=style_format_id) \
        .first_or_404()
    
    with db.session.begin_nested():
        style_format.name = name
    
    db.session.commit()
    
    return style_format


def get_identifier_system(system_name, system_version):
    """Return the identifier of classification system and classes.
    
    :param system_name: name of a classification system
    :type system_name: string
    :param system_version: version of a classification system
    :type system_version: string
    """
    system = db.session.query(LucClassificationSystem) \
        .filter(LucClassificationSystem.name == system_name, LucClassificationSystem.version == system_version) \
        .first_or_404()
    
    return system


def get_identifier_style_format(style_format_name):
    """Return the identifier of style format.
    
    :param style_format_name: name of a style format
    :type style_format_name: string
    """
    style = db.session.query(StyleFormats)\
        .filter_by(name=style_format_name)\
        .first_or_404()
    
    return style
