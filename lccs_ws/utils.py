#
# This file is part of BDC-Auth-Client.
# Copyright (C) 2020 INPE.
#
# BDC-Auth-Client is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Decorators used to integrate with BDC-Auth Provider."""

from functools import wraps

from lccs_db.models.base import translation_hybrid
from flask import request


def set_locale(locale: str):
    translation_hybrid.current_locale = locale

#TODO: see cache
def language(locale=None, required=False):
    """Decorator for locale."""
    def _language(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            support_locale = ['pt-br', 'en']
            locale_str = request.headers['locale'] if request.headers.get('locale') else \
                            request.args.get('locale')
            if locale_str:
                if locale_str in support_locale:
                    set_locale(locale_str)
            return func(*args, **kwargs)
        return wrapped
    return _language