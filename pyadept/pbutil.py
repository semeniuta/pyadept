"""
Protobuf utilities
"""

def get_attributes_dict(attr_entries):
    """
    Handle Protobuf AttributeList.entries defined below, and return
    the attibutes as a dictionary.

    syntax = "proto2";

    message Attribute {

        enum Type { STRING = 1; DOUBLE = 2; INT = 3; }

        required Type type = 1;

        required string key = 2;

        optional string str_val = 3;
        optional double double_val = 4;
        optional int32 int_val = 5;

    }

    message AttributeList {
        repeated Attribute entries = 1;
    }

    """

    attr_dict = dict()
    for entry in attr_entries:

        if entry.type == 1:
            val = entry.str_val
        elif entry.type == 2:
            val = entry.double_val
        else:
            val = entry.int_val

        attr_dict[entry.key] = val

    return attr_dict
