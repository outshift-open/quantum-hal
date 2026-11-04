# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class ResourceHealthCheckRequest(_message.Message):
    __slots__ = ("product_id", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class ResourceHealthCheckResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class AutoRecoverRequest(_message.Message):
    __slots__ = ("product_id", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class AutoRecoverResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class TuneRequest(_message.Message):
    __slots__ = ("product_id", "config_json", "resource_type")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_JSON_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    product_id: str
    config_json: str
    resource_type: str
    def __init__(self, product_id: _Optional[str] = ..., config_json: _Optional[str] = ..., resource_type: _Optional[str] = ...) -> None: ...

class TuneResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
