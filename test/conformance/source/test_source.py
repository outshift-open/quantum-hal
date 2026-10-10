# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Conformance tests for AdapterSourceService"""
import os
import grpc
import pytest

from hal.adapters.common.v1 import common_pb2
from hal.adapters.source.v1 import source_pb2, source_pb2_grpc
from utils import (
    validate_response_field,
    validate_response_fields,
    check_optional_rpc,
)

from ..proto_constants import (
    VALID_HEALTH_CHECK_STATUSES,
    VALID_RESOURCE_HEALTH_STATUSES,
)
from .request_config import rpc_request


def get_adapter_address():
    """Get adapter address from environment variable"""
    address = os.getenv("SOURCE_ADAPTER_ADDRESS")
    if not address:
        raise ValueError(
            "SOURCE_ADAPTER_ADDRESS environment variable not set. "
            "Copy test/.env.example to test/.env and configure "
            "adapter addresses."
        )
    return address


@pytest.fixture(scope="module")
def grpc_channel():
    """Create gRPC channel to adapter"""
    channel = grpc.insecure_channel(get_adapter_address())
    yield channel
    channel.close()


@pytest.fixture(scope="module")
def metadata():
    """Get gRPC metadata from environment if specified."""
    reqtype = os.getenv("GRPC_HEADER_METADATA_REQTYPE", "")
    if not reqtype:
        return None
    return [("reqtype", reqtype.strip())]


@pytest.fixture(scope="module")
def client(grpc_channel, metadata):
    """Create gRPC client stub with optional metadata interceptor."""
    if metadata:
        class MetadataInterceptor(grpc.UnaryUnaryClientInterceptor):
            def __init__(self, metadata):
                self._metadata = metadata

            def intercept_unary_unary(
                self, continuation, client_call_details, request
            ):
                new_details = client_call_details._replace(
                    metadata=self._metadata
                )
                return continuation(new_details, request)

        channel = grpc.intercept_channel(
            grpc_channel, MetadataInterceptor(metadata)
        )
        return source_pb2_grpc.AdapterSourceServiceStub(channel)

    return source_pb2_grpc.AdapterSourceServiceStub(grpc_channel)


def test_health_check(client):
    """Test HealthCheck RPC"""
    request = common_pb2.HealthCheckRequest()
    response = client.HealthCheck(request)
    assert response is not None
    assert response.message in VALID_HEALTH_CHECK_STATUSES, (
        "HealthCheck message must be one of "
        "{0}, got '{1}'".format(
            VALID_HEALTH_CHECK_STATUSES, response.message
        )
    )


class TestSource:
    """Device-scoped RPCs; class-scoped source_kind runs one kind at a time."""

    def test_resource_health_check(self, client, source_kind):
        """Test ResourceHealthCheck RPC"""
        request = common_pb2.ResourceHealthCheckRequest(
            **rpc_request(source_kind, "ResourceHealthCheck")
        )
        response = client.ResourceHealthCheck(request)
        assert response is not None
        assert response.message in VALID_RESOURCE_HEALTH_STATUSES, (
            "ResourceHealthCheck message must be one of "
            "{0}, got '{1}'".format(
                VALID_RESOURCE_HEALTH_STATUSES, response.message
            )
        )

    def test_auto_recover(self, client, source_kind):
        """Test AutoRecover RPC (optional)"""
        request = common_pb2.AutoRecoverRequest(
            **rpc_request(source_kind, "AutoRecover")
        )
        implemented, response = check_optional_rpc(
            lambda: client.AutoRecover(request)
        )
        if implemented:
            assert response is not None
            validate_response_field(
                response, "message", str, allow_empty=False
            )

    def test_tune(self, client, source_kind):
        """Test Tune RPC (optional)"""
        request = common_pb2.TuneRequest(
            **rpc_request(source_kind, "Tune")
        )
        implemented, response = check_optional_rpc(
            lambda: client.Tune(request)
        )
        if implemented:
            assert response is not None
            validate_response_field(
                response, "message", str, allow_empty=False
            )

    def test_get_product_info(self, client, source_kind):
        """Test GetProductInfo RPC"""
        request = source_pb2.GetProductInfoRequest(
            **rpc_request(source_kind, "GetProductInfo")
        )
        response = client.GetProductInfo(request)
        assert response is not None
        validate_response_fields(response, {
            "serial_number": (str, True),
            "product_code": (str, True),
            "software_version": (str, True),
        })

    def test_initialize(self, client, source_kind):
        """Test Initialize RPC"""
        request = source_pb2.InitializeRequest(
            **rpc_request(source_kind, "Initialize")
        )
        response = client.Initialize(request)
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_deinitialize(self, client, source_kind):
        """Test Deinitialize RPC"""
        request = source_pb2.DeinitializeRequest(
            **rpc_request(source_kind, "Deinitialize")
        )
        response = client.Deinitialize(request)
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_get_status(self, client, source_kind):
        """Test GetStatus RPC"""
        request = source_pb2.GetStatusRequest(
            **rpc_request(source_kind, "GetStatus")
        )
        response = client.GetStatus(request)
        assert response is not None
        validate_response_fields(response, {
            "run_id": (str, True),
            "uptime_seconds": (float, True),
            "status_json": (str, True),
        })
        valid_states = [
            source_pb2.SOURCE_STATE_UNSPECIFIED,
            source_pb2.SOURCE_STATE_IDLE,
            source_pb2.SOURCE_STATE_INITIALIZING,
            source_pb2.SOURCE_STATE_LOCKING,
            source_pb2.SOURCE_STATE_READY,
            source_pb2.SOURCE_STATE_EMITTING,
            source_pb2.SOURCE_STATE_FAULT,
            source_pb2.SOURCE_STATE_DEINITIALIZING,
            source_pb2.SOURCE_STATE_DEGRADED,
        ]
        assert response.state in valid_states, (
            "GetStatus state must be a valid SourceState enum value, "
            "got {0}".format(response.state)
        )

    def test_set_config(self, client, source_kind):
        """Test SetConfig RPC"""
        request = source_pb2.SetConfigRequest(
            **rpc_request(source_kind, "SetConfig")
        )
        response = client.SetConfig(request)
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_start_emission(self, client, source_kind):
        """Test StartEmission RPC"""
        request = source_pb2.StartEmissionRequest(
            **rpc_request(source_kind, "StartEmission")
        )
        response = client.StartEmission(request)
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_stop_emission(self, client, source_kind):
        """Test StopEmission RPC"""
        request = source_pb2.StopEmissionRequest(
            **rpc_request(source_kind, "StopEmission")
        )
        response = client.StopEmission(request)
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_trigger_event(self, client, source_kind):
        """Test TriggerEvent RPC (optional)"""
        request = source_pb2.TriggerEventRequest(
            **rpc_request(source_kind, "TriggerEvent")
        )
        implemented, response = check_optional_rpc(
            lambda: client.TriggerEvent(request)
        )
        if implemented:
            assert response is not None
            validate_response_field(
                response, "message", str, allow_empty=False
            )
