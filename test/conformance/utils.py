# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Utility functions for conformance tests"""
import grpc


def is_unimplemented(error):
    """
    Check if a gRPC error is UNIMPLEMENTED status.
    
    Args:
        error: The exception to check
    
    Returns:
        bool: True if error is UNIMPLEMENTED, False otherwise
    
    Note:
        UNIMPLEMENTED is acceptable for optional RPCs in the HAL API.
    """
    return isinstance(error, grpc.RpcError) and error.code() == grpc.StatusCode.UNIMPLEMENTED


def check_optional_rpc(rpc_call):
    """
    Helper to test optional RPCs that may return UNIMPLEMENTED.
    
    Args:
        rpc_call: Callable that makes the RPC call
    
    Returns:
        tuple: (implemented: bool, response: object or None)
               - If RPC is implemented: (True, response)
               - If RPC returns UNIMPLEMENTED: (False, None)
    
    Raises:
        grpc.RpcError: If RPC fails with any status other than UNIMPLEMENTED
    
    Note:
        Optional RPCs in HAL API may return UNIMPLEMENTED. This helper treats
        both successful responses and UNIMPLEMENTED as acceptable outcomes.
    """
    try:
        response = rpc_call()
        return True, response
    except grpc.RpcError as e:
        if is_unimplemented(e):
            return False, None
        raise


def validate_response_field(response, field_name, field_type, allow_empty=False):
    """
    Validate a response field exists, has correct type, and optionally is non-empty.
    
    Args:
        response: The protobuf response message
        field_name: Name of the field to validate
        field_type: Expected Python type (str, int, float, etc.)
        allow_empty: If False, string fields must be non-empty
    
    Raises:
        AssertionError: If validation fails
    
    Note:
        Due to Protocol Buffers' wire format limitations, this cannot detect when a
        server returns the wrong response type if both types have identical field
        structures. Proto3 creates all fields with default values even if not sent,
        so we can only check for non-empty values to detect potential type mismatches.
    """
    # Check field exists (always true in proto3, but explicit for clarity)
    assert hasattr(response, field_name), \
        f"Response missing '{field_name}' field - wrong response type returned"
    
    # Get field value
    field_value = getattr(response, field_name)
    
    # Validate type
    assert isinstance(field_value, field_type), \
        f"Field '{field_name}' should be {field_type.__name__}, got {type(field_value).__name__}"
    
    # Validate non-empty for strings (if required)
    if not allow_empty and field_type == str:
        assert field_value, \
            f"Field '{field_name}' should not be empty - wrong response type or server didn't set field"


def validate_response_fields(response, field_specs):
    """
    Validate multiple response fields at once.
    
    Args:
        response: The protobuf response message
        field_specs: Dict mapping field names to (type, allow_empty) tuples
                    Example: {"message": (str, False), "count": (int, True)}
    
    Raises:
        AssertionError: If any field validation fails
    """
    for field_name, (field_type, allow_empty) in field_specs.items():
        validate_response_field(response, field_name, field_type, allow_empty)
