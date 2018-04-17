import numpy as np
from pyadept.rcommands import MoveRelWorld
from pyadept.rsession import RobotSession

ROBOT_HOST = '172.16.120.64'
ROBOT_PORT = 1234

if __name__ == '__main__':

    cmd = MoveRelWorld(np.array([0, 0, 10, 0, 45, 0]))

    session = RobotSession()
    session.connect(ROBOT_HOST, ROBOT_PORT)

    session.cmdsend([cmd])

