"""Conformance tests for AdapterSwitchService"""
import os
import grpc
import pytest

from hal.adapters.common.v1 import common_pb2
from hal.adapters.switch.v1 import switch_pb2, switch_pb2_grpc
from utils import validate_response_field, validate_response_fields, check_optional_rpc

# Import proto constants using relative import
from ..proto_constants import (
    VALID_HEALTH_CHECK_STATUSES,
    VALID_RESOURCE_HEALTH_STATUSES
)


TEST_PRODUCT_ID = "test-switch-001"
TEST_RESOURCE_TYPE = "test-switch-type"
TEST_RUN_ID = "test-run-123"


def get_adapter_address():
    """Get adapter address from environment variable"""
    address = os.getenv("SWITCH_ADAPTER_ADDRESS")
    if not address:
        raise ValueError(
            "SWITCH_ADAPTER_ADDRESS environment variable not set. "
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
def client(grpc_channel):
    """Create gRPC client stub"""
    return switch_pb2_grpc.AdapterSwitchServiceStub(grpc_channel)


# Common RPC Tests (from hal/adapters/common/v1/common.proto)

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
    request = switch_pb2.GetProductInfoRequest(
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
    request = switch_pb2.InitializeRequest(
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
    request = switch_pb2.DeinitializeRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE
    )
    response = client.Deinitialize(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)


def test_get_status(client):
    """Test GetStatus RPC"""
    request = switch_pb2.GetStatusRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE
    )
    response = client.GetStatus(request)
    assert response is not None
    
    # Validate all fields (switch doesn't have run_id, only uptime and status_json)
    validate_response_fields(response, {
        "uptime_seconds": (float, True),  # Numeric fields can be 0
        "status_json": (str, True),  # May be empty
    })
    
    # Validate state is a valid SwitchState enum value (from proto definition)
    valid_states = [
        switch_pb2.SWITCH_STATE_UNSPECIFIED,
        switch_pb2.SWITCH_STATE_IDLE,
        switch_pb2.SWITCH_STATE_INITIALIZING,
        switch_pb2.SWITCH_STATE_READY,
        switch_pb2.SWITCH_STATE_FAULT,
        switch_pb2.SWITCH_STATE_DEINITIALIZING,
        switch_pb2.SWITCH_STATE_DEGRADED,
    ]
    assert response.state in valid_states, \
        f"GetStatus state must be a valid SwitchState enum value, got {response.state}"


def test_set_config(client):
    """Test SetConfig RPC"""
    request = switch_pb2.SetConfigRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        config_json='{"test": "config"}'
    )
    response = client.SetConfig(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)


def test_commit_connection(client):
    """Test CommitConnection RPC"""
    request = switch_pb2.CommitConnectionRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        input_port=1,
        output_port=2,
        routing_case=0
    )
    response = client.CommitConnection(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)


def test_clear_connections(client):
    """Test ClearConnections RPC"""
    request = switch_pb2.ClearConnectionsRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        ports=[1, 2]
    )
    response = client.ClearConnections(request)
    assert response is not None
    
    # Validate message field (must be non-empty)
    validate_response_field(response, "message", str, allow_empty=False)


def test_execute_command(client):
    """Test ExecuteCommand RPC (optional)"""
    request = switch_pb2.ExecuteCommandRequest(
        product_id=TEST_PRODUCT_ID,
        resource_type=TEST_RESOURCE_TYPE,
        command_json='{"command": "test"}'
    )
    implemented, response = check_optional_rpc(lambda: client.ExecuteCommand(request))
    if implemented:
        assert response is not None
        # Validate response_json field (must be non-empty when implemented)
        validate_response_field(response, "response_json", str, allow_empty=False)


def test_trigger_event(client):
    """Test TriggerEvent RPC (optional)"""
    request = switch_pb2.TriggerEventRequest(
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
