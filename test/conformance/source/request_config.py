# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Load source request testdata. Address and metadata stay in .env."""
import json
import os

from hal.adapters.source.v1 import source_pb2

CONFIG_ENV = "SOURCE_CONFORMANCE_CONFIG"
_DEFAULT_CONFIG = os.path.join(
    os.path.dirname(__file__), "..", "testdata", "source.json"
)


def config_path():
    """Resolve the source JSON path from env or the default testdata file."""
    return os.path.abspath(os.getenv(CONFIG_ENV, _DEFAULT_CONFIG))


def load_source_kinds():
    """Load the source array from JSON; missing file yields []."""
    path = config_path()
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    kinds = data.get("source", [])
    if kinds is None:
        return []
    if not isinstance(kinds, list):
        raise ValueError(
            "{0}: 'source' must be a JSON array".format(path)
        )
    for index, kind in enumerate(kinds):
        if not isinstance(kind, dict):
            raise ValueError(
                "{0}: source[{1}] must be an object".format(path, index)
            )
    return kinds


def kind_ids(kinds):
    """Pytest ids from resource_type, with suffixes if names repeat."""
    ids = []
    seen = {}
    for kind in kinds:
        base = str(kind.get("resource_type") or "source")
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
        elif key == "config" and isinstance(value, dict):
            cfg = dict(value)
            config_json = cfg.get("config_json")
            if isinstance(config_json, (dict, list)):
                cfg["config_json"] = json.dumps(config_json)
            normalized["config"] = cfg
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
    fields = _normalize_fields(fields)
    config = fields.get("config")
    if isinstance(config, dict):
        fields["config"] = source_pb2.SourceConfig(**config)
    return fields
