# Integration guide

This is the practical "how do I actually use this spec" guide: generating
stubs, a worked client example, and how to explore a running adapter
without writing any code at all.

> `buf build`/`buf lint` and the Go `buf generate` path (including a
> compile check of the generated code) have been run end-to-end against
> this repo. The raw-`protoc` and Python commands are standard
> `protoc`/`grpc_tools` usage but weren't independently re-verified here —
> install the plugins for your language before running them.

## 1. Validate the spec compiles

```sh
buf build proto
buf lint proto
```

Both should exit cleanly. If you're only reading the spec (not generating
code), this is enough to confirm you have a consistent checkout.

## 2. Generate stubs

Both Go and Python already have a published SDK generated straight from
this repo's `proto/` — install it instead of generating your own copy:

```sh
# Go
go get github.com/outshift-open/quantum-hal/sdk/go@latest

# Python
pip install "git+https://github.com/outshift-open/quantum-hal.git#subdirectory=sdk/python"
```

See [`sdk/README.md`](./sdk/README.md) for the full table (both languages,
plus how to pin to a release) and the root `README.md`'s
[Installing the SDKs](./README.md#installing-the-sdks) section for how
those SDKs get regenerated and tagged.

The rest of this section covers generating stubs yourself instead — useful
for a language other than Go/Python, or to regenerate locally before
sending a proto change as a PR (`make generate`, see the root `Makefile`,
regenerates both and is what CI's stale-SDK check in `proto-ci.yml`
compares against).

`proto/hal/adapters/**/*.proto` files deliberately **do not** set
`go_package` (or an equivalent for other languages) — that's injected at
generation time, not something this shared spec should dictate.

### Go (via Buf — the supported path)

`buf.gen.yaml` is wired up with [managed mode](https://buf.build/docs/generate/managed-mode/),
which injects `go_package` at generation time based on `go_package_prefix.default`
in that file (currently `github.com/outshift-open/quantum-hal/sdk/go`, the
published SDK's own module path):

```sh
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

buf generate proto   # writes to ./sdk/go -- the same path CI commits to
```

If you're generating for a codebase other than this repo, edit
`go_package_prefix.default` in your own copy of `buf.gen.yaml` to wherever
you'll actually import the generated code from.

### Go (raw `protoc`, if you'd rather not use Buf)

```sh
protoc \
  --proto_path=proto \
  --go_out=. --go_opt=paths=source_relative \
  --go_opt=Mhal/adapters/common/v1/common.proto=yourmodule/genpb/hal/adapters/common/v1 \
  --go_opt=Mhal/adapters/source/v1/source.proto=yourmodule/genpb/hal/adapters/source/v1 \
  --go-grpc_out=. --go-grpc_opt=paths=source_relative \
  --go-grpc_opt=Mhal/adapters/common/v1/common.proto=yourmodule/genpb/hal/adapters/common/v1 \
  --go-grpc_opt=Mhal/adapters/source/v1/source.proto=yourmodule/genpb/hal/adapters/source/v1 \
  proto/hal/adapters/common/v1/common.proto \
  proto/hal/adapters/source/v1/source.proto
```

Repeat the `-M` mapping pair for `switch/v1/switch.proto` and
`timetagger/v1/timetagger.proto` if you need those too.

### Python (via `grpc_tools.protoc`)

Python isn't generated through Buf — there's no local (non-BSR)
gRPC-Python plugin buf can shell out to, since Python's gRPC codegen lives
inside the `grpc_tools.protoc` module itself, not as a standalone
`protoc-gen-*` binary. `make generate-python` (or the equivalent raw
command) produces both the message classes and the service stubs in one
shot:

```sh
pip install grpcio-tools
python -m grpc_tools.protoc \
  --proto_path=proto \
  --python_out=sdk/python \
  --grpc_python_out=sdk/python \
  --pyi_out=sdk/python \
  proto/hal/adapters/common/v1/common.proto \
  proto/hal/adapters/source/v1/source.proto \
  proto/hal/adapters/switch/v1/switch.proto \
  proto/hal/adapters/timetagger/v1/timetagger.proto
```

Python doesn't need an import-path mapping — packages fall out of the
directory structure.

Other languages follow the same shape: `protoc --proto_path=proto
--<lang>_out=... <files>`, with whatever plugin that language's grpc
tooling provides.

## 3. Worked example: calling HealthCheck (Go)

```go
package main

import (
	"context"
	"log"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	commonv1 "github.com/outshift-open/quantum-hal/sdk/go/hal/adapters/common/v1"
	sourcev1 "github.com/outshift-open/quantum-hal/sdk/go/hal/adapters/source/v1"
)

func main() {
	conn, err := grpc.NewClient("localhost:50051",
		grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("dial: %v", err)
	}
	defer conn.Close()

	client := sourcev1.NewAdapterSourceServiceClient(conn)
	resp, err := client.HealthCheck(context.Background(), &commonv1.HealthCheckRequest{})
	if err != nil {
		log.Fatalf("HealthCheck: %v", err)
	}
	log.Printf("adapter says: %s", resp.GetMessage())
}
```

Every other RPC follows the same pattern: construct the typed request
(remembering `product_id`/`resource_type` on device-scoped calls), call the
method on the generated client, check the returned `message` field and/or
gRPC status code.

## 4. Exploring an adapter without writing a client

If your adapter implementation enables **gRPC server reflection**
([`grpc.reflection`](https://grpc.io/docs/guides/reflection/)), you can
poke at a running instance with
[`grpcurl`](https://github.com/fullstorydev/grpcurl) before writing any
integration code:

```sh
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 hal.adapters.source.v1.AdapterSourceService/HealthCheck
```

We recommend every adapter implementation enable reflection for exactly
this reason — it's the fastest way for another team to sanity-check their
setup against the spec.

## 5. Pinning a version

Releases are tagged `vMAJOR.MINOR.PATCH` at the repo root (see
`CHANGELOG.md`'s versioning policy). Pin to one instead of tracking the
default branch, so a spec change upstream doesn't silently change what
your installed SDK expects:

```sh
# Go -- sdk/go is a nested module, so it's pinned via its own
# sdk/go/vMAJOR.MINOR.PATCH tag, not the bare repo-root tag
go get github.com/outshift-open/quantum-hal/sdk/go@v1.0.0

# Python
pip install "git+https://github.com/outshift-open/quantum-hal.git@v1.0.0#subdirectory=sdk/python"
```

If you're generating your own stubs instead of using the published SDK,
pin the clone itself the same way:

```sh
git clone --branch v1.0.0 <this-repo-url>
```
