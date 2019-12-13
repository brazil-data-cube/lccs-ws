#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Land Cover Classification System Web Service Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, MetaData, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


class DatabaseWrapper(object):
    """DatabaseWrapper."""

    def __init__(self):
        """Construct DatabaseWrapper."""
        maker = sessionmaker()
        self.DBSession = scoped_session(maker)
        self.session = None
        self.Model = declarative_base(metadata=MetaData(schema="bdc"))

    def init_model(self, uri):
        """Init models."""
        self.engine = create_engine(uri)
        self.DBSession.configure(bind=self.engine)
        self.session = self.DBSession()


db = DatabaseWrapper()


class BaseModel(db.Model):
    """Abstract class for ORM models."""

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow(),
                        onupdate=datetime.utcnow())

    def save(self, commit=True):
        """Save and persists object in database."""
        db.session.add(self)

        if not commit:
            return

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """Delete object from database."""
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def _filter(cls, **properties):
        """Filter abstraction."""
        return db.session.query(cls).filter_by(**properties)

    @classmethod
    def filter(cls, **properties):
        """Filter data set rows following the provided restrictions.

        Provides a wrapper of SQLAlchemy session query.

        :param properties: List of properties to filter of.
        :type properties: dict.
        """
        return cls._filter(**properties).all()

    @classmethod
    def get(cls, **restrictions):
        """Get one data set from database.

        Throws exception **NoResultFound** when the filter does not match any result.

        :param properties: List of properties to filter of.
        :type propertiesdict
        """
        return cls._filter(**restrictions).one()