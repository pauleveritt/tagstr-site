SHELL := /bin/bash
PYTHON_VERSION := 3.12
VENV_PATH := .venv
SITE_PREFIX := $(or $(SITE_PREFIX), /)

.PHONY: setup
setup:
	python3 -m venv $(VENV_PATH)
	$(VENV_PATH)/bin/pip install --upgrade pip setuptools wheel build

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
build-playground: install-extras wheel
	source $(VENV_PATH)/bin/activate && $(MAKE) build-playground-without-venv

.PHONY: build-playground-without-venv
build-playground-without-venv: check-jq
	cd playground && rm -fr pypi/* && cp -v ../dist/*.whl pypi/ && jupyter lite build && \
		WHL_FILE=$$(ls pypi | grep .whl) && \
		jq '.["jupyter-config-data"]["litePluginSettings"]["@jupyterlite/pyodide-kernel-extension:kernel"].pyodideUrl = "https://koxudaxi.github.io/pyodide/pyodide.js"' dist/jupyter-lite.json | \
		jq '.["jupyter-config-data"]["litePluginSettings"]["@jupyterlite/pyodide-kernel-extension:kernel"]["loadPyodideOptions"]["packages"] = ["$(SITE_PREFIX)pypi/'$$WHL_FILE'"]' > temp.json && mv temp.json dist/jupyter-lite.json

.PHONY: wheel
wheel: clean-wheel
	$(VENV_PATH)/bin/python -m build


.PHONY: clean-wheel
clean-wheel:
	rm -rf dist

.PHONY: clean-playground
clean-playground:
	rm -rf playground/dist

.PHONY: run-playground
run-playground:
	source $(VENV_PATH)/bin/activate && cd playground/dist && python -m http.server 8000

.PHONY: check-jq
check-jq:
	which jq || (echo "jq is not installed. Please install jq to continue." && exit 1)

.PHONY: all
all: setup install install-extras build-docs build-playground
