.ONESHELL:
SHELL := bash

#=General Commands

.PHONY: help

help: # Shows this list of available actions (targets)
  # Only includes targets with comments, but not if they have Commands with two ## chars
	@sed -nr \
		-e 's|^#=(.*)|\n\1:|p' \
		-e 's|^([a-zA-Z-]*):([^#]*?\s# (.*))| \1\x1b[35m - \3\x1b[0m|p' \
		$(lastword $(MAKEFILE_LIST)) \
		| expand -t20

#=Lint Commands

.PHONY: check black mypy ruff typos pytest test format

check: black mypy ruff typos # Run all linters

black: # Lint with black (formatting checker)
	black --diff --check .

mypy: # Lint with mypy (type checker)
	mypy .

ruff: # Lint with ruff
	ruff check .

typos: # Lint with typos (typo checker)
	typos .

format: # Auto format the code
	black .
	ruff check . --fix