# Cisco's Quantum Network Controller - HAL (Hardware Abstraction Layer) API

The **Cisco's Quantum Network Controller** orchestrates the
hardware behind quantum-networking experiments — bringing devices up,
running jobs or networking intent such as an entanglement-distribution intent between two
endpoints, and monitoring and recovering hardware health while a job runs.
It does this by driving each physical device through a **Hardware
Abstraction Layer (HAL)**: a fixed gRPC contract that every device-type
adapter implements, so the controller drives a source, a switch, or a time
tagger the same way regardless of vendor.

**This repo is that contract, and only that contract.** It holds the
Protocol Buffer / gRPC service and message definitions for the HAL — no
controller code, no adapter implementations, no vendor drivers. That
separation is deliberate: any team building a device adapter (in-house or
third-party) integrates against a single, versioned spec, independent of
how the controller or any other adapter happens to be implemented
internally.

For the deeper look — how the controller, adapters, and physical devices
fit together, why the HAL is shaped the way it is, and what each device
type's hardware actually does — see [`ARCHITECTURE.md`](./ARCHITECTURE.md).
This README stays focused on the spec itself.

## Proto spec at a glance

Three device types are defined today. Each gets its own gRPC service and
its own independently-versioned package; a shared `common` package holds
the request/response shapes every service reuses.

| Package | Service | Device |
|---|---|---|
| `hal.adapters.common.v1` | *(shared messages, no service)* | — |
| `hal.adapters.source.v1` | `AdapterSourceService` | Entangled-photon source |
| `hal.adapters.switch.v1` | `AdapterSwitchService` | Optical switch |
| `hal.adapters.timetagger.v1` | `AdapterTimeTaggerService` | Time-correlated single-photon counter |

All three services are built from the same RPC groups, in the same order —
learn the shape once and all three read the same way. Where a device type
doesn't have an RPC, it's marked `—`; where its behavior diverges from the
others, that's called out in the last column.

| RPC | Source | Switch | Time Tagger | What it does |
|---|---|---|---|---|
| `HealthCheck` | ✓ | ✓ | ✓ | Adapter process liveness (no hardware access) |
| `ResourceHealthCheck` | ✓ | ✓ | ✓ | Health of the physical device behind the adapter |
| `GetProductInfo` | ✓ | ✓ | ✓ | Serial number, vendor, firmware/software version |
| `Initialize` | ✓ — async, can take minutes; poll `GetStatus` | ✓ — sync, blocks (homing is fast) | ✓ — sync or immediate no-op | Bring the device up to its `READY` state |
| `Deinitialize` | ✓ | ✓ | ✓ | Orderly shutdown back toward `IDLE` |
| `GetStatus` | ✓ | ✓ | ✓ | Current lifecycle state + vendor-specific detail |
| `SetConfig` | ✓ | ✓ | ✓ | Update operating config without a full re-init |
| `AutoRecover` | ✓ — async | ✓ — sync | ✓ | Adapter's own remediation from `DEGRADED`/`FAULT` |
| `Tune` | ✓ | ✓ | ✓ | One narrower, targeted fix instead of full recovery |
| `StartEmission` / `StopEmission` | ✓ | — | — | Start/stop generating entangled pairs for a run |
| `CommitConnection` / `ClearConnections` | — | ✓ | — | Set/tear down a signal path between ports |
| `StartDataCollection` / `StopDataCollection` | — | — | ✓ | Start/stop recording detector-click data for a run |
| `ExecuteCommand` | — | ✓ *(optional)* | — | Raw vendor passthrough command |
| `TriggerEvent` | ✓ *(optional)* | ✓ *(optional)* | ✓ *(optional)* | Adapter-defined mid-job hook (fault injection, environmental perturbation, etc.) — `UNIMPLEMENTED` if the adapter has no such capability |

Lifecycle states follow the same pattern in every service — `IDLE` →
bring-up → `READY` → a device-specific "busy" state while a job is bound to
it, with `DEGRADED`/`FAULT` as the two ways things go wrong:

