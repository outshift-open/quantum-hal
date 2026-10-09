# quantum-hal SDKs

Generated client bindings for the [HAL proto spec](../proto). Both SDKs are
install-from-source only — there is no PyPI package or Go module proxy
involved, just this repo and its tags.

## Table of contents

- [Go](#go)
- [Python](#python)

## Go

```sh
go get github.com/outshift-open/quantum-hal/sdk/go@latest
```

Pin to a specific release instead of `@latest`:

```sh
go get github.com/outshift-open/quantum-hal/sdk/go@vX.Y.Z
```

`sdk/go` is a nested Go module (its own `go.mod`, rooted at
`github.com/outshift-open/quantum-hal/sdk/go`), so Go only resolves a
tagged release for it from a `sdk/go/vX.Y.Z`-form tag, not a bare
`vX.Y.Z` tag at the repo root — see the root [`README.md`](../README.md)
for how releases are tagged.

## Python

```sh
pip install "git+https://github.com/outshift-open/quantum-hal.git#subdirectory=sdk/python"
```

Pin to a specific release:

```sh
pip install "git+https://github.com/outshift-open/quantum-hal.git@vX.Y.Z#subdirectory=sdk/python"
```
