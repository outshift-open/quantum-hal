# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`qentra-hal-api` holds the Protocol Buffer / gRPC **API contracts** for the Hardware
Abstraction Layer (HAL) agents in the Qentra quantum-networking stack. There is no
implementation code here — just the `.proto` service and message definitions that get
compiled into stubs consumed elsewhere (the `go_package` option in each file points at
`github.com/cisco-eti/qentra-controller/pkg/agents/v1/...`, i.e. the `qentra-controller`
repo). There is currently no build/lint/codegen tooling (no `buf.yaml`, `Makefile`, or
`protoc` invocation) checked into this repo — generation happens downstream.

## The HAL agent pattern

Each `.proto` file defines one gRPC service for a class of lab hardware. Every service
follows the same shape, so understanding one means understanding all three:

- **`AgentSource`** (`agent_source.proto`) — entangled-photon source hardware (pump laser,
  TEC, resonance locking). Two RPC groups, called out explicitly in comments:
  - *Common* RPCs (`HealthCheck`, `GetStatus`, `SetConfig`, `Reserve`/`Release`,
    `StartEmission`/`StopEmission`) are served identically by mock and hardware adapters.
  - *Hardware* RPCs (`ResourceHealthCheck`, `Initialize`, `Deinitialize`) drive the real
    physical init sequence; only the hardware adapter actually talks to the device
    (e.g. opens a socket to a Red Pitaya or commands the pump laser).
  - Has an explicit `SourceState` lifecycle (`IDLE` → `INITIALIZING` → `LOCKING` →
    `READY` → `EMITTING`/`DEGRADED`, plus `FAULT`/`DEINITIALIZING`). `Initialize` is
    fire-and-forget — the resonance scan takes minutes, so the RPC returns as soon as
    the sequence is accepted and callers poll `GetStatus`.
  - `Reserve`/`Release` are ownership leases keyed by `run_id`, not hardware actions —
    the control loops keep running underneath; `Release` returns the source to `READY`,
    not `IDLE`.
- **`AgentSwitch`** (`agent_switch.proto`) — optical switch hardware (Polatis, JW, OSW,
  QSwitch). Connection-oriented: `CommitConnection`/`ClearConnections` manage port
  routing; `ExecuteCommand` is a raw pass-through command channel with TCP or serial
  transport config (`oneof connection_config`).
- **`AgentTimeTagger`** (`agent_timetagger.proto`) — time-correlated single-photon
  counting hardware (Swabian). `ListMeasurementTypes` advertises which measurements
  are supported in mock vs. hardware mode per type; `StartDataCollection`/
  `StopDataCollection` are keyed by `runId` and write to an InfluxDB bucket.

### Cross-cutting conventions

- **`ResourceType` enum per service**: identifies which hardware family/vendor a
  request targets (matches `hardware_resource.type` in the controller database).
  Nearly every request message carries one. `RESOURCE_TYPE_UNSPECIFIED` (`= 0`) is
  rejected with `INVALID_ARGUMENT` rather than defaulted — a single running HAL server
  process dispatches on this field to serve every hardware family for that agent type
  at once (see `src/source/grpc/hal.py` referenced in `agent_source.proto`, which lives
  in the implementation repo, not here).
- **`HealthCheck` vs `ResourceHealthCheck`**: `HealthCheck` is liveness of the adapter
  *process* itself (no args). `ResourceHealthCheck` checks the hardware *behind* the
  adapter and takes `product_id` + `resource_type`.
- **Mock vs. hardware adapters**: every service is implemented twice downstream — a
  mock (simulates behavior, no real I/O) and a real hardware adapter — behind the same
  proto contract, selected by `resource_type` and/or deployment config.
- **Response messages are thin**: most responses are just `{ string message = 1; }`
  (or `ServerOutput`/`TimeTaggerServerOutput` in the switch/timetagger services) —
  state is queried separately (e.g. `GetStatus`), not returned inline from action RPCs.
- **Wire-compatibility discipline**: enum values are never renumbered once shipped —
  see the comment on `SourceState` explaining why values 1-3 keep their original
  numbers, and fields kept only for wire compatibility (e.g. `SourceConfig.mrr_current_ma`,
  `chip_temperature_c`) even after the underlying actuator/control strategy changed.
  When deprecating a field, prefer a comment explaining why it's now unused over
  removing/renumbering it.

## Working in this repo

- Package naming: `qentra.agents.<domain>.v1` proto package, mirrored by
  `github.com/cisco-eti/qentra-controller/pkg/agents/v1/<domain>` Go package.
- When adding a new HAL agent service, follow the existing pattern: a `ResourceType`
  enum scoped to that hardware class, `HealthCheck`/`ResourceHealthCheck` split, and
  `resource_type` (plus `product_id` or `run_id` where relevant) on every request.
