# Makefile for PyWebService
# Variables
POETRY ?= poetry
UVICORN ?= uvicorn
APP_MODULE ?= main:app
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: help run install lint

help:
	@echo "Available commands:"
	@echo "  make run        - Run development server (poetry run uvicorn --reload)"
	@echo "  make install    - Install deps via Poetry (creates/uses virtualenv)"
	@echo "  make lint       - Run pylint against project files (via Poetry)"

run:
	$(POETRY) run $(UVICORN) $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

install:
	$(POETRY) install --no-root

lint:
	$(POETRY) run pylint *.py
