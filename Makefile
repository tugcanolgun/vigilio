.ONESHELL:
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VENV:=${ROOT_DIR}/venv/bin

default:
	@echo "== Available commands for python =="
	@echo "'pylint'\truns flake8"
	@echo "'pyfix'\t\truns black"
	@echo "'run'\t\truns manage.py runserver"
	@echo "'test'\t\truns pytest"
	@echo "'upgrade'\tupgrades python dependencies"
	@echo "'deploy'\truns deploy script for vigilio"
	@echo ""
	@echo "== Available commands for JS =="
	@echo "'jslint'\truns prettier check"
	@echo "'jsfix'\t\truns prettier write"
	@echo "'install'\truns yarn install"
	@echo "'start'\t\truns webpack in dev mode (watch)"
	@echo "'build'\t\truns webpack build in prod mode"

check_venv:
	@if [ -a ${ROOT_DIR}/venv/bin/activate ]; \
	then \
		echo "Found virtualenv"; \
	else \
		echo "Virtualenv could not be found. Initiating..." && \
		python3 -m venv ${ROOT_DIR}/venv && \
		echo "Activating the virtualenv..." && \
		. ${VENV}/activate && echo "Installing the dependencies..." && \
		pip install wheel && \
		pip install -r ${ROOT_DIR}/requirements/dev.txt && \
		echo "Installation complete. Disabling the virtualenv for consistency..." && \
		deactivate && \
		echo "Resuming normal operation"; \
	fi;

# ========================================================
# JS
# ========================================================

jslint:
	@echo "Running JS linter"
	yarn --cwd ${ROOT_DIR}/frontend lint
	@echo "Linter process ended"

jsfix:
	@echo "Running JS linter"
	yarn --cwd ${ROOT_DIR}/frontend fix
	@echo "Linter process ended"

install:
	@echo "Initiating node server..."
	yarn --cwd ${ROOT_DIR}/frontend install

start:
	@echo "Initiating node server..."
	yarn --cwd ${ROOT_DIR}/frontend start

build:
	@echo "Compiling js files..."
	yarn --cwd ${ROOT_DIR}/frontend build
	@echo "Compilation has finished."

# ========================================================
# PYTHON
# ========================================================

activate: check_venv
	@echo "Activating virtualenv"
	@. ${VENV}/activate;

pylint: activate
	@echo "Running linter"
	@${VENV}/flake8 ${ROOT_DIR}
	@echo "Linter process ended"

pyfix: activate
	@echo "Running syntax fixer"
	@${VENV}/black --exclude venv ${ROOT_DIR}
	@echo "Syntax fixer process ended"

test: activate
	@echo "Testing..."
	@${VENV}/pytest ${ROOT_DIR}

run: activate
	@echo "Running the server"
	@${VENV}/python ${ROOT_DIR}/manage.py runserver

upgrade: activate
	@echo "Upgrading dependencies"
	@${VENV}/python ${ROOT_DIR}/requirements/upgrade_dependencies.py

deploy:
	set -e
	@echo "Deploying to production"
	rm -rf ${ROOT_DIR}/frontend/dist
	@echo "Fetching latest version"
	git pull
	@if [ -a ${ROOT_DIR}/venv/bin/activate ]; \
	then \
		echo "Found virtualenv"; \
	else \
		echo "Virtualenv could not be found. Initiating..." && \
		python3 -m venv ${ROOT_DIR}/venv && \
		echo "Activating the virtualenv..."; \
	fi;
	. ${VENV}/activate
	@echo "Upgrading pip..."
	pip install --upgrade pip
	pip install wheel
	@echo "Installing the dependencies..."
	pip install -r ${ROOT_DIR}/requirements/prod.txt
	@echo "Requirements installation is complete."
	@echo "Attempting to migrate database..."
	${VENV}/python ${ROOT_DIR}/manage.py migrate
	${VENV}/python ${ROOT_DIR}/manage.py collectstatic --no-input
	@echo "Installation is complete. Attempting to restarting the service..."
	@echo "If prompt, please enter password."
	systemctl restart vigilio.service
	systemctl restart celery-vigilio.service

