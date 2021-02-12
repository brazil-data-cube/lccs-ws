#
# This file is part of Land Cover Classification System Web Service.
# Copyright (C) 2020-2021 INPE.
#
# Land Cover Classification System Web Service is a free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""LCCS-WS Test module."""

import pytest

if __name__ == "__main__":
    from lccs_ws_tests.test_app import TestLCCSWS

    pytest.main(["--color=auto", "--no-cov", "-v"])