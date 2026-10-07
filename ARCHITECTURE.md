# Architecture

This is the deep dive behind [`README.md`](./README.md): where the HAL
fits in the system that uses it, why the spec in this repo is shaped the
way it is, and what each device type's hardware actually does.

## Where HAL fits

The HAL exists to serve one job: letting the Cisco Quantum Network
Controller run a quantum-networking intent task — for example, an
entanglement-distribution request between two endpoints — without caring
which vendor's hardware is on the bench. Running a task means bringing up
and coordinating several pieces of lab hardware at once: a source
generating entangled photon pairs, switches routing them through the
optical path, and time taggers recording the detector clicks used to
measure coincidence rate, CAR (coincidence-to-accidental ratio),
pair rate or whatever the experiment is measuring.

The controller never talks to that hardware directly. It talks to
**adapters** — one gRPC server per device type — over the contract defined
in this repo, and each adapter owns everything below that boundary:
translating HAL calls into whatever the vendor's SDK, driver, or wire
protocol requires, or simulating that behavior entirely (a mock adapter)
when no bench hardware is attached.

```
                     gRPC (this repo's contract)      vendor SDK / driver / API
 Controller  <----------------------------------->  Adapter  <----------------------->  Physical device
   (client)                                     (gRPC server,
                                               one process per
                                              device type; mock or
                                             hardware behind the
                                                 same contract)
```

Why put a HAL between them at all, rather than have the controller talk to
each vendor's SDK directly:

- **The controller's code doesn't change per vendor.** Swapping which
  optical switch is on the bench, or adding a second source vendor, is an
  adapter-side change plus a controller-side product registration — not a
  controller code change.
- **Development and CI don't need a bench.** A mock adapter implements the
  exact same service the hardware adapter does, so the controller (and
  anyone testing against it) can run without physical devices attached.
- **One adapter process can front more than one physical unit.**
  `product_id` picks the unit; `resource_type` picks which onboarded
  product family it belongs to. A single running adapter dispatches on
  both rather than needing one process per device.
- **Third parties can build an adapter without touching controller code.**
  That's the whole reason this spec lives in its own repo: build to the
  contract, and the controller drives your device the same way it drives
  every other one of that type.

## The device types

### Source — entangled-photon generation

`AdapterSourceService` (`hal.adapters.source.v1`) fronts hardware that
generates entangled photon pairs — bring-up involves pump-laser power,
temperature/TEC setpoint control, and laser resonance locking, then a
multi-minute temperature sweep and resonance-dip acquisition before the
source is usable (`SourceState`: `IDLE` → `INITIALIZING` →
`LOCKING` → `READY`).

Because that bring-up sequence can take minutes, `Initialize` and
`AutoRecover` are **fire-and-poll**: the RPC returns as soon as the
sequence is *accepted*, not once it's *done*, and the caller polls
`GetStatus` for the outcome. This is different from switch and time
tagger, where the equivalent operations are fast enough to just block.

A task binds a source to itself via `StartEmission(run_id, ...)`, which
moves the source into `SOURCE_STATE_EMITTING` — busy, and unavailable for
another task — until `StopEmission` returns it to `READY`.

### Switch — optical path routing

`AdapterSwitchService` (`hal.adapters.switch.v1`) fronts optical switch
fabrics (e.g. MEMS-mirror-based) that route signals between ports.
`Initialize` homes and calibrates the fabric — fast enough that, unlike
source, the call is expected to **block until it completes** rather than
requiring a status poll.

