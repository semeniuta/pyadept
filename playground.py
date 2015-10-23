from adeptclient import AdeptClient
import config
import time

host = config.controller_ip
port = config.controller_port

client = AdeptClient()
client.connect_to_server(host, port)

client.send_msg("move_relative:0,-5,0,0,0,0")
client.send_msg("break")
client.send_msg("movehome")
