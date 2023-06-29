VIRTUAL_ENV     ?= venv
PROJECT         ?= app

all: $(VIRTUAL_ENV)

.PHONY: run
run: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python -m botapp -run

.PHONY: dev
dev: $(VIRTUAL_ENV)
	export ENV=develop && \
	$(VIRTUAL_ENV)/bin/python -m botapp -run

.PHONY: t test
t test: $(VIRTUAL_ENV)
	export ENV=tests && pytest

.PHONY: init_db
init_db: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python -m botapp -init_db
