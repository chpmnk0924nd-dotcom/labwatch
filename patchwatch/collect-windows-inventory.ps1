$ErrorActionPreference = "Stop"

$outputDirectory = "D:\Scripts\LabWatch\patchwatch\data"
$outputFile = Join-Path $outputDirectory "windows-host.json"

New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null

$computerSystem = Get-CimInstance Win32_ComputerSystem
$operatingSystem = Get-CimInstance Win32_OperatingSystem

$fixedDisks = Get-CimInstance Win32_LogicalDisk |
    Where-Object {
        $_.DriveType -eq 3 -and
        $_.Size -ne $null
    }

$totalDiskBytes = (
    $fixedDisks |
    Measure-Object -Property Size -Sum
).Sum

$totalFreeBytes = (
    $fixedDisks |
    Measure-Object -Property FreeSpace -Sum
).Sum

$networkConfig = Get-NetIPConfiguration |
    Where-Object {
        $_.IPv4Address -and
        $_.IPv4DefaultGateway
    } |
    Select-Object -First 1

$lastBoot = $operatingSystem.LastBootUpTime
$uptime = (Get-Date) - $lastBoot

$pendingUpdates = 0
$pendingSecurityUpdates = 0
$updateScanStatus = "NotChecked"

try {
    $updateSession = New-Object -ComObject Microsoft.Update.Session
    $updateSearcher = $updateSession.CreateUpdateSearcher()

    $searchResult = $updateSearcher.Search(
        "IsInstalled=0 and IsHidden=0"
    )

    $pendingUpdates = $searchResult.Updates.Count

    foreach ($update in $searchResult.Updates) {
        $isSecurityUpdate = $false

        foreach ($category in $update.Categories) {
            if (
                $category.Name -match "Security Updates" -or
                $category.Name -match "Critical Updates"
            ) {
                $isSecurityUpdate = $true
                break
            }
        }

        if (
            $update.Title -match "Microsoft Defender" -or
            $update.Title -match "Security Intelligence" -or
            $update.Title -match "KB2267602"
        ) {
            $isSecurityUpdate = $true
        }

        if ($isSecurityUpdate) {
            $pendingSecurityUpdates++
        }
    }

    $updateScanStatus = "Completed"
}
catch {
    $updateScanStatus = "Failed: $($_.Exception.Message)"
}

if ($pendingSecurityUpdates -gt 0) {
    $complianceStatus = "Security Updates Required"
}
elseif ($pendingUpdates -gt 0) {
    $complianceStatus = "Updates Available"
}
else {
    $complianceStatus = "Current"
}

$inventory = [ordered]@{
    hostname                 = $env:COMPUTERNAME
    ip_address               = $networkConfig.IPv4Address.IPAddress
    operating_system         = $operatingSystem.Caption
    os_version               = $operatingSystem.Version
    pending_updates          = $pendingUpdates
    pending_security_updates = $pendingSecurityUpdates
    last_boot_time           = $lastBoot.ToString("yyyy-MM-dd HH:mm:ss")
    uptime_days              = [math]::Round($uptime.TotalDays, 2)

    disk_total_gb = [math]::Round(
        $totalDiskBytes / 1GB,
        2
    )

    disk_free_gb = [math]::Round(
        $totalFreeBytes / 1GB,
        2
    )

    compliance_status  = $complianceStatus
    scan_source        = "Windows PowerShell"
    update_scan_status = $updateScanStatus

    scanned_at = (Get-Date).ToString(
        "yyyy-MM-dd HH:mm:ss"
    )
}

$inventory |
    ConvertTo-Json -Depth 4 |
    Set-Content -Path $outputFile -Encoding UTF8

Write-Host "PatchWatch inventory saved to:"
Write-Host $outputFile
Write-Host ""

$inventory | Format-List


