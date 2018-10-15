"""
Utilities for creation and processing
of strings and byte sequences
"""

import uuid


def generate_id_str():
    return str(uuid.uuid4())[:8]


def generate_id_bytes():
    return generate_id_str().encode()


def vec_to_str(vec):

    size = len(vec)
    template = '{:.3f},'*size
    template = template[:-1]
    vec_str = template.format(*vec)

    return vec_str


def split_data(data, delimiter):

    if not data:
        return None, None

    messages = data.split(delimiter)
    n = len(messages)

    if n == 1:
        return None, data

    else:

        if data.endswith(delimiter):
            return messages[:-1], None
        else:
            return messages[:-1], messages[-1]
