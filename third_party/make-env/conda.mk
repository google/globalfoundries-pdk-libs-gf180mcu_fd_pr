# Copyright (C) 2020-2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:	ISC

.SUFFIXES:

MAKE_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

SHELL := bash

# Makefile for downloading and creating a conda environment.

# Usage
#  - Set TOP_DIR to the top directory where environment will be created.
#  - Set CONDA_ENV_NAME
#  - Set REQUIREMENTS_FILE to a pip `requirements.txt` file.
#  - Set ENVIRONMENT_FILE to a conda `environment.yml` file.
#  - Put $(IN_CONDA_ENV) before commands which should run inside the
#    environment.

# Configuration
ifeq (,$(TOP_DIR))
$(error "Set TOP_DIR value before including 'conda.mk'.")
endif

include $(MAKE_DIR)/os.mk

ifeq ($(OS_TYPE),Windows)
TOP_DIR    := $(subst /,\,$(TOP_DIR))
OS_EXT     := exe
PYTHON_BIN := python.exe
SHELL      := cmd.exe
CONDA_ENV_NAME_LINE := $(shell findstr "name:" $(ENVIRONMENT_FILE))
CONDA_ACTIVATE = call $(CONDA_DIR)$(SEP)condabin$(SEP)conda.bat activate
else
OS_EXT     := sh
PYTHON_BIN := bin/python
SHELL      := bash
CONDA_ENV_NAME_LINE := $(shell grep "name:" $(ENVIRONMENT_FILE))
CONDA_ACTIVATE = source $(CONDA_DIR)/bin/activate
endif

ifeq (,$(REQUIREMENTS_FILE))
$(error "Set REQUIREMENTS_FILE value before including 'conda.mk'.")
else
REQUIREMENTS_FILE := $(abspath $(REQUIREMENTS_FILE))
endif
ifeq (,$(wildcard $(REQUIREMENTS_FILE)))
$(error "REQUIREMENTS_FILE ($(REQUIREMENTS_FILE)) does not exist!?")
endif

ifeq (,$(ENVIRONMENT_FILE))
$(error "Set ENVIRONMENT_FILE value before including 'conda.mk'.")
ENVIRONMENT_FILE := $(abspath $(ENVIRONMENT_FILE))
endif
ifeq (,$(wildcard $(ENVIRONMENT_FILE)))
$(error "ENVIRONMENT_FILE ($(ENVIRONMENT_FILE)) does not exist!?")
endif

CONDA_ENV_NAME    := $(strip $(patsubst name:%,,$(CONDA_ENV_NAME_LINE)))

# Read the conda environment name from the environment.yml file.
ENV_DIR           := $(TOP_DIR)$(SEP)env
CONDA_DIR         := $(ENV_DIR)$(SEP)conda
DOWNLOADS_DIR     := $(ENV_DIR)$(SEP)downloads

CONDA_INSTALLER   := Miniconda3-latest-$(OS_TYPE)-$(CPU_TYPE).$(OS_EXT)
CONDA_PYTHON      := $(CONDA_DIR)$(SEP)$(PYTHON_BIN)
CONDA_PYVENV      := $(CONDA_DIR)$(SEP)pyvenv.cfg
CONDA_PKGS_DIR    := $(DOWNLOADS_DIR)$(SEP)conda-pkgs
CONDA_PKGS_DEP    := $(CONDA_PKGS_DIR)$(SEP)urls.txt

CONDA_ENVS_DIR    := $(CONDA_DIR)$(SEP)envs
CONDA_ENV_PYTHON  := $(CONDA_ENVS_DIR)$(SEP)$(CONDA_ENV_NAME)$(SEP)$(PYTHON_BIN)
IN_CONDA_ENV_BASE := $(CONDA_ACTIVATE) &&
IN_CONDA_ENV      := $(CONDA_ACTIVATE) $(CONDA_ENV_NAME) &&

CONDA_INSTALLER_DOWNLOAD := $(DOWNLOADS_DIR)$(SEP)$(CONDA_INSTALLER)

CONDA_ALWAYS_YES  := 1
export CONDA_ALWAYS_YES

# Force ignoring a user's Python site.py config.
PYTHONNOUSERSITE  := 1
export PYTHONNOUSERSITE

# Check spaces are not found in important locations
NULL_STRING :=
SPACE := $(NULL_STRING) $(NULL_STRING)
ifneq ($(CONDA_ENV_NAME),$(subst $(SPACE),?,$(CONDA_ENV_NAME)))
  $(error "Space not allowed in conda environment name: '$(SPACE)' '$(CONDA_ENV_NAME)' '$(subst $(SPACE),?,$(CONDA_ENV_NAME))'")
endif
ifneq ($(TOP_DIR),$(subst $(SPACE),?,$(TOP_DIR)))
  $(error "Spaces are not allowed in conda directory path: '$(TOP_DIR)'")
endif

