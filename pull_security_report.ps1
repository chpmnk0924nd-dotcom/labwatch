$KeyFile = "$env:USERPROFILE\.ssh\labwatch_security_pull"
$RemoteFile = "nick@192.168.10.60:/home/nick/Projects/homelab-security-watch/reports/latest_security_report.txt"
$LocalFile = "D:\Scripts\LabWatch\security_reports\latest_security_report.txt"

scp -i $KeyFile $RemoteFile $LocalFile