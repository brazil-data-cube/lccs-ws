#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Defines Marshmallow Forms for LCCSWS abstractions."""

from marshmallow_sqlalchemy import ModelSchema

from lccs_ws.models import ClassMapping, LucClass, LucClassificationSystem


class LucClassificationSystemSchema(ModelSchema):
    """Marshmallow Forms for LucClassificationSystem."""

    class Meta:
        """Generate marshmallow Schemas from model."""

        model = LucClassificationSystem


class LucClassSchema(ModelSchema):
    """Marshmallow Forms for LucClass."""

    class Meta:
        """Generate marshmallow Schemas from model."""

        model = LucClass
