CFLAGS = -fpack-struct=8
PIP = $(VENV)/bin/pip
PYTHON ?= python
TEST_EXECUTABLE = tests/test-executable
TOX = $(VENV)/bin/tox
VENV ?= $(PWD)/venv

.DEFAULT_GOAL := install
.PHONY : clean dev-install install test test-all test-install

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)
	$(PIP) install .

dev-install: $(VENV)
	$(PIP) install -e .[test]

test-install: $(VENV)
	$(PIP) install .[test]

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

test test-all: export TEST_EXECUTABLE := $(TEST_EXECUTABLE)

test: $(TEST_EXECUTABLE) test-install
	$(TOX) -e py

test-all: $(TEST_EXECUTABLE) test-install
	$(TOX)

clean:
	rm -rf $(TEST_EXECUTABLE) $(VENV)