There's no busy/emitting state here: `CommitConnection(input_port,
output_port, routing_case)` and `ClearConnections(ports)` are treated as
near-instant path changes, not long-running operations bound to a task.
`routing_case` distinguishes "bar" (straight-through) vs. "cross" routing
for fabrics that support more than one mode; adapters for simpler hardware
can ignore it.

Switch is also the one device type with `ExecuteCommand` — a raw
vendor-passthrough channel for provisioning or diagnostic commands that
don't have a structured equivalent elsewhere in the service. It's
optional; adapters with no need for it return `UNIMPLEMENTED`.

### Time tagger — timing/coincidence data collection

`AdapterTimeTaggerService` (`hal.adapters.timetagger.v1`) fronts
time-correlated single-photon counting hardware — the equipment that
records detector-click timestamps used for heralding or QBER measurement
during a task. Bring-up varies by product: some need to connect and load
calibration; others are ready as soon as they're powered, in which case
`Initialize` (and `AutoRecover`) can be an immediate no-op that reports
`READY` right away.

A task binds a time tagger to itself via `StartDataCollection(run_id,
config_json)`, moving it into `TIME_TAGGER_STATE_COLLECTING` until
`StopDataCollection` returns it to `READY`. Which channels to record,
coincidence windows, per-channel delays, and where results are written are
all vendor-specific and carried in `config_json` rather than modeled as
typed fields.

## The DEGRADED recovery pattern, generalized

Every device type's lifecycle enum includes a `DEGRADED` value alongside
`FAULT` — signaling "still basically working, but something is off spec"
(a loop out of tolerance on source, elevated insertion loss on switch, a
noisy channel on time tagger). The controller has two ways to respond
without a full `Deinitialize`/`Initialize` cycle:

- **`AutoRecover`** — run the adapter's own built-in remediation (re-run a
  resonance lock, re-home a fabric, reconnect and reload calibration —
  whatever's appropriate for that product).
- **`Tune`** — apply one narrower, targeted adjustment instead (nudge a
  single setpoint, re-home one path, re-calibrate one channel) via
  `config_json`. Adapters without this kind of fine-grained control return
  `UNIMPLEMENTED`.

Every service also exposes `TriggerEvent` — a generic, adapter-defined,
optional hook for anything a device needs mid-task that doesn't fit the
RPCs above: fault injection or an environmental perturbation for testing,
or anything else a specific product requires. Same `UNIMPLEMENTED` escape
hatch applies if an adapter has no such capability.

## Design conventions, and why

**`resource_type` is an opaque string, not an enum.** Enumerating every
onboarded product in the proto itself would mean a spec change every time
the controller onboards new hardware — which defeats the point of a
stable, versioned contract for third parties to build against. Instead,
the controller maintains its own registry of onboarded product types, and
an adapter is simply told (out of band, at onboarding time) which
identifier to use. `resource_type` — along with `product_id`, which picks
the specific physical unit when an adapter fronts more than one — is never
defaulted: omitting either is rejected with `INVALID_ARGUMENT`, because
guessing which bench hardware a request meant is worse than failing loudly.

**Vendor-specific data travels as JSON strings, not typed proto fields.**
`config_json`, `status_json`, `command_json`, and `payload_json` show up
across all three services. This spec deliberately doesn't try to model
every vendor's operating parameters, status detail, or command shape —
doing so would mean a proto change (and a version bump) every time a new
product has a field the others don't. Each adapter implementation defines
and documents its own JSON schema for these fields and is solely
responsible for parsing them; neither the controller nor this spec ever
interprets their contents.

**Wire-compatibility discipline.** Field numbers and enum values, once
shipped, are never reused or renumbered — retired fields get `reserved`
rather than being deleted and reused; deprecated behavior gets a comment
explaining why it's unused rather than silent removal. A breaking change
to one device type's contract gets a new version directory
(`proto/hal/adapters/<type>/v2/`) rather than an in-place edit to `v1`,
which is also why each device type versions independently — a `switch.v2`
doesn't force a `source.v2`.

**`HealthCheck` vs. `ResourceHealthCheck`.** These answer two different
questions that are easy to conflate: `HealthCheck` is liveness of the
*adapter process* itself (no hardware access, no arguments) — is the
service even reachable. `ResourceHealthCheck` is health of the *physical
device* behind it, as reported by whatever the vendor's own driver/API
exposes, translated into an UP/DOWN/DEGRADED-style result that may be
informed by the device's own lifecycle state.

## Where the implementation lives

This repo intentionally contains no controller code, adapter
implementations, or vendor drivers — only the contract. The `.proto` files
also deliberately omit `go_package` (and equivalents for other languages);
see `buf.gen.yaml`'s managed-mode config for how that's injected at
generation time instead. That keeps this spec decoupled from any one
consumer's internal module layout — including the controller's own
codebase, wherever your team currently vendors the generated stubs from.
