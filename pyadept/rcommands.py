import numpy as np
from pyadept.strutil import vec_to_str

DELIMITER = b'\r\n'
BREAK_CMD = b'break' + DELIMITER


def join_commands(*commands):
    return JoinedCommand(commands)


def create_motion_command(template, vec, break_move=True):

    vec_bytes = vec_to_str(vec)

    cmd_bytes = template.format(vec_bytes).encode() + DELIMITER

    if break_move:
        return cmd_bytes, BREAK_CMD

    return cmd_bytes,


class RobotCommand(object):

    def get_messages(self):
        return DELIMITER,

    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}[{}]'.format(class_name, self._repr_args())

    def _repr_args(self):
        return ''

    def __len__(self):
        return sum((len(msg) for msg in self.get_messages()))
         


class JoinedCommand(RobotCommand):

    def __init__(self, commands):

        messages = tuple()
        for cmd in commands:
            messages += cmd.get_messages()

        self._messages = messages
        self._commands_str = ','.join((str(cmd) for cmd in commands))

    def get_messages(self):
        return self._messages

    def _repr_args(self):
        return self._commands_str


class DirectCommand(RobotCommand):

    def __init__(self, cmd):
        self._cmd = cmd

    def get_messages(self):
        return self._cmd.encode() + DELIMITER,

    def _repr_args(self):
        return '"{}"'.format(self._cmd)


class SetSpeed(RobotCommand):

    def __init__(self, speed_factor):
        self._speed_factor = speed_factor

    def get_messages(self):
        return 'set_speed:{:d}'.format(self._speed_factor).encode() + DELIMITER,

    def _repr_args(self):
        return '{:d}'.format(self._speed_factor)


class MotionCommand(RobotCommand):

    def __init__(self, template, vec, break_move=True):

        assert len(vec) == 6

        self._template = template
        self._vec = vec
        self._break = break_move

    def get_messages(self):
        return create_motion_command(self._template, self._vec, self._break)

    def _repr_args(self):
        vs = vec_to_str(self._vec)
        return '{}, break={}'.format(vs, self._break)


class MoveToPose(MotionCommand):

    def __init__(self, pose, break_move=True):
        template = 'move_to:{:s}'
        super(MoveToPose, self).__init__(template, pose, break_move)


class MoveRelWorld(MotionCommand):

    def __init__(self, pose, break_move=True):
        template = 'move_rel_world:{:s}'
        super(MoveRelWorld, self).__init__(template, pose, break_move)


class MoveJoints(MotionCommand):

    def __init__(self, jconf, break_move=True):
        template = 'move_joints:{:s}'
        super(MoveJoints, self).__init__(template, jconf, break_move)


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
        self._z = z
        pose = np.array([0, 0, z, 0, 0, 0])
        super(MoveToolZ, self).__init__(pose, break_move)

    def _repr_args(self):
        return 'z={:.3f}, break={}'.format(self._z, self._break)
