import numpy as np
from adeptclient import AdeptClient

def vec_to_str(vec):
    size = len(vec)
    template = '{.3f},'*size
    template = template[:-1]
    return template.format(vec)


class AdeptAgent:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = AdeptClient()
        self.frames = dict()

    def connect(self):
        self.client.connect_to_server(self.host, self.port)

    def add_frame(self, fname, pose):
        self.frames[fname] = np.array(pose)

    def move_rel_tool(self, pose, break_move=True):
        pose_str = vec_to_str(pose)
        self.client.send_msg("move_rel_tool:{:s}".format(pose_str))
        if break_move:
            self.client.send_msg("break")

    def move_rel_world(self, pose, break_move=True):
        pose_str = vec_to_str(pose)
        self.client.send_msg("move_rel_world:{:s}".format(pose_str))
        if break_move:
            self.client.send_msg("break")

    def move_rel_frame(self, fname, pose, break_move=True):
        vec = np.hstack((self.frames[fname], np.array(pose)))
        cmd = vec_to_str(vec)
        self.client.send_msg("move_rel_frame:{:s}".format(cmd))
        if break_move:
            self.client.send_msg("break")

    def move_tool_z(self, z, break_move=True):
        self.move_rel_tool([0,0,z,0,0,0], break_move)

    def move_to(self, pose, break_move=True):
        pose_str = vec_to_str(pose)
        self.client.send_msg("move_to:{:s}".format(pose_str))
        if break_move:
            self.client.send_msg("break")

    def move_dedicated(self, name, break_move=True):
        self.client.send_msg(name)
        if break_move:
            self.client.send_msg("break")

    def execute(self, program):
        self.client.send_msg(program)

    def get_tool(self, tool_id):
        self.client.send_msg("get_tool:{:d}".format(tool_id))

if __name__ == '__main__':
    import config
    host = config.controller_ip
    port = config.controller_port
    a = AdeptAgent(host, port)
    a.connect()
