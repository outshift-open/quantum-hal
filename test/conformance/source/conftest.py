# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Parametrize source tests over whatever kinds the JSON config lists."""
import pytest

from .request_config import (
    CONFIG_ENV,
    config_path,
    kind_ids,
    load_source_kinds,
)

_SOURCE_KINDS = load_source_kinds()


if _SOURCE_KINDS:

    @pytest.fixture(
        scope="class",
        params=_SOURCE_KINDS,
        ids=kind_ids(_SOURCE_KINDS),
    )
    def source_kind(request):
        """One JSON source object; class tests run all RPCs for this kind."""
        return request.param

else:

    @pytest.fixture
    def source_kind():
        """Skip device-scoped tests when the JSON lists no source kinds."""
        pytest.skip(
            "No source kinds in {0} (set {1})".format(
                config_path(), CONFIG_ENV
            )
        )
