# Changelog

All notable changes to this API spec are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Three device-type services: `AdapterSourceService`,
  `AdapterSwitchService`, `AdapterTimeTaggerService`, each versioned
  independently under `hal.adapters.<type>.v1`.
- `hal.adapters.common.v1` package with the request/response shapes shared
  across every device type: `HealthCheck`, `ResourceHealthCheck`,
  `AutoRecover`, `Tune`.
- Per-device lifecycle state enums (`SourceState`, `SwitchState`,
  `TimeTaggerState`) with a consistent `DEGRADED`/`FAULT` recovery story:
  `AutoRecover` runs the adapter's own remediation, `Tune` applies a single
  targeted adjustment.
- `TriggerEvent` — a generic, optional, adapter-defined hook for anything a
  device needs mid-job that doesn't fit the rest of the service (fault
  injection for testing, an environmental perturbation, or anything else a
  product needs).
- `resource_type` as an opaque, controller-assigned string on every
  device-scoped request: onboarding a new product is a controller-side
  registration, never a change to this spec.
- `config_json`/`status_json`/`command_json` conventions for vendor-specific
  operating parameters and status detail, so this spec never has to model
  per-vendor fields directly.
- `proto/buf.yaml` with lint and breaking-change configuration.
- `buf.gen.yaml` for Go (with managed mode), generating straight into
  `sdk/go`; Python is generated via `grpc_tools.protoc` into `sdk/python`
  (see `Makefile`/`INTEGRATION.md`).
- SDK registry workflow: `sdk/go` and `sdk/python` are now generated,
  license-headered (`scripts/add-license-headers.sh`), and committed
  in-repo rather than left to each consumer to generate locally.
  Contributors run `make generate` and commit the result as part of their
  PR; three GitHub Actions workflows guard it:
  - `proto-ci.yml` — PR checks: `buf lint`, `buf breaking`, and a
    stale-SDK check that regenerates both SDKs and fails the pipeline if
    the committed `sdk/go`/`sdk/python` don't match fresh codegen,
    whenever a PR touches `proto/**`, so proto and generated code can't
    drift apart.
  - `license-headers.yml` — on every PR and push to `main`:
    `scripts/check-license-headers.sh` fails if any `.proto`/`.go`/`.py`/
    `.yml`/`.yaml`/`.sh` file (hand-written or generated) is missing the
    copyright/SPDX header.
  - `publish.yaml` — on tag push: validates both SDKs actually install
    from GitHub source (`go get`/`pip install git+...`), and creates the
    nested `sdk/go/vX.Y.Z` tag Go's module resolver requires for `sdk/go`.
  Release tags are cut manually by a maintainer
  (`git tag vX.Y.Z && git push origin vX.Y.Z`) once a PR with up-to-date
  generated SDKs has merged to `main` — there is no bot-driven auto-commit
  or auto-tag. Both SDKs are install-from-source only — no PyPI package,
  no Go module proxy. See `sdk/README.md` for install commands.

## Versioning policy

- Releases are tagged with a single repo-wide `vMAJOR.MINOR.PATCH` tag,
  cut manually by a maintainer once a proto change (with its regenerated
  SDKs) has merged to `main`. This supersedes the original per-package
  versioning policy below: a release tag now covers the whole spec (all
  device-type packages) and both generated SDKs together, not one device
  type at a time.
- `sdk/go` additionally gets a matching nested-module tag,
  `sdk/go/vMAJOR.MINOR.PATCH`, pointing at the same commit — required
  because `sdk/go` is a nested Go module (own `go.mod`) and Go's module
  system only resolves tagged releases for a nested module from tags of
  the form `<module-subdir>/vX.Y.Z`.
- Each device-type package is still versioned independently in its *path*
  (`hal.adapters.<type>.v1`, `v2`, ...) — a breaking change to one device
  type still doesn't require bumping the others' package version — but the
  repo-wide release tag advances regardless of which package(s) changed.
- Once a version is tagged, breaking changes are made by introducing a new
  version directory/package rather than mutating the existing one; removed
  fields get `reserved` rather than deleted outright.
- Tags follow semver (`v1.0.0`, `v1.1.0`, ...).
