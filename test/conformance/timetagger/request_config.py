# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Load time tagger request testdata. Address and metadata stay in .env."""
import json
import os

CONFIG_ENV = "TIMETAGGER_CONFORMANCE_CONFIG"
_DEFAULT_CONFIG = os.path.join(
    os.path.dirname(__file__), "..", "testdata", "timetagger.json"
)


def config_path():
    """Resolve the time tagger JSON path from env or the default testdata file."""
    return os.path.abspath(os.getenv(CONFIG_ENV, _DEFAULT_CONFIG))


def load_timetagger_kinds():
    """Load the timetagger array from JSON; missing file yields []."""
    path = config_path()
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    kinds = data.get("timetagger", [])
    if kinds is None:
        return []
    if not isinstance(kinds, list):
        raise ValueError(
            "{0}: 'timetagger' must be a JSON array".format(path)
        )
    for index, kind in enumerate(kinds):
        if not isinstance(kind, dict):
            raise ValueError(
                "{0}: timetagger[{1}] must be an object".format(
                    path, index
                )
            )
        for field in ("product_id", "resource_type"):
            value = kind.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    "{0}: timetagger[{1}] requires non-empty {2}".format(
                        path, index, field
                    )
                )
    return kinds


def kind_ids(kinds):
    """Pytest ids from resource_type, with suffixes if names repeat."""
    ids = []
    seen = {}
    for kind in kinds:
        base = str(kind.get("resource_type") or "timetagger")
        count = seen.get(base, 0)
        seen[base] = count + 1
        ids.append(base if count == 0 else "{0}-{1}".format(base, count))
    return ids


def _normalize_fields(fields):
    """json.dumps *_json values that were written as objects in testdata."""
    normalized = dict(fields)
    for key, value in list(normalized.items()):
        if key.endswith("_json") and isinstance(value, (dict, list)):
            normalized[key] = json.dumps(value)
    return normalized


# Base fields injected from the kind into each RPC's request kwargs.
# RPCs absent from this table get the default set (product_id + resource_type).
# Use an empty list for RPCs that need no base fields (e.g. HealthCheck).
_RPC_BASE_FIELDS: "dict[str, list[str]]" = {
    # Common RPCs — no device-scoped fields
    "HealthCheck": [],
    # ListMeasurementTypesRequest only declares resource_type (no product_id)
    "ListMeasurementTypes": ["resource_type"],
}
_DEFAULT_BASE_FIELDS = ["product_id", "resource_type"]


def rpc_request(kind, rpc_name):
    """Build one RPC's request kwargs; copy product_id/resource_type from the kind."""
    rpcs = kind.get("rpcs") or {}
    rpc_fields = rpcs.get(rpc_name) or {}
    if not isinstance(rpc_fields, dict):
        raise TypeError(
            "rpcs.{0} must be an object, got {1}".format(
                rpc_name, type(rpc_fields).__name__
            )
        )
    base_field_names = _RPC_BASE_FIELDS.get(rpc_name, _DEFAULT_BASE_FIELDS)
    fields = {f: kind.get(f, "") for f in base_field_names}
    fields.update(rpc_fields)
    return _normalize_fields(fields)
