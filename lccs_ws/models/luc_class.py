#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Land Cover Classification System Web Service Model."""

from .base_sql import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

class LucClass(BaseModel):
    """LucClass."""

    __tablename__ = 'luc_class'

    id = Column(Integer, primary_key=True)
    codigo = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    style = Column(Text, nullable=False)
    luc_classification_system_id = Column(Integer, ForeignKey('luc_classification_system.id',
                                                              ondelete='NO ACTION'), nullable=False)
    parent_id = Column(Integer, ForeignKey('luc_class.id', ondelete='NO ACTION'), nullable=True)

    luc_classification_system = relationship('LucClassificationSystem')