#
# This file is part of LCCS-WS.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#
"""Data module of Land Cover Classification System Web Service."""

import json
from io import BytesIO
from typing import Dict, List, Tuple, Union

from flask import abort
from lccs_db.models import (ClassMapping, LucClass, LucClassificationSystem,
                            StyleFormats, Styles, db)
from lccs_db.utils import get_extension, get_mimetype
from sqlalchemy import and_, distinct
from sqlalchemy.orm.util import aliased
from werkzeug.datastructures import FileStorage

from .forms import (ClassesMappingSchema, ClassesSchema,
                    ClassificationSystemSchema, StyleFormatsSchema)


def _get_classification_system(system_id_or_identifier: str) -> LucClassificationSystem:
    """Return the classification system matching search criteria.

    :param system_id_or_identifier: The id or identifier of a classification system
    :type system_id_or_identifier: string
    """
    try:
        system_id = int(system_id_or_identifier)
        where = [LucClassificationSystem.id == system_id]
    except ValueError:
        where = [LucClassificationSystem.identifier == system_id_or_identifier]

    system = db.session.query(LucClassificationSystem).filter(*where).first_or_404()

    return system


def _get_style_format(style_format_id_or_name: str) -> StyleFormats:
    """Return the style format matching search criteria.

    :param style_format_id_or_name: The id or identifier of a classification system
    :type style_format_id_or_name: string
    """
    try:
        style_format_id = int(style_format_id_or_name)
        where = [StyleFormats.id == style_format_id]
    except ValueError:
        where = [StyleFormats.name == style_format_id_or_name]

    style = db.session.query(StyleFormats).filter(*where).first_or_404()

    return style


def get_classification_systems() -> List[dict]:
    """Retrieve all classification systems available in service."""
    system = db.session.query(LucClassificationSystem.id,
                              LucClassificationSystem.identifier,
                              LucClassificationSystem.title.label("title"),
                              LucClassificationSystem.name,
                              LucClassificationSystem.authority_name,
                              LucClassificationSystem.version,
                              LucClassificationSystem.description.label("description"),
                              LucClassificationSystem.version_successor,
                              LucClassificationSystem.version_predecessor
                              ).all()
    return ClassificationSystemSchema().dump(system, many=True)


def get_classification_system(system_id_or_identifier: str) -> Dict:
    """Retrieve information for a given classification system.

    :param system_id_or_identifier: The id or identifier of a classification system
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)
    return ClassificationSystemSchema(only=("id", "name", "version", "title", "authority_name", "description",
                                            "version_predecessor", "identifier", "version_successor")).dump(system)


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


def get_classification_system_style(system_id_or_identifier: str, style_format_id_or_name: str) -> Union[str, BytesIO]:
    """Return the style of a classification system.

    :param system_id_or_identifier: The id or identifier of a specific classification system
    :type system_id_or_identifier: string
    :param style_format_id_or_name: The id or name of a specific of Style Format
    :type style_format_id_or_name: string
    """
    system = _get_classification_system(system_id_or_identifier)
    style_format = _get_style_format(style_format_id_or_name)

    columns = [
        Styles.style,
        Styles.mime_type
    ]
    
    where = [
        Styles.classification_system_id == system.id,
        and_(Styles.style_format_id == style_format.id),
    ]
    
    style_file = db.session.query(*columns) \
        .join(StyleFormats, StyleFormats.id == Styles.style_format_id) \
        .filter(*where) \
        .first()

    extension = get_extension(style_file.mime_type)

    file_name = f"{system.identifier}_{style_format.name}" + extension

    return file_name, BytesIO(style_file.style)


def get_mappings(system_id_or_identifier: str) -> Tuple[LucClassificationSystem, List]:
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


def get_system_mapping(system_id_source: int, system_id_target: int) -> ClassMapping:
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

    mappings = db.session.query(ClassMapping)\
        .filter(
            and_(ClassMapping.source_class_id.in_(classes_source), ClassMapping.target_class_id.in_(classes_target)),
            ClassMapping.source_class_id == source_alias.id,
            ClassMapping.target_class_id == LucClass.id
    ).all()

    return mappings


def get_mapping(system_id_or_identifier_source: str, system_id_or_identifier_target: str) -> Tuple[int, int, list]:
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


def create_classification_system(name: str, authority_name: str, version: str, title: dict, description: dict) -> dict:
    """Create a full classification system.

    :param name: Classification system name
    :type name: string
    :param authority_name: The authority name of Classification system
    :type authority_name: string
    :param version: The Classification system version
    :type version: string
    :param title: The Classification system title
    :type title: string
    :param description: The Classification system description
    :type description: string
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


