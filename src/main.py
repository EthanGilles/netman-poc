# Configure routers here (netmiko to SSH into nodes and run commands)

from netmiko import ConnectHandler

routers = [
{
"device_type": "cisco_ios",
"host": "198.51.100.101",
"username": "netman",
"password": "password123",
"secret": "password123"
},
{
"device_type": "cisco_ios",
"host": "198.51.100.102",
"username": "netman",
"password": "password123",
"secret": "password123"
},
{
"device_type": "cisco_ios",
"host": "198.51.100.103",
"username": "netman",
"password": "password123",
"secret": "password123"
},
{
"device_type": "cisco_ios",
"host": "198.51.100.104",
"username": "netman",
"password": "password123",
"secret": "password123"
},
{
"device_type": "cisco_ios",
"host": "198.51.100.105",
"username": "netman",
"password": "password123",
"secret": "password123"
},
{
"device_type": "cisco_ios",
"host": "198.51.100.106",
"username": "netman",
"password": "password123",
"secret": "password123"
},
{
"device_type": "cisco_ios",
"host": "198.51.100.107",
"username": "netman",
"password": "password123",
"secret": "password123"
},
{
"device_type": "cisco_ios",
"host": "198.51.100.108",
"username": "netman",
"password": "password123",
"secret": "password123"
}
]

for r in routers:

    connection = ConnectHandler(**r)

    connection.enable()

    router_ip = r["host"]

    print(f"connecting to {router_ip}")

    if router_ip.endswith("101"):
        file = "configs/r1.cfg"
    elif router_ip.endswith("102"):
        file = "configs/r2.cfg"
    elif router_ip.endswith("103"):
        file = "configs/r3.cfg"
    elif router_ip.endswith("104"):
        file = "configs/r4.cfg"
    elif router_ip.endswith("105"):
        file = "configs/r5.cfg"
    elif router_ip.endswith("106"):
        file = "configs/r6.cfg"
    elif router_ip.endswith("107"):
        file = "configs/r7.cfg"
    elif router_ip.endswith("108"):
        file = "configs/r8.cfg"

    with open(file) as f:
        commands = f.read().splitlines()

    output = connection.send_config_set(commands)

    print(output)

    connection.disconnect()