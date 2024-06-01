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
build-playground: install-extras clean-playground
	source $(VENV_PATH)/bin/activate && cd playground && jupyter lite build --contents content --output-dir dist && cp -r ./pyodide dist/pyodide

.PHONY: clean-playground
clean-playground:
	rm -rf playground/dist

.PHONY: run-playground
run-playground:
	source $(VENV_PATH)/bin/activate && cd playground/dist && python -m http.server 8000

.PHONY: all
all: setup install install-extras build-docs build-playground