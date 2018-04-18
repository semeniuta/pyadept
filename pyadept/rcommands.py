import numpy as np
from pyadept.strutil import vec_to_str

DELIMITER = b'\r\n'
BREAK_CMD = b'break' + DELIMITER


def create_motion_command(template, vec, break_move=True):

    vec_bytes = vec_to_str(vec)

    cmd_bytes = template.format(vec_bytes).encode() + DELIMITER

    if break_move:
        return cmd_bytes, BREAK_CMD

    return cmd_bytes


class RobotCommand(object):

    def get_bytes(self):
        return DELIMITER,


class DirectCommand(RobotCommand):

    def __init__(self, cmd):
        self._cmd = cmd

    def get_bytes(self):
        return self._cmd.encode() + DELIMITER,


class MotionCommand(RobotCommand):

    def __init__(self, template, vec, break_move=True):

        assert len(vec) == 6

        self._template = template
        self._vec = vec
        self._break = break_move

    def get_bytes(self):
        return create_motion_command(self._template, self._vec, self._break)


class MoveToPose(MotionCommand):

    def __init__(self, pose, break_move=True):
        template = 'move_to:{:s}'
        super(MoveToPose, self).__init__(template, pose, break_move)


class MoveRelWorld(MotionCommand):

    def __init__(self, pose, break_move=True):
        template = 'move_rel_world:{:s}'
        super(MoveRelWorld, self).__init__(template, pose, break_move)


class MoveRelJoints(MotionCommand):

    def __init__(self, jconf, break_move=True):
        template = 'move_rel_joints:{:s}'
        super(MoveRelJoints, self).__init__(template, jconf, break_move)


class MoveRelTool(MotionCommand):

    def __init__(self, pose, break_move=True):
        template = 'move_rel_tool:{:s}'
        super(MoveRelTool, self).__init__(template, pose, break_move)


class MoveToolZ(MoveRelTool):

    def __init__(self, z, break_move=True):
        pose = np.array([0, 0, z, 0, 0, 0])
        super(MoveToolZ, self).__init__(pose, break_move)

