default: deps
	@echo "deps installed"

web-dev:
	pnpm run --filter=./web dev

web-build:
	pnpm run --filter=./web build
		
fastapi-dev: deps
	venv/bin/fastapi dev src/bgm_archive/api

fastapi-openapi: deps
	curl http://127.0.0.1:8000/openapi.json -o web/openapi.json
	pnpm run --filter=./web format openapi.json

fastapi-prod: deps
	venv/bin/fastapi run src/bgm_archive/api

test-db: deps
	@mkdir -p db
	@rm -fv db/test.duckdb
	./cli import-duckdb dataset/dump-2025-06-03.210251Z.zip db/test.duckdb --limit 1000

full-db: deps
	@mkdir -p db
	@rm -fv db/full.duckdb
	./cli import-duckdb dataset/dump-2025-06-03.210251Z.zip db/full.duckdb

###
### SECTION dev scripts
###
format-web:
	pnpm run --filter=./web format

format-py:
	venv/bin/ruff format src notebooks

test: deps
	. venv/bin/activate && exec pytest src

test-watch: deps
	. venv/bin/activate && exec pytest-watcher src

###
### SECTION deps
###

PYTHON_VER ?= 3.13

# comma separated packages
FREEZE_PY_REQ = elasticsearch

REQUIREMENTS = -r requirements.txt --editable .

deps: venv/.deps_installed # .PHONY

venv/.deps_installed: venv requirements.txt
	@# the most useful feature of uv
	UV_PYTHON=venv UV_LINK_MODE=symlink uv pip install $(REQUIREMENTS)
	@echo "deps installed"
	@touch $@

upgrade-deps:
	venv/bin/pur -r requirements.txt --force --skip=$(FREEZE_PY_REQ)

venv: venv/.venv_created

venv/.venv_created: Makefile
	@# the 2nd most useful feature of uv
	uv venv --clear --python=$(PYTHON_VER) venv
	@touch $@
	rm -vf venv/.deps_installed

.PHONY:
