# Copyright (C) 2020-2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
<#
.SYNOPSIS
    Creates a file or update modification time.

.PARAMETER path
    The parameter path is the file to be created / updated.

.EXAMPLE
    Make the C:\random\test123 file
    PS C:\> touch C:\random\test123
    Update the C:\random\test123 modification time (as it now exists).
    PS C:\> touch C:\random\test123

.NOTES
    Author: SymbiFlow Authors
    License: ISC
#>
param (
    [string]$filename
)

if (Test-Path $filename) {
    (Get-ChildItem $filename).LastWriteTime = Get-Date
} else {
    New-Item -Path $filename -ItemType File | Out-Null
}
