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

`proto/hal/adapters/**/*.proto` files deliberately **do not** set
`go_package` (or an equivalent for other languages) — that's an internal
detail of your own codebase, not something this shared spec should dictate.

### Go (via Buf — the supported path)

`buf.gen.yaml` is wired up with [managed mode](https://buf.build/docs/generate/managed-mode/),
which injects `go_package` at generation time based on `go_package_prefix.default`
in that file:

```sh
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

buf generate proto   # writes to ./gen/go, which is gitignored -- not committed here
```

Before relying on this for real, edit `go_package_prefix.default` in
`buf.gen.yaml` to the actual module path you'll import the generated code
from — it's currently a placeholder (`github.com/cisco-eti/hal-api/gen/go`).

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

### Python (message classes via Buf, service stubs via grpc_tools)

Python is **commented out** in `buf.gen.yaml` by default, so a plain `buf
generate proto` only produces Go. To generate Python:

1. Open `buf.gen.yaml` and uncomment the `plugin: python` block (there's a
   `gen/python` output path right there, plus this same set of steps
   repeated in that file's comments).
2. Run `buf generate proto` — writes `gen/python/**/*_pb2.py` message
   classes via Buf's built-in `python` plugin, no extra binary needed.
3. There's no local (non-BSR) gRPC-Python plugin to add to `buf.gen.yaml` —
   Python's gRPC codegen lives inside the `grpc_tools.protoc` module
   itself, not as a standalone `protoc-gen-*` binary buf could shell out
   to. Generate the `_pb2_grpc.py` service stubs separately and let them
   land alongside:

```sh
pip install grpcio-tools
python -m grpc_tools.protoc \
  --proto_path=proto \
  --grpc_python_out=gen/python \
  proto/hal/adapters/common/v1/common.proto \
  proto/hal/adapters/source/v1/source.proto
```

(Skipping `--python_out` here since `buf generate` already produced those
message classes in step 2 -- this command only adds the `_grpc.py` files.)

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

	commonv1 "yourmodule/genpb/hal/adapters/common/v1"
	sourcev1 "yourmodule/genpb/hal/adapters/source/v1"
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

Once this repo starts tagging releases (see `CHANGELOG.md`), pin your
`proto_path`/generation step to a specific tag or commit rather than
tracking the default branch, so a spec change upstream doesn't silently
change what your generated code expects:

```sh
git clone --branch v1.0.0 <this-repo-url>
```
