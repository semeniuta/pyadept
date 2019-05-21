// Grammar for Adept server commands

root ::= command_message_chain
command_message_chain ::= command_message+
command_message ::= motion_msg | break_msg | air_msg | speed_msg
speed_msg ::= "set_speed" ":" (digit | digit digit | digit digit digit) // speed factor range: 0-100
air_msg ::= ('enable_air' | 'disable_air') delimiter
break_msg ::= "break" delimiter
motion_msg ::= motion_command_name ":" location delimiter
motion_command_name ::= "move_to" | "move_rel_world" | "move_rel_tool" | "move_joints" | "move_rel_joints"
location ::= real "," real "," real "," real "," real "," real
real ::= digit+ "." fractional;
fractional ::= digit digit digit
digit ::= [0-9]
delimiter ::= "\r\n"
