# Cisco's Quantum Network Controller - HAL API

Protocol Buffer / gRPC contracts for the Hardware Abstraction Layer (HAL)
that sits between our controller and the lab hardware it drives. This repo
contains **only the API contract** — no implementation. It exists so that
any team building a device adapter (in-house or third-party) has a single,
versioned spec to build against, independent of how our controller happens
to be implemented internally.

## Architecture

```
                     gRPC                          vendor SDK / driver / API
 Controller  <---------------------->  Adapter  <---------------------------->  Physical device
                                     (one process
                                    per device type,
                                  implements one of the
                                  services below)
```

- The **controller** is the client: it calls into adapters to drive lab
  hardware as part of running jobs (e.g. an entanglement-distribution
  intent between two endpoints).
- An **adapter** is a gRPC server implementing one of the services in this
  repo. It owns everything below the API boundary: talking to the real
  device over whatever vendor SDK/driver/socket/serial protocol applies, or
  simulating that hardware (a "mock" adapter) for development and testing
  without a bench setup.
- Today there are three device types — **source** (entangled-photon
  sources), **switch** (optical switches), **time tagger**
  (time-correlated single-photon counting hardware) — and the set is meant
  to grow: adding a new device type means adding a new
  `proto/hal/adapters/<type>/v1/` package that follows the same shape as
  the existing three, not changing how the controller or existing adapters
  work.

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

Each device-type package is versioned independently (`hal.adapters.<type>.v1`)
so one device type's spec can evolve without forcing a version bump on the
others. See [`CHANGELOG.md`](./CHANGELOG.md) for what's changed release to
release, and [`INTEGRATION.md`](./INTEGRATION.md) for how to generate client
or server stubs and a worked example.

## What every service looks like

All three device-type services are built from the same five RPC groups, in
the same order — learn the shape once, and `AdapterSourceService`,
`AdapterSwitchService`, and `AdapterTimeTaggerService` all read the same
way. Four of the five groups are identical across all three:

| Group | RPCs | What it's for |
|---|---|---|
| Liveness & discovery | `HealthCheck`, `ResourceHealthCheck`, `GetProductInfo` | Is the adapter process up, is the device behind it healthy, what device is it (serial number, vendor, firmware) |
| Lifecycle | `Initialize`, `Deinitialize` | Bring the device up to its READY state and back down |
| Status & configuration | `GetStatus`, `SetConfig` | Current lifecycle state + vendor-specific detail; adjust operating config without a full re-init |
| Recovery | `AutoRecover`, `Tune` | Called when `GetStatus` reports `DEGRADED`/`FAULT`: `AutoRecover` runs the adapter's own built-in remediation, `Tune` applies one narrower, targeted fix instead |

The fifth group is where each device type actually earns its name — this is
the part worth reading closely per service:

| | `AdapterSourceService` | `AdapterSwitchService` | `AdapterTimeTaggerService` |
|---|---|---|---|
| **Domain action** | `StartEmission` / `StopEmission` | `CommitConnection` / `ClearConnections` | `StartDataCollection` / `StopDataCollection` |
| **"Busy" state** | `SOURCE_STATE_EMITTING` | *(none — connection changes are near-instant, no busy window)* | `TIME_TAGGER_STATE_COLLECTING` |
| **Extra optional RPC** | — | `ExecuteCommand` (raw vendor passthrough) | — |
| **`Initialize`/`AutoRecover` timing** | Async — returns as soon as accepted, poll `GetStatus` (bring-up can take minutes) | Synchronous — blocks until done (homing is fast) | Either — may be an immediate no-op if the product needs no bring-up |

Every service also has `TriggerEvent`: a generic, adapter-defined hook for
anything a device needs mid-job that doesn't fit the RPCs above (fault
injection for testing, an environmental perturbation, or anything else a
specific product requires). Like `ExecuteCommand`, it's optional — an
adapter with no such capability returns `UNIMPLEMENTED`.

Every device-scoped request, across every RPC in every group, carries
`product_id` (which physical unit — one adapter can front multiple devices
of the same product) and `resource_type` (which onboarded product type).
Neither is defaulted: omitting either is rejected with `INVALID_ARGUMENT`.

### Design conventions worth knowing before you integrate

- **`resource_type` is an opaque string, not an enum.** The controller
  maintains its own registry of which product types it has onboarded;
  onboarding a new one is a controller-side change, not a change to this
  spec. Your adapter sets it to whatever identifier the controller has
  assigned your product.
- **Vendor-specific data travels as JSON, not typed fields.** Fields like
  `config_json` and `status_json` are deliberately opaque strings — this
  spec doesn't try to model every vendor's operating parameters or status
  detail. Your adapter defines and documents its own JSON schema for these
  and is responsible for parsing/populating them; the controller and this
  spec never interpret their contents.
- **Every device type has the same DEGRADED-driven recovery pattern.**
  Each lifecycle state enum (`SourceState`, `SwitchState`,
  `TimeTaggerState`) includes a `..._DEGRADED` value alongside `..._FAULT`.
  When the controller observes DEGRADED via `GetStatus`, it can call
  `AutoRecover` (let the adapter run its own remediation) or `Tune` (a
  narrower, targeted fix) rather than a full `Deinitialize`/`Initialize`
  cycle.
- **Lifecycle RPCs aren't always async.** `Initialize`/`AutoRecover` on
  source are documented as fire-and-poll (the operation can take minutes,
  so the call returns as soon as it's accepted and the caller polls
  `GetStatus`). Switch's equivalents are documented as synchronous/blocking
  since homing is fast. Read each service's RPC comments — don't assume one
  device type's behavior applies to another.

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
don't set it themselves — see the design conventions above):

```sh
# install the plugins buf shells out to, once:
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

buf generate proto   # writes to ./gen/go (gitignored -- not committed here)
```

Before generating for real, update `go_package_prefix.default` in
`buf.gen.yaml` to match wherever you actually vendor/import the generated
code from, then set `go_package_prefix.default` to that module path.

**Python** is off by default (`buf generate proto` only writes `./gen/go`
unless you opt in), since not everyone needs both languages. To generate
Python too, uncomment the `plugin: python` block in `buf.gen.yaml` — full
instructions are in the comment right above it, including the follow-up
`grpc_tools` command needed for the gRPC service stubs (Python's gRPC
codegen is bundled inside the `grpc_tools.protoc` module itself rather than
exposed as a standalone plugin binary buf can shell out to, so it can't
join `buf generate` without depending on a remote Buf Schema Registry
plugin — the exact third-party dependency this repo avoids).

**Other languages** aren't wired into `buf.gen.yaml` — generate them
directly with `protoc`/that language's plugin. See
[`INTEGRATION.md`](./INTEGRATION.md) for the raw `protoc` equivalent for Go,
a worked client example, how to explore a running adapter with `grpcurl`
via gRPC reflection, and version pinning once tags exist.

## License

Not yet finalized — see [`LICENSE`](./LICENSE) for the open decisions and a
placeholder notice. Until that file is replaced with real license text,
treat this spec as internal and confirm usage rights with the owning team
before building against it externally.
