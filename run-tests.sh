#!/usr/bin/env bash
#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2019 INPE.
#
# Land Cover Classification System Web Service is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

pydocstyle lccs_ws && \
isort lccs_ws tests setup.py --check-only --diff && \
check-manifest --ignore ".travis-*" --ignore ".readthedocs.*" && \
pytest &&
sphinx-build -qnW --color -b doctest doc/sphinx/ doc/sphinx/_build/doctest