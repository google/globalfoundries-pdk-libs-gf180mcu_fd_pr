# Copyright (C) 2020-2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
<#
.SYNOPSIS
    Downloads a file if it doesn't exist.

.PARAMETER url
    URL of the file to be download downloaded.

.PARAMETER o
    The value '-O'

.PARAMETER output
    The output file to downloading into.

.EXAMPLE
    Make the C:\random\test123 file
    PS C:\> wget https://example.com/file.zip C:\random\file.zip

.NOTES
    Author: SymbiFlow Authors
    License: ISC
#>
$url=$args[0]
$o=$args[1]
$output=$args[2]

# Download with HTTPS
$AllProtocols = [System.Net.SecurityProtocolType]'Ssl3,Tls,Tls11,Tls12'
[System.Net.ServicePointManager]::SecurityProtocol = $AllProtocols
$ProgressPreference = 'SilentlyContinue' # Faster download with Invoke-WebRequest

$outdir = Split-Path -Path $output
New-Item -Path $outdir -ItemType directory -Force

If(!(test-path $output)) {
    Write-Host "'$output' is missing."
    Invoke-WebRequest $url -OutFile $output
    Write-Host "'$output' download."
} else {
    Write-Host "'$output' already exists."
}
