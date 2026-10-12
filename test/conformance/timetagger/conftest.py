# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Parametrize time tagger tests over whatever kinds the JSON config lists."""
import pytest

from .request_config import (
    CONFIG_ENV,
    config_path,
    kind_ids,
    load_timetagger_kinds,
)

_TIMETAGGER_KINDS = load_timetagger_kinds()


if _TIMETAGGER_KINDS:

    @pytest.fixture(
        scope="class",
        params=_TIMETAGGER_KINDS,
        ids=kind_ids(_TIMETAGGER_KINDS),
    )
    def timetagger_kind(request):
        """One JSON time tagger object; class tests run all RPCs for this kind."""
        return request.param

else:

    @pytest.fixture
    def timetagger_kind():
        """Skip device-scoped tests when the JSON lists no time tagger kinds."""
        pytest.skip(
            "No time tagger kinds in {0} (set {1})".format(
                config_path(), CONFIG_ENV
            )
        )
