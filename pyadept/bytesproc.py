

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
