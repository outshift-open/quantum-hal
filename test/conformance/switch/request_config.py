# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Load switch request testdata. Address and metadata stay in .env."""
import json
import os

CONFIG_ENV = "SWITCH_CONFORMANCE_CONFIG"
_DEFAULT_CONFIG = os.path.join(
    os.path.dirname(__file__), "..", "testdata", "switch.json"
)


def config_path():
    """Resolve the switch JSON path from env or the default testdata file."""
    return os.path.abspath(os.getenv(CONFIG_ENV, _DEFAULT_CONFIG))


def load_switch_kinds():
    """Load the switch array from JSON; missing file yields []."""
    path = config_path()
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    kinds = data.get("switch", [])
    if kinds is None:
        return []
    if not isinstance(kinds, list):
        raise ValueError(
            "{0}: 'switch' must be a JSON array".format(path)
        )
    for index, kind in enumerate(kinds):
        if not isinstance(kind, dict):
            raise ValueError(
                "{0}: switch[{1}] must be an object".format(path, index)
            )
    return kinds


def kind_ids(kinds):
    """Pytest ids from resource_type, with suffixes if names repeat."""
    ids = []
    seen = {}
    for kind in kinds:
        base = str(kind.get("resource_type") or "switch")
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
    if rpc_name == "HealthCheck":
        return _normalize_fields(rpc_fields)
    # Kind-level product_id and resource_type are used by every RPC.
    fields = {
        "product_id": kind.get("product_id", ""),
        "resource_type": kind.get("resource_type", ""),
    }
    fields.update(rpc_fields)
    return _normalize_fields(fields)
