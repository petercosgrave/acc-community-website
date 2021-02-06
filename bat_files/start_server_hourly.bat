@ECHO OFF
set datetimeft=%date:~0,2%%date:~3,2%%date:~-4%%time:~0,2%00
netsh advfirewall firewall add rule name="accServerOut_%datetimeft%" dir=out action=allow program=C:\Users\peter\Documents\acc-community-website\servers\%datetimeft%\accServer.exe enable=yes profile=domain,private,public
netsh advfirewall firewall add rule name="accServerIn_%datetimeft%" dir=in action=allow program=C:\Users\peter\Documents\acc-community-website\servers\%datetimeft%\accServer.exe enable=yes profile=domain,private,public
curl -s http://127.0.0.1:5000/start-server/?event_type=hourly