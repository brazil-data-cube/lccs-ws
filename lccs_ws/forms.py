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
"""Defines Marshmallow Forms for LCCSWS abstractions."""

from lccs_db.models import (ClassMapping, LucClass, LucClassificationSystem,
                            StyleFormats, Styles, db)
from marshmallow import Schema, fields, post_dump, pre_load
from marshmallow.validate import ValidationError
from marshmallow_sqlalchemy import ModelSchema


def validate_fields_in(in_data: dict):
    """Validate title and description."""
    if 'title' in in_data:
        title = in_data['title']
        if 'pt-br' not in title and 'en' not in title:
            raise ValidationError(f"Title language not found in key 'title'. You must specify: 'en' or 'pt-br'")
    if 'description' in in_data:
        description = in_data['description']
        if 'pt-br' not in description and 'en' not in description:
            raise ValidationError(
                f"Description language not found in key 'description'. You must specify: 'en' or 'pt-br'")


class ClassificationSystemSchema(ModelSchema):
    """Form definition for the model LucClassificationSystem."""
    
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    title = fields.String(required=True)
    version = fields.String(required=True)
    identifier = fields.String(dump_only=True)
    authority_name = fields.String(required=True)
    description = fields.String(required=True)
    version_successor = fields.Integer(required=False)
    version_predecessor = fields.Integer(required=False)

    class Meta:
        """Generate marshmallow Schemas from LucClassificationSystem model."""
        
        model = LucClassificationSystem
        sqla_session = db.session
        exclude = ('created_at', 'updated_at',)


class ClassificationSystemMetadataSchema(Schema):
    """Define parser for classification system update."""
    
    name = fields.String(required=True, allow_none=False)
    title = fields.Dict(required=True, allow_none=False)
    authority_name = fields.String(required=True, allow_none=False)
    description = fields.Dict(required=True, allow_none=False)
    version = fields.String(required=True, allow_none=False)

    @pre_load
    def validate_system(self, in_data, **kwargs):
        """Validate the classification system fields."""
        import re

        if 'name' in in_data:
            result = re.search(r'(^[A-Za-z0-9\-]{1,32}$)', in_data.get("name", ""))
            if result is None:
                raise ValidationError('Classification System name is not valid!')

        if 'title' in in_data:
            title = in_data['title']
            if 'pt-br' not in title and 'en' not in title:
                raise ValidationError(f"Title language not found in key 'title'. You must specify: 'en' or 'pt-br'")
        if 'description' in in_data:
            description = in_data['description']
            if 'pt-br' not in description and 'en' not in description:
                raise ValidationError(
                    f"Description language not found in key 'description'. You must specify: 'en' or 'pt-br'")

        return in_data


class ClassesSchema(ModelSchema):
    """Marshmallow Forms for LucClass."""

    SKIP_NONE_VALUES = set([None])

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    code = fields.String(required=True)
    title = fields.String(required=True)
    description = fields.String(required=True)
    class_parent_id = fields.Integer(required=False)
    classification_system_id = fields.Integer(dump_only=True)

    class Meta:
        """Generate marshmallow Schemas from LucClass model."""
        
        model = LucClass
        sqla_session = db.session
        include_fk = True,
        exclude = ('created_at', 'updated_at', 'classification_system', 'class_parent')

    @post_dump
    def remove_optional_none(self, data, **kwargs):
        """Skip none values."""
        output = {
            key: value for key, value in data.items()
            if value not in self.SKIP_NONE_VALUES
        }
        return output


class ClassMetadataSchema(Schema):
    """Define parser for classification system update."""
    
    name = fields.String(required=True, allow_none=False)
    title = fields.Dict(required=True, allow_none=False)
    code = fields.String(required=True, allow_none=False)
    description = fields.Dict(required=True, allow_none=False)
    class_parent_id = fields.Integer(required=False)
    children = fields.Nested('ClassMetadataSchema', required=False, allow_none=None, many=True)

    @pre_load
    def validate_class(self, in_data, **kwargs):
        """Validate the classification system fields."""
        import re
        if 'name' in in_data:
            result = re.search(r'(^[A-Za-z0-9\-]{1,32}$)', in_data.get("name", ""))
            if result is None:
                raise ValidationError(f'Class name {in_data.get("name", "")} is not valid!')

        validate_fields_in(in_data)

        return in_data


class ClassMetadataForm(Schema):
    """Define parser for classification system."""

    classes = fields.List(fields.Nested('ClassMetadataSchema', required=True))


class ClassesMappingSchema(ModelSchema):
    """Marshmallow Forms for ClassMapping."""
    
    source_class_id = fields.String(required=True)
    target_class_id = fields.String(required=True)
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
    
    source_class = fields.Integer(required=True, allow_none=False)
    target_class = fields.Integer(required=True, allow_none=False)
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

    @pre_load
    def validate_style_format(self, in_data, **kwargs):
        """Validate the classification system fields."""
        import re
        if 'name' in in_data:
            result = re.search(r'(^[A-Za-z0-9\-]{1,64}$)', in_data.get("name", ""))
            if result is None:
                raise ValidationError('Style Format name is not valid!')
        return in_data


class StyleFormatsMetadataSchema(Schema):
    """Define parser for classification system update."""
    
    name = fields.String(required=False, allow_none=False)


class StyleSchema(ModelSchema):
    """Marshmallow Forms for StyleSchema."""
    
    class Meta:
        """Generate marshmallow Schemas from StyleSchema model."""
        
        model = Styles
        exclude = ('created_at', 'updated_at',)
