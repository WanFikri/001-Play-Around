###Prerequisite from Windows (Target) 

###Enables WinRM service 

winrm quickconfig –q 

###Create self-signed certificate if none exists 

$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -like "WinRM" } | Select-Object -First 1 if (-not $cert) { $hostname = $env:COMPUTERNAME $cert = New-SelfSignedCertificate -DnsName $hostname -CertStoreLocation Cert:\LocalMachine\My -FriendlyName "WinRM Self-Signed Cert" Write-Host "Created certificate: $($cert.Thumbprint)" } else { Write-Host "Using existing certificate: $($cert.Thumbprint)" } 

###Creates HTTPS listener (port 5986) -> using self-signed certificate 

$listener = winrm enumerate winrm/config/listener | findstr HTTPS  

if (-not $listener) {  

    New-Item -Path WSMan:\LocalHost\Listener -Transport HTTPS Address * -CertificateThumbprint $cert.Thumbprint | Out-Null  

    Write-Host "HTTPS listener created on port 5986"  

} else {  

    Write-Host "HTTPS listener already exists"  

} 

###Enables Basic Authentication 

Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $true 

###Configures firewall rule 

if (-not (Get-NetFirewallRule -DisplayName "WinRM HTTPS (5986)" ErrorAction SilentlyContinue)) { 

    New-NetFirewallRule -DisplayName "WinRM HTTPS (5986)" Direction Inbound -Protocol TCP -LocalPort 5986 -Action Allow | Out-Null 

    Write-Host "Firewall rule created" 

} else { 

    Write-Host "Firewall rule already exists" 

} 

###Verifies configuration 

winrm enumerate winrm/config/listener 

winrm get winrm/config/service 

Enable-WSManCredSSP -Role Server 
