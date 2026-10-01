# Conformance Tests

## Purpose

These tests are used to verify the basic runtime validation of an adapters implementation per the HAL API specification. These tests do not verify the actual functionality of the adapter. They ensure:
- Adapters returns valid responses as per the HAL API specification
- All required fields are present and correctly formatted as per of the response structure
- Optional RPCs if implemented by the server are verified or skipped if unimplemented.

These tests are designed to be run against a running adapter instance. They do not start the adapters themselves. Please see the instruction below for running the tests with a specific adapter instance.

## Architecture

```
┌─────────────────────────┐                    ┌──────────────────────────┐
│   Test Machine          │                    │   Adapter                │
│                         │                    │   (any location)         │
│  Python Test            │    gRPC/HTTP2      │                          │
│  + Python Stubs ────────┼───────────────────►│   Adapter Implementation │
│  (gen/python/hal/...)   │   Wire Protocol    │   + Stubs                │
│                         │                    │   (Go/Python/any)        │
└─────────────────────────┘                    └──────────────────────────┘
```

## Key Design Principles

### 1. Language-Agnostic Testing

The conformance tests communicate with adapters over gRPC, which means:
- **Tests are in Python** - Using pytest and generated Python stubs
- **Adapters can be in any language** - Go, Python, Rust, Java, C++, etc.
- **Communication via wire protocol** - Protocol Buffers over HTTP/2
- **No shared code required** - Only the `.proto` contract matters

### 2. Location-Agnostic Testing

Adapters can run anywhere:
- **Localhost** - For quick validation
- **Remote servers** - Production deployment with access and connectivity to the adapter from the test machine

Configuration is via environment variables in `.env`:
```bash
SOURCE_ADAPTER_ADDRESS=remote-server.example.com:50051
SWITCH_ADAPTER_ADDRESS=10.0.1.100:50052
TIMETAGGER_ADAPTER_ADDRESS=adapter.cloud.com:9000
```

## Setup

### 1. Generate Python stubs

Install grpcio-tools (if not already installed):

```bash
pip install `grpcio-tools>=1.84.0`
```

Generate stubs from repository root:

```bash
mkdir -p gen/python
python -m grpc_tools.protoc \
  --proto_path=proto \
  --python_out=gen/python \
  --grpc_python_out=gen/python \
  proto/hal/adapters/common/v1/common.proto \
  proto/hal/adapters/source/v1/source.proto \
  proto/hal/adapters/switch/v1/switch.proto \
  proto/hal/adapters/timetagger/v1/timetagger.proto
```

**Note:** Stubs are generated to `gen/python/` at the repository root so they can be used as a shared dependency. 

### 2. Configure environment

```bash
cd test/conformance
cp .env.example .env
# Edit .env to set adapter addresses
```

Adapter addresses should be set in `.env` :

```bash
SOURCE_ADAPTER_ADDRESS=localhost:50051
SWITCH_ADAPTER_ADDRESS=localhost:50052
TIMETAGGER_ADAPTER_ADDRESS=localhost:50053
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```
**Note:** The `conftest.py` (supported by pytest) automatically reads the env and adds the `gen/python/` path for tests to import the generated stubs.

## Running Tests

### Test all adapters
```bash
python -m pytest -v
```

### Test specific adapter
```bash
python -m pytest source/test_source.py -v
python -m pytest switch/test_switch.py -v
python -m pytest timetagger/test_timetagger.py -v
```

### Test specific RPC
```bash
python -m pytest source/test_source.py::test_health_check -v
```
