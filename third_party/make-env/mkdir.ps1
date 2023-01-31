# Copyright (C) 2020-2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
<#
.SYNOPSIS
    Creates a directory if it doesn't exist.

.PARAMETER path
    The parameter path is the directory to be created.

.EXAMPLE
    Make the C:\random\test123 directory
    PS C:\> mkdir C:\random\test123 directory

.NOTES
    Author: SymbiFlow Authors
    License: ISC
#>
param (
    [string]$filename
)

New-Item -Path $filename -ItemType directory -Force | Out-Null
