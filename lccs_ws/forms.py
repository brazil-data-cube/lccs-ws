#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Defines Marshmallow Forms for LCCSWS abstractions."""

from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

from lccs_db.models import LucClass, LucClassificationSystem, ClassMapping

class LucClassificationSystemsSchema(ModelSchema):
    """Marshmallow Forms for LucClassificationSystem."""

    class Meta:
        """Generate marshmallow Schemas from model."""

        model = LucClassificationSystem
        exclude = ('created_at', 'updated_at', )

class LucClassSchema(ModelSchema):
    """Marshmallow Forms for LucClass."""

    class Meta:
        """Generate marshmallow Schemas from model."""

        model = LucClass
        exclude = ('created_at', 'updated_at',)