def delete_classification_system(system_id_or_identifier: str) -> None:
    """Delete an classification system by a identifier.

    :param system_id_or_identifier: The id or identifier of a classification system to be deleted
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)

    with db.session.begin_nested():
        db.session.delete(system)

    db.session.commit()


def update_classification_system(system_id_or_identifier: str, obj: dict) -> dict:
    """Update an classification system by a given name.

    :param system_id_or_identifier: The id or identifier of Classification System.
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


def delete_classes(system_id_or_identifier: str) -> None:
    """Delete all class by a given classification system.

    :param system_id_or_identifier: The id or identifier of Classification System.
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)
    classes = db.session.query(LucClass).filter(LucClass.classification_system_id == system.id)

    with db.session.begin_nested():
        for c in classes:
            db.session.delete(c)
    db.session.commit()


def delete_class(system_id_or_identifier: str, class_id_or_identifier: str):
    """Delete an class by a given name and classification system."""
    system = _get_classification_system(system_id_or_identifier)

    where = [LucClass.classification_system_id == system.id]

    try:
        class_id = int(class_id_or_identifier)
        where += [LucClass.id == class_id]
    except ValueError:
        where += [LucClass.name == class_id_or_identifier]

    class_to_delete = db.session.query(LucClass)\
        .filter(*where)\
        .first_or_404()
    
    with db.session.begin_nested():
        db.session.delete(class_to_delete)
    
    db.session.commit()


def update_class(system_id_or_identifier: int, class_id_or_identifier: int, obj: dict) -> dict:
    """Update an classification system by a given name."""
    system = _get_classification_system(system_id_or_identifier)

    where = [LucClass.classification_system_id == system.id]

    try:
        class_id = int(class_id_or_identifier)
        where += [LucClass.id == class_id]
    except ValueError:
        where += [LucClass.name == class_id_or_identifier]

    system_class = db.session.query(LucClass)\
        .filter(*where)\
        .first_or_404()

    if 'title' in obj:
        obj['title_translations'] = obj.pop('title')

    if 'description' in obj:
        obj['description_translations'] = obj.pop('description')
    
    with db.session.begin_nested():
        for attr in obj.keys():
            setattr(system_class, attr, obj.get(attr))
    
    db.session.commit()

    return ClassesSchema(only=("id", "name", "title", "code", "class_parent_id",)).dump(system_class)


def insert_class(system_id: int, name: str, code: str,
                 title: dict, description: dict, class_parent_id: str = None) -> int:
    """Create a new class.

    :param system_id: identifier of classification system.
    :type system_id: int

    :param name: name of a class.
    :type name: string

    :param code: class code.
    :type code: string

    :param title: class title.
    :type title: string

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
    db.session.flush()

    return system_class.id


