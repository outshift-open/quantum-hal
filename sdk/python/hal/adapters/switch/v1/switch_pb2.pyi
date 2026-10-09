# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from hal.adapters.common.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SwitchState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SWITCH_STATE_UNSPECIFIED: _ClassVar[SwitchState]
    SWITCH_STATE_IDLE: _ClassVar[SwitchState]
    SWITCH_STATE_INITIALIZING: _ClassVar[SwitchState]
    SWITCH_STATE_READY: _ClassVar[SwitchState]
    SWITCH_STATE_FAULT: _ClassVar[SwitchState]
    SWITCH_STATE_DEINITIALIZING: _ClassVar[SwitchState]
    SWITCH_STATE_DEGRADED: _ClassVar[SwitchState]
SWITCH_STATE_UNSPECIFIED: SwitchState
SWITCH_STATE_IDLE: SwitchState
SWITCH_STATE_INITIALIZING: SwitchState
SWITCH_STATE_READY: SwitchState
SWITCH_STATE_FAULT: SwitchState
SWITCH_STATE_DEINITIALIZING: SwitchState
SWITCH_STATE_DEGRADED: SwitchState

class GetProductInfoRequest(_message.Message):
    __slots__ = ("product_id", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class GetProductInfoResponse(_message.Message):
    __slots__ = ("serial_number", "product_code", "software_version", "vendor", "switch_sizes")
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_CODE_FIELD_NUMBER: _ClassVar[int]
    SOFTWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FIELD_NUMBER: _ClassVar[int]
    SWITCH_SIZES_FIELD_NUMBER: _ClassVar[int]
    serial_number: str
    product_code: str
    software_version: str
    vendor: str
    switch_sizes: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, serial_number: _Optional[str] = ..., product_code: _Optional[str] = ..., software_version: _Optional[str] = ..., vendor: _Optional[str] = ..., switch_sizes: _Optional[_Iterable[int]] = ...) -> None: ...

class InitializeRequest(_message.Message):
    __slots__ = ("product_id", "config_json", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    config_json: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., config_json: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class InitializeResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class DeinitializeRequest(_message.Message):
    __slots__ = ("product_id", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class DeinitializeResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class GetStatusRequest(_message.Message):
    __slots__ = ("product_id", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class GetStatusResponse(_message.Message):
    __slots__ = ("state", "uptime_seconds", "status_json")
    STATE_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_JSON_FIELD_NUMBER: _ClassVar[int]
    state: SwitchState
    uptime_seconds: float
    status_json: str
    def __init__(self, state: _Optional[_Union[SwitchState, str]] = ..., uptime_seconds: _Optional[float] = ..., status_json: _Optional[str] = ...) -> None: ...

class SetConfigRequest(_message.Message):
    __slots__ = ("product_id", "config_json", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    config_json: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., config_json: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class SetConfigResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class CommitConnectionRequest(_message.Message):
    __slots__ = ("product_id", "input_port", "output_port", "routing_case", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_PORT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_PORT_FIELD_NUMBER: _ClassVar[int]
    ROUTING_CASE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    input_port: int
    output_port: int
    routing_case: int
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., input_port: _Optional[int] = ..., output_port: _Optional[int] = ..., routing_case: _Optional[int] = ..., resource_type: _Optional[str] = ...) -> None: ...

class CommitConnectionResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class ClearConnectionsRequest(_message.Message):
    __slots__ = ("product_id", "ports", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    ports: _containers.RepeatedScalarFieldContainer[int]
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., ports: _Optional[_Iterable[int]] = ..., resource_type: _Optional[str] = ...) -> None: ...

class ClearConnectionsResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class ExecuteCommandRequest(_message.Message):
    __slots__ = ("product_id", "command_json", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_JSON_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    command_json: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., command_json: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class ExecuteCommandResponse(_message.Message):
    __slots__ = ("response_json",)
    RESPONSE_JSON_FIELD_NUMBER: _ClassVar[int]
    response_json: str
    def __init__(self, response_json: _Optional[str] = ...) -> None: ...

class TriggerEventRequest(_message.Message):
    __slots__ = ("product_id", "run_id", "event_type", "payload_json", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_JSON_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    run_id: str
    event_type: str
    payload_json: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., run_id: _Optional[str] = ..., event_type: _Optional[str] = ..., payload_json: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class TriggerEventResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
