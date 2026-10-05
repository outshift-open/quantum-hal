# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Conformance tests for AdapterTimeTaggerService"""
import os
import grpc
import pytest

from hal.adapters.common.v1 import common_pb2
from hal.adapters.timetagger.v1 import timetagger_pb2, timetagger_pb2_grpc
from utils import validate_response_field, validate_response_fields, check_optional_rpc

# Import proto constants using relative import
from ..proto_constants import (
    VALID_HEALTH_CHECK_STATUSES,
    VALID_RESOURCE_HEALTH_STATUSES
)


TEST_PRODUCT_ID = "test-timetagger-001"
TEST_RESOURCE_TYPE = "test-timetagger-type"
TEST_RUN_ID = "test-run-123"


def get_adapter_address():
    """Get adapter address from environment variable"""
    address = os.getenv("TIMETAGGER_ADAPTER_ADDRESS")
    if not address:
        raise ValueError(
            "TIMETAGGER_ADAPTER_ADDRESS environment variable not set. "
            "Copy test/.env.example to test/.env and configure adapter addresses."
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
    """Get gRPC metadata from environment if specified"""
    # Get reqType header if specified
    reqtype = os.getenv("GRPC_HEADER_METADATA_REQTYPE", "")
    if not reqtype:
        return None
    
    return [("reqtype", reqtype.strip())]


@pytest.fixture(scope="module")
def client(grpc_channel, metadata):
    """Create gRPC client stub with optional metadata interceptor"""
    if metadata:
        # Create interceptor that adds metadata to all calls
        class MetadataInterceptor(grpc.UnaryUnaryClientInterceptor):
            def __init__(self, metadata):
                self._metadata = metadata
            
            def intercept_unary_unary(self, continuation, client_call_details, request):
                new_details = client_call_details._replace(metadata=self._metadata)
                return continuation(new_details, request)
        
        interceptor = MetadataInterceptor(metadata)
        channel = grpc.intercept_channel(grpc_channel, interceptor)
        return timetagger_pb2_grpc.AdapterTimeTaggerServiceStub(channel)
    
    return timetagger_pb2_grpc.AdapterTimeTaggerServiceStub(grpc_channel)


def test_health_check(client):
    """Test HealthCheck RPC"""
    request = common_pb2.HealthCheckRequest()
    response = client.HealthCheck(request)
    assert response is not None
    assert response.message in VALID_HEALTH_CHECK_STATUSES, \
        f"HealthCheck message must be one of {VALID_HEALTH_CHECK_STATUSES}, got '{response.message}'"


def test_resource_health_check(client):
    """Test ResourceHealthCheck RPC"""
    request = common_pb2.ResourceHealthCheckRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE
    )
    response = client.ResourceHealthCheck(request)
    assert response is not None
    assert response.message in VALID_RESOURCE_HEALTH_STATUSES, \
        f"ResourceHealthCheck message must be one of {VALID_RESOURCE_HEALTH_STATUSES}, got '{response.message}'"


def test_auto_recover(client):
    """Test AutoRecover RPC (optional)"""
    request = common_pb2.AutoRecoverRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE
    )
    implemented, response = check_optional_rpc(lambda: client.AutoRecover(request))
    if implemented:
        assert response is not None
        # Validate message field (must be non-empty when implemented)
        validate_response_field(response, "message", str, allow_empty=False)


def test_tune(client):
    """Test Tune RPC (optional)"""
    request = common_pb2.TuneRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        config_json='{"test": "config"}'
    )
    implemented, response = check_optional_rpc(lambda: client.Tune(request))
    if implemented:
        assert response is not None
        # Validate message field (must be non-empty when implemented)
        validate_response_field(response, "message", str, allow_empty=False)

def test_get_product_info(client):
    """Test GetProductInfo RPC"""
    request = timetagger_pb2.GetProductInfoRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE
    )
    response = client.GetProductInfo(request)
    assert response is not None
    
    # Validate all fields (allow empty as they may not be set for all devices)
    validate_response_fields(response, {
        "serial_number": (str, True),
        "product_code": (str, True),
        "software_version": (str, True),
    })


def test_initialize(client):
    """Test Initialize RPC"""
    request = timetagger_pb2.InitializeRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        config_json='{"test": "config"}'
    )
    response = client.Initialize(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)


def test_deinitialize(client):
    """Test Deinitialize RPC"""
    request = timetagger_pb2.DeinitializeRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE
    )
    response = client.Deinitialize(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)


def test_get_status(client):
    """Test GetStatus RPC"""
    request = timetagger_pb2.GetStatusRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE
    )
    response = client.GetStatus(request)
    assert response is not None
    
    # Validate all fields
    validate_response_fields(response, {
        "run_id": (str, True),  # May be empty if not in a run
        "uptime_seconds": (float, True),  # Numeric fields can be 0
        "status_json": (str, True),  # May be empty
    })
    
    # Validate state is a valid TimeTaggerState enum value (from proto definition)
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
    assert response.state in valid_states, \
        f"GetStatus state must be a valid TimeTaggerState enum value, got {response.state}"


def test_set_config(client):
    """Test SetConfig RPC"""
    request = timetagger_pb2.SetConfigRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        config_json='{"test": "config"}'
    )
    response = client.SetConfig(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)


def test_start_data_collection(client):
    """Test StartDataCollection RPC"""
    request = timetagger_pb2.StartDataCollectionRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        run_id=TEST_RUN_ID,
        config_json='{"test": "config"}'
    )
    response = client.StartDataCollection(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)

def test_stop_data_collection(client):
    """Test StopDataCollection RPC"""
    request = timetagger_pb2.StopDataCollectionRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        run_id=TEST_RUN_ID
    )
    response = client.StopDataCollection(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)

def test_trigger_event(client):
    """Test TriggerEvent RPC (optional)"""
    request = timetagger_pb2.TriggerEventRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        run_id=TEST_RUN_ID,
        event_type="test-event",
        payload_json='{"test": "payload"}'
    )
    implemented, response = check_optional_rpc(lambda: client.TriggerEvent(request))
    if implemented:
        assert response is not None
        # Validate message field (must be non-empty when implemented)
        validate_response_field(response, "message", str, allow_empty=False)