def insert_classes(system_id_or_identifier: str, classes_files_json: dict) -> List:
    """Create classes for a given classification system.

    :param classes_files_json: classes file
    :type classes_files_json: dict

    :param system_id_or_identifier: The id or identifier of classification system
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)
    
    if system is None:
        abort(400, f'Error to add new class Classification System {system_id_or_identifier} not exist')

    with db.session.begin_nested():
        for system_class in classes_files_json:
            _add_classes(system.id, system_class)

    db.session.commit()

    classes = db.session.query(LucClass.id,
                               LucClass.name,
                               LucClass.title.label('title'),
                               LucClass.description.label('description'),
                               LucClass.code,
                               LucClass.classification_system_id,
                               LucClass.class_parent_id)\
        .filter(LucClass.classification_system_id == system.id)\
        .all()
    
    return classes


def _add_classes(system_id: int, classes: dict):
    """Add class to a classification system."""
    class_id = insert_class(system_id, **classes)

    if classes.get('children') is not None:
        for child in classes['children']:
            child["class_parent_id"] = class_id
            _add_classes(system_id, child)
    return


def insert_file(system_id_or_identifier: str, style_format_id_or_name: str, file: FileStorage) -> Union[int, int]:
    """Insert File method.

    :param style_format_id_or_name: The ir or name of style format.
    :type style_format_id_or_name: string
    :param system_id_or_identifier: The id or name of classification system
    :type system_id_or_identifier: string
    :param file: Style File.
    :type file: binary
    """
    system = _get_classification_system(system_id_or_identifier)
    style_format = _get_style_format(style_format_id_or_name)

    style_file = file.read()
    mime_type = get_mimetype(file.filename)

    with db.session.begin_nested():
        style = Styles(classification_system_id=system.id,
                       style_format_id=style_format.id,
                       mime_type=mime_type,
                       style=style_file)

        db.session.add(style)
    db.session.commit()
    
    return system.id, style_format.id


def update_file(style_format_id_or_name: str, system_id_or_identifier: str, file: FileStorage) -> Union[int, int]:
    """Update File style.
    
    :param style_format_id_or_name: The id or name of style format
    :type style_format_id_or_name: string
    :param system_id_or_identifier: The id or identification of classification system
    :type system_id_or_identifier: string
    :param file: Style File
    :type file: binary
    """
    system = _get_classification_system(system_id_or_identifier)
    style_format = _get_style_format(style_format_id_or_name)

    style = db.session.query(Styles) \
        .filter(Styles.classification_system_id == system.id,
                Styles.style_format_id == style_format.id) \
        .first_or_404()
    
    style_file = file.read()
    
    mime_type = get_mimetype(file.filename)
    
    with db.session.begin_nested():
        style.style = style_file
        style.mime_type = mime_type
    
    db.session.commit()
    
    return system.id, style_format.id


def delete_file(style_format_id_or_name: str, system_id_or_identifier: str) -> None:
    """Delete a style from a classification system.

    :param style_format_id_or_name: The id or name of style format
    :type style_format_id_or_name: string
    :param system_id_or_identifier: The id or identification of classification system
    :type system_id_or_identifier: string
    """
    system = _get_classification_system(system_id_or_identifier)
    style_format = _get_style_format(style_format_id_or_name)

    style = db.session.query(Styles) \
        .filter(Styles.classification_system_id == system.id,
                Styles.style_format_id == style_format.id) \
        .first_or_404()

    with db.session.begin_nested():
        db.session.delete(style)
    
    db.session.commit()


def insert_mapping(system_id_source: int, system_id_target: int, target_class: str, source_class: str, description,
                   degree_of_similarity) -> None:
    """Insert mapping."""
    target_class_alias = aliased(LucClass)

    try:
        class_id_source = int(source_class)
        class_id_target = int(target_class)
        where = [target_class_alias.id == class_id_target,
                 LucClass.id == class_id_source]
    except ValueError:
        where = [target_class_alias.name == source_class,
                 LucClass.id == target_class]
    where.append(and_(LucClass.classification_system_id == system_id_source, target_class_alias.classification_system_id == system_id_target))

    class_mappings = db.session.query(LucClass, target_class_alias). \
        filter(*where) \
        .first_or_404()

    mapping_infos = dict(
        source_class_id=class_mappings[0].id,
        target_class_id=class_mappings[1].id,
        description=description,
        degree_of_similarity=degree_of_similarity
    )
    
    mapping = ClassMapping(**dict(mapping_infos))
    
    db.session.add(mapping)


def insert_mappings(system_id_or_identifier_source: str, system_id_or_identifier_target: str, mapping_file: dict) \
        -> List:
    """Create classes for a given classification system.

    :param system_id_or_identifier_source: identifier of a source classification system
    :type system_id_or_identifier_source: integer
    :param system_id_or_identifier_target: identifier of a target classification system
    :type system_id_or_identifier_target: string
    :param mapping_file: json file with mappings
    :type mapping_file: json
    """
    system_source = _get_classification_system(system_id_or_identifier_source)
    system_target = _get_classification_system(system_id_or_identifier_target)

    with db.session.begin_nested():
        for mapping in mapping_file:
            insert_mapping(system_source.id, system_target.id, **mapping)
    db.session.commit()
    
    _, _, mappings = get_mapping(system_source.id, system_target.id)

    return ClassesMappingSchema().dump(mappings, many=True)


def update_mapping(system_id_or_identifier_source: str, system_id_or_identifier_target: str, degree_of_similarity: float,
                   description: str, source_class: str, target_class: str) -> dict:
    """Update mappings.

    :param system_id_or_identifier_source: The id or identifier of Source Classification System
    :type system_id_or_identifier_source: string
    :param system_id_or_identifier_target: The id or identifier of  Target Classification System
    :type system_id_or_identifier_target: string
    :param degree_of_similarity: The degree of similarity in mapping
    :type degree_of_similarity: float
    :param description: The description of mapping
    :type description: string
    :param source_class: The id or identifier of source class
    :type source_class: string
    :param target_class: The id or identifier of target class
    :type target_class: string
    """
    system_source = _get_classification_system(system_id_or_identifier_source)
    system_target = _get_classification_system(system_id_or_identifier_target)

    where_source = [LucClass.classification_system_id == system_source.id]
    where_target = [LucClass.classification_system_id == system_target.id]

    if isinstance(source_class, int) and isinstance(target_class, int):
        where_source.append(LucClass.id == source_class)
        where_target.append(LucClass.id == target_class)

    else:
        where_source.append(LucClass.name == source_class)
        where_target.append(LucClass.name == target_class)

    classes_source = db.session.query(LucClass.id) \
        .filter(*where_source) \
        .first_or_404()

    classes_target = db.session.query(LucClass.id) \
        .filter(*where_target) \
        .first_or_404()

    source_alias = aliased(LucClass)

    mappings = db.session.query(
        ClassMapping
    ).filter(
        and_(ClassMapping.source_class_id.in_(classes_source), ClassMapping.target_class_id.in_(classes_target)),
        ClassMapping.source_class_id == source_alias.id,
        ClassMapping.target_class_id == LucClass.id
    ).first_or_404()

    with db.session.begin_nested():
        if description:
            mappings.description = description
        if degree_of_similarity:
            mappings.degree_of_similarity = degree_of_similarity

    db.session.commit()

    return ClassesMappingSchema().dump(mappings)


def delete_mappings(system_id_or_identifier_source: str, system_id_or_identifier_target: str):
    """Delete classification system mappings."""
    system_source = _get_classification_system(system_id_or_identifier_source)
    system_target = _get_classification_system(system_id_or_identifier_target)

    mappings = get_system_mapping(system_source.id, system_target.id)
    
    if mappings is None:
        abort(400, f'Error to delete mapping')
    
    with db.session.begin_nested():
        for m in mappings:
            db.session.delete(m)
    
    db.session.commit()
    
    return


def create_style_format(name: str) -> dict:
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
    
    return StyleFormatsSchema().dump(style_format)


def delete_style_format(style_format_id_or_name:str):
    """Delete an style format a identifier.

    :param style_format_id_or_name: The id or identifier of a style format to be deleted
    :type style_format_id_or_name: string
    """
    style = _get_style_format(style_format_id_or_name)

    with db.session.begin_nested():
        db.session.delete(style)
    db.session.commit()


def update_style_format(style_format_id_or_name: str, name: str) -> dict:
    """Update an style format.

    :param style_format_id_or_name: The name or identifier of style format.
    :type style_format_id_or_name: string
    :param name: name of style format for update.
    :type name: string
    """
    style_format = _get_style_format(style_format_id_or_name)

    with db.session.begin_nested():
        style_format.name = name
    
    db.session.commit()
    
    return StyleFormatsSchema().dump(style_format)


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
    
    return ClassificationSystemSchema().dump(system), 200


def get_identifier_style_format(style_format_name):
    """Return the identifier of style format.
    
    :param style_format_name: name of a style format
    :type style_format_name: string
    """
    style = db.session.query(StyleFormats)\
        .filter_by(name=style_format_name)\
        .first_or_404()
    
    return StyleFormatsSchema().dump(style)
