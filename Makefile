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
	$(VENV_PYTHON) -m pip install --upgrade pip grpcio-tools mypy-protobuf
	touch $(VENV_STAMP)

.PHONY: venv
venv: $(VENV_STAMP)

.PHONY: tools
tools: $(VENV_STAMP)
	go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
	go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

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
