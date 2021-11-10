#
# This file is part of  Land Cover Classification System Web Service.
# Copyright (C) 2021 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Decorators used to integrate with Land Cover Classification System Web Service."""

from functools import wraps

from flask import abort, request
from lccs_db.config import Config
from lccs_db.models.base import translation_hybrid


def set_locale(locale: str):
    """Update the location."""
    translation_hybrid.current_locale = locale


def language(language=None, required=False):
    """Decorate for locale."""
    def _language(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            support_language = [Config.I18N_LANGUAGES['current_locale'][0],
                                Config.I18N_LANGUAGES['default_locale'][0]]

            language_str = request.headers['language'] if request.headers.get('language') else \
                            request.args.get('language')
            if language_str:
                if language_str not in support_language:
                    abort(403, 'Language not supported!')
                set_locale(language_str)
            return func(*args, **kwargs)
        return wrapped
    return _language