| State | Source (`SourceState`) | Switch (`SwitchState`) | Time Tagger (`TimeTaggerState`) |
|---|---|---|---|
| Idle | `SOURCE_STATE_IDLE` | `SWITCH_STATE_IDLE` | `TIME_TAGGER_STATE_IDLE` |
| Initializing | `SOURCE_STATE_INITIALIZING` | `SWITCH_STATE_INITIALIZING` | `TIME_TAGGER_STATE_INITIALIZING` |
| *(source only)* Locking | `SOURCE_STATE_LOCKING` | — | — |
| Ready | `SOURCE_STATE_READY` | `SWITCH_STATE_READY` | `TIME_TAGGER_STATE_READY` |
| Busy (bound to a run) | `SOURCE_STATE_EMITTING` | *(none — connection changes are near-instant)* | `TIME_TAGGER_STATE_COLLECTING` |
| Degraded | `SOURCE_STATE_DEGRADED` | `SWITCH_STATE_DEGRADED` | `TIME_TAGGER_STATE_DEGRADED` |
| Fault | `SOURCE_STATE_FAULT` | `SWITCH_STATE_FAULT` | `TIME_TAGGER_STATE_FAULT` |
| Deinitializing | `SOURCE_STATE_DEINITIALIZING` | `SWITCH_STATE_DEINITIALIZING` | `TIME_TAGGER_STATE_DEINITIALIZING` |

### Conventions every integrator should know

- **`resource_type` is an opaque string, not an enum.** The controller
  registers which product types it has onboarded; your adapter sets this
  field to whatever identifier the controller assigned your product.
  Omitting it (or `product_id`) on a device-scoped request is rejected
  with `INVALID_ARGUMENT` — neither is ever defaulted.
- **Vendor-specific data travels as JSON, not typed fields.**
  `config_json`, `status_json`, `command_json`, `payload_json` are
  deliberately opaque strings. This spec doesn't model per-vendor
  parameters; your adapter defines and documents its own schema for them,
  and the controller never interprets their contents.
- **Fields and enum values, once shipped, don't move.** Retired fields get
  `reserved`, not deleted-and-reused slots; enum values keep their
  original numbers even after what they mean has evolved. A breaking
  change to one device type gets a new version directory
  (`proto/hal/adapters/<type>/v2/`), not an edit in place to `v1`.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the reasoning behind each of
these, and for how `AutoRecover`/`Tune` and the async-vs-sync split on
`Initialize` map onto the physical hardware for each device type.

## Repository layout

```
proto/
  buf.yaml                              # lint/breaking-change config
  hal/adapters/
    common/v1/common.proto              # shapes shared by every device type
    source/v1/source.proto              # AdapterSourceService
    switch/v1/switch.proto              # AdapterSwitchService
    timetagger/v1/timetagger.proto      # AdapterTimeTaggerService
```

Each device-type package is versioned independently
(`hal.adapters.<type>.v1`), so one device type's spec can evolve without
forcing a version bump on the others. Adding a new device type means
adding a new `proto/hal/adapters/<type>/v1/` package that follows the same
shape as the existing three — it doesn't change how the controller or
existing adapters work.

## Building and validating

This repo uses [Buf](https://buf.build) rather than raw `protoc` for
linting and breaking-change detection.

```sh
buf build proto    # confirms everything compiles/resolves
buf lint proto     # style/consistency checks (see proto/buf.yaml for the one
                    # deliberate exception and why)
```

## Generating stubs

**Go** is generated via Buf (`buf.gen.yaml`, using
[managed mode](https://buf.build/docs/generate/managed-mode/) to inject
`go_package` at generation time, since these `.proto` files deliberately
don't set it themselves):

```sh
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

buf generate proto   # writes to ./gen/go (gitignored -- not committed here)
```

Before generating for real, update `go_package_prefix.default` in
`buf.gen.yaml` to wherever you actually vendor/import the generated code
from.

**Python** is off by default (`buf generate proto` only writes `./gen/go`
unless you opt in) — uncomment the `plugin: python` block in
`buf.gen.yaml` to enable it; full instructions are in the comment right
above that block.

**Other languages** aren't wired into `buf.gen.yaml` — generate them
directly with `protoc`/that language's plugin.

See [`INTEGRATION.md`](./INTEGRATION.md) for the raw-`protoc` equivalent,
a worked client example, exploring a running adapter with `grpcurl` via
gRPC reflection, and version pinning once tags exist.

## Further reading

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — how the controller, adapters,
  and physical devices fit together; what each device type's hardware
  does; and the reasoning behind the spec's design conventions.
- [`INTEGRATION.md`](./INTEGRATION.md) — generating stubs, a worked
  client example, and exploring a running adapter without writing code.
- [`CHANGELOG.md`](./CHANGELOG.md) — what's changed release to release,
  and the versioning policy.

## License

Copyright 2026 Cisco Systems, Inc. and its affiliates.

Licensed under the Apache License, Version 2.0. See [`LICENSE.md`](./LICENSE.md).
