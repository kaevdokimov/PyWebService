# Makefile for PyWebService
# Variables
PYTHON ?= python3
UVICORN ?= uvicorn
APP_MODULE ?= main:app
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: help run install lint

help:
	@echo "Available commands:"
	@echo "  make run        - Run development server (uvicorn --reload)"
	@echo "  make install    - Install runtime and dev dependencies (fastapi, uvicorn, pylint)"
	@echo "  make lint       - Run pylint against project files"

run:
	$(UVICORN) $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install fastapi uvicorn pylint

lint:
	pylint --rcfile=.pylintrc *.py
