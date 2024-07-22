SHELL := /bin/bash
PYTHON_VERSION := 3.12
VENV_PATH := .venv

.PHONY: setup
setup:
	python3 -m venv $(VENV_PATH)
	$(VENV_PATH)/bin/pip install --upgrade pip setuptools wheel

.PHONY: install
install:
	$(VENV_PATH)/bin/pip install .

.PHONY: install-extras
install-extras:
	$(VENV_PATH)/bin/pip install .[jupyterlite]

.PHONY: build-docs
build-docs:
	source $(VENV_PATH)/bin/activate && $(MAKE) -C docs html

.PHONY: build-playground
build-playground: install-extras check-jq
	source $(VENV_PATH)/bin/activate && cd playground && jupyter lite build --contents content --output-dir dist && \
		jq '.["jupyter-config-data"]["litePluginSettings"]["@jupyterlite/pyodide-kernel-extension:kernel"].pyodideUrl = "https://koxudaxi.github.io/pyodide/pyodide.js"' dist/jupyter-lite.json > temp.json && mv temp.json dist/jupyter-lite.json

.PHONY: clean-playground
clean-playground:
	rm -rf playground/dist

# Run a built copy of the playground locally.
.PHONY: run-playground
run-playground:
	source $(VENV_PATH)/bin/activate && cd playground/dist && python -m http.server 8000

# Run the jupyter lite server locally, no build step required.
.PHONY: dev-playground
dev-playground:
	source $(VENV_PATH)/bin/activate && jupyter lite serve --contents playground/content --config playground/jupyter-lite.json

.PHONY: check-jq
check-jq:
	which jq || (echo "jq is not installed. Please install jq to continue." && exit 1)

.PHONY: all
all: setup install install-extras build-docs build-playground
