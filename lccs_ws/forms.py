#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Defines Marshmallow Forms for LCCSWS abstractions."""

from lccs_db.models import (ClassMapping, LucClass, LucClassificationSystem,
                            StyleFormats, Styles, db)
from marshmallow import Schema, fields, post_dump
from marshmallow_sqlalchemy import ModelSchema


class ClassificationSystemSchema(ModelSchema):
    """Form definition for the model LucClassificationSystem."""
    
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    authority_name = fields.String(required=True)
    description = fields.String(required=True)
    version = fields.String(required=True)
    
    class Meta:
        """Generate marshmallow Schemas from LucClassificationSystem model."""
        
        model = LucClassificationSystem
        sqla_session = db.session
        exclude = ('created_at', 'updated_at',)


class ClassificationSystemMetadataSchema(Schema):
    """Define parser for classification system update."""
    
    name = fields.String(required=False, allow_none=False)
    authority_name = fields.String(required=False, allow_none=False)
    description = fields.String(required=False, allow_none=False)
    version = fields.String(required=False, allow_none=False)


class ClassesSchema(ModelSchema):
    """Marshmallow Forms for LucClass."""

    SKIP_NONE_VALUES = ['class_parent_id']

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    code = fields.String(required=True)
    description = fields.String(required=True)
    class_parent_id = fields.Integer(required=False)
    
    class Meta:
        """Generate marshmallow Schemas from LucClass model."""
        
        model = LucClass
        sqla_session = db.session
        include_fk = True,
        exclude = ('created_at', 'updated_at', 'classification_system', 'class_parent')

    @post_dump
    def remove_optional_none(self, data, **kwargs):
        """Remove optional none fields."""
        output = {
            key: value for key, value in data.items()
            if key not in self.SKIP_NONE_VALUES
        }
        return output


class ClassMetadataSchema(Schema):
    """Define parser for classification system update."""
    
    name = fields.String(required=False, allow_none=False)
    code = fields.String(required=False, allow_none=False)
    description = fields.String(required=False, allow_none=False)
    class_parent_id = fields.Integer(required=False)


class ClassesMappingSchema(ModelSchema):
    """Marshmallow Forms for ClassMapping."""
    
    source_class_id = fields.Integer(required=True)
    target_class_id = fields.Integer(required=True)
    description = fields.String(required=True)
    degree_of_similarity = fields.Number(required=False)
    
    class Meta:
        """Generate marshmallow Schemas from ClassMapping model."""
        
        model = ClassMapping
        sqla_session = db.session
        include_fk = True
        exclude = ('created_at', 'updated_at', 'source_class', 'target_class')


class ClassesMappingMetadataSchema(Schema):
    """Define parser for classification system update."""
    
    source_class_id = fields.Integer(required=True, allow_none=False)
    target_class_id = fields.Integer(required=True, allow_none=False)
    description = fields.String(required=False, allow_none=False)
    degree_of_similarity = fields.Number(required=False)


class StyleFormatsSchema(ModelSchema):
    """Marshmallow Forms for StyleFormatsSchema."""
    
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    
    class Meta:
        """Generate marshmallow Schemas from StyleFormatsSchema model."""
        
        model = StyleFormats
        sqla_session = db.session
        exclude = ('created_at', 'updated_at',)


class StyleFormatsMetadataSchema(Schema):
    """Define parser for classification system update."""
    
    name = fields.String(required=False, allow_none=False)


class StyleSchema(ModelSchema):
    """Marshmallow Forms for StyleSchema."""
    
    class Meta:
        """Generate marshmallow Schemas from StyleSchema model."""
        
        model = Styles
        exclude = ('created_at', 'updated_at',)
