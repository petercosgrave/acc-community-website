@ECHO OFF
set datetimeft=%date:~0,2%%date:~3,2%%date:~-4%%time:~0,2%00
curl -s http://127.0.0.1:5000/stop-server/?event_type=hourly
netsh advfirewall firewall delete rule profile=domain,private,public name="accServerIn_%datetimeft%"
netsh advfirewall firewall delete rule profile=domain,private,public name="accServerOut_%datetimeft%"