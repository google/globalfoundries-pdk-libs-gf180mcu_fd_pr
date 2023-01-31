# Copyright (C) 2020-2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier:      ISC

MAKE_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

# If OS_TYPE isn't provided, then we need detect it.
ifeq ($(OS_TYPE),)
    # First check if we find Windows_NT in $(OS), then we know we are
    # on XP, 2000, 7, Vista, 10
    ifeq ($(OS),Windows_NT)
        OS_TYPE := Windows
    endif

    # Use $PATH to detect if on Windows.
    ifeq ($(findstring ;,$(PATH)),;)
        OS_TYPE := Windows
    else
        DETECTED_OS := $(shell uname -s 2>/dev/null)
        DETECTED_OS := $(patsubst CYGWIN%,Cygwin,$(DETECTED_OS))
        DETECTED_OS := $(patsubst MSYS%,MSYS,$(DETECTED_OS))
        DETECTED_OS := $(patsubst MINGW%,MSYS,$(DETECTED_OS))

        # Basic windows
        ifeq ($(DETECTED_OS),Windows)
            OS_TYPE := Windows
        endif

        # Cygwin windows
        ifeq ($(DETECTED_OS),Cygwin)
            OS_TYPE := Linux
        endif

        # MingW windows
        ifeq ($(DETECTED_OS),MSYS)
            OS_TYPE := Linux
        endif

        # Mac OS X
        ifeq ($(DETECTED_OS),Darwin)
            OS_TYPE := MacOSX
        endif

        # Basic Linux
        ifeq ($(DETECTED_OS),Linux)
            OS_TYPE := Linux
        endif
    endif
endif
ifeq ($(OS_TYPE),)
$(error Unable to detect OS_TYPE \(detected '$(DETECTED_OS)'\) - run make with OS_TYPE=Linux)
endif

ifeq ($(CPU_TYPE),)
    # Work out the CPU_ARCH on Windows
    ifeq ($(OS_TYPE),Windows)
        ifeq ($(PROCESSOR_ARCHITEW6432),AMD64)
            CPU_TYPE := x86_64
        else
            ifeq ($(PROCESSOR_ARCHITECTURE),AMD64)
                CPU_TYPE := x86_64
            endif
            ifeq ($(PROCESSOR_ARCHITECTURE),x86)
                CPU_TYPE := x86 # IA32
            endif
        endif
    else
        DETECTED_CPU := $(shell uname -m 2>/dev/null)
        ifneq ($(DETECTED_CPU),)
            CPU_TYPE := $(DETECTED_CPU)
        endif
    endif
endif
ifeq ($(CPU_TYPE),)
$(error Unable to detect CPU_TYPE \(detected '$(DETECTED_CPU)'\) - run make with CPU_TYPE=x86)
endif

ifeq ($(OS_TYPE),Windows)
MAKE_DIR := $(subst /,\,$(MAKE_DIR))
SEP   := $(strip \ )
CAT   := type
TOUCH := powershell $(MAKE_DIR)$(SEP)touch.ps1
MKDIR := powershell $(MAKE_DIR)$(SEP)mkdir.ps1
WGET  := powershell $(MAKE_DIR)$(SEP)wget.ps1
else
SEP   := $(strip /)
CAT   := cat
TOUCH := touch
MKDIR := mkdir -p
WGET  := wget
endif
