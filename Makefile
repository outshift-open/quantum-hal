# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

PROTO_DIR := proto
PY_OUT := sdk/python
GOBIN := $(shell go env GOPATH)/bin
PROTO_FILES := $(shell find $(PROTO_DIR) -name '*.proto')

VENV := .venv
VENV_PYTHON := $(VENV)/bin/python3
VENV_STAMP := $(VENV)/.deps-installed

.PHONY: all
all: generate

$(VENV_PYTHON):
	python3 -m venv $(VENV)

$(VENV_STAMP): $(VENV_PYTHON)
	$(VENV_PYTHON) -m pip install --upgrade pip 'grpcio-tools==1.84.0' 'mypy-protobuf==5.1.0'
	touch $(VENV_STAMP)

.PHONY: venv
venv: $(VENV_STAMP)

# Keep in sync with .github/workflows/proto-ci.yml. Unpinned @latest on
# CI vs an older local plugin rewrites the SDK and fails generate-check.
PROTOC_GEN_GO := google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.11
PROTOC_GEN_GO_GRPC := google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.6.2

.PHONY: tools
tools: $(VENV_STAMP)
	go install $(PROTOC_GEN_GO)
	go install $(PROTOC_GEN_GO_GRPC)

.PHONY: lint
lint:
	buf lint proto

.PHONY: breaking
breaking:
	buf breaking proto --against ".git#branch=main,subdir=proto"

.PHONY: generate
generate: generate-go generate-python

.PHONY: generate-go
generate-go:
	go install $(PROTOC_GEN_GO)
	go install $(PROTOC_GEN_GO_GRPC)
	PATH="$(GOBIN):$$PATH" buf generate proto
	./scripts/add-license-headers.sh sdk/go

.PHONY: generate-python
generate-python: $(VENV_STAMP)
	mkdir -p $(PY_OUT)
	$(VENV_PYTHON) -m grpc_tools.protoc \
		-I $(PROTO_DIR) \
		--python_out=$(PY_OUT) \
		--grpc_python_out=$(PY_OUT) \
		--pyi_out=$(PY_OUT) \
		$(PROTO_FILES)
	find $(PY_OUT) -type d -not -path '$(PY_OUT)' -exec sh -c 'test -f "$$1/__init__.py" || touch "$$1/__init__.py"' _ {} \;
	./scripts/add-license-headers.sh $(PY_OUT)

.PHONY: build-go
build-go:
	cd sdk/go && go build ./...

.PHONY: check-headers
check-headers:
	./scripts/check-license-headers.sh

.PHONY: check
check: lint breaking generate check-headers
	git diff --exit-code -- sdk/go sdk/python

.PHONY: clean
clean:
	find sdk/go -name '*.pb.go' -delete
	rm -rf sdk/python/hal
	find sdk/python -name '__pycache__' -type d -exec rm -rf {} +

.PHONY: distclean
distclean: clean
	rm -rf $(VENV)
