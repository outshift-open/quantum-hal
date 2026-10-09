# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from hal.adapters.common.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SourceState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOURCE_STATE_UNSPECIFIED: _ClassVar[SourceState]
    SOURCE_STATE_IDLE: _ClassVar[SourceState]
    SOURCE_STATE_EMITTING: _ClassVar[SourceState]
    SOURCE_STATE_FAULT: _ClassVar[SourceState]
    SOURCE_STATE_INITIALIZING: _ClassVar[SourceState]
    SOURCE_STATE_LOCKING: _ClassVar[SourceState]
    SOURCE_STATE_READY: _ClassVar[SourceState]
    SOURCE_STATE_DEGRADED: _ClassVar[SourceState]
    SOURCE_STATE_DEINITIALIZING: _ClassVar[SourceState]
SOURCE_STATE_UNSPECIFIED: SourceState
SOURCE_STATE_IDLE: SourceState
SOURCE_STATE_EMITTING: SourceState
SOURCE_STATE_FAULT: SourceState
SOURCE_STATE_INITIALIZING: SourceState
SOURCE_STATE_LOCKING: SourceState
SOURCE_STATE_READY: SourceState
SOURCE_STATE_DEGRADED: SourceState
SOURCE_STATE_DEINITIALIZING: SourceState

class GetProductInfoRequest(_message.Message):
    __slots__ = ("product_id", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class GetProductInfoResponse(_message.Message):
    __slots__ = ("serial_number", "product_code", "software_version", "vendor")
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_CODE_FIELD_NUMBER: _ClassVar[int]
    SOFTWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FIELD_NUMBER: _ClassVar[int]
    serial_number: str
    product_code: str
    software_version: str
    vendor: str
    def __init__(self, serial_number: _Optional[str] = ..., product_code: _Optional[str] = ..., software_version: _Optional[str] = ..., vendor: _Optional[str] = ...) -> None: ...

class SourceConfig(_message.Message):
    __slots__ = ("config_json",)
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    config_json: str
    def __init__(self, config_json: _Optional[str] = ...) -> None: ...

class InitializeRequest(_message.Message):
    __slots__ = ("product_id", "config", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    config: SourceConfig
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., config: _Optional[_Union[SourceConfig, _Mapping]] = ..., resource_type: _Optional[str] = ...) -> None: ...

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
    __slots__ = ("state", "run_id", "uptime_seconds", "status_json")
    STATE_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_JSON_FIELD_NUMBER: _ClassVar[int]
    state: SourceState
    run_id: str
    uptime_seconds: float
    status_json: str
    def __init__(self, state: _Optional[_Union[SourceState, str]] = ..., run_id: _Optional[str] = ..., uptime_seconds: _Optional[float] = ..., status_json: _Optional[str] = ...) -> None: ...

class SetConfigRequest(_message.Message):
    __slots__ = ("product_id", "config", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    config: SourceConfig
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., config: _Optional[_Union[SourceConfig, _Mapping]] = ..., resource_type: _Optional[str] = ...) -> None: ...

class SetConfigResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class StartEmissionRequest(_message.Message):
    __slots__ = ("product_id", "run_id", "config", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    run_id: str
    config: SourceConfig
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., run_id: _Optional[str] = ..., config: _Optional[_Union[SourceConfig, _Mapping]] = ..., resource_type: _Optional[str] = ...) -> None: ...

class StartEmissionResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class StopEmissionRequest(_message.Message):
    __slots__ = ("product_id", "run_id", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    run_id: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., run_id: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class StopEmissionResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

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
