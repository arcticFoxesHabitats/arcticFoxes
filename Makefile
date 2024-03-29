SHELL := /bin/bash

.PHONY: setup
setup:
	pyenv local 3.9.8
	python -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements_dev.txt

data_clean:
	python clean.py

features:
	python features.py