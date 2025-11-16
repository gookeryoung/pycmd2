.DEFAULT_GOAL := help

PYTHONPATH=
SHELL=bash
ifeq ($(VENV),)
VENV := .venv
endif

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

# Detect CPU architecture.
ifeq ($(OS),Windows_NT)
    ifeq ($(PROCESSOR_ARCHITECTURE),AMD64)
		ARCH := x86_64
	else ifeq ($(PROCESSOR_ARCHITECTURE),x86)
		ARCH := x86
	else ifeq ($(PROCESSOR_ARCHITECTURE),ARM64)
		ARCH := arm64
	else
		ARCH := unknown
    endif

	TARGET := $(ARCH)-win7-windows-msvc
	OPTIONS := -Z build-std=std
else
    UNAME_P := $(shell uname -p)
    ifeq ($(UNAME_P),x86_64)
		ARCH := x86_64
	else ifneq ($(filter %86,$(UNAME_P)),)
		ARCH := x86
	else ifneq ($(filter arm%,$(UNAME_P)),)
		ARCH := arm64
	else
		ARCH := unknown
    endif

	TARGET := $(ARCH)-unknown-linux-gnu
	OPTIONS :=
endif

# Ensure boolean arguments are normalized to 1/0 to prevent surprises.
ifdef LTS_CPU
	ifeq ($(LTS_CPU),0)
	else ifeq ($(LTS_CPU),1)
	else
$(error LTS_CPU must be 0 or 1 (or undefined, default to 0))
	endif
endif

# Define command to filter pip warnings when running maturin
FILTER_PIP_WARNINGS=| grep -v "don't match your environment"; test $${PIPESTATUS[0]} -eq 0

.venv:  ## Set up Python virtual environment and install requirements
	python3 -m venv $(VENV)
	$(MAKE) requirements

.PHONY: build
build: .venv  ## Compile and install for development
	maturin b -r $(OPTIONS) --target $(TARGET)

.PHONY: publish
publish: .venv  ## Publish to PyPI
	maturin publish $(OPTIONS) --target $(TARGET)

.PHONY: check
check:  ## Run cargo check with all features
	cargo check --workspace --all-targets --all-features

.PHONY: clippy
clippy:  ## Run clippy with all features
	cargo clippy --workspace --all-targets --all-features --locked -- -D warnings -D clippy::dbg_macro

.PHONY: clippy-default
clippy-default:  ## Run clippy with default features
	cargo clippy --all-targets --locked -- -D warnings -D clippy::dbg_macro

.PHONY: fmt
fmt:  ## Run autoformatting and linting
	$(VENV_BIN)/ruff check
	$(VENV_BIN)/ruff format
	cargo fmt --all
	dprint fmt
	$(VENV_BIN)/typos

.PHONY: help
help:  ## Display this help screen
	@echo -e "\033[1mAvailable commands:\033[0m"
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' | sort
	@echo
	@echo The build commands support LTS_CPU=1 for building for older CPUs, and ARGS which is passed through to maturin.
	@echo 'For example to build without default features use: make build ARGS="--no-default-features".'
