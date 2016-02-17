from adeptclient import AdeptClient
import config
import time

host = config.controller_ip
port = config.controller_port

client = AdeptClient()
client.connect_to_server(host, port)


#client.send_msg("movehome")
#for i in range(5):
#    client.send_msg("move_rel_tool:0,-50,0,0,0,0")
#    client.send_msg("break")
#client.send_msg("moveinterm")
#client.send_msg("break")
#client.send_msg("movehome")

client.send_msg("movehome")
client.send_msg("break")
client.send_msg("move_rel_tool:50,0,0,0,0,0")
client.send_msg("break")
client.send_msg("move_rel_tool:0,50,0,0,0,0")
client.send_msg("break")
client.send_msg("move_rel_tool:0,0,50,0,0,0")
client.send_msg("break")
client.send_msg("movehome")

#client.send_msg("moveinterm")
#client.send_msg("break")
#client.send_msg("movehome")
#client.send_msg("break")

#client.send_msg("fcalib_sc")
#client.send_msg("break")

#client.send_msg('stop_server')