# Rules to download and setup conda
$(ENV_DIR): | $(DOWNLOADS_DIR)
	$(MKDIR) "$(ENV_DIR)"

$(DOWNLOADS_DIR):
	$(MKDIR) "$(DOWNLOADS_DIR)"

ifeq ($(OS_TYPE),Windows)
$(CONDA_INSTALLER_DOWNLOAD): | $(DOWNLOADS_DIR)
	$(WGET) https://repo.anaconda.com/miniconda/$(CONDA_INSTALLER) -O $(CONDA_INSTALLER_DOWNLOAD) 2>&1
else
$(CONDA_INSTALLER_DOWNLOAD): | $(DOWNLOADS_DIR)
	$(WGET) https://repo.anaconda.com/miniconda/$(CONDA_INSTALLER) -O $(CONDA_INSTALLER_DOWNLOAD) 2>&1 | $(CAT)
endif

$(CONDA_PKGS_DEP): $(CONDA_PYTHON)
	$(IN_CONDA_ENV_BASE) conda config --system --add pkgs_dirs $(CONDA_PKGS_DIR)
	$(MKDIR) "$(CONDA_PKGS_DIR)"
	$(TOUCH) "$(CONDA_PKGS_DEP)"

ifeq ($(OS_TYPE),Windows)
$(CONDA_PYTHON): $(CONDA_INSTALLER_DOWNLOAD)
	cmd.exe /c start "" /WAIT  $(CONDA_INSTALLER_DOWNLOAD) /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /NoScripts=1 /S /D=$(CONDA_DIR)
	$(TOUCH) "$(CONDA_PYTHON)"
else
$(CONDA_PYTHON): $(CONDA_INSTALLER_DOWNLOAD)
	chmod a+x $(CONDA_INSTALLER_DOWNLOAD)
	bash $(CONDA_INSTALLER_DOWNLOAD) -p $(CONDA_DIR) -b -f
	$(TOUCH) "$(CONDA_PYTHON)"
endif

# FIXME: Why does this break on Windows?
ifeq ($(OS_TYPE),Windows)
CONDA_PYVENV := $(CONDA_PYTHON)
else
$(CONDA_PYVENV): $(CONDA_PYTHON) $(MAKE_DIR)/conda.mk
	echo "include-system-site-packages=false" >> $(CONDA_PYVENV)
endif

$(CONDA_ENVS_DIR): $(CONDA_PYTHON)
	$(IN_CONDA_ENV_BASE) conda config --system --add envs_dirs $(CONDA_ENVS_DIR)
	$(MKDIR) "$(CONDA_ENVS_DIR)"

$(CONDA_ENV_PYTHON): $(ENVIRONMENT_FILE) $(REQUIREMENTS_FILE) | $(CONDA_PYTHON) $(CONDA_PKGS_DEP) $(CONDA_ENVS_DIR) $(CONDA_PYVENV)
	$(IN_CONDA_ENV_BASE) conda env update --name $(CONDA_ENV_NAME) --file $(ENVIRONMENT_FILE)
	$(TOUCH) "$(CONDA_ENV_PYTHON)"

env:: $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) conda info

.PHONY: env

enter: $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) bash

.PHONY: enter

clean::
	rm -rf $(CONDA_DIR)

.PHONY: clean

dist-clean::
	rm -rf $(ENV_DIR)

.PHONY: dist-clean

FILTER_TOP = sed -e's@$(TOP_DIR)/@$$TOP_DIR/@'
env-info:
	@echo "               Currently running on: '$(OS_TYPE) ($(CPU_TYPE))'"
	@echo
	@echo "         Conda environment is named: '$(CONDA_ENV_NAME)'"
	@echo "   Conda Env Top level directory is: '$(TOP_DIR)'"
	@echo "         Git top level directory is: '$$(git rev-parse --show-toplevel)'"
	@echo "              The version number is: '$$(git describe)'"
	@echo "            Git repository is using: $$(du -h -s $$(git rev-parse --show-toplevel)/.git | sed -e's/\s.*//')" \
		| $(FILTER_TOP)
	@echo
	@echo "     Environment setup directory is: '$(ENV_DIR)'" \
		| $(FILTER_TOP)
	@echo "    Download and cache directory is: '$(DOWNLOADS_DIR)' (using $$(du -h -s $(DOWNLOADS_DIR) | sed -e's/\s.*//'))" \
		| $(FILTER_TOP)
	@echo "               Conda's directory is: '$(CONDA_DIR)' (using $$(du -h -s $(CONDA_DIR) | sed -e's/\s.*//'))" \
		| $(FILTER_TOP)
	@echo " Conda's packages download cache is: '$(CONDA_PKGS_DIR)' (using $$(du -h -s $(CONDA_PKGS_DIR) | sed -e's/\s.*//'))" \
		| $(FILTER_TOP)
	@echo "           Conda's Python binary is: '$(CONDA_ENV_PYTHON)'"\
		| $(FILTER_TOP)

.PHONY: env-info
