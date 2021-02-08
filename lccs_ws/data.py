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
from sqlalchemy.orm import aliased
from sqlalchemy import and_

from .config import Config
from .forms import ClassificationSystemSchema, ClassesSchema, StyleFormatsSchema, StyleSchema


def get_classification_systems(system_id=None):
    """Retrieve information for a given classification system."""
    if system_id:
        system = db.session.query(LucClassificationSystem) \
            .filter(LucClassificationSystem.id == system_id).first()
        return ClassificationSystemSchema().dump(system)

    system = db.session.query(LucClassificationSystem).all()
    
    return ClassificationSystemSchema().dump(system, many=True)


def get_classification_system_classes(system_id, class_id=None):
    """Retrieve a list of classes for a given classification system.

    :param system_id: classification system identifier
    :type system_id: str
    :return: list of classes
    :rtype: list
    """
    if class_id:
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

    classes = db.session.query(LucClass) \
        .join(LucClassificationSystem, LucClass.class_system_id == LucClassificationSystem.id) \
        .filter(LucClassificationSystem.id == system_id) \
        .all()

    return ClassesSchema().dump(classes, many=True)


def get_style_formats(style_format_id=None, system_id=None):
    """Return the styles formats available."""
    if style_format_id:
        style_format = db.session.query(StyleFormats).\
            filter(StyleFormats.id == style_format_id).first()

        return StyleFormatsSchema().dump(style_format)

    if system_id:
        style_formats_id = db.session.query(Styles.style_format_id)\
            .filter(Styles.class_system_id == system_id)\
            .all()
        return style_formats_id

    style_formats = db.session.query(StyleFormats.id).all()

    return StyleFormatsSchema().dump(style_formats, many=True)


def get_classification_system_style(system_id, style_format_id: None):
    """Get Styles.

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

    style_file = db.session.query(*columns)\
        .join(StyleFormats, StyleFormats.id == Styles.style_format_id)\
        .filter(*where) \
        .first()

    return style_file


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


def get_available_mappings(system_id):
    """Return available mapping for a given classification system.

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
    classification_system = LucClassificationSystem.filter(name=name, version=version)
    if classification_system:
        abort(409, 'Classification System already registered!')
    
    classification_system_infos = dict(name=name, authority_name=authority_name, version=version,
                                       description=description)
    
    with db.session.begin_nested():
        classification_system = LucClassificationSystem(**dict(classification_system_infos))
        
        db.session.add(classification_system)
    
    db.session.commit()
    
    return classification_system


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


def delete_classes(class_system):
    """Delete all class by a given classification system."""
    classes = LucClass.filter(class_system_id=class_system.id)
    
    with db.session.begin_nested():
        for c in classes:
            db.session.delete(c)
    db.session.commit()


def delete_one_classe(class_system, class_id):
    """Delete an class by a given name and classification system."""
    class_to_delete = LucClass.get(class_system_id=class_system.id, name=class_id)
    
    with db.session.begin_nested():
        db.session.delete(class_to_delete)
    
    db.session.commit()


def update_class(classification_system: int, class_info: dict):
    """Update an classification system by a given name."""
    for classe_name, class_info in class_info.items():
        
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
    classification_system = LucClassificationSystem.query.filter_by(name=system_id).first_or_404()
    
    with db.session.begin_nested():
        if name:
            classification_system.name = name
        if description:
            classification_system.description = description
        if authority_name:
            classification_system.authority_name = authority_name
        if version:
            classification_system.version = version
    
    db.session.commit()
    
    return classification_system


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


def insert_classes(classes_files_json: dict, system_id: str):
    """Create classes for a given classification system.

    :param classes_files_json: classes file
    :type classes_files_json: dict
    :param system_id: classification system identifier
    :type system_id: string
    """
    class_system = verify_class_system_exist(system_id)
    
    if class_system is None:
        abort(400, f'Error to add new class Classification System {system_id} not exist')
    
    for classes in classes_files_json["classes"]:
        insert_class(class_system.id, classes)
    
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
    
    try:
        style = Styles(class_system_id=system.id,
                       style_format_id=style_format.id,
                       style=style_file)
        
        style.save()
    except Exception as e:
        abort(500, f'Error while insert style: {e}')


def delete_file(style_format_id, system_id):
    """Delete a style from a classification system."""
    try:
        style_format = StyleFormats.get(name=style_format_id)
        system = LucClassificationSystem.get(name=system_id)
        style = Styles.get(class_system_id=system.id,
                           style_format_id=style_format.id)
        
        file = json.loads(style.style)
        
        style.delete()
        
        os.remove(os.path.join(Config.LCCS_UPLOAD_FOLDER, file["filename"]))
    
    except Exception as e:
        raise e


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
    
    try:
        for classes in classes_files_json:
            mapping = None
            class_source = LucClass.get(name=classes["class_source"], class_system_id=system_source.id)
            class_target = LucClass.get(name=classes["class_target"], class_system_id=system_target.id)
            
            mapping = ClassMapping(source_class_id=class_source.id, target_class_id=class_target.id,
                                   description=classes["description"],
                                   degree_of_similarity=classes["degree_of_similarity"])
            
            mapping.save(commit=False)
            db.session.flush()
        
        db.session.commit()
    except Exception as e:
        raise e


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
    
    with db.session.begin_nested():
        for m in mappings:
            db.session.delete(m)
    
    db.session.commit()
    
    return
