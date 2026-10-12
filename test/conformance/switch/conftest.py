# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Parametrize switch tests over whatever kinds the JSON config lists."""
import pytest

from .request_config import (
    CONFIG_ENV,
    config_path,
    kind_ids,
    load_switch_kinds,
)

_SWITCH_KINDS = load_switch_kinds()


if _SWITCH_KINDS:

    @pytest.fixture(
        scope="class",
        params=_SWITCH_KINDS,
        ids=kind_ids(_SWITCH_KINDS),
    )
    def switch_kind(request):
        """One JSON switch object; class tests run all RPCs for this kind."""
        return request.param

else:

    @pytest.fixture
    def switch_kind():
        """Skip device-scoped tests when the JSON lists no switch kinds."""
        pytest.skip(
            "No switch kinds in {0} (set {1})".format(
                config_path(), CONFIG_ENV
            )
        )
