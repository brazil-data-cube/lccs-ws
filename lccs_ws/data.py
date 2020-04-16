#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Data module of Land Cover Classification System Web Service."""

from lccs_db.models import ClassMapping, db

session = db.session


def get_mappings(classes_source, classes_target):
    """Filter all mapping."""
    where = [ClassMapping.source_class_id.in_([value.id for value in classes_source])]

    if classes_target is not None:
        where += [ClassMapping.target_class_id.in_([value.id for value in classes_target])]

    return session.query(ClassMapping).filter(*where).all()