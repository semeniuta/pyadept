from adeptclient import AdeptClient
import config
import time

host = config.controller_ip
port = config.controller_port

client = AdeptClient()
client.connect_to_server(host, port)



client.send_msg("movehome")
for i in range(5):
    client.send_msg("move_relative:0,-50,0,0,0,0")
    client.send_msg("break")
client.send_msg("moveinterm")
client.send_msg("break")
client.send_msg("movehome")
