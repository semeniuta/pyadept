import numpy as np
from pyadept.commands import MoveRelWorld

if __name__ == '__main__':
    cmd = MoveRelWorld(np.array([0, 0, 10, 0, 45, 0]))
    print(cmd.get_bytes())


