# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Conformance tests for AdapterTimeTaggerService"""
import os
import grpc
import pytest

from hal.adapters.common.v1 import common_pb2
from hal.adapters.timetagger.v1 import timetagger_pb2, timetagger_pb2_grpc
from utils import (
    validate_response_field,
    validate_response_fields,
    check_command_rpc,
    check_optional_rpc,
)

from ..proto_constants import (
    VALID_HEALTH_CHECK_STATUSES,
    VALID_RESOURCE_HEALTH_STATUSES,
)
from .request_config import rpc_request


def get_adapter_address():
    """Get adapter address from environment variable"""
    address = os.getenv("TIMETAGGER_ADAPTER_ADDRESS")
    if not address:
        raise ValueError(
            "TIMETAGGER_ADAPTER_ADDRESS environment variable not set. "
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
        return timetagger_pb2_grpc.AdapterTimeTaggerServiceStub(channel)

    return timetagger_pb2_grpc.AdapterTimeTaggerServiceStub(grpc_channel)


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


class TestTimeTagger:
    """Device-scoped RPCs; class-scoped timetagger_kind runs one kind at a time."""

    def test_resource_health_check(self, client, timetagger_kind):
        """Test ResourceHealthCheck RPC"""
        request = common_pb2.ResourceHealthCheckRequest(
            **rpc_request(timetagger_kind, "ResourceHealthCheck")
        )
        response = client.ResourceHealthCheck(request)
        assert response is not None
        assert response.message in VALID_RESOURCE_HEALTH_STATUSES, (
            "ResourceHealthCheck message must be one of "
            "{0}, got '{1}'".format(
                VALID_RESOURCE_HEALTH_STATUSES, response.message
            )
        )

    def test_auto_recover(self, client, timetagger_kind):
        """Test AutoRecover RPC (optional)"""
        request = common_pb2.AutoRecoverRequest(
            **rpc_request(timetagger_kind, "AutoRecover")
        )
        implemented, response = check_optional_rpc(
            lambda: client.AutoRecover(request)
        )
        if implemented:
            assert response is not None
            validate_response_field(
                response, "message", str, allow_empty=False
            )

    def test_tune(self, client, timetagger_kind):
        """Test Tune RPC (optional)"""
        request = common_pb2.TuneRequest(
            **rpc_request(timetagger_kind, "Tune")
        )
        implemented, response = check_optional_rpc(
            lambda: client.Tune(request)
        )
        if implemented:
            assert response is not None
            validate_response_field(
                response, "message", str, allow_empty=False
            )

    def test_get_product_info(self, client, timetagger_kind):
        """Test GetProductInfo RPC"""
        request = timetagger_pb2.GetProductInfoRequest(
            **rpc_request(timetagger_kind, "GetProductInfo")
        )
        response = client.GetProductInfo(request)
        assert response is not None
        validate_response_fields(response, {
            "serial_number": (str, True),
            "product_code": (str, True),
            "software_version": (str, True),
            "vendor": (str, True),
        })

    def test_get_product_info_missing_resource_type(self, client):
        """GetProductInfo with empty resource_type is INVALID_ARGUMENT"""
        request = timetagger_pb2.GetProductInfoRequest(product_id="any")
        with pytest.raises(grpc.RpcError) as exc_info:
            client.GetProductInfo(request)
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    def test_list_measurement_types(self, client, timetagger_kind):
        """Test ListMeasurementTypes RPC"""
        request = timetagger_pb2.ListMeasurementTypesRequest(
            **rpc_request(timetagger_kind, "ListMeasurementTypes")
        )
        response = client.ListMeasurementTypes(request)
        assert response is not None
        assert len(response.measurement_types) > 0, (
            "ListMeasurementTypes must return at least one measurement type"
        )
        ids = set()
        for info in response.measurement_types:
            validate_response_field(info, "id", str, allow_empty=False)
            validate_response_field(info, "description", str, allow_empty=True)
            assert info.id not in ids, (
                "Duplicate measurement type id '{0}'".format(info.id)
            )
            ids.add(info.id)
            # usecase and name are optional: when set they must be non-empty.
            for optional_field in ("usecase", "name"):
                if info.HasField(optional_field):
                    validate_response_field(
                        info, optional_field, str, allow_empty=False
                    )

    def test_list_measurement_types_missing_resource_type(self, client):
        """ListMeasurementTypes with empty resource_type is INVALID_ARGUMENT"""
        request = timetagger_pb2.ListMeasurementTypesRequest()
        with pytest.raises(grpc.RpcError) as exc_info:
            client.ListMeasurementTypes(request)
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    def test_initialize(self, client, timetagger_kind):
        """Test Initialize RPC"""
        request = timetagger_pb2.InitializeRequest(
            **rpc_request(timetagger_kind, "Initialize")
        )
        response = check_command_rpc(lambda: client.Initialize(request))
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_deinitialize(self, client, timetagger_kind):
        """Test Deinitialize RPC"""
        request = timetagger_pb2.DeinitializeRequest(
            **rpc_request(timetagger_kind, "Deinitialize")
        )
        response = check_command_rpc(lambda: client.Deinitialize(request))
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_get_status(self, client, timetagger_kind):
        """Test GetStatus RPC"""
        request = timetagger_pb2.GetStatusRequest(
            **rpc_request(timetagger_kind, "GetStatus")
        )
        response = client.GetStatus(request)
        assert response is not None
        validate_response_fields(response, {
            "run_id": (str, True),
            "uptime_seconds": (float, True),
            "status_json": (str, True),
        })
        valid_states = [
            timetagger_pb2.TIME_TAGGER_STATE_UNSPECIFIED,
            timetagger_pb2.TIME_TAGGER_STATE_IDLE,
            timetagger_pb2.TIME_TAGGER_STATE_INITIALIZING,
            timetagger_pb2.TIME_TAGGER_STATE_READY,
            timetagger_pb2.TIME_TAGGER_STATE_COLLECTING,
            timetagger_pb2.TIME_TAGGER_STATE_FAULT,
            timetagger_pb2.TIME_TAGGER_STATE_DEINITIALIZING,
            timetagger_pb2.TIME_TAGGER_STATE_DEGRADED,
        ]
        assert response.state in valid_states, (
            "GetStatus state must be a valid TimeTaggerState enum value, "
            "got {0}".format(response.state)
        )

    def test_set_config(self, client, timetagger_kind):
        """Test SetConfig RPC"""
        request = timetagger_pb2.SetConfigRequest(
            **rpc_request(timetagger_kind, "SetConfig")
        )
        response = check_command_rpc(lambda: client.SetConfig(request))
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_start_data_collection(self, client, timetagger_kind):
        """Test StartDataCollection RPC"""
        request = timetagger_pb2.StartDataCollectionRequest(
            **rpc_request(timetagger_kind, "StartDataCollection")
        )
        response = check_command_rpc(lambda: client.StartDataCollection(request))
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_stop_data_collection(self, client, timetagger_kind):
        """Test StopDataCollection RPC"""
        request = timetagger_pb2.StopDataCollectionRequest(
            **rpc_request(timetagger_kind, "StopDataCollection")
        )
        response = check_command_rpc(lambda: client.StopDataCollection(request))
        assert response is not None
        validate_response_field(
            response, "message", str, allow_empty=False
        )

    def test_trigger_event(self, client, timetagger_kind):
        """Test TriggerEvent RPC (optional)"""
        request = timetagger_pb2.TriggerEventRequest(
            **rpc_request(timetagger_kind, "TriggerEvent")
        )
        implemented, response = check_optional_rpc(
            lambda: client.TriggerEvent(request)
        )
        if implemented:
            assert response is not None
            validate_response_field(
                response, "message", str, allow_empty=False
            )
