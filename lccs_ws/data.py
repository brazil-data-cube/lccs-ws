#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Data module of Land Cover Classification System Web Service."""

from lccs_db.models import ApplicationsStyle, ClassMapping, db, Style

session = db.session


def get_mappings(classes_source, classes_target):

    if classes_source is not None:
        where = [ClassMapping.source_class_id.in_([value.id for value in classes_source])]
    if classes_target is not None:
        where += [ClassMapping.target_class_id.in_([value.id for value in classes_target])]

    return session.query(ClassMapping).filter(*where).all()


def get_application_style(sytem_id):

    result = list()
    style = Style.filter(class_system_id=sytem_id)

    [result.append(value.application_style) for value in style]

    # where = [ApplicationsStyle.application_style_id.in_([value.application_style_id for value in style])]

    # application_style = session.query(ApplicationsStyle).filter(*where).all()

    # return application_style

    return result