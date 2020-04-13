#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Defines Marshmallow Forms for LCCSWS abstractions."""

from lccs_db.models import ClassMapping, LucClass, LucClassificationSystem
from marshmallow_sqlalchemy import ModelSchema, fields


class ClassificationSystemSchema(ModelSchema):
    """Marshmallow Forms for LucClassificationSystem."""

    class Meta:
        """Generate marshmallow Schemas from LucClassificationSystem model."""

        model = LucClassificationSystem
        exclude = ('created_at', 'updated_at',)


class ClassesSchema(ModelSchema):
    """Marshmallow Forms for LucClass."""

    class Meta:
        """Generate marshmallow Schemas from LucClass model."""

        model = LucClass
        include_fk = True,
        exclude = ('created_at', 'updated_at','classification_system', 'class_parent')

class ClassesMappingSchema(ModelSchema):
    """Marshmallow Forms for ClassMapping."""

    class Meta:
        """Generate marshmallow Schemas from ClassMapping model."""

        model = ClassMapping
        include_fk = True
        exclude = ('created_at', 'updated_at',)