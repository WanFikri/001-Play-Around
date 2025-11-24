###Prerequisite from Windows (Target) 

###Enable SSH-Server on Windows’s optional features 

###Allow inbound connections on port 22 

netsh advfirewall firewall add rule name=sshd dir=in action=allow protocol=TCP localport=22 

###Create the SSH Server service and set it to start automatically. 

Set-Service -Name sshd -StartupType 'Automatic' 

###Start SSH services 

Start-Service sshd 
