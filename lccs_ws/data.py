#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Data module of Land Cover Classification System Web Service."""
import json

from lccs_db.models import (ClassMapping, LucClass, LucClassificationSystem,
                            StyleFormats, Styles)
from lccs_db.models import db as _db

from .forms import ClassesSchema


def get_mappings(classes_source, classes_target):
    """Filter all mapping."""
    where = [ClassMapping.source_class_id.in_([value.id for value in classes_source])]

    if classes_target is not None:
        where += [ClassMapping.target_class_id.in_([value.id for value in classes_target])]

    return _db.session.query(ClassMapping).filter(*where).all()

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
        style = LucClassificationSystem.get(name=name)
        return style
    except:
        return None

def insert_classification_systems(classification_system: dict):
    """Create a full classification system."""
    class_system = LucClassificationSystem(name=classification_system['name'],
                                           description=classification_system['description'],
                                           authority_name=classification_system['authority_name'],
                                           version=classification_system['version'])

    class_system.save()

    try:
        if 'styles' in classification_system:

            styles = classification_system['styles']

            style_format = verify_style_format(styles['name'])

            if style_format is None:
                style_format = StyleFormats(name=styles['name'])
                style_format.save()

            json_file = json.dumps(styles['file'])

            style = Styles(class_system_id=class_system.id,
                           style_format_id=style_format.id,
                           style=json_file)

            style.save()

        return class_system

    except:
        class_system.delete()
        return None

def insert_class(classification_system: LucClassificationSystem, class_info: dict):
    """Create a new class."""
    name = class_info['name']
    code = class_info['code']
    description = None
    parent = None

    if 'description' in class_info:
        description = class_info['description']

    if 'parent' in class_info:
        parent =  class_info['parent']

    if parent is not None:
        try:
            parent_class = LucClass.get(class_system_id=classification_system.id, name=parent)

            classes = LucClass(name=name,
                               description=description,
                               code=code,
                               class_system_id=classification_system.id,
                               class_parent_id=parent_class.id)
            classes.save()

            class_schema = ClassesSchema(exclude=['id', 'class_system_id', 'class_parent_id']).dump(classes)

            class_schema['parent_name'] = parent_class.name

            return class_schema

        except:
            return None

    else:
        classes = LucClass(name=name, description=description,
                           code=code, class_system_id=classification_system.id)
        classes.save(commit=False)

        class_schema = ClassesSchema(exclude=['id', 'class_system_id', 'class_parent_id']).dump(classes)

        class_schema['parent_name'] = None

        return class_schema