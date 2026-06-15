$ErrorActionPreference = "Stop"

$LabWatchDirectory = "D:\Scripts\LabWatch"
$PatchWatchDirectory = Join-Path $LabWatchDirectory "patchwatch"
$DataDirectory = Join-Path $PatchWatchDirectory "data"
$LogFile = Join-Path $PatchWatchDirectory "patchwatch-refresh.log"

$PythonExecutable = Join-Path `
    $LabWatchDirectory `
    "venv\Scripts\python.exe"

$Importer = Join-Path `
    $PatchWatchDirectory `
    "import_inventory.py"

$WindowsCollector = Join-Path `
    $PatchWatchDirectory `
    "collect-windows-inventory.ps1"

$DC01Collector = Join-Path `
    $PatchWatchDirectory `
    "collect-dc01-inventory.ps1"

function Write-PatchWatchLog {
    param(
        [Parameter(Mandatory)]
        [string]$Message
    )

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Entry = "[$Timestamp] $Message"

    Write-Host $Entry
    Add-Content -Path $LogFile -Value $Entry
}

try {
    Write-PatchWatchLog "PatchWatch refresh started."

    Write-PatchWatchLog "Collecting WIN11-01 inventory."
    & $WindowsCollector

    Write-PatchWatchLog "Collecting DC01 inventory."
    & $DC01Collector

    Write-PatchWatchLog "Pulling Ansible JSON files."
    & scp `
        "nick@192.168.10.151:/home/nick/ansible-homelab/output/*.json" `
        "$DataDirectory\"

    if ($LASTEXITCODE -ne 0) {
        throw "SCP failed with exit code $LASTEXITCODE."
    }

    Write-PatchWatchLog "Importing JSON files into PostgreSQL."
    & $PythonExecutable $Importer

    if ($LASTEXITCODE -ne 0) {
        throw "Importer failed with exit code $LASTEXITCODE."
    }

    Write-PatchWatchLog "PatchWatch refresh completed successfully."
}
catch {
    Write-PatchWatchLog "ERROR: $($_.Exception.Message)"
    exit 1
}